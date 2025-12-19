from email.headerregistry import Group
from multiprocessing import context
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Sale, Customer, Car
from .forms import NewsletterForm, SaleForm
from urllib import request
from django.utils import timezone
from datetime import date, datetime, time
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_GET, require_POST
import math
import json
import razorpay
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from store.models import *

from django.contrib.auth import authenticate, login, logout
from .models import Sale, Car
from .forms import SaleForm
from django.views.generic import DetailView

from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from .models import Car, Customer, Sale, TestDrive, CarFeature, Service, Inquiry
from .forms import (
    CarForm, CustomerForm, SaleForm, TestDriveForm, 
    InquiryForm, LoginForm, SignUpForm)
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

def home(request):
    featured_cars = Car.objects.filter(is_featured=True, status='available')[:3]
    services = Service.objects.filter(is_featured=True)[:4]
    
    context = {
        'featured_cars': featured_cars,
        'services': services,
    }
    return render(request, 'home.html', context)

@require_POST
def subscribe_newsletter(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        # Check if email already exists
        if NewsletterSubscriber.objects.filter(email=email).exists():
            message = 'You are already subscribed to our newsletter!'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': message})
            else:
                messages.info(request, message)
        else:
            form.save()
            message = 'Thank you for subscribing to our newsletter!'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': message})
            else:
                messages.success(request, message)
    else:
        message = 'Please enter a valid email address.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': message})
        else:
            messages.error(request, message)
    
    # For non-AJAX requests
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def about(request):
    return render(request, 'about.html')


def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    similar_cars = Car.objects.filter(
        make=car.make, 
        status='available'
    ).exclude(id=car.id)[:3]
    
    context = {
        'car': car,
        'similar_cars': similar_cars,
    }
    return render(request, 'car_detail.html', context)


def car_list(request):
    cars = Car.objects.all()
    return render(request, 'cars/car_list.html', {'cars': cars})

@login_required
def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            messages.success(request, f'{car.make} {car.model} added successfully!')
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm()
    
    context = {'form': form}
    return render(request, 'add_car.html', context)

@login_required
def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f'{car.make} {car.model} updated successfully!')
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm(instance=car)
    
    context = {'form': form, 'car': car}
    return render(request, 'add_car.html', context)


class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'
    context_object_name = 'cars'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context here if needed
        return context

class CarListView(ListView):
    model = Car
    template_name = 'cars/car_list.html'
    context_object_name = 'cars'
    paginate_by = 12  # Optional pagination



def is_salesperson(user):
    """Check if user belongs to Sales group"""
    return user.groups.filter(name='Sales').exists()

def sales_form(request):
    # Check if user is authenticated and is staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return render(request, 'not_authorized.html', status=403)
    
    # Get available cars
    available_cars = Car.objects.filter(is_available=True)
    
    # Get all customers
    customers = Customer.objects.all()
    
    # Get sales persons - handle the case where Group might not exist
    sales_persons = User.objects.filter(groups__name='Sales')
    
    # If no sales group exists yet, show all staff users as fallback
    if not sales_persons.exists():
        sales_persons = User.objects.filter(is_staff=True)
    
    return render(request, 'sales_form.html', {
        'customers': customers,
        'available_cars': available_cars,
        'sales_persons': sales_persons
    })

