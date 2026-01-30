
import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_django.settings')
django.setup()

from ministry.models import Parish
from operations.models import Finance
from people.models import Member

def seed_parish_returns():
    print("Seeding Parish Returns...")
    
    parishes = Parish.objects.all()
    if not parishes.exists():
        print("No parishes found. Creating some...")
        names = ["Grace Parish", "Victory Sanctuary", "Peace Assembly", "Life Gate", "Divine Favor", "Kings Court"]
        for name in names:
            Parish.objects.create(name=name)
        parishes = Parish.objects.all()

    # Define periods: This Year and Last Year
    now = timezone.now().date()
    start_this_year = now.replace(month=1, day=1)
    start_last_year = start_this_year.replace(year=start_this_year.year - 1)
    
    # Categories
    categories = ["Monthly Return", "Tithe Remittance", "Special Offering", "Mission Support"]

    count = 0
    # Determine a "Top Parish" to ensure distinct winner
    top_parish = parishes[0]
    
    for parish in parishes:
        # Base amount multiplier
        multiplier = 2.0 if parish == top_parish else 1.0
        
        # Generate data for last 18 months
        for i in range(18):
            date_point = now - timedelta(days=30 * i)
            # Random amount between 5000 and 20000
            for _ in range(random.randint(2, 5)):
                amount = random.uniform(5000, 25000) * multiplier
                # Randomize slightly more
                amount = amount * random.uniform(0.8, 1.2)
                
                Finance.objects.create(
                    category=random.choice(categories),
                    amount=round(amount, 2),
                    date=date_point,
                    parish=parish,
                    description=f"Automated seed return for {date_point.strftime('%B %Y')}"
                )
                count += 1
                
    print(f"Successfully created {count} finance records for {parishes.count()} parishes.")
    print(f"Top Parish designated: {top_parish.name}")

if __name__ == '__main__':
    seed_parish_returns()
