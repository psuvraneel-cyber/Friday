from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Car, Customer, 
    SalesPerson, TestDrive,
    Service, Inquiry,
    NewsletterSubscriber
)
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from .models import Car, Sale, Customer, TestDrive
from django.db.models import Count, Q
from datetime import datetime, timedelta

# Register your models here.
# store/admin.py

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Stats
        car_count = Car.objects.count()
        recent_sales_count = Sale.objects.filter(
            sale_date__gte=datetime.now()-timedelta(days=7)
        ).count()
        new_customers_count = Customer.objects.filter(
            created_at__gte=datetime.now()-timedelta(days=30)
        ).count()
        test_drive_count = TestDrive.objects.filter(
            completed=False
        ).count()

        # Recent content
        recent_cars = Car.objects.order_by('-created_at')[:5]
        pending_test_drives = TestDrive.objects.filter(
            completed=False
        ).order_by('scheduled_date')[:5]

        # Recent activity (you might want to implement a proper activity log)
        recent_activity = []  # Replace with your activity log query

        context = {
            **self.each_context(request),
            'car_count': car_count,
            'recent_sales_count': recent_sales_count,
            'new_customers_count': new_customers_count,
            'test_drive_count': test_drive_count,
            'recent_cars': recent_cars,
            'pending_test_drives': pending_test_drives,
            'recent_activity': recent_activity,
        }
        return TemplateResponse(request, 'admin/dashboard.html', context)

# Replace default admin site
admin_site = CustomAdminSite(name='custom_admin')


@admin.register(Car, site=admin_site)
class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'price', 'status', 'is_featured', 'image_url')
    list_filter = ('status', 'is_featured', 'car_type', 'fuel_type')
    search_fields = ('make', 'model', 'vin')
    readonly_fields = ('date_added',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('make', 'model', 'year', 'vin', 'car_type', 'fuel_type', 'transmission')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'status', 'is_featured')
        }),
        ('Details', {
            'fields': ('mileage', 'color', 'description', 'image_url')
        }),
    )
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['make'].required = True
        form.base_fields['model'].required = True
        return form

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email')

class SaleAdmin(admin.ModelAdmin):
    list_display = ('car', 'customer', 'sale_date', 'sale_amount')
    list_filter = ('sale_date', 'payment_method')
    date_hierarchy = 'sale_date'


class UserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.groups.filter(name='Sales').exists():
            SalesPerson.objects.get_or_create(user=obj)



# admin.py
@admin.register(TestDrive)
class TestDriveAdmin(admin.ModelAdmin):
    list_display = ('car', 'customer_name', 'customer_email', 'scheduled_date', 'completed')
    list_filter = ('completed', 'scheduled_date')
    search_fields = ('car__make', 'car__model', 'customer_name', 'customer_email')
    date_hierarchy = 'scheduled_date' 

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    ordering = ('-subscribed_at',)   

admin.site.register(Car, CarAdmin)
admin.site.register(SalesPerson)
admin.site.register(Sale)
admin.site.register(Service)
admin.site.register(Inquiry)




