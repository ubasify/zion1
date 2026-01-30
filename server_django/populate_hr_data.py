import os
import django
import random
from datetime import date, timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from employees.models import Employee, LeaveRequest, PayrollRecord
from ministry.models import Ministry
from core.models import User
from people.models import Member

def seed_hr_data():
    print("Seeding HR Data...")
    
    # Get or create dependencies
    ministries = list(Ministry.objects.all())
    if not ministries:
        print("No ministries found. Please seed ministries first.")
        return
        
    users = list(User.objects.all())
    members = list(Member.objects.all())
    
    # Sample Data
    job_titles = ['Church Administrator', 'Accountant', 'Choir Director', 'Youth Pastor', 'Media Lead', 'Facility Manager']
    
    # Create Employees
    for i in range(10):
        first_name = f"Staff_{i}"
        last_name = "User"
        emp_id = f"EMP{100+i}"
        
        # Pick a ministry
        dept = random.choice(ministries)
        
        # Create Employee
        emp, created = Employee.objects.get_or_create(
            employee_id=emp_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f"staff{i}@example.com",
                'phone': f"080000000{i}",
                'department': dept,
                'job_title': random.choice(job_titles),
                'hire_date': date(2023, 1, 1) + timedelta(days=i*30),
                'employment_type': random.choice(['full_time', 'part_time']),
                'status': 'active',
                'base_salary': random.randint(50000, 250000),
            }
        )
        
        if created:
            print(f"Created Employee: {emp.get_full_name}")
            
            # Create Leave Request
            LeaveRequest.objects.create(
                employee=emp,
                leave_type=random.choice(['vacation', 'sick']),
                start_date=timezone.now().date() + timedelta(days=random.randint(1, 60)),
                end_date=timezone.now().date() + timedelta(days=random.randint(61, 70)),
                reason="Regular annual leave request.",
                status='pending'
            )
            
            # Create Payroll Record for Dec 2025
            PayrollRecord.objects.create(
                employee=emp,
                month=12,
                year=2025,
                basic_salary=emp.base_salary,
                allowances=10000,
                deductions=5000,
                net_pay=emp.base_salary + 5000,
                status='paid',
                payment_date=date(2025, 12, 30)
            )

    print("HR Data Seeding Completed!")

if __name__ == "__main__":
    seed_hr_data()
