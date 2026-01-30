from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from people.models import Member, Volunteer
from operations.models import Attendance, Finance, CommunityImpact, Event
from ministry.models import Ministry, SmallGroup, Parish

class Command(BaseCommand):
    help = 'Seeds dashboard with realistic executive data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding dashboard data...")
        
        # 1. Finances (Weekly Giving)
        # Goal: ~$45.2k this week
        categories = ['Tithes', 'Offerings', 'Projects', 'Missions']
        today = timezone.now().date()
        
        # Create giving for this week
        for i in range(7):
            day = today - timedelta(days=i)
            # Random large amounts
            Finance.objects.create(
                date=day, 
                category=random.choice(categories),
                amount=random.uniform(1000, 8000),
                description="Seeded donation"
            )
            
        self.stdout.write("- Created Finance records")

        # 2. Attendance (Service Specifics)
        # Specific service types mentioned in design
        services = [
            ("9:00 AM Classic", 345),
            ("11:00 AM Modern", 615),
            ("Online Campus", 280),
            ("Grace Kids", 142)
        ]
        
        # Create trend data (last 20 weeks)
        for i in range(20):
            week_date = today - timedelta(weeks=i)
            # Make Sunday
            sunday = week_date - timedelta(days=week_date.weekday() + 1)
            
            total_week = 0
            for svc_name, avg_count in services:
                # Random variation +- 10%
                count = int(avg_count * random.uniform(0.9, 1.1))
                
                # Create Event if needed (simplified: just store in Attendance)
                # But Attendance requires Event FK? No, looks like it's optional or we can reuse one
                # Checking model: event can be null.
                
                Attendance.objects.create(
                    date=sunday,
                    service_type=svc_name,
                    total_count=count,
                    first_timers_count=random.randint(1, 10)
                )
        
        self.stdout.write("- Created Attendance Trend records")

        # 3. Small Groups (Active: 65)
        # Create some if none exist
        if SmallGroup.objects.count() < 65:
            to_create = 65 - SmallGroup.objects.count()
            for i in range(to_create):
                SmallGroup.objects.create(
                    name=f"Small Group {i+1}",
                    semester="Spring 2025",
                    leader_name=f"Leader {i}",
                    status='active'
                )
        self.stdout.write("- Created Small Groups")

        # 4. Community Impact
        impacts = [
            ("Mobile Food Pantry", "Served 145 families in downtown district.", 145),
            ("Backpack Drive", "Distributed 500 backpacks to local schools.", 500),
            ("Homeless Shelter Dinner", "Served hot meals to 200 residents.", 200),
            ("City Cleanup", "Removed 50 bags of trash from local park.", 0)
        ]
        
        for name, desc, ppl in impacts:
            CommunityImpact.objects.create(
                name=name,
                description=desc,
                people_impacted=ppl,
                date=today - timedelta(days=random.randint(1, 14))
            )
        self.stdout.write("- Created Community Impact records")

        # 5. Volunteers
        # Ensure we have some 'Worker' members for the count
        # (Assuming Member model exists)
        current_workers = Member.objects.filter(member_type='Worker').count()
        if current_workers < 412:
            needed = 412 - current_workers
            for i in range(needed):
                Member.objects.create(
                    first_name=f"Vol{i}",
                    last_name=f"Worker{i}",
                    member_type='Worker',
                    status='active',
                    email=f"vol{i}@example.com"
                )
        
        self.stdout.write("Done! Dashboard seeded.")
