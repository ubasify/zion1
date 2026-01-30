import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operations.models import Announcement, Finance
from ministry.models import Event
from people.models import Member
from django.contrib.auth import get_user_model

User = get_user_model()
first_user = User.objects.first()
first_member = Member.objects.first()

print(f"Populating data...")

# Create Announcements
a1, c1 = Announcement.objects.get_or_create(
    title="Sunday Service Update",
    defaults={
        'content': "Join us this Sunday for a special thanksgiving service. Don't forget to invite your friends and family!",
        'is_public': True
    }
)
print(f"- Announcement: {a1.title}")

a2, c2 = Announcement.objects.get_or_create(
    title="Youth Conference 2026",
    defaults={
        'content': "Registration for the annual Youth Conference is now open. Early bird tickets available until the end of the month.",
        'is_public': True
    }
)
print(f"- Announcement: {a2.title}")

# Create Mock Contribution (Finance) if none
if first_member:
    if not Finance.objects.filter(member=first_member).exists():
        Finance.objects.create(
            date=date.today(),
            category="Tithe",
            amount=500.00,
            description="Online Tithe",
            member=first_member,
            recorded_by=first_user
        )
        print(f"- Created mock contribution for {first_member}")
    else:
        print(f"- Contribution exists for {first_member}")

print("✅ Portal data populated successfully!")
