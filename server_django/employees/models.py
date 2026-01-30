from django.db import models
from django.conf import settings

class Employee(models.Model):
    EMPLOYMENT_TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('volunteer', 'Volunteer'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employee_profile'
    )
    member = models.OneToOneField(
        'people.Member', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employee_record'
    )
    
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100) # Denormalized for non-member staff
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    department = models.ForeignKey(
        'ministry.Ministry', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employees'
    )
    job_title = models.CharField(max_length=100)
    hire_date = models.DateField()
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    salary_grade = models.CharField(max_length=50, blank=True, null=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class LeaveRequest(models.Model):
    LEAVE_TYPES = (
        ('vacation', 'Vacation/Annual Leave'),
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('study', 'Study Leave'),
        ('unpaid', 'Unpaid Leave'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_leaves'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.start_date})"

class PayrollRecord(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_history')
    month = models.IntegerField()
    year = models.IntegerField()
    
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"

class EmployeeDocument(models.Model):
    DOC_TYPES = (
        ('contract', 'Employment Contract'),
        ('id', 'Identification (Passport/NIN)'),
        ('cert', 'Certification/Degree'),
        ('other', 'Other'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='employee_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.title}"

class PerformanceReview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    review_date = models.DateField()
    score = models.IntegerField(help_text="Score from 1 to 5")
    comments = models.TextField()
    goals_met = models.TextField(blank=True, null=True)
    areas_for_improvement = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.review_date} ({self.score}/5)"
