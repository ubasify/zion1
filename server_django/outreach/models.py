from django.db import models
from django.conf import settings
from django.utils import timezone
from people.models import Member

class Visitor(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('pending', 'In Progress'),
        ('converted', 'Converted to Member'),
        ('lost', 'Lost Contact'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married')], blank=True, null=True)
    
    visit_date = models.DateField(default=timezone.now)
    how_did_you_hear = models.CharField(max_length=255, blank=True, null=True)
    invited_by = models.CharField(max_length=255, blank=True, null=True)
    prayer_request = models.TextField(blank=True, null=True)
    interest_in_membership = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    converted_member = models.OneToOneField(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitor_record')
    
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def formatted_visit_date(self):
        return self.visit_date.strftime("%b %d, %Y")

    @property
    def safe_email(self):
        return self.email if self.email else "-"

    @property
    def safe_whatsapp(self):
        return self.whatsapp_number if self.whatsapp_number else "-"

    @property
    def safe_phone(self):
        return self.phone if self.phone else "-"

    @property
    def safe_source(self):
        return self.how_did_you_hear if self.how_did_you_hear else "-"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class FollowUpLog(models.Model):
    TYPE_CHOICES = (
        ('call', 'Phone Call'),
        ('text', 'WhatsApp/SMS'),
        ('email', 'Email'),
        ('visit', 'Home Visit'),
        ('other', 'Other'),
    )

    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='follow_ups')
    date = models.DateField(auto_now_add=True)
    follow_up_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    notes = models.TextField()
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Follow-up for {self.visitor} on {self.date}"
