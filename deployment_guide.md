# Deployment Guide for RCCGHGZ Django Application

This guide outlines the steps to deploy your Django application to a production environment (e.g., a VPS like DigitalOcean, Linode, AWS EC2, or a PaaS like Heroku/Railway) using **SQLite**.

## 1. Prerequisites

*   **Virtual Private Server (VPS)**: Ubuntu 22.04 LTS recommended.
*   **Domain Name**: Pointed to your server's IP address.
*   **Python 3.10+**: Installed on the server.
*   **SQLite**: Included with Python, so no extra installation is needed.

---

## 2. Prepare Your Project for Production

### A. Dependencies
Ensure you have a `requirements.txt` file. Run this locally:
```bash
pip freeze > requirements.txt
```
*Review the file and remove any local-only packages if necessary.*

### B. Environment Variables
**NEVER** commit secrets to your code repository. Use environment variables.
1. Install `python-dotenv`:
   ```bash
   pip install python-dotenv
   ```
2. Create a `.env` file in your root directory (add it to `.gitignore`):
   ```env
   DEBUG=False
   SECRET_KEY=your-super-strong-secret-key-here
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,123.45.67.89
   # DATABASE_URL is not needed for SQLite if using the default configuration below
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_SECRET_KEY=sk_live_...
   ```

### C. Update `config/settings.py`
Modify your settings to load from environment variables and configure SQLite.

**Install needed packages first:**
```bash
pip install whitenoise
```
*(Note: `dj-database-url` is optional if you are not parsing a DATABASE_URL for Postgres)*

**Edit `config/settings.py`:**
```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-dev-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static Files (WhiteNoise recommended for serving static files)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add this right here after SecurityMiddleware
    # ... other middleware ...
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Stripe
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
```

---

## 3. Server Setup (Ubuntu Linux Example)

### A. Install System Packages
```bash
sudo apt update
sudo apt install python3-pip python3-venv python3-dev nginx curl
```

### B. Clone & Configure Project
1. Clone your repo to `/var/www/rccghgz`.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt gunicorn
   ```
4. Create the `.env` file with your production values.

### C. Upload Database (Important for SQLite)
Since you are using SQLite, you need to copy your local `db.sqlite3` file to the server if you want to keep your existing data.

**From your local machine:**
```bash
scp db.sqlite3 root@your_server_ip:/var/www/rccghgz/
```
*Make sure the permissions allow the web server to write to it:*
```bash
# On the server:
sudo chown www-data:www-data /var/www/rccghgz/db.sqlite3
sudo chown www-data:www-data /var/www/rccghgz  # The directory must also be writable for SQLite journaling
```

### D. Run Migrations & Collect Static
```bash
python manage.py migrate
python manage.py collectstatic
# python manage.py createsuperuser # Only if you didn't upload an existing DB with a superuser
```

---

## 4. Deployment with Gunicorn & Nginx

### A. Test Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 config.wsgi
```
*Visit your server IP:8000 to verify it loads (ensure firewall allows 8000).*

### B. Create Systemd Service for Gunicorn
Create `/etc/systemd/system/gunicorn.service`:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/rccghgz
ExecStart=/var/www/rccghgz/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/rccghgz/rccghgz.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start and enable it:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### C. Configure Nginx
Create `/etc/nginx/sites-available/rccghgz`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/rccghgz;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/rccghgz/rccghgz.sock;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/rccghgz /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### D. SSL Certificate (HTTPS)
Use Certbot for free SSL:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 5. Maintenance
*   **Logs**: Check `journalctl -u gunicorn` for app errors and `/var/log/nginx/error.log` for web server errors.
*   **Updates**: Pull new code, update deps, migrate, and restart gunicorn: `sudo systemctl restart gunicorn`.
