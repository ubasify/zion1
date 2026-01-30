import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from people.models import Member
from ministry.models import Ministry, Service, Event, Parish
from operations.models import Attendance, Finance, Expense, MemberAttendance, BankAccount, Budget

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with 3 years of sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # 0. Ensure Admin User
        admin_user = User.objects.first()
        if not admin_user:
            self.stdout.write(self.style.WARNING("No admin user found. Creating one..."))
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')

        # 1. Create Default Parish
        parish, created = Parish.objects.get_or_create(
            name='RCCG Holy Ghost Zone',
            defaults={
                'address': '123 Church Street, London',
                'pastor_name': 'Pastor John Doe',
                'contact_email': 'info@rccghgz.org'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Parish: {parish.name}"))

        # 2. Create Bank Accounts
        gtbank, _ = BankAccount.objects.get_or_create(
            name="GTBank Main Account",
            defaults={'account_number': '0123456789', 'bank_name': 'GTBank', 'currency': 'GBP'}
        )
        access, _ = BankAccount.objects.get_or_create(
            name="Access Building Fund",
            defaults={'account_number': '9876543210', 'bank_name': 'Access Bank', 'currency': 'GBP'}
        )
        cash, _ = BankAccount.objects.get_or_create(
            name="Petty Cash",
            defaults={'account_number': 'N/A', 'bank_name': 'Cash', 'currency': 'GBP'}
        )
        
        bank_accounts = [gtbank, access] # Use main accounts for most transactions

        # Create Budgets for Current Year
        current_year = timezone.now().year
        budget_categories = ['Rent', 'Salaries', 'Utilities', 'Maintenance', 'Welfare', 'Honorarium', 'Equipment']
        for cat in budget_categories:
            Budget.objects.get_or_create(
                category=cat,
                year=current_year,
                defaults={
                    'amount': random.randint(5000, 20000),
                    'start_date': date(current_year, 1, 1),
                    'end_date': date(current_year, 12, 31),
                    'description': f'Budget for {cat}'
                }
            )

        # 3. Create Members (if few exist)
        if Member.objects.count() < 50:
            self.stdout.write("Creating sample members...")
            first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Emma', 'Robert', 'Olivia', 'William', 'Ava']
            last_names = ['Smith', 'Johnson', 'Brown', 'Williams', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
            
            for _ in range(50):
                Member.objects.create(
                    first_name=random.choice(first_names),
                    last_name=random.choice(last_names),
                    email=f"user{random.randint(1000,9999)}@example.com",
                    status=random.choice(['Active', 'Active', 'Active', 'Inactive'])
                )
        
        members = list(Member.objects.all())

        # 4. Create Ministries
        ministry_names = ['Choir', 'Ushers', 'Technical', 'Children', 'Evangelism', 'Youth']
        ministries = []
        for name in ministry_names:
            m, _ = Ministry.objects.get_or_create(
                name=name, 
                defaults={
                    'description': f'{name} Ministry',
                    'parish': parish 
                }
            )
            ministries.append(m)

        # 5. Create Services (Sunday & Midweek)
        sunday_srv, _ = Service.objects.get_or_create(name='Sunday Service', defaults={'day_of_week': 'Sunday', 'time': '09:00'})
        midweek_srv, _ = Service.objects.get_or_create(name='Bible Study', defaults={'day_of_week': 'Wednesday', 'time': '18:00'})
        
        # 6. Loop through last 3 years (approx 156 weeks)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365 * 3)
        current_date = start_date
        
        transactions_created = 0
        attendance_created = 0
        expenses_created = 0

        self.stdout.write(f"Generating data from {start_date} to {end_date}...")

        while current_date <= end_date:
            # --- ATTENDANCE ---
            if current_date.weekday() == 6: # Sunday
                adults = random.randint(80, 150)
                children = random.randint(20, 50)
                ft = random.randint(0, 5)
                att = Attendance.objects.create(
                    date=current_date,
                    service=sunday_srv,
                    service_type='Sunday Service',
                    adult_count=adults,
                    children_count=children,
                    first_timers_count=ft
                )
                attendance_created += 1
                
                # Inflows
                Finance.objects.create(
                    date=current_date,
                    category='Offering',
                    amount=random.uniform(500, 2000),
                    description='Sunday Service Offering',
                    recorded_by=admin_user,
                    bank_account=random.choice(bank_accounts) # Assign to bank
                )
                transactions_created += 1
                
                for _ in range(random.randint(5, 15)): 
                    Finance.objects.create(
                        date=current_date,
                        category='Tithe',
                        amount=random.uniform(50, 500),
                        member=random.choice(members),
                        description='Tithe',
                        recorded_by=admin_user,
                        bank_account=gtbank
                    )
                    transactions_created += 1

            elif current_date.weekday() == 2: # Wednesday
                adults = random.randint(30, 60)
                Attendance.objects.create(
                    date=current_date,
                    service=midweek_srv,
                    service_type='Bible Study',
                    adult_count=adults,
                    children_count=0,
                    first_timers_count=random.randint(0, 2)
                )
                attendance_created += 1
                
                Finance.objects.create(
                    date=current_date,
                    category='Offering',
                    amount=random.uniform(100, 400),
                    description='Midweek Offering',
                    recorded_by=admin_user,
                    bank_account=random.choice(bank_accounts)
                )

            # --- EXPENSES ---
            if current_date.day == 1:
                Expense.objects.create(
                    date=current_date,
                    category='Rent',
                    amount=1500,
                    description='Monthly Facility Rent',
                    authorized_by=admin_user,
                    bank_account=gtbank
                )
                Expense.objects.create(
                    date=current_date,
                    category='Salaries',
                    amount=3000,
                    description='Staff Salaries',
                    authorized_by=admin_user,
                    bank_account=gtbank
                )
                expenses_created += 2

            if random.random() < 0.1: 
                Expense.objects.create(
                    date=current_date,
                    category=random.choice(['Utilities', 'Maintenance', 'Honorarium', 'Welfare', 'Equipment']),
                    amount=random.uniform(50, 500),
                    description='Ad-hoc expense',
                    authorized_by=admin_user,
                    bank_account=cash if random.random() < 0.3 else gtbank # 30% petty cash
                )
                expenses_created += 1

            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f"Done! Created {attendance_created} attendance records, {transactions_created} income records, {expenses_created} expense records."))
