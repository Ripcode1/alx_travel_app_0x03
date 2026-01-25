# ALX Travel App - Chapa Payment Integration

A Django-based travel booking application with integrated Chapa payment gateway for secure online payments.

## 📋 Project Overview

This project demonstrates the integration of the **Chapa Payment Gateway** into a Django REST API application for handling travel bookings and payments.

### Key Features

- ✅ Travel listings and booking management
- ✅ Chapa payment gateway integration
- ✅ Secure payment initiation and verification
- ✅ Asynchronous email notifications (Celery)
- ✅ RESTful API with Django REST Framework
- ✅ PostgreSQL database
- ✅ Complete admin dashboard

## 🚀 Quick Start

```bash
# Navigate to project
cd alx_travel_app

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your CHAPA_SECRET_KEY to .env

# Setup database
python manage.py migrate

# Run server
python manage.py runserver
```

## 📁 Project Structure

```
alx_travel_app_0x02/
├── README.md                    # This file
└── alx_travel_app/             # Django project
    ├── listings/               # Main app
    │   ├── models.py          # Payment, Booking, Listing models
    │   ├── views.py           # Chapa API integration
    │   ├── serializers.py     # DRF serializers
    │   └── tasks.py           # Celery tasks
    ├── settings.py            # Project settings
    ├── urls.py                # URL configuration
    ├── requirements.txt       # Dependencies
    └── README.md              # Detailed documentation
```

## 💳 Payment Flow

1. **Create Booking** → User creates a travel booking
2. **Initiate Payment** → POST to `/api/payments/initiate/`
3. **User Pays** → Redirect to Chapa checkout page
4. **Verify Payment** → GET `/api/payments/verify/?reference=XXX`
5. **Confirm Booking** → Booking status updated, email sent

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bookings/` | Create new booking |
| POST | `/api/payments/initiate/` | Initiate payment with Chapa |
| GET | `/api/payments/verify/` | Verify payment status |
| GET | `/api/payments/status/<id>/` | Get payment details |
| GET | `/api/listings/` | List available properties |

## 🔧 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery)
- Chapa API account ([Get API keys](https://developer.chapa.co/))

## 📖 Full Documentation

For complete setup instructions, API documentation, and testing guide, see:

**[alx_travel_app/README.md](alx_travel_app/README.md)**

## 🧪 Testing

### Chapa Test Cards

Use these test cards in sandbox mode:

- **Success**: 4200 0000 0000 0000
- **Failed**: 4100 0000 0000 0000
- **CVV**: Any 3 digits
- **Expiry**: Any future date
- **OTP**: 123456

### Example API Test

```bash
# Initiate payment
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "YOUR_BOOKING_ID",
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+251911234567"
  }'
```

## 📸 Manual Review Documentation

For manual review, include screenshots of:

1. ✅ Payment initiation API response (with checkout_url)
2. ✅ Chapa payment page
3. ✅ Payment verification response
4. ✅ Django admin showing Payment record
5. ✅ Booking status updated to "confirmed"
6. ✅ Confirmation email (if configured)

## 🔐 Security

- ✅ API keys stored in environment variables
- ✅ Secure payment processing via Chapa
- ✅ HTTPS required for production
- ✅ Input validation on all endpoints
- ✅ Transaction logging

## 📝 Environment Variables

Required in `.env`:

```bash
CHAPA_SECRET_KEY=your-chapa-secret-key
DB_NAME=travel_app_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

## 🤝 Contributing

This is an educational project for ALX Backend Specialization.

## 📄 License

ALX Backend Specialization Program

## 🆘 Support

- Chapa Docs: https://developer.chapa.co/docs
- Django REST Framework: https://www.django-rest-framework.org/
- Celery: https://docs.celeryproject.org/

---

**Repository**: `alx_travel_app_0x02`  
**Directory**: `alx_travel_app`  
**Files**: `listings/views.py`, `listings/models.py`, `README.md`
