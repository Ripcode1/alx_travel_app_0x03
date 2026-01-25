"""
Models for the listings app - Listings, Bookings, and Payments
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Listing(models.Model):
    """Travel listing model"""
    PROPERTY_TYPES = [
        ('hotel', 'Hotel'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('resort', 'Resort'),
        ('hostel', 'Hostel'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    location = models.CharField(max_length=255)
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    max_guests = models.PositiveIntegerField(default=1)
    available = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.location}"


class Booking(models.Model):
    """Booking model for travel reservations"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    booking_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    check_in = models.DateField()
    check_out = models.DateField()
    number_of_guests = models.PositiveIntegerField()
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.email}"

    def calculate_total_price(self):
        """Calculate total price based on number of nights"""
        if self.check_out and self.check_in:
            nights = (self.check_out - self.check_in).days
            if nights > 0:
                self.total_price = self.listing.price_per_night * nights
                return self.total_price
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        """Override save to calculate total price"""
        if not self.total_price or self.total_price == 0:
            self.calculate_total_price()
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment model to track Chapa payment transactions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    payment_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="Transaction ID from Chapa"
    )
    reference = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique reference for this payment"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='ETB')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    
    # Chapa response data
    chapa_reference = models.CharField(max_length=255, blank=True, null=True)
    checkout_url = models.URLField(blank=True, null=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional metadata
    error_message = models.TextField(blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-initiated_at']

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"

    def mark_as_completed(self, transaction_id=None):
        """Mark payment as completed"""
        from django.utils import timezone
        self.status = 'completed'
        if transaction_id:
            self.transaction_id = transaction_id
        self.completed_at = timezone.now()
        self.save()
        
        # Update booking status
        self.booking.status = 'confirmed'
        self.booking.save()

    def mark_as_failed(self, error_message=None):
        """Mark payment as failed"""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message
        self.save()
        
        # Update booking status
        self.booking.status = 'cancelled'
        self.booking.save()
