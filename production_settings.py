"""
Production settings for Friday project.
"""
import os
from pathlib import Path
from .settings import *
from Friday.settings import BASE_DIR

# SECURITY
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-very-long-random-secret-key-here')
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS SECURITY
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# DATABASE (keep SQLite for now, can switch to PostgreSQL later)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# RAZORPAY (use environment variables in production)
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_R7Z5CIbifhdbdA')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'HegvkvAJR5H1262XZX4dQgLt')