def record_sale(request):
    # Check if user is authenticated and is staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return render(request, 'not_authorized.html', status=403)
    
    if request.method == 'POST':
        # Process the form data
        customer_id = request.POST.get('customer')
        car_id = request.POST.get('car')
        sale_amount = request.POST.get('sale_amount')
        sale_date = request.POST.get('sale_date')
        payment_method = request.POST.get('payment_method')
        sales_person_id = request.POST.get('sales_person')
        notes = request.POST.get('notes')
        
        try:
            # Create the sale record
            customer = Customer.objects.get(id=customer_id)
            car = Car.objects.get(id=car_id)
            sales_person = User.objects.get(id=sales_person_id)
            
            sale = Sale(
                customer=customer,
                car=car,
                sale_amount=sale_amount,
                sale_date=sale_date,
                payment_method=payment_method,
                sales_person=sales_person,
                notes=notes
            )
            sale.save()
            
            # Update car availability
            car.is_available = False
            car.status = 'sold'
            car.save()
            
            messages.success(request, 'Sale recorded successfully!')
            return redirect('sales_form')
            
        except Customer.DoesNotExist:
            messages.error(request, 'Selected customer does not exist.')
        except Car.DoesNotExist:
            messages.error(request, 'Selected car does not exist.')
        except User.DoesNotExist:
            messages.error(request, 'Selected sales person does not exist.')
        except Exception as e:
            messages.error(request, f'Error recording sale: {str(e)}')
    
    return redirect('sales_form')











@login_required
def customer_form(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # This line actually saves the data to the database
            customer=form.save()  # CRITICAL MISSING STEP
    else:
        form = CustomerForm()
    
    return render(request, 'customer_form.html', {'form': form})





def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    purchases = Sale.objects.filter(customer=customer).order_by('-sale_date')
    
    context = {
        'customer': customer,
        'purchases': purchases,
    }
    return render(request, 'customer_detail.html', context)


@login_required  # If you're using authentication
def test_drive(request, car_id=None):
    if car_id: # type: ignore
        # Handle specific car test drive
        car = get_object_or_404(Car, id=car_id)
        if request.method == 'POST':
         form = TestDriveForm(request.POST)
        if form.is_valid():
            test_drive = form.save(commit=False)
            
            # For authenticated users, associate with their customer profile
            if request.user.is_authenticated and hasattr(request.user, 'customer'):
                test_drive.customer = request.user.customer
            
            test_drive.save()
            
            messages.success(request, 'Test drive scheduled successfully!')
            return redirect('car_detail', car_id=test_drive.car.id)
    else:
        # Handle general test drive form
        cars = Car.objects.all()  # Or filter as needed
        return render(request, 'test_drive.html', {'cars': cars})
    



@csrf_exempt
def schedule_test_drive(request):
    if request.method == 'POST':
        # Combine date and time
        date_str = request.POST.get('scheduled_date')
        time_str = request.POST.get('scheduled_time')
        
        try:
            # Create datetime object
            datetime_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            # Make timezone aware
            scheduled_datetime = timezone.make_aware(datetime_obj)
            
            # Create TestDrive instance manually
            test_drive = TestDrive(
                customer_name=request.POST.get('customer_name'),
                customer_email=request.POST.get('customer_email'),
                customer_phone=request.POST.get('customer_phone'),
                car_id=request.POST.get('car'),
                scheduled_date=scheduled_datetime,
                notes=request.POST.get('notes', '')
            )
            test_drive.save()
            
            return JsonResponse({'success': True, 'test_drive_id': test_drive.id})
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'errors': {'datetime': ['Invalid date/time format']}
            }, status=400)
    
    # GET request handling remains the same
    
    # Handle GET request
    cars = Car.objects.all()
    return render(request, 'test_drive.html', {'cars': cars})
        
        
        
        
        
        
        
        
        
          
def test_drive_about(request):
    return render(request, 'about.html')
def car_list_about(request):
    return render(request, 'about.html')

