"""
Script to populate Attendance records with realistic random values
for adult_count, children_count, and first_timers_count.

The total_count will be auto-calculated by the model's save() method.
"""

import os
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operations.models import Attendance

# Get all attendance records
records = Attendance.objects.all()
total = records.count()

print(f"Updating {total} attendance records with realistic values...")

# Define realistic ranges based on service type
service_ranges = {
    'Sunday Service': {'adults': (150, 400), 'children': (50, 150), 'first_timers': (0, 25)},
    'Midweek Service': {'adults': (80, 200), 'children': (20, 80), 'first_timers': (0, 15)},
    'Special Event': {'adults': (100, 500), 'children': (30, 200), 'first_timers': (5, 50)},
    'Evening Sacrifice': {'adults': (60, 150), 'children': (15, 60), 'first_timers': (0, 10)},
    'Prayer Meeting': {'adults': (40, 120), 'children': (10, 40), 'first_timers': (0, 8)},
    'Youth Service': {'adults': (30, 100), 'children': (20, 80), 'first_timers': (2, 20)},
    'Marriage Counselling': {'adults': (10, 40), 'children': (0, 10), 'first_timers': (0, 5)},
}

# Default range for unknown service types
default_range = {'adults': (50, 200), 'children': (20, 80), 'first_timers': (0, 15)}

updated = 0
for i, record in enumerate(records.iterator(chunk_size=1000), 1):
    # Get the appropriate range for this service type
    ranges = service_ranges.get(record.service_type, default_range)
    
    # Generate random counts
    record.adult_count = random.randint(*ranges['adults'])
    record.children_count = random.randint(*ranges['children'])
    record.first_timers_count = random.randint(*ranges['first_timers'])
    
    # Save (total_count will be auto-calculated)
    record.save()
    updated += 1
    
    # Progress indicator
    if i % 100 == 0:
        print(f"Progress: {i}/{total} ({(i/total)*100:.1f}%)")

print(f"\n✅ Completed! Updated {updated} records with realistic attendance values.")

# Show some sample records
print("\nSample records:")
for record in Attendance.objects.all()[:5]:
    print(f"{record.date} | {record.service_type:20} | Adults:{record.adult_count:3} Children:{record.children_count:3} FirstTimers:{record.first_timers_count:2} Total:{record.total_count:3}")
