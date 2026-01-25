from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

# Available endpoints:
# 
# Listings:
# - GET    /api/listings/                     - List all listings
# - POST   /api/listings/                     - Create a new listing
# - GET    /api/listings/{id}/                - Retrieve a specific listing
# - PUT    /api/listings/{id}/                - Update a listing
# - PATCH  /api/listings/{id}/                - Partial update a listing
# - DELETE /api/listings/{id}/                - Delete a listing
# - GET    /api/listings/my_listings/         - Get current user's listings
# - GET    /api/listings/available/           - Get available listings
# - POST   /api/listings/{id}/toggle_availability/ - Toggle listing availability
#
# Bookings:
# - GET    /api/bookings/                     - List all bookings
# - POST   /api/bookings/                     - Create a new booking
# - GET    /api/bookings/{id}/                - Retrieve a specific booking
# - PUT    /api/bookings/{id}/                - Update a booking
# - PATCH  /api/bookings/{id}/                - Partial update a booking
# - DELETE /api/bookings/{id}/                - Delete a booking
# - GET    /api/bookings/my_bookings/         - Get current user's bookings
# - GET    /api/bookings/my_property_bookings/ - Get bookings for user's properties
# - GET    /api/bookings/upcoming/            - Get upcoming bookings
# - POST   /api/bookings/{id}/confirm/        - Confirm a booking (host only)
# - POST   /api/bookings/{id}/cancel/         - Cancel a booking
