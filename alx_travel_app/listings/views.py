"""
Views for the listings app - Including Chapa payment integration
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
import requests
import uuid
import logging

from .models import Listing, Booking, Payment
from .serializers import (
    ListingSerializer,
    BookingSerializer,
    PaymentSerializer,
    PaymentInitiateSerializer,
    PaymentVerifySerializer
)
from .tasks import send_booking_confirmation_email

logger = logging.getLogger(__name__)


class ListingViewSet(viewsets.ModelViewSet):
    """ViewSet for Listing model"""
    queryset = Listing.objects.filter(available=True)
    serializer_class = ListingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter listings by query parameters"""
        queryset = super().get_queryset()
        
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filter by property type
        property_type = self.request.query_params.get('property_type', None)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Filter by max price
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        return queryset


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return bookings for the current user"""
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create booking and initiate payment"""
        booking = serializer.save(user=self.request.user)
        
        # Calculate total price
        booking.calculate_total_price()
        booking.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    Initiate payment with Chapa API
    
    Expected payload:
    {
        "booking_id": "uuid-of-booking",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+251911234567"
    }
    """
    serializer = PaymentInitiateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    booking_id = serializer.validated_data['booking_id']
    email = serializer.validated_data['email']
    first_name = serializer.validated_data['first_name']
    last_name = serializer.validated_data['last_name']
    phone_number = serializer.validated_data.get('phone_number', '')

    # Get booking
    try:
        booking = Booking.objects.get(
            booking_id=booking_id,
            user=request.user
        )
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if payment already exists
    if hasattr(booking, 'payment'):
        if booking.payment.status in ['completed', 'processing']:
            return Response(
                {"error": "Payment already initiated or completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Generate unique reference
    reference = f"TRV-{uuid.uuid4().hex[:12].upper()}"

    # Create Payment record
    payment = Payment.objects.create(
        booking=booking,
        reference=reference,
        amount=booking.total_price,
        currency='ETB',
        status='pending'
    )

    # Prepare Chapa API request
    chapa_url = f"{settings.CHAPA_BASE_URL}/transaction/initialize"
    
    payload = {
        "amount": str(booking.total_price),
        "currency": "ETB",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "tx_ref": reference,
        "callback_url": f"{settings.CHAPA_CALLBACK_URL}?reference={reference}",
        "return_url": f"{settings.CHAPA_CALLBACK_URL}?reference={reference}",
        "customization": {
            "title": f"Booking Payment - {booking.listing.title}",
            "description": f"Payment for booking {booking.booking_id}"
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Make request to Chapa API
        response = requests.post(chapa_url, json=payload, headers=headers, timeout=30)
        response_data = response.json()

        logger.info(f"Chapa API Response: {response_data}")

        if response.status_code == 200 and response_data.get('status') == 'success':
            # Update payment with Chapa response
            payment.checkout_url = response_data['data']['checkout_url']
            payment.chapa_reference = response_data['data'].get('tx_ref', reference)
            payment.status = 'processing'
            payment.raw_response = response_data
            payment.save()

            return Response({
                "status": "success",
                "message": "Payment initiated successfully",
                "data": {
                    "payment_id": str(payment.payment_id),
                    "reference": payment.reference,
                    "checkout_url": payment.checkout_url,
                    "amount": str(payment.amount),
                    "currency": payment.currency
                }
            }, status=status.HTTP_200_OK)
        else:
            # Payment initiation failed
            error_message = response_data.get('message', 'Payment initiation failed')
            payment.mark_as_failed(error_message)
            
            logger.error(f"Chapa API Error: {response_data}")
            
            return Response({
                "status": "error",
                "message": error_message,
                "data": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.RequestException as e:
        # Network or request error
        error_message = f"Failed to connect to payment gateway: {str(e)}"
        payment.mark_as_failed(error_message)
        
        logger.error(f"Payment initiation error: {str(e)}")
        
        return Response({
            "status": "error",
            "message": error_message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        # Unexpected error
        error_message = f"Unexpected error: {str(e)}"
        payment.mark_as_failed(error_message)
        
        logger.error(f"Unexpected payment error: {str(e)}")
        
        return Response({
            "status": "error",
            "message": "An unexpected error occurred"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_payment(request):
    """
    Verify payment with Chapa API
    
    Expected query parameter: reference or tx_ref
    """
    # Get reference from query params
    reference = request.query_params.get('reference') or request.query_params.get('tx_ref')
    
    if not reference:
        return Response(
            {"error": "Payment reference is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get payment record
    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if already completed
    if payment.status == 'completed':
        return Response({
            "status": "success",
            "message": "Payment already verified and completed",
            "data": PaymentSerializer(payment).data
        }, status=status.HTTP_200_OK)

    # Verify with Chapa API
    chapa_url = f"{settings.CHAPA_BASE_URL}/transaction/verify/{reference}"
    
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
    }

    try:
        # Make verification request
        response = requests.get(chapa_url, headers=headers, timeout=30)
        response_data = response.json()

        logger.info(f"Chapa Verification Response: {response_data}")

        if response.status_code == 200 and response_data.get('status') == 'success':
            transaction_data = response_data.get('data', {})
            transaction_status = transaction_data.get('status')

            # Update payment based on transaction status
            if transaction_status == 'success':
                transaction_id = transaction_data.get('reference')
                payment.mark_as_completed(transaction_id=transaction_id)
                payment.payment_method = transaction_data.get('method', '')
                payment.raw_response = response_data
                payment.save()

                # Send confirmation email asynchronously
                send_booking_confirmation_email.delay(
                    booking_id=str(payment.booking.booking_id),
                    user_email=payment.booking.user.email
                )

                return Response({
                    "status": "success",
                    "message": "Payment verified and completed successfully",
                    "data": PaymentSerializer(payment).data
                }, status=status.HTTP_200_OK)
            
            elif transaction_status == 'failed':
                payment.mark_as_failed("Payment failed at gateway")
                payment.raw_response = response_data
                payment.save()

                return Response({
                    "status": "failed",
                    "message": "Payment verification failed",
                    "data": PaymentSerializer(payment).data
                }, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                # Payment still pending or processing
                payment.status = 'processing'
                payment.raw_response = response_data
                payment.save()

                return Response({
                    "status": "processing",
                    "message": "Payment is still being processed",
                    "data": PaymentSerializer(payment).data
                }, status=status.HTTP_200_OK)

        else:
            error_message = response_data.get('message', 'Verification failed')
            logger.error(f"Chapa Verification Error: {response_data}")
            
            return Response({
                "status": "error",
                "message": error_message
            }, status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.RequestException as e:
        error_message = f"Failed to verify payment: {str(e)}"
        logger.error(f"Payment verification error: {str(e)}")
        
        return Response({
            "status": "error",
            "message": error_message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected verification error: {str(e)}")
        
        return Response({
            "status": "error",
            "message": "An unexpected error occurred"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, payment_id):
    """Get payment status by payment ID"""
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        
        # Check if user owns this payment's booking
        if payment.booking.user != request.user:
            return Response(
                {"error": "Unauthorized access"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response({
            "status": "success",
            "data": PaymentSerializer(payment).data
        }, status=status.HTTP_200_OK)

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found"},
            status=status.HTTP_404_NOT_FOUND
        )
