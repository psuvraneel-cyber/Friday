from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, default='')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Car(models.Model):
    CAR_TYPES = (
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('coupe', 'Coupe'),
        ('hatchback', 'Hatchback'),
    )
    STATUS_CHOICES = [
        ('is_available', 'Available'),
        ('pending', 'Pending Sale'),
        ('sold', 'Sold'),
        ('maintenance', 'In Maintenance'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='is_available'
    )
    
    make = models.CharField(max_length=25)
    model = models.CharField(max_length=25)
    year = models.PositiveIntegerField()
    vin = models.CharField(max_length=17, unique=True)
    fuel_type = models.CharField(max_length=50, default='Petrol')
    transmission = models.CharField(max_length=50, default='Automatic')
    car_type = models.CharField(max_length=20, choices=CAR_TYPES, default='sedan')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mileage = models.PositiveIntegerField()
    color = models.CharField(max_length=30)
    description = models.CharField(max_length=2000, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Image URL",
        help_text="Enter full URL to the car image"
    )
    is_featured = models.BooleanField(default=False, verbose_name="Featured Car")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Date Added")
    
    
    class Meta:
        ordering = ['-date_added']
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.vin})"

class Sale(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('credit', 'Credit Card'),
        ('finance', 'Bank Finance'),
        ('check', 'Check'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    notes = models.TextField(blank=True)
    sales_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales_as_salesperson'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    


class CarFeature(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, blank=True, 
                          help_text="Font Awesome icon class (e.g., 'fas fa-car')")
    
    def __str__(self):
        return self.name



class SalesPerson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    hire_date = models.DateField()
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# models.py
class TestDrive(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, default=None)
    customer_email = models.EmailField(default=None)
    customer_phone = models.CharField(max_length=20, default=None)
    scheduled_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"Test Drive - {self.car} by {self.customer_name}"


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Inquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Inquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inquiry from {self.name} about {self.car or 'general'}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email
    
    
class Order(models.Model):
    # ... existing fields
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ), default='pending')