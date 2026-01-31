from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Role choices mapped to IDs for backward compatibility logic
    # Role ID 1 = Super Admin, 2 = Ministry Lead, 3 = Data Analyst, 4 = User
    ROLE_CHOICES = (
        (1, 'Super Admin'),
        (2, 'Ministry Lead'),
        (3, 'Data Analyst'),
        (4, 'User'),
    )

    REGISTRATION_TYPE_CHOICES = (
        ('first_timer', 'First Timer'),
        ('worker', 'Worker'),
        ('member', 'Member'),
    )

    role_id = models.IntegerField(choices=ROLE_CHOICES, default=4)
    registration_type = models.CharField(
        max_length=20, 
        choices=REGISTRATION_TYPE_CHOICES, 
        default='member'
    )
    ministry = models.ForeignKey('ministry.Ministry', on_delete=models.SET_NULL, null=True, blank=True)
    parish = models.ForeignKey('ministry.Parish', on_delete=models.SET_NULL, null=True, blank=True)
    member = models.OneToOneField('people.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_account')
    
    # Resolving backwards compatibility with old SQLite schema
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role_id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
