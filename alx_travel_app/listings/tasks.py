"""
Celery tasks for the listings app
This module contains asynchronous tasks for sending notifications.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id, user_email, user_name, 
                                    listing_title, check_in, check_out):
    """
    Send a booking confirmation email to the user.
    
    This task runs asynchronously to avoid blocking the request-response cycle.
    
    Args:
        booking_id (int): The ID of the booking
        user_email (str): Email address of the user
        user_name (str): Name of the user
        listing_title (str): Title of the booked listing
        check_in (str): Check-in date
        check_out (str): Check-out date
    
    Returns:
        dict: Success status and message
    """
    try:
        # Email subject
        subject = f'Booking Confirmation - {listing_title}'
        
        # Email body
        message = f"""
Dear {user_name},

Thank you for your booking!

Booking Details:
----------------
Booking ID: {booking_id}
Property: {listing_title}
Check-in: {check_in}
Check-out: {check_out}

We look forward to hosting you!

Best regards,
ALX Travel App Team
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        print(f"✅ Booking confirmation email sent to {user_email} for booking #{booking_id}")
        
        return {
            'status': 'success',
            'message': f'Email sent to {user_email}',
            'booking_id': booking_id
        }
        
    except Exception as exc:
        # Retry the task if it fails
        print(f"❌ Failed to send email for booking #{booking_id}: {str(exc)}")
        
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
