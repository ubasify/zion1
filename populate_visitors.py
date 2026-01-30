import os
import django
import random
from datetime import date, timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from outreach.models import Visitor, FollowUpLog
from core.models import User

def populate_visitors():
    print("Populating Visitors...")
    
    # Get a user to handle follow-ups
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin_seed', 'admin@example.com', 'password123')

    visitor_data = [
        {
            'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com', 
            'phone': '08012345678', 'whatsapp_number': '08012345678', 'city': 'Lagos', 'gender': 'Male', 
            'how_did_you_hear': 'Social Media', 'status': 'new',
            'prayer_request': 'Praying for a new job opportunity.'
        },
        {
            'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane.smith@example.com', 
            'phone': '08023456789', 'whatsapp_number': '08023456789', 'city': 'Abuja', 'gender': 'Female', 
            'how_did_you_hear': 'Friend', 'invited_by': 'Bro. Samuel', 'status': 'pending',
            'prayer_request': 'Safe travel for my family.'
        },
        {
            'first_name': 'Michael', 'last_name': 'Okon', 'email': 'm.okon@gmail.com', 
            'phone': '07033445566', 'whatsapp_number': '07033445566', 'city': 'Port Harcourt', 'gender': 'Male', 
            'how_did_you_hear': 'Banner', 'status': 'converted',
            'interest_in_membership': True
        },
        {
            'first_name': 'Sarah', 'last_name': 'Williams', 'email': 'sarah.w@outlook.com', 
            'phone': '09011223344', 'whatsapp_number': '09011223344', 'city': 'Ibadan', 'gender': 'Female', 
            'how_did_you_hear': 'Radio', 'status': 'lost',
            'prayer_request': 'Healing for my mother.'
        },
        {
            'first_name': 'David', 'last_name': 'Adeleke', 'email': 'david.a@example.com', 
            'phone': '08155667788', 'whatsapp_number': '08155667788', 'city': 'Lagos', 'gender': 'Male', 
            'how_did_you_hear': 'Search Engine', 'status': 'new',
            'interest_in_membership': True
        },
        {
            'first_name': 'Chinelo', 'last_name': 'Eze', 'email': 'chinelo.e@gmail.com', 
            'phone': '08099887766', 'whatsapp_number': '08099887766', 'city': 'Enugu', 'gender': 'Female', 
            'how_did_you_hear': 'Social Media', 'status': 'pending',
            'prayer_request': 'Academic success.'
        }
    ]

    for data in visitor_data:
        visitor, created = Visitor.objects.update_or_create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            defaults={
                'email': data.get('email'),
                'phone': data.get('phone'),
                'whatsapp_number': data.get('whatsapp_number'),
                'city': data.get('city'),
                'gender': data.get('gender'),
                'how_did_you_hear': data.get('how_did_you_hear'),
                'invited_by': data.get('invited_by'),
                'prayer_request': data.get('prayer_request'),
                'status': data.get('status'),
                'interest_in_membership': data.get('interest_in_membership', False)
            }
        )
        
        if created:
            print(f"Created Visitor: {visitor}")
            
            # Add some follow-up logs for specific statuses
            if visitor.status in ['pending', 'converted']:
                num_logs = random.randint(1, 3)
                for i in range(num_logs):
                    FollowUpLog.objects.create(
                        visitor=visitor,
                        follow_up_type=random.choice(['call', 'text', 'email']),
                        notes=f"Follow-up session {i+1}: Discussed church activities and spiritual growth.",
                        handled_by=admin_user
                    )
                print(f"  Added {num_logs} follow-up logs.")

    print("Success: Fictitious data added.")

if __name__ == "__main__":
    populate_visitors()
