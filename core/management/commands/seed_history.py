from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import random
from people.models import Member
from operations.models import Attendance, Finance, MemberAttendance, Expense
from ministry.models import Ministry, Parish

class Command(BaseCommand):
    help = 'Seeds historical data (Attendance & Finance)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning up old data...")
        Attendance.objects.all().delete() # Cascades to MemberAttendance
        Finance.objects.all().delete()
        Expense.objects.all().delete()
        # Member.objects.all().delete() # Optional: Keep members
        
        self.stdout.write(f"Starting historical data seed (2020-2025)...")

        start_date = date(2020, 1, 1)
        end_date = date(2025, 12, 31)
        
        
        # Ensure we have members to reuse
        if Member.objects.count() < 100:
            self.stdout.write("Creating base members...")
            members = []
            for i in range(200):
                members.append(Member(
                    first_name=f"Member{i}",
                    last_name=f"Historical{i}",
                    email=f"history{i}@example.com",
                    status='active'
                ))
            Member.objects.bulk_create(members)
        
        all_members = list(Member.objects.all())
        
        # --- SEED MINISTRIES ---
        self.stdout.write("Seeding Ministries...")
        # Ensure default parish
        default_parish, _ = Parish.objects.get_or_create(name="Main Parish", defaults={"address": "123 Main St"})
        
        ministry_names = [
            "Operations", "Noble men", "Virtuous Women", "Protocol", "Sound", "Band", "Worship",
            "Security", "Conflict Resolution", "Drama", "Follow up", "Stewards/ Welcome",
            "Growth Group", "Beautification", "Finance", "Watchers", "The Lord's Heritage",
            "Sanctuary Keepers", "Logistics", "Evangelism", "Garbage 2 Gold", "Welfare/Hospitality",
            "\"D\" Generation", "Food Bank", "Youth Church", "Christian Education", "Events",
            "Sports", "Career Development", "Student Recruitment"
        ]
        
        # Clear old and bulk create new
        Ministry.objects.all().delete()
        ministry_objs = [Ministry(name=name, parish=default_parish) for name in ministry_names]
        Ministry.objects.bulk_create(ministry_objs)
        prominent_ministries = list(Ministry.objects.all())

        # Iterate weeks
        current_date = start_date
        
        member_attendance_buffer = []
        finance_buffer = []
        expense_buffer = []

        while current_date <= end_date:
            # ... (Attendance logic unchanged) ...
            # Determine day of week (0=Mon, 6=Sun)
            weekday = current_date.weekday()
            
            services_today = []

            if weekday == 0: # Monday
                services_today.append(("Evening Sacrifice", "Online/Physical", 50, 100))
            elif weekday == 2: # Wednesday
                services_today.append(("Marriage Counselling", "Online (YouTube)", 200, 500)) # Higher for online?
            elif weekday == 3: # Thursday
                services_today.append(("Blast Service", "Physical", 80, 150))
            elif weekday == 5: # Saturday
                services_today.append(("Evangelism", "Physical", 20, 50))
            elif weekday == 6: # Sunday
                services_today.append(("Sunday Service", "Online/Physical", 300, 600))
            
            for svc_name, medium, min_att, max_att in services_today:
                # Randomize total count
                total_count = random.randint(min_att, max_att)
                
                att = Attendance.objects.create(
                    date=current_date,
                    service_type=svc_name,
                    total_count=total_count,
                    first_timers_count=random.randint(0, 5)
                )

                present_members = random.sample(all_members, k=min(len(all_members), int(total_count * 0.6)))
                
                for mem in present_members:
                    member_attendance_buffer.append(MemberAttendance(
                        attendance=att,
                        member=mem,
                        status='Present',
                        check_in_time=timezone.now()
                    ))

            # 2. FINANCE (Income)
            if weekday == 6:
                giving_members = random.sample(all_members, k=random.randint(50, 150))
                
                finance_buffer_batch = []
                for mem in giving_members:
                    if random.random() < 0.3: 
                        amount = random.uniform(50, 500)
                        finance_buffer_batch.append(Finance(
                            date=current_date,
                            category="Tithes",
                            amount=round(amount, 2),
                            description=f"Tithes from {mem.first_name} {mem.last_name}",
                            member=mem,
                            ministry=None
                        ))
                    
                    if random.random() < 0.8:
                        amount = random.uniform(5, 100)
                        finance_buffer_batch.append(Finance(
                            date=current_date,
                            category="Offering",
                            amount=round(amount, 2),
                            description=f"Offering from {mem.first_name} {mem.last_name}",
                            member=mem,
                            ministry=None
                        ))
                        
                    if random.random() < 0.05:
                        amount = random.uniform(20, 200)
                        finance_buffer_batch.append(Finance(
                            date=current_date,
                            category="Missions",
                            amount=round(amount, 2),
                            description=f"Mission support from {mem.first_name}",
                            member=mem,
                            ministry=None
                        ))
                finance_buffer.extend(finance_buffer_batch)

            # 3. EXPENSES (Monthly & Weekly)
            # Weekly Expenses (e.g. Honorarium, Cleaning)
            if weekday == 0: # on Monday
                amount = random.uniform(500, 2000)
                expense_buffer.append(Expense(
                    date=current_date,
                    category="Operations",
                    amount=round(amount, 2),
                    description="Weekly operations cost"
                ))

            # Monthly Expenses (Rent, Salaries) - 1st of month
            if current_date.day == 1:
                expense_buffer.append(Expense(
                    date=current_date,
                    category="Rent",
                    amount=15000.00,
                    description="Monthly Venue Rent"
                ))
                expense_buffer.append(Expense(
                    date=current_date,
                    category="Salaries",
                    amount=random.uniform(20000, 25000),
                    description="Staff Salaries"
                ))

            # Batch create buffers
            if len(member_attendance_buffer) > 5000:
                self.stdout.write(f"Saving batch... ({current_date})")
                MemberAttendance.objects.bulk_create(member_attendance_buffer)
                member_attendance_buffer = []
            
            if len(finance_buffer) > 1000:
                Finance.objects.bulk_create(finance_buffer)
                finance_buffer = []
                
            if len(expense_buffer) > 1000:
                Expense.objects.bulk_create(expense_buffer)
                expense_buffer = []

            # Advance by 1 day
            current_date += timedelta(days=1)

        # Final batch
        if member_attendance_buffer:
            MemberAttendance.objects.bulk_create(member_attendance_buffer)
        if finance_buffer:
            Finance.objects.bulk_create(finance_buffer)
        if expense_buffer:
            Expense.objects.bulk_create(expense_buffer)

        self.stdout.write(self.style.SUCCESS('Successfully seeded historical data (Attendance & Finance)!'))
