import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ministry.models import Service

defaults = [
    {"name": "Sunday Service", "day_of_week": "sunday", "time": "09:00"},
    {"name": "Digging Deep", "day_of_week": "tuesday", "time": "18:00"},
    {"name": "Faith Clinic", "day_of_week": "thursday", "time": "18:00"},
]

print("Populating standard services...")
for data in defaults:
    obj, created = Service.objects.get_or_create(name=data['name'], defaults=data)
    if created:
        print(f"- Created Service: {obj.name}")
    else:
        print(f"- Service exists: {obj.name}")

print("✅ Standard services populated!")
