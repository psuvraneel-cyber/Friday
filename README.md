# 🚗 Car Sales & Inventory Management System

A full-featured web application for managing car dealership operations including inventory management, sales tracking, customer management, and online payments.

![Django](https://img.shields.io/badge/Django-5.2.4-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🚙 Inventory Management
- Add, edit, and delete car listings
- Track car status (Available, Pending Sale, Sold, In Maintenance)
- Support for multiple car types (Sedan, SUV, Truck, Coupe, Hatchback)
- Image URL support for car photos
- Featured cars showcase

### 👥 Customer Management
- Customer registration and profiles
- Customer inquiry tracking
- Newsletter subscription management

### 💰 Sales & Payments
- Complete sales workflow
- Multiple payment methods (Cash, Credit Card, Bank Finance, Check)
- **Razorpay Payment Gateway Integration** for online payments
- Sales tracking and reporting

### 🚗 Test Drive Scheduling
- Online test drive booking
- Schedule management
- Customer notifications

### 📊 Dashboard
- Sales overview
- Inventory statistics
- Recent activities

### 🔐 Authentication
- User registration and login
- Role-based access control
- Secure password handling

## 🛠️ Tech Stack

- **Backend:** Django 5.2.4
- **Database:** SQLite (development) / PostgreSQL (production-ready)
- **Payment Gateway:** Razorpay
- **Static Files:** WhiteNoise
- **Server:** Gunicorn
- **Styling:** CSS3, Bootstrap

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/car-sales-inventory.git
   cd car-sales-inventory
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin

## ⚙️ Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

# Razorpay Payment Gateway
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Security (set to True in production)
SECURE_SSL_REDIRECT=False
```

## 🚀 Deployment

### Deploy to Render

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New** → **Blueprint**
4. Connect your repository
5. Render will auto-detect the `render.yaml` configuration
6. Set environment variables in Render dashboard:
   - `RAZORPAY_KEY_ID`
   - `RAZORPAY_KEY_SECRET`
7. Deploy!

## 💳 Razorpay Test Mode

This project uses Razorpay in **TEST MODE** for payment processing.

### Test Credentials
- **Test Card Number:** `4111 1111 1111 1111`
- **Expiry:** Any future date
- **CVV:** Any 3 digits
- **OTP:** `1234`

> ⚠️ No real money is processed in test mode.

## 📁 Project Structure

```
Friday/
├── Friday/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                  # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── forms.py           # Django forms
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── Templates/         # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # Uploaded media files
├── manage.py
├── requirements.txt
├── .env.example
├── render.yaml            # Render deployment config
├── railway.json           # Railway deployment config
├── nixpacks.toml          # Nixpacks build config
└── Procfile               # Process file for deployment
```

## 🧪 Running Tests

```bash
python manage.py test
```

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/cars/` | GET | List all cars |
| `/cars/<id>/` | GET | Car details |
| `/test-drive/` | POST | Schedule test drive |
| `/sales/` | GET/POST | Sales management |
| `/payment/` | POST | Process payment |
| `/admin/` | GET | Admin dashboard |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Sauvraneel Paul**

---

⭐ If you found this project helpful, please give it a star!
