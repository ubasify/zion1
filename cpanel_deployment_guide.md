# Deploying Django on cPanel (Shared Hosting)

This guide covers deploying your Django application on shared hosting environments using cPanel (e.g., Namecheap, Bluehost, HostGator, GoDaddy).

## 1. Prerequisites

*   **cPanel Access**: Ensure your hosting plan supports "Setup Python App".
*   **SSH Access**: Highly recommended for running commands (migrations, static files).
*   **Database**: MySQL is standard on cPanel. You can also use SQLite (simplest for small apps).

---

## 2. Setting Up the Python Application

1.  Log in to **cPanel**.
2.  Find and click on **"Setup Python App"** under the *Software* section.
3.  Click **"Create Application"**.
4.  **Python Version**: Select **3.x** (preferably 3.9 or newer, matching your local env if possible).
5.  **Application Root**: Enter the folder name where your code will live (e.g., `rccghgz_app`).
6.  **Application URL**: Select your domain (e.g., `yourdomain.com`).
7.  **Application Startup File**: Leave blank or enter `passenger_wsgi.py` (it will be created automatically).
8.  **Application Entry Point**: Enter `application`.
9.  Click **Create**.

*After creation, copy the "Command for entering virtual environment" displayed at the top of the page. You will need this.*

---

## 3. Uploading Your Project

1.  Go to **File Manager** in cPanel.
2.  Navigate to the folder you created (e.g., `rccghgz_app`).
3.  **Upload** your project files here.
    *   Ideally, upload a **ZIP** of your project and extract it.
    *   **Exclude**: `venv`, `.git`, `__pycache__` folders.
    *   **Include**: `manage.py`, `requirements.txt`, `.env`, `db.sqlite3` (if using SQLite), and your app folders (`config`, `core`, etc.).

---

## 4. Install Dependencies & Upgrade Pip (Terminal)

You need to install your packages inside the virtual environment created by cPanel.

1.  Open **Terminal** in cPanel (or SSH into your server).
2.  **Activate the Virtual Environment**: Paste the command you copied in Step 2. It looks like this:
    ```bash
    source /home/username/virtualenv/rccghgz_app/3.9/bin/activate
    ```
3.  **Upgrade Pip** (Common Issue Fix):
    Many cPanel environments have an old pip version. Run this command while the venv is active:
    ```bash
    pip install --upgrade pip
    ```
4.  **Install Requirements**:
    ```bash
    cd /home/username/rccghgz_app
    pip install -r requirements.txt
    ```
    *Note: If `mysqlclient` fails to install, you might need to use `pymysql` as a drop-in replacement in `settings.py` or stick to SQLite.*

---

## 5. Configure `passenger_wsgi.py`

cPanel uses Phusion Passenger to serve Python apps. You need to edit the `passenger_wsgi.py` file created in your app root to point to your Django project.

1.  Go to **File Manager**, find `passenger_wsgi.py` in your app folder.
2.  **Edit** it and replace the contents with:

```python
import os
import sys
from config.wsgi import application

# Adjust the path to point to your project root
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables if not using a .env loading library efficiently in loading
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
```

---

## 6. Static Files Configuration

Serving static files on cPanel can be tricky because `DEBUG=False` stops Django from serving them.

1.  **Configure Settings**:
    Ensure `whitenoise` is installed and configured in `settings.py` (as per the main deployment guide). This is the **easiest method**.
    
    ```python
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        # ...
    ]
    ```

2.  **Run Collectstatic**:
    In the terminal (with venv active):
    ```bash
    python manage.py collectstatic
    ```

---

## 7. Final Steps

1.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```
2.  **Create Superuser**:
    ```bash
    python manage.py createsuperuser
    ```
3.  **Restart Application**:
    Go back to the **"Setup Python App"** page in cPanel and click **Restart** for your application.

4.  **Visit your website!**

---

## Troubleshooting

*   **Internal Server Error?** Check the errors log file in your app directory (often `stderr.log`).
*   **Static files missing?** Ensure WhiteNoise is set up correctly.
*   **Database locked?** SQLite on cPanel can sometimes have permission issues. typical for high traffic. Consider switching to MySQL in cPanel "MySQL Databases" section if issues persist.
