
import os
import django
import random
from datetime import date
from django.utils import timezone
import sys
# Add current directory relative to script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ministry.models import Parish
from operations.models import Finance

def seed_2026_data():
    print("Seeding SPECIFIC 2026 Data...")
    
    parishes = Parish.objects.all()
    if not parishes.exists():
        print("No parishes found!")
        return

    # Targeting Jan 2026 specifically
    # Current date in simulation is 2026-01-25
    
    dates_2026 = [
        date(2026, 1, 5),
        date(2026, 1, 12),
        date(2026, 1, 19),
        date(2026, 1, 24)
    ]
    
    categories = ["Monthly Return", "Special Offering"]
    
    # "Grace Parish" should be winner again for consistency, or "Kings Court"
    winner = parishes.filter(name="Grace Parish").first() or parishes[0]
    
    count = 0
    for parish in parishes:
        multiplier = 3.0 if parish == winner else 1.0
        
        for d in dates_2026:
            # Create a big chunk of returns
            amount = random.uniform(10000, 50000) * multiplier
            Finance.objects.create(
                category=random.choice(categories),
                amount=amount,
                date=d,
                parish=parish,
                description=f"2026 Seed {d}"
            )
            count += 1
            
    print(f"Added {count} records for 2026.")

if __name__ == '__main__':
    seed_2026_data()