def inquiry(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            messages.success(request, 'Your inquiry has been submitted successfully!')
            return redirect('home')
    else:
        car_id = request.GET.get('car')
        initial = {}
        if car_id:
            try:
                car = Car.objects.get(id=car_id)
                initial['car'] = car
                initial['subject'] = f'Inquiry about {car.year} {car.make} {car.model}'
            except Car.DoesNotExist:
                pass
        
        # Pre-fill for logged-in users
        if request.user.is_authenticated and hasattr(request.user, 'customer'):
            customer = request.user.customer
            initial.update({
                'name': f'{customer.first_name} {customer.last_name}',
                'email': customer.email,
                'phone': customer.phone,
            })
        
        form = InquiryForm(initial=initial)
    
    context = {'form': form}
    return render(request, 'inquiry.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'login.html', context)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create customer profile
            Customer.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the highlighted errors and try again.')
    else:
        form = SignUpForm()
    
    context = {'form': form}
    return render(request, 'signup.html', context)

def service_list(request):
    services = Service.objects.all()
    context = {'services': services}
    return render(request, 'service_list.html', context)

def contact(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')
    else:
        # Pre-fill for logged-in users
        initial = {}
        if request.user.is_authenticated and hasattr(request.user, 'customer'):
            customer = request.user.customer
            initial.update({
                'name': f'{customer.first_name} {customer.last_name}',
                'email': customer.email,
                'phone': customer.phone,
            })
        
        form = InquiryForm(initial=initial)
    
    context = {'form': form}
    return render(request, 'contact.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return render(request, 'logout.html')

# views.py
def register_salesperson(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            SalesPerson.objects.create(user=user)
            return redirect('home')


@staff_member_required
def admin_dashboard(request):
    # Add your custom dashboard logic here
    return render(request, 'admin/dashboard.html')




# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
@require_POST
def create_razorpay_order(request):
    try:
        data = json.loads(request.body)
        amount = float(data.get('amount', 0))
        currency = data.get('currency', 'INR')
        
        # Validate amount
        if amount <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Create a Razorpay order
        order_data = {
            'amount': int(amount * 100),  # Amount in paise
            'currency': currency,
            'payment_capture': 1  # Auto capture payment
        }
        
        order = razorpay_client.order.create(order_data)
        
        return JsonResponse({
            'id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key': settings.RAZORPAY_KEY_ID
        })
        
    except ValueError:
        return JsonResponse({'error': 'Invalid amount format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def verify_razorpay_payment(request):
    try:
        data = json.loads(request.body)
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        
        # Check if all required parameters are present
        if not all([payment_id, order_id, signature]):
            return JsonResponse({'success': False, 'error': 'Missing payment parameters'})
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        # Verify the payment signature
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # If verification is successful, fetch payment details to confirm
            payment = razorpay_client.payment.fetch(payment_id)
            
            # Check if payment was successful
            if payment['status'] == 'captured':
                return JsonResponse({
                    'success': True, 
                    'message': 'Payment verified successfully',
                    'payment_id': payment_id,
                    'order_id': order_id
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': f'Payment not captured. Status: {payment["status"]}'
                })
                
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'success': False, 'error': 'Signature verification failed'})
            
    except razorpay.errors.BadRequestError as e:
        return JsonResponse({'success': False, 'error': f'Bad request: {str(e)}'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Verification error: {str(e)}'})





def car_financing(request):
    """Render the car financing page"""
    context = {
        'page_title': 'Car Financing - Premium Auto Services',
        'services': [
            {
                'name': 'Car Financing',
                'url': 'car_financing',
                'active': True
            },
            {
                'name': 'Maintenance',
                'url': 'maintenance'
            },
            {
                'name': 'Trade-In',
                'url': 'tradein'
            },
            {
                'name': 'Extended Warranty',
                'url': 'extended_warranty'
            },
            {
                'name': 'Contact Support',
                'url': 'contact_support'
            }
        ],
        'testimonials': [
            {
                'text': '"The financing process was incredibly smooth. I was approved within hours and got a much better rate than my bank offered. Highly recommend their services!"',
                'author': 'John Smith',
                'purchase': 'Toyota Camry',
                'initials': 'JS'
            },
            {
                'text': '"As a first-time buyer, I was nervous about the process. The team walked me through everything and found a program perfect for my situation. Couldn\'t be happier!"',
                'author': 'Maria Davis',
                'purchase': 'Honda Civic',
                'initials': 'MD'
            },
            {
                'text': '"I refinanced my auto loan and saved over $100 per month! The process was simple and the customer service was exceptional throughout."',
                'author': 'Robert Johnson',
                'purchase': 'Ford F-150',
                'initials': 'RJ'
            }
        ],
        'faqs': [
            {
                'question': 'What credit score do I need to qualify for financing?',
                'answer': 'We work with customers across the credit spectrum. While rates are most competitive for those with scores above 680, we have options available for those with lower scores or limited credit history. Our specialists will find the best solution for your situation.'
            },
            {
                'question': 'How much down payment is required?',
                'answer': 'Down payment requirements vary based on creditworthiness and the vehicle. Typically, we recommend at least 10-20% for used vehicles and 5-10% for new vehicles. Special programs may allow for lower down payments for qualified buyers.'
            },
            {
                'question': 'Can I finance a vehicle from a private seller?',
                'answer': 'Yes, we offer financing for vehicles purchased from private sellers. The process is similar to dealership purchases, but may require a vehicle inspection to ensure it meets our lending criteria.'
            },
            {
                'question': 'How long does the approval process take?',
                'answer': 'Most applicants receive a decision within 1-2 hours during business hours. Once approved, you\'ll receive a pre-approval certificate that you can use at any dealership. The final loan documentation can often be completed the same day.'
            }
        ]
    }
    return render(request, 'car_financing.html', context)

def calculate_payment(request):
    """API endpoint to calculate loan payment"""
    if request.method == 'POST':
        try:
            # Get form data
            vehicle_price = float(request.POST.get('vehicle_price', 30000))
            down_payment = float(request.POST.get('down_payment', 5000))
            loan_term = int(request.POST.get('loan_term', 60))
            interest_rate = float(request.POST.get('interest_rate', 4.5))
            
            # Validate inputs
            if down_payment >= vehicle_price:
                return JsonResponse({'error': 'Down payment cannot exceed vehicle price'})
            
            if loan_term <= 0:
                return JsonResponse({'error': 'Loan term must be greater than zero'})
            
            # Calculate loan details
            loan_amount = vehicle_price - down_payment
            monthly_rate = interest_rate / 100 / 12  # Monthly interest rate
            
            # Calculate monthly payment using formula: P = (Pv * r) / (1 - (1 + r)^(-n))
            if monthly_rate > 0:
                monthly_payment = (loan_amount * monthly_rate) / (1 - math.pow(1 + monthly_rate, -loan_term))
            else:
                monthly_payment = loan_amount / loan_term
            
            total_interest = (monthly_payment * loan_term) - loan_amount
            total_cost = vehicle_price + total_interest
            
            # Return results
            return JsonResponse({
                'monthly_payment': round(monthly_payment, 2),
                'total_interest': round(total_interest, 2),
                'loan_amount': round(loan_amount, 2),
                'total_cost': round(total_cost, 2)
            })
            
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': 'Invalid input values'})
    
    return JsonResponse({'error': 'Invalid request method'})

def submit_financing_application(request):
    """Handle financing application submission"""
    if request.method == 'POST':
        # In a real application, you would process the form data here
        # and save it to the database
        
        # For this example, we'll just return a success message
        return JsonResponse({
            'success': True,
            'message': 'Application submitted successfully! We will contact you within 24 hours.'
        })
    
    return JsonResponse({'error': 'Invalid request method'})


def contact_support(request):
    """Render the contact support page"""
    context = {
        'page_title': 'Contact Support - Premium Auto Services',
        'services': [
            {
                'name': 'Home',
                'url': 'home'
            },
            {
                'name': 'Car Financing',
                'url': 'car_financing'
            },
            {
                'name': 'Maintenance',
                'url': 'maintenance'
            },
            {
                'name': 'Trade-In',
                'url': 'tradein'
            },
            {
                'name': 'Extended Warranty',
                'url': 'extended_warranty'
            },
            {
                'name': 'Contact Support',
                'url': 'contact_support',
                'active': True
            }
        ],
        'faqs': [
            {
                'question': 'What are your customer support hours?',
                'answer': 'Our customer support team is available Monday through Friday from 8am to 8pm EST, and on Saturdays from 9am to 5pm EST. For emergency roadside assistance, we\'re available 24/7.'
            },
            {
                'question': 'How quickly can I expect a response to my inquiry?',
                'answer': 'We strive to respond to all inquiries within 24 hours during business days. For urgent matters, we recommend calling our support line directly.'
            },
            {
                'question': 'Do you offer support in languages other than English?',
                'answer': 'Yes, we have support representatives who speak Spanish and French. Please let us know your language preference when you contact us.'
            },
            {
                'question': 'What information should I have ready when contacting support?',
                'answer': 'For faster service, please have your account number, vehicle information, and any relevant documentation ready when you contact our support team.'
            }
        ]
    }
    return render(request, 'contact_support.html', context)

@csrf_exempt
def submit_support_request(request):
    """Handle support form submission"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            service = request.POST.get('service', '').strip()
            message = request.POST.get('message', '').strip()
            
            # Validate required fields
            if not name or not email or not message:
                return JsonResponse({
                    'success': False,
                    'error': 'Please fill in all required fields.'
                })
            
            # Validate email format
            if '@' not in email or '.' not in email:
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter a valid email address.'
                })
            
            # In a real application, you would:
            # 1. Save the support request to the database
            # 2. Send email notifications to the support team
            # 3. Send a confirmation email to the user
            
            # Example of sending an email (requires proper email configuration)
            """
            send_mail(
                f'New Support Request: {service}',
                f'''
                Name: {name}
                Email: {email}
                Phone: {phone}
                Service: {service}
                
                Message:
                {message}
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPPORT_EMAIL],
                fail_silently=True,
            )
            """
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your message! We\'ll get back to you within 24 hours.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing your request. Please try again later.'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })
    
    


def extended_warranty(request):
    """Render the extended warranty page"""
    context = {
        'page_title': 'Extended Warranty - Premium Auto Services',
        'services': [
            {
                'name': 'Home',
                'url': 'home'
            },
            {
                'name': 'Car Financing',
                'url': 'car_financing'
            },
            {
                'name': 'Maintenance',
                'url': 'maintenance'
            },
            {
                'name': 'Trade-In',
                'url': 'tradein'
            },
            {
                'name': 'Extended Warranty',
                'url': 'extended_warranty',
                'active': True
            },
            {
                'name': 'Contact Support',
                'url': 'contact_support'
            }
        ],
        'testimonials': [
            {
                'text': '"The extended warranty paid for itself when my transmission failed. The claims process was smooth, and I was back on the road in no time with minimal out-of-pocket expense."',
                'author': 'Michael Rodriguez',
                'vehicle': '2018 Ford F-150 Owner',
                'initials': 'MR'
            },
            {
                'text': '"I was skeptical about extended warranties, but this one proved its worth when my hybrid system needed expensive repairs. The coverage was comprehensive and the process was hassle-free."',
                'author': 'Sarah Johnson',
                'vehicle': '2020 Toyota Prius Owner',
                'initials': 'SJ'
            },
            {
                'text': '"The peace of mind is worth every penny. When my infotainment system failed, it was fully covered without any hassle. I recommend this warranty to all my friends and family."',
                'author': 'David Wilson',
                'vehicle': '2019 BMW X5 Owner',
                'initials': 'DW'
            }
        ],
        'faqs': [
            {
                'question': 'What is covered under an extended warranty?',
                'answer': 'Coverage varies by plan, but typically includes major components like engine, transmission, drivetrain, electrical systems, and more. Our bumper-to-bumper coverage offers the most comprehensive protection, while powertrain plans focus on essential components.'
            },
            {
                'question': 'Can I use my own mechanic?',
                'answer': 'Yes, you can choose any licensed repair facility. However, for the claims process to be most efficient, we recommend using one of our certified repair facilities within our nationwide network.'
            },
            {
                'question': 'How long does the coverage last?',
                'answer': 'Coverage terms vary based on the plan you select. We offer options ranging from 2 to 7 years of additional coverage beyond the manufacturer\'s warranty, or specific mileage limits up to 150,000 miles.'
            },
            {
                'question': 'Are there any deductibles?',
                'answer': 'Yes, most plans have a deductible that you pay per repair visit. We offer deductible options ranging from $0 to $200, allowing you to choose a plan that fits your budget and needs.'
            }
        ]
    }
    return render(request, 'extended_warranty.html', context)

@csrf_exempt
def request_warranty_quote(request):
    """Handle warranty quote requests"""
    if request.method == 'POST':
        try:
            # Get form data
            make = request.POST.get('vehicleMake', '').strip()
            model = request.POST.get('vehicleModel', '').strip()
            year = request.POST.get('vehicleYear', '').strip()
            mileage = request.POST.get('vehicleMileage', '').strip()
            coverage = request.POST.get('coverageType', '').strip()
            
            # Validate required fields
            if not make or not model or not year or not mileage or not coverage:
                return JsonResponse({
                    'success': False,
                    'error': 'Please fill in all required fields.'
                })
            
            # In a real application, you would:
            # 1. Save the quote request to the database
            # 2. Generate a quote based on vehicle details
            # 3. Send email notifications to the sales team
            # 4. Send a confirmation email to the user
            
            # Example of sending an email (requires proper email configuration)
            """
            send_mail(
                f'New Warranty Quote Request: {year} {make} {model}',
                f'''
                Vehicle Details:
                Make: {make}
                Model: {model}
                Year: {year}
                Mileage: {mileage}
                Preferred Coverage: {coverage}
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [settings.SALES_EMAIL],
                fail_silently=True,
            )
            """
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': f'Thank you for your quote request! We\'ll contact you shortly with coverage options for your {year} {make} {model}.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing your request. Please try again later.'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })



from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import razorpay
from django.conf import settings
import time
from datetime import datetime  # Add this import

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def maintenance(request):
    """View for the maintenance services page"""
    return render(request, 'maintenance.html')

@csrf_exempt
def create_order(request):
    """Create a Razorpay order"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount = int(data['amount'])  # Amount should already be in paise
            
            # Create order
            order_data = {
                'amount': amount,
                'currency': data.get('currency', 'INR'),
                'receipt': f'maintenance_plan_{int(time.time())}',
                'notes': {
                    'plan': data['plan'],
                }
            }
            
            order = client.order.create(data=order_data)
            return JsonResponse({
                'id': order['id'],
                'amount': order['amount'],
                'currency': order['currency']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def payment_success(request):
    """Handle successful payment verification"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }
            
            # Verify signature
            client.utility.verify_payment_signature(params_dict)
            
            # Payment successful, save to database
            # You would typically create a MaintenancePlanPurchase model
            # and save the transaction details here
            
            return JsonResponse({
                'success': True,
                'message': 'Payment verified successfully',
                'payment_id': data['razorpay_payment_id']
            })
            
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid payment signature'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def schedule_appointment(request):
    """Handle appointment scheduling form submission"""
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        vehicle = request.POST.get('vehicle')
        service_type = request.POST.get('service')
        date_str = request.POST.get('date')  # This will be a string like "2023-12-15"
        time_slot = request.POST.get('time')  # This will be a string like "morning"
        message = request.POST.get('message')
        
        # Convert date string to datetime object if needed
        appointment_date = None
        if date_str:
            try:
                appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                # Handle invalid date format
                pass
        
        # Process time slot
        time_display = ""
        if time_slot == "morning":
            time_display = "Morning (8am - 11am)"
        elif time_slot == "afternoon":
            time_display = "Afternoon (11am - 3pm)"
        elif time_slot == "late":
            time_display = "Late Afternoon (3pm - 6pm)"
        
        # Save appointment to database or send email notification
        # You would typically create an Appointment model
        
        # For now, just return a success message
        return render(request, 'maintenance/appointment_success.html', {
            'name': name,
            'service_type': service_type,
            'date': appointment_date.strftime('%Y-%m-%d') if appointment_date else date_str,
            'time': time_display
        })
    
    return redirect('maintenance')



def tradein(request):
    """View for the trade-in services page"""
    return render(request, 'tradein.html')

@require_GET
def tradein_years(request):
    """Get distinct years from Car model"""
    years = Car.objects.values_list('year', flat=True).distinct().order_by('-year')
    return JsonResponse(list(years), safe=False)

@require_GET
def tradein_makes(request):
    """Get distinct makes for a specific year"""
    year = request.GET.get('year')
    if year:
        makes = Car.objects.filter(year=year).values_list('make', flat=True).distinct().order_by('make')
        return JsonResponse(list(makes), safe=False)
    return JsonResponse([], safe=False)

@require_GET
def tradein_models(request):
    """Get distinct models for a specific year and make"""
    year = request.GET.get('year')
    make = request.GET.get('make')
    if year and make:
        models = Car.objects.filter(year=year, make=make).values_list('model', flat=True).distinct().order_by('model')
        return JsonResponse(list(models), safe=False)
    return JsonResponse([], safe=False)

@csrf_exempt
@require_POST
def tradein_valuate(request):
    """Calculate trade-in value based on vehicle information"""
    try:
        data = json.loads(request.body)
        year = data.get('year')
        make = data.get('make')
        model = data.get('model')
        mileage = int(data.get('mileage', 0))
        condition = data.get('condition')
        
        # Your valuation logic here
        # This is a simplified example - adjust based on your business rules
        
        # Base value calculation (simplified)
        try:
            # Try to find a similar car in your inventory
            similar_car = Car.objects.filter(year=year, make=make, model=model).first()
            if similar_car:
                base_value = float(similar_car.price) * 0.7  # 70% of retail price
            else:
                # Fallback calculation if no similar car found
                base_value = 15000  # Default base value
        except:
            base_value = 15000  # Default base value
        
        # Adjust for mileage
        mileage_adjustment = max(0, 1 - (mileage / 150000))
        base_value *= mileage_adjustment
        
        # Adjust for condition
        condition_multipliers = {
            "excellent": 1.0,
            "good": 0.9,
            "fair": 0.75,
            "poor": 0.6
        }
        base_value *= condition_multipliers.get(condition, 0.8)
        
        # Round to nearest hundred
        estimated_value = round(base_value / 100) * 100
        
        return JsonResponse({
            'estimatedValue': estimated_value,
            'currency': 'USD'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

class ServiceListView(ListView):
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        return [
            {
                'name': 'Oil Change',
                'icon': 'fas fa-oil-can',
                'description': 'Regular oil changes are essential for maintaining your engine\'s health and performance.'
            },
            {
                'name': 'Brake Service',
                'icon': 'fas fa-stop-circle',
                'description': 'Ensure your safety with our comprehensive brake inspection and repair services.'
            },
            {
                'name': 'Tire Service',
                'icon': 'fas fa-tachometer-alt',
                'description': 'From rotations to replacements, we handle all your tire needs with expertise.'
            },
            {
                'name': 'Engine Repair',
                'icon': 'fas fa-engine',
                'description': 'Expert diagnostics and repair for all engine-related issues.'
            },
            {
                'name': 'Battery Service',
                'icon': 'fas fa-battery-full',
                'description': 'Keep your vehicle starting reliably with our battery services.'
            },
            {
                'name': 'AC Service',
                'icon': 'fas fa-air-freshener',
                'description': 'Stay comfortable in all seasons with our air conditioning services.'
            }
        ]