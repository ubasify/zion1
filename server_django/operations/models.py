from django.db import models
from django.conf import settings
from ministry.models import Ministry, Parish, Event
from people.models import Member

class BankAccount(models.Model):
    name = models.CharField(max_length=255) # e.g. "GTBank Main", "Access Building Fund", "Petty Cash"
    account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=10, default='NGN')
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.account_number})"

class Budget(models.Model):
    category = models.CharField(max_length=100)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} Budget ({self.year})"

class Attendance(models.Model):
    date = models.DateField()
    service = models.ForeignKey('ministry.Service', on_delete=models.SET_NULL, null=True, blank=True)
    service_type = models.CharField(max_length=100, blank=True, null=True) # Keeping for backward compat or ad-hoc
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    total_count = models.IntegerField()
    # keeping simple breakdowns for now
    ministry = models.ForeignKey(Ministry, on_delete=models.SET_NULL, null=True, blank=True)
    parish = models.ForeignKey(Parish, on_delete=models.SET_NULL, null=True, blank=True)
    adult_count = models.IntegerField(default=0)
    children_count = models.IntegerField(default=0)
    first_timers_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate total as: Adults + Children + First Timers
        self.total_count = self.adult_count + self.children_count + self.first_timers_count
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_type} - {self.date}"

class MemberAttendance(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='details')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='Present')
    check_in_time = models.DateTimeField(auto_now_add=True)

class Finance(models.Model):
    date = models.DateField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ministry = models.ForeignKey(Ministry, on_delete=models.SET_NULL, null=True, blank=True)
    parish = models.ForeignKey(Parish, on_delete=models.SET_NULL, null=True, blank=True)
    
    # New Relation
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='inflows')
    
    created_at = models.DateTimeField(auto_now_add=True)

class Expense(models.Model):
    date = models.DateField()
    category = models.CharField(max_length=100) # Maintenance, Salaries, Utilities
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    authorized_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # New Relation
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='outflows')
    
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50) # LOGIN, UPDATE
    entity_type = models.CharField(max_length=50) # USER, MEMBER
    entity_id = models.IntegerField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class CommunityImpact(models.Model):
    name = models.CharField(max_length=255) # e.g. "Mobile Food Pantry"
    description = models.TextField()
    date = models.DateField()
    people_impacted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    publication_date = models.DateField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
