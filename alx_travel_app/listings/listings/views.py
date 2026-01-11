"""
Views for the listings app
This module contains viewsets for handling bookings and other listing operations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Booking, Listing
from .serializers import BookingSerializer
from .tasks import send_booking_confirmation_email


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    Automatically sends email confirmation when a booking is created.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter bookings to show only the current user's bookings.
        """
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Create a booking and trigger the email notification task.
        """
        # Save the booking with the current user
        booking = serializer.save(user=self.request.user)
        
        # Trigger the async email task
        # Using delay() to run the task asynchronously
        send_booking_confirmation_email.delay(
            booking_id=booking.id,
            user_email=booking.user.email,
            user_name=booking.user.get_full_name() or booking.user.username,
            listing_title=booking.listing.title,
            check_in=str(booking.check_in),
            check_out=str(booking.check_out)
        )
        
        print(f"📧 Email task queued for booking #{booking.id}")
    
    def create(self, request, *args, **kwargs):
        """
        Create a new booking and return success response.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'message': 'Booking created successfully! Confirmation email will be sent shortly.',
                'booking': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listings.
    """
    queryset = Listing.objects.all()
    
    def get_permissions(self):
        """
        Only authenticated users can create/update/delete listings.
        Anyone can view listings.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []
