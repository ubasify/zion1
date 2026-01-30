
import os
import sys
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
from django.conf import settings

try:
    django.setup()
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"BASE_DIR: {settings.BASE_DIR}")
    
    # Check if .env is actually loaded
    print(f"Environment variable DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    from dotenv import load_dotenv
    # Try loading explicitly to see if it works here
    load_dotenv()
    print(f"SECRET_KEY from env directly: {os.getenv('SECRET_KEY')}")
    
except Exception as e:
    print(f"Error: {e}")
