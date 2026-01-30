from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import random
from employees.models import Employee, LeaveRequest, PayrollRecord, EmployeeDocument, PerformanceReview
from ministry.models import Ministry


class Command(BaseCommand):
    help = 'Seed employee data for testing HR module'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding employee data...')
        
        # Get or create departments (using Ministry as departments)
        departments = list(Ministry.objects.all()[:5])
        if not departments:
            self.stdout.write(self.style.WARNING('No ministries found. Please create ministries first.'))
            return
        
        # Sample employee data
        employee_data = [
            {'first_name': 'John', 'last_name': 'Adeyemi', 'job_title': 'Senior Pastor', 'employment_type': 'full_time'},
            {'first_name': 'Grace', 'last_name': 'Okonkwo', 'job_title': 'Worship Leader', 'employment_type': 'full_time'},
            {'first_name': 'David', 'last_name': 'Mensah', 'job_title': 'Youth Pastor', 'employment_type': 'full_time'},
            {'first_name': 'Sarah', 'last_name': 'Ibrahim', 'job_title': 'Administrator', 'employment_type': 'full_time'},
            {'first_name': 'Michael', 'last_name': 'Okafor', 'job_title': 'Finance Officer', 'employment_type': 'full_time'},
            {'first_name': 'Esther', 'last_name': 'Banda', 'job_title': 'Children Ministry Coordinator', 'employment_type': 'part_time'},
            {'first_name': 'Peter', 'last_name': 'Mwangi', 'job_title': 'Facilities Manager', 'employment_type': 'full_time'},
            {'first_name': 'Ruth', 'last_name': 'Nkrumah', 'job_title': 'Outreach Coordinator', 'employment_type': 'part_time'},
            {'first_name': 'Daniel', 'last_name': 'Kamara', 'job_title': 'Media Director', 'employment_type': 'contract'},
            {'first_name': 'Mary', 'last_name': 'Afolabi', 'job_title': 'Secretary', 'employment_type': 'full_time'},
        ]
        
        employees_created = 0
        
        for i, emp_data in enumerate(employee_data):
            # Check if employee already exists
            if Employee.objects.filter(
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name']
            ).exists():
                continue
            
            # Create employee
            employee = Employee.objects.create(
                employee_id=f'EMP{str(i+1).zfill(4)}',
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                email=f"{emp_data['first_name'].lower()}.{emp_data['last_name'].lower()}@church.org",
                phone=f'+234{random.randint(7000000000, 9999999999)}',
                hire_date=date(random.randint(2015, 2023), random.randint(1, 12), 1),
                department=random.choice(departments),
                job_title=emp_data['job_title'],
                employment_type=emp_data['employment_type'],
                status='active',
                salary_grade=str(random.randint(1, 10)),
                base_salary=random.randint(150000, 500000),
                emergency_contact_name=f"{emp_data['first_name']} Family",
                emergency_contact_phone=f'+234{random.randint(7000000000, 9999999999)}'
            )
            employees_created += 1
            
            # Create leave requests for some employees
            if random.choice([True, False]):
                leave_types = ['vacation', 'sick', 'casual']
                for _ in range(random.randint(1, 3)):
                    start_date = timezone.now().date() + timedelta(days=random.randint(-60, 60))
                    LeaveRequest.objects.create(
                        employee=employee,
                        leave_type=random.choice(leave_types),
                        start_date=start_date,
                        end_date=start_date + timedelta(days=random.randint(1, 10)),
                        reason=f'Personal {random.choice(leave_types)} leave',
                        status=random.choice(['pending', 'approved', 'rejected'])
                    )
            
            # Create payroll records for the last 6 months
            for month_offset in range(6):
                target_date = timezone.now().date() - timedelta(days=30 * month_offset)
                basic_salary = random.randint(150000, 500000)
                allowances = random.randint(20000, 100000)
                deductions = random.randint(10000, 50000)
                
                PayrollRecord.objects.get_or_create(
                    employee=employee,
                    month=target_date.month,
                    year=target_date.year,
                    defaults={
                        'basic_salary': basic_salary,
                        'allowances': allowances,
                        'deductions': deductions,
                        'net_pay': basic_salary + allowances - deductions,
                        'status': 'paid' if month_offset > 0 else 'draft'
                    }
                )
            
            # Create performance reviews
            if random.choice([True, False, False]):  # 33% chance
                PerformanceReview.objects.create(
                    employee=employee,
                    review_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
                    reviewer=None,  # Can be linked to a User later
                    score=random.randint(60, 100),
                    comments=f'Performance review for {employee.get_full_name}. Shows dedication and commitment.'
                )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {employees_created} employees with related data'))
        self.stdout.write(self.style.SUCCESS(f'Total employees in system: {Employee.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total leave requests: {LeaveRequest.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total payroll records: {PayrollRecord.objects.count()}'))
