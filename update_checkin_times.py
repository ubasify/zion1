"""
Script to update MemberAttendance check_in_time to random dates
between 2020-01-01 00:00:00 and 2026-01-25 23:59:59
with an imbalanced distribution (more recent dates have higher probability)

Usage:
    python update_checkin_times.py
"""

import os
import django
import random
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operations.models import MemberAttendance
from django.utils import timezone

# Define date range
start_date = datetime(2020, 1, 1, 0, 0, 0)
end_date = datetime(2026, 1, 25, 23, 59, 59)

# Make timezone-aware
start_date = timezone.make_aware(start_date)
end_date = timezone.make_aware(end_date)

def random_weighted_datetime(start, end):
    """
    Generate a random datetime with bias towards more recent dates.
    Uses exponential distribution to create imbalance.
    """
    # Calculate total seconds in range
    total_seconds = (end - start).total_seconds()
    
    # Use exponential distribution (higher values = more recent)
    # Lambda = 2 gives moderate bias towards recent dates
    random_factor = random.expovariate(2.0)
    
    # Clamp to [0, 1] range (most values will be < 1)
    random_factor = min(random_factor, 1.0)
    
    # Calculate random seconds from start
    random_seconds = total_seconds * random_factor
    
    return start + timedelta(seconds=random_seconds)

# Get all MemberAttendance records
records = MemberAttendance.objects.all()
total = records.count()

print(f"Updating {total} MemberAttendance check-in times...")
print(f"Date range: {start_date} to {end_date}")
print(f"Distribution: Imbalanced (weighted towards recent dates)\n")

# Update records in batches for better performance
batch_size = 1000
updated = 0

for i, record in enumerate(records.iterator(chunk_size=batch_size), 1):
    # Generate random check-in time
    record.check_in_time = random_weighted_datetime(start_date, end_date)
    record.save(update_fields=['check_in_time'])
    
    updated += 1
    
    # Progress indicator
    if i % 1000 == 0:
        print(f"Progress: {i}/{total} ({(i/total)*100:.1f}%)")

print(f"\n✅ Completed! Updated {updated} records.")
print(f"Check-in times now range from {start_date.date()} to {end_date.date()}")
