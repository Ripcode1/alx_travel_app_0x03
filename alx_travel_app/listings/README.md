# ALX Travel App - Payment Integration with Chapa API

A Django-based travel booking application with integrated Chapa payment gateway for secure online payments.

## 🌟 Features

- **Travel Listings Management**: Browse and search available properties
- **Booking System**: Create and manage travel bookings
- **Chapa Payment Integration**: Secure payment processing with Chapa API
- **Payment Verification**: Automatic payment status verification
- **Email Notifications**: Asynchronous confirmation emails via Celery
- **RESTful API**: Complete API for all operations
- **Admin Dashboard**: Django admin for managing listings, bookings, and payments

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Payment Flow](#payment-flow)
- [Testing](#testing)
- [Project Structure](#project-structure)

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery)
- pip (Python package manager)
- virtualenv (recommended)

## 📥 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/alx_travel_app_0x02.git
cd alx_travel_app_0x02/alx_travel_app
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Django Configuration
SECRET_KEY=your-unique-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=travel_app_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Chapa API (Get from https://developer.chapa.co/)
CHAPA_SECRET_KEY=your-chapa-secret-key
CHAPA_BASE_URL=https://api.chapa.co/v1
CHAPA_CALLBACK_URL=http://localhost:8000/api/payments/verify/

# Email (Gmail example)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 2. Get Chapa API Credentials

1. Sign up at [Chapa Developer Portal](https://developer.chapa.co/)
2. Navigate to your dashboard
3. Get your Secret Key from API Keys section
4. For testing, use the **Test Mode** keys

## 🗄️ Database Setup

### 1. Create PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE travel_app_db;

# Create user (if needed)
CREATE USER your_db_user WITH PASSWORD 'your_db_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE travel_app_db TO your_db_user;

# Exit
\q
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

## 🚀 Running the Application

### 1. Start Redis Server

```bash
redis-server
```

### 2. Start Celery Worker

In a new terminal:

```bash
cd alx_travel_app_0x02/alx_travel_app
source venv/bin/activate
celery -A celery worker -l info
```

### 3. Start Django Development Server

In another terminal:

```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000`

## 📡 API Endpoints

### Listings

- **GET** `/api/listings/` - List all available listings
- **GET** `/api/listings/{id}/` - Get specific listing details
- **POST** `/api/listings/` - Create new listing (admin)

**Query Parameters for Listings:**
- `location`: Filter by location
- `property_type`: Filter by property type
- `max_price`: Filter by maximum price

### Bookings

- **GET** `/api/bookings/` - List user's bookings
- **POST** `/api/bookings/` - Create new booking
- **GET** `/api/bookings/{id}/` - Get booking details

### Payments

- **POST** `/api/payments/initiate/` - Initiate payment
- **GET/POST** `/api/payments/verify/` - Verify payment status
- **GET** `/api/payments/status/{payment_id}/` - Get payment status

## 💳 Payment Flow

### 1. Create a Booking

```bash
POST /api/bookings/
Content-Type: application/json
Authorization: Token YOUR_TOKEN

{
  "listing": 1,
  "check_in": "2025-12-20",
  "check_out": "2025-12-25",
  "number_of_guests": 2
}
```

**Response:**
```json
{
  "id": 1,
  "booking_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_price": "5000.00",
  "status": "pending"
}
```

### 2. Initiate Payment

```bash
POST /api/payments/initiate/
Content-Type: application/json
Authorization: Token YOUR_TOKEN

{
  "booking_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+251911234567"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment initiated successfully",
  "data": {
    "payment_id": "123e4567-e89b-12d3-a456-426614174000",
    "reference": "TRV-ABC123DEF456",
    "checkout_url": "https://checkout.chapa.co/checkout/payment/...",
    "amount": "5000.00",
    "currency": "ETB"
  }
}
```

### 3. User Completes Payment

- Redirect user to `checkout_url`
- User completes payment on Chapa's secure page
- Chapa redirects back to your callback URL

### 4. Verify Payment

```bash
GET /api/payments/verify/?reference=TRV-ABC123DEF456
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment verified and completed successfully",
  "data": {
    "payment_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "completed",
    "transaction_id": "CHW_...",
    "amount": "5000.00"
  }
}
```

### 5. Confirmation Email

After successful payment verification:
- Booking status updated to "confirmed"
- Confirmation email sent automatically via Celery

## 🧪 Testing

### Testing with Chapa Sandbox

Chapa provides test cards for sandbox testing:

**Test Card Numbers:**
- **Successful Payment**: 4200 0000 0000 0000
- **Failed Payment**: 4100 0000 0000 0000

**Test Card Details:**
- CVV: Any 3 digits
- Expiry: Any future date
- OTP: 123456

### Manual Testing Steps

1. **Create a test listing** via Django admin
2. **Create a booking** using the API
3. **Initiate payment** with test data
4. **Complete payment** using test card
5. **Verify payment status**
6. **Check email** for confirmation

### API Testing with cURL

```bash
# Test payment initiation
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "booking_id": "YOUR_BOOKING_ID",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+251911234567"
  }'

# Test payment verification
curl http://localhost:8000/api/payments/verify/?reference=TRV-ABC123DEF456
```

## 📁 Project Structure

```
alx_travel_app_0x02/
└── alx_travel_app/
    ├── listings/
    │   ├── migrations/
    │   ├── __init__.py
    │   ├── admin.py           # Django admin configuration
    │   ├── apps.py            # App configuration
    │   ├── models.py          # Listing, Booking, Payment models
    │   ├── serializers.py     # DRF serializers
    │   ├── tasks.py           # Celery tasks
    │   └── views.py           # API views with Chapa integration
    ├── .env.example           # Environment variables template
    ├── celery.py              # Celery configuration
    ├── manage.py              # Django management script
    ├── requirements.txt       # Python dependencies
    ├── settings.py            # Django settings
    ├── urls.py                # URL configuration
    └── README.md              # This file
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Keep it in `.gitignore`
2. **Use environment variables** for all sensitive data
3. **Use HTTPS in production** for callback URLs
4. **Validate all user inputs**
5. **Use Test Mode** for Chapa during development
6. **Implement rate limiting** for payment endpoints
7. **Log all payment transactions**

## 🐛 Troubleshooting

### Common Issues

**Issue: Payment initiation fails**
- Check Chapa API credentials in `.env`
- Verify you're using the correct API endpoint
- Check network connectivity

**Issue: Celery tasks not running**
- Ensure Redis is running
- Check Celery worker is started
- Verify `CELERY_BROKER_URL` in settings

**Issue: Email not sending**
- Check email configuration in `.env`
- For Gmail, use App-Specific Password
- Verify Celery worker is processing tasks

**Issue: Database connection error**
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists

## 📊 Payment Status Flow

```
Booking Created (pending)
    ↓
Payment Initiated (pending → processing)
    ↓
User Completes Payment on Chapa
    ↓
Payment Verified (processing → completed)
    ↓
Booking Confirmed (confirmed)
    ↓
Email Sent (via Celery)
```

## 🔍 Logging

All payment transactions are logged:
- Payment initiation requests
- Chapa API responses
- Verification results
- Email sending status

Check logs in console or configure Django logging to file.

## 📝 License

This project is part of the ALX Backend Specialization Program.

## 👥 Support

For issues or questions:
- Check Chapa documentation: https://developer.chapa.co/docs
- Review Django REST Framework docs: https://www.django-rest-framework.org/
- Check Celery docs: https://docs.celeryproject.org/

## ✨ Features in Development

- [ ] Multiple payment methods
- [ ] Refund processing
- [ ] Payment history dashboard
- [ ] Booking cancellation with refunds
- [ ] SMS notifications
- [ ] Multi-currency support

---

**Built with ❤️ for ALX Backend Specialization**
