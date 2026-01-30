"""
Script to populate Ministry records with new field values:
- icon_type
- active_participation_rate
- reporting_status
- last_report_date
- meeting_day
- team_lead (random member)
"""

import os
import django
import random
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ministry.models import Ministry
from people.models import Member

# Icon mapping for different ministry types
MINISTRY_ICONS = {
    'worship': 'music',
    'choir': 'music',
    'steward': 'shield',
    'youth': 'heart',
    'sunday school': 'book-open',
    'media': 'camera',
    'evangelism': 'megaphone',
    'follow-up': 'user-check',
    'sanctuary': 'home',
    'sound': 'mic',
    'tech': 'monitor',
}

WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
STATUSES = ['up_to_date', 'pending', 'overdue']

# Get all ministries
ministries = Ministry.objects.all()
members = list(Member.objects.filter(status='active'))

print(f"Updating {ministries.count()} ministries with new data...")

for ministry in ministries:
    # Assign icon based on ministry name
    icon = 'users'  # default
    for keyword, icon_name in MINISTRY_ICONS.items():
        if keyword in ministry.name.lower():
            icon = icon_name
            break
    
    ministry.icon_type = icon
    
    # Random participation rate (higher for some ministries)
    ministry.active_participation_rate = random.randint(55, 95)
    
    # Random reporting status (weighted towards up_to_date)
    ministry.reporting_status = random.choices(
        STATUSES,
        weights=[60, 30, 10]  # 60% up to date, 30% pending, 10% overdue
    )[0]
    
    # Last report date (within last 30 days, some older for overdue)
    if ministry.reporting_status == 'overdue':
        days_ago = random.randint(15, 45)
    elif ministry.reporting_status == 'pending':
        days_ago = random.randint(5, 15)
    else:  # up_to_date
        days_ago = random.randint(1, 7)
    
    ministry.last_report_date = date.today() - timedelta(days=days_ago)
    
    # Random meeting day
    ministry.meeting_day = random.choice(WEEKDAYS)
    
    # Assign random team lead if members exist
    if members:
        ministry.team_lead = random.choice(members)
    
    ministry.save()
    
    print(f"✓ {ministry.name}: {icon}, {ministry.active_participation_rate}%, {ministry.reporting_status}, {ministry.meeting_day}")

print(f"\n✅ Successfully updated {ministries.count()} ministries!")

# Show summary stats
total_volunteers = sum(m.member_count for m in ministries)
avg_participation = sum(m.active_participation_rate for m in ministries) / ministries.count() if ministries.count() > 0 else 0
up_to_date_count = ministries.filter(reporting_status='up_to_date').count()

print(f"\nSummary Stats:")
print(f"Total Volunteers: {total_volunteers}")
print(f"Average Participation: {avg_participation:.0f}%")
print(f"Reporting Compliance: {up_to_date_count}/{ministries.count()}")
