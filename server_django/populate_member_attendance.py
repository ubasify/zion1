import os
import django
import random
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operations.models import Attendance, MemberAttendance
from people.models import Member

def populate():
    print("Populating MemberAttendance based on Attendance.total_count...")
    
    attendances = Attendance.objects.all()
    members = list(Member.objects.all())
    
    if not members:
        print("No members found! Cannot populate attendance.")
        return

    count = 0
    total_recs = 0
    
    with transaction.atomic():
        for att in attendances:
            # Check if already has details
            if att.details.exists():
                continue
                
            target_count = att.total_count
            # Pick random members
            # If target > members, allow duplicates or just cap at members count?
            # Unlikely for this demo, 5000 members.
            
            selected_members = random.sample(members, min(len(members), target_count))
            
            objs = [
                MemberAttendance(
                    attendance=att,
                    member=m,
                    status='Present'
                ) for m in selected_members
            ]
            
            MemberAttendance.objects.bulk_create(objs)
            count += 1
            total_recs += len(objs)
            print(f"Created {len(objs)} records for {att.date}")

    print(f"Done! Processed {count} services. Created {total_recs} granular records.")

if __name__ == '__main__':
    populate()
