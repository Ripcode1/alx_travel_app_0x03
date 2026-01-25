#!/usr/bin/env python3
"""Management command to seed the database with sample data."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from decimal import Decimal
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seeds the database with sample listings, bookings, and reviews'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Create sample users
        self.stdout.write('Creating users...')
        host1 = User.objects.create_user(
            username='host1',
            email='host1@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        
        host2 = User.objects.create_user(
            username='host2',
            email='host2@example.com',
            password='password123',
            first_name='Jane',
            last_name='Smith'
        )
        
        guest1 = User.objects.create_user(
            username='guest1',
            email='guest1@example.com',
            password='password123',
            first_name='Alice',
            last_name='Johnson'
        )
        
        guest2 = User.objects.create_user(
            username='guest2',
            email='guest2@example.com',
            password='password123',
            first_name='Bob',
            last_name='Williams'
        )
        
        # Create sample listings
        self.stdout.write('Creating listings...')
        listing1 = Listing.objects.create(
            host=host1,
            title='Cozy Beach House',
            description='Beautiful beach house with ocean views. Perfect for a relaxing getaway.',
            location='Malibu, California',
            price_per_night=Decimal('250.00')
        )
        
        listing2 = Listing.objects.create(
            host=host1,
            title='Mountain Cabin Retreat',
            description='Rustic cabin in the mountains. Great for hiking and nature lovers.',
            location='Aspen, Colorado',
            price_per_night=Decimal('180.00')
        )
        
        listing3 = Listing.objects.create(
            host=host2,
            title='Downtown Luxury Apartment',
            description='Modern apartment in the heart of the city. Close to restaurants and shops.',
            location='New York, NY',
            price_per_night=Decimal('350.00')
        )
        
        listing4 = Listing.objects.create(
            host=host2,
            title='Countryside Villa',
            description='Spacious villa surrounded by vineyards. Perfect for wine enthusiasts.',
            location='Napa Valley, California',
            price_per_night=Decimal('420.00')
        )
        
        listing5 = Listing.objects.create(
            host=host1,
            title='Lakeside Cottage',
            description='Charming cottage on a peaceful lake. Great for fishing and boating.',
            location='Lake Tahoe, Nevada',
            price_per_night=Decimal('200.00')
        )
        
        # Create sample bookings
        self.stdout.write('Creating bookings...')
        today = date.today()
        
        Booking.objects.create(
            listing=listing1,
            user=guest1,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15),
            total_price=Decimal('1250.00'),
            status='confirmed'
        )
        
        Booking.objects.create(
            listing=listing2,
            user=guest2,
            start_date=today + timedelta(days=20),
            end_date=today + timedelta(days=25),
            total_price=Decimal('900.00'),
            status='confirmed'
        )
        
        Booking.objects.create(
            listing=listing3,
            user=guest1,
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=8),
            total_price=Decimal('1050.00'),
            status='pending'
        )
        
        Booking.objects.create(
            listing=listing4,
            user=guest2,
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=33),
            total_price=Decimal('1260.00'),
            status='confirmed'
        )
        
        # Create sample reviews
        self.stdout.write('Creating reviews...')
        Review.objects.create(
            listing=listing1,
            user=guest1,
            rating=5,
            comment='Amazing place! The ocean view was breathtaking. Highly recommend!'
        )
        
        Review.objects.create(
            listing=listing2,
            user=guest2,
            rating=4,
            comment='Great cabin with beautiful surroundings. A bit remote but worth it.'
        )
        
        Review.objects.create(
            listing=listing3,
            user=guest1,
            rating=5,
            comment='Perfect location and very modern. Loved the amenities!'
        )
        
        Review.objects.create(
            listing=listing4,
            user=guest2,
            rating=5,
            comment='Wonderful villa! Great wine tours nearby. Will visit again.'
        )
        
        Review.objects.create(
            listing=listing5,
            user=guest1,
            rating=4,
            comment='Peaceful and relaxing. Perfect for a quiet weekend getaway.'
        )
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(f'Created {User.objects.count()} users')
        self.stdout.write(f'Created {Listing.objects.count()} listings')
        self.stdout.write(f'Created {Booking.objects.count()} bookings')
        self.stdout.write(f'Created {Review.objects.count()} reviews')
