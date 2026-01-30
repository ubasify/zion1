import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from events.models import Event, EventCategory, EventRSVP
from people.models import Member
from ministry.models import Ministry

fake = Faker()

def create_categories():
    categories = [
        {'name': 'Sunday Service', 'color': 'blue'},
        {'name': 'Bible Study', 'color': 'green'},
        {'name': 'Revival', 'color': 'red'},
        {'name': 'Concert', 'color': 'purple'},
        {'name': 'Outreach', 'color': 'orange'},
        {'name': 'Social', 'color': 'yellow'},
    ]
    created = []
    for cat in categories:
        obj, _ = EventCategory.objects.get_or_create(
            name=cat['name'],
            defaults={'color': cat['color']}
        )
        created.append(obj)
    return created

def create_events(categories, members, ministries):
    events = []
    
    # Generate events for the past year and next 3 months
    start_date = timezone.now() - timedelta(days=365)
    end_date = timezone.now() + timedelta(days=90)
    
    current = start_date
    while current <= end_date:
        # 50% chance of event on any given day, higher on Sundays
        is_sunday = current.weekday() == 6
        if is_sunday or random.random() < 0.3:
            category = categories[0] if is_sunday else random.choice(categories[1:])
            
            title = f"{category.name}: {fake.catch_phrase()}"
            if is_sunday:
                title = "Sunday Celebration Service"
            
            # Start time between 9am and 7pm
            hour = 9 if is_sunday else random.randint(17, 19)
            event_start = current.replace(hour=hour, minute=0, second=0, microsecond=0)
            duration = 2 if is_sunday else 1.5
            event_end = event_start + timedelta(hours=duration)
            
            status = 'published'
            if event_start > timezone.now() and random.random() < 0.2:
                status = 'draft'
            
            event = Event.objects.create(
                title=title,
                description=fake.paragraph(nb_sentences=5),
                category=category,
                start_date=event_start,
                end_date=event_end,
                location="Main Sanctuary" if is_sunday else fake.address(),
                is_virtual=random.choice([True, False]),
                organizer=random.choice(ministries) if ministries and random.random() > 0.5 else None,
                status=status,
            )
            events.append(event)
            print(f"Created event: {event.title} on {event.start_date.date()}")
            
        current += timedelta(days=random.randint(2, 5)) # Skip a few days
        
    return events

def create_rsvps(events, members):
    print("Generating RSVPs...")
    for event in events:
        # Skip drafts
        if event.status != 'published':
            continue
            
        # Random attendance
        attendees = random.sample(list(members), k=random.randint(5, min(30, len(members))))
        
        for member in attendees:
            status = random.choice(['going', 'going', 'going', 'maybe', 'not_going'])
            
            # If event is in past, maybe they checked in
            checked_in = False
            checked_in_at = None
            if event.start_date < timezone.now() and status == 'going':
                checked_in = random.choice([True, True, False])
                if checked_in:
                    checked_in_at = event.start_date + timedelta(minutes=random.randint(-15, 30))
            
            EventRSVP.objects.get_or_create(
                event=event,
                member=member,
                defaults={
                    'status': status,
                    'checked_in': checked_in,
                    'checked_in_at': checked_in_at
                }
            )

def run():
    print("Starting data population...")
    categories = create_categories()
    members = list(Member.objects.all())
    ministries = list(Ministry.objects.all())
    
    if not members:
        print("No members found! Run populate_portal_data.py first.")
        return

    events = create_events(categories, members, ministries)
    create_rsvps(events, members)
    print("Done!")

if __name__ == '__main__':
    run()
