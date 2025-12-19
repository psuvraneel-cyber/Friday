from django.urls import path
from django.urls import re_path
from .views import ServiceListView, admin_dashboard
from django.contrib.auth import views as auth_views
from . import views
from .views import CarDetailView, CarListView
from django.views.generic.base import RedirectView

urlpatterns = [
    # Core pages
    path('', views.home, name='home'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.service_list, name='services'),
    
    # Car-related URLs
    path('cars/', CarListView.as_view(), name='car_list'),
    path('cars/<int:pk>/', CarDetailView.as_view(), name='car_detail'),
    path('test_drive/', views.schedule_test_drive, name='schedule_test_drive'),
    path('cars/add/', views.add_car, name='add_car'),
    path('cars/edit/<int:car_id>/', views.edit_car, name='edit_car'),
    path('car_list/', RedirectView.as_view(url='/cars/', permanent=True)),
    
    # Sales process
    path('sales/', views.sales_form, name='sales_form'),
    path('sales/record/', views.record_sale, name='record_sale'),
    
    # Add authentication URLs if they don't exist
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    

    
    # Customer management
    path('customers/add/', views.customer_form, name='add_customer'),
    path('customers/edit/<int:customer_id>/', views.customer_form, name='edit_customer'),
    path('customers/form/', views.customer_form, name='customer_form'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customer_form/', views.customer_form, name='customer_form'),
    
    # Test drives
    path('test_drive/', views.schedule_test_drive, name='schedule_test_drive'),
    path('test_drive/about/', views.test_drive_about, name='test_drive_about'),
    path('test_drive/<int:car_id>/', views.schedule_test_drive, name='test_drive'),  # Required
    # Forms
    path('inquiry/', views.inquiry, name='inquiry'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),

     # Razorpay endpoints
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('verify-razorpay-payment/', views.verify_razorpay_payment, name='verify_razorpay_payment'),
    
    
    
    path('car-financing/', views.car_financing, name='car_financing'),
    path('api/calculate-payment/', views.calculate_payment, name='calculate_payment'),
    path('api/submit-application/', views.submit_financing_application, name='submit_application'),
    
    
    
    path('contact-support/', views.contact_support, name='contact_support'),
    path('api/submit-support-request/', views.submit_support_request, name='submit_support_request'),
    
    
    path('extended-warranty/', views.extended_warranty, name='extended_warranty'),
    path('api/request-warranty-quote/', views.request_warranty_quote, name='request_warranty_quote'),
    
    
    path('maintenance/', views.maintenance, name='maintenance'),
    path('create-order/', views.create_order, name='create_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('schedule-appointment/', views.schedule_appointment, name='schedule_appointment'),
    
    
    path('tradein/', views.tradein, name='tradein'),
    path('api/tradein/years/', views.tradein_years, name='tradein_years'),
    path('api/tradein/makes/', views.tradein_makes, name='tradein_makes'),
    path('api/tradein/models/', views.tradein_models, name='tradein_models'),
    path('api/tradein/valuate/', views.tradein_valuate, name='tradein_valuate'),
    
    
    path('services/', ServiceListView.as_view(), name='service_list'),


]

