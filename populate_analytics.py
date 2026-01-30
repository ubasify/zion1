import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from people.models import Member
from operations.models import Finance, Expense, Attendance
from ministry.models import Ministry

fake = Faker()

def create_finances():
    print("Generating finances...")
    # Last 12 months
    today = timezone.now().date()
    
    # Categories
    income_cats = ['Tithes', 'Offering', 'Thanksgiving', 'Donation', 'Project Pledge']
    expense_cats = ['Salaries', 'Utilities', 'Maintenance', 'Outreach', 'Equipment']
    
    ministries = list(Ministry.objects.all())
    members = list(Member.objects.all())
    
    records = []
    
    # Generate 5-10 records per week
    for i in range(52):
        week_start = today - timedelta(weeks=i)
        
        # income
        for _ in range(random.randint(5, 15)):
            date = week_start + timedelta(days=random.randint(0, 6))
            Finance.objects.create(
                date=date,
                category=random.choice(income_cats),
                amount=random.uniform(50, 500), # Small amounts frequent
                member=random.choice(members) if members and random.random() > 0.3 else None,
                ministry=random.choice(ministries) if ministries and random.random() > 0.8 else None,
                description=fake.sentence()
            )
            
        # occasional big income
        if random.random() > 0.7:
             Finance.objects.create(
                date=week_start,
                category='Donation',
                amount=random.uniform(1000, 5000),
                description='Large donation'
            )

        # expense
        for _ in range(random.randint(1, 3)):
             date = week_start + timedelta(days=random.randint(0, 6))
             Expense.objects.create(
                date=date,
                category=random.choice(expense_cats),
                amount=random.uniform(200, 1500),
                description=fake.sentence()
             )

def create_attendance_history():
    print("Generating historical attendance...")
    # Check if we have attendance
    if Attendance.objects.count() > 10:
        print("Attendance already populated.")
        return

    today = timezone.now().date()
    for i in range(52):
        sunday = today - timedelta(weeks=i)
        # Find nearest Sunday
        while sunday.weekday() != 6:
            sunday -= timedelta(days=1)
            
        # Create attendance record
        adults = random.randint(50, 80) + (i % 10) # slight variation
        children = random.randint(10, 25)
        first_timers = random.randint(0, 5)
        
        Attendance.objects.create(
            date=sunday,
            total_count=adults + children + first_timers,
            adult_count=adults,
            children_count=children,
            first_timers_count=first_timers,
            service_type="Sunday Service"
        )

def run():
    create_finances()
    create_attendance_history()
    print("Done!")

if __name__ == '__main__':
    run()
