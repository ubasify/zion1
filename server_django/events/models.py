from django.db import models
from django.conf import settings
from ministry.models import Ministry

class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='blue', help_text='Tailwind color name e.g. blue, red, green')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Event Categories"

    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    location = models.CharField(max_length=255, blank=True, null=True)
    is_virtual = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True, null=True)
    
    organizer = models.ForeignKey(Ministry, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_events')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    banner = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class EventRSVP(models.Model):
    STATUS_CHOICES = [
        ('going', 'Going'),
        ('maybe', 'Maybe'),
        ('not_going', 'Not Going'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    member = models.ForeignKey('people.Member', on_delete=models.CASCADE, related_name='event_rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='going')
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'member']

    def __str__(self):
        return f"{self.member} - {self.event} ({self.status})"
