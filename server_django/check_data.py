import os
import django
from django.db.models import Count
from django.db.models.functions import ExtractYear

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operations.models import Attendance, Finance

print("Checking Attendance Data...")
att_counts = Attendance.objects.annotate(year=ExtractYear('date')).values('year').annotate(count=Count('id'))
for entry in att_counts:
    print(f"Year {entry['year']}: {entry['count']} records")

print("\nChecking Finance Data...")
fin_counts = Finance.objects.annotate(year=ExtractYear('date')).values('year').annotate(count=Count('id'))
for entry in fin_counts:
    print(f"Year {entry['year']}: {entry['count']} records")

if not att_counts and not fin_counts:
    print("\nNO DATA FOUND!")
