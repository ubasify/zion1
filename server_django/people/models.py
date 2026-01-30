from django.db import models
from ministry.models import Ministry, Parish

class Member(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    TYPE_CHOICES = (
        ('Member', 'Member'),
        ('Guest', 'Guest'),
        ('Worker', 'Worker'),
        ('New Convert', 'New Convert'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married')], blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    salvation_date = models.DateField(blank=True, null=True)
    baptism_date = models.DateField(blank=True, null=True)
    
    membership_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    member_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Member')
    ministry = models.ForeignKey(Ministry, on_delete=models.SET_NULL, null=True, blank=True)
    parish = models.ForeignKey(Parish, on_delete=models.SET_NULL, null=True, blank=True)
    
    family = models.ForeignKey('Family', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    family_role = models.CharField(max_length=20, choices=[('Head', 'Head'), ('Spouse', 'Spouse'), ('Child', 'Child'), ('Relative', 'Relative')], blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Family(models.Model):
    name = models.CharField(max_length=255) # e.g. "The Adeleke Family"
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Volunteer(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='Worker')
    joined_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.member} - {self.ministry}"
