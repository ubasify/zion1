from django.db import models

class Parish(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    pastor_name = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Ministry(models.Model):
    WEEKDAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    STATUS_CHOICES = [
        ('up_to_date', 'Up to date'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE)
    
    # New fields for redesign
    icon_type = models.CharField(max_length=50, default='users', help_text='Lucide icon name')
    active_participation_rate = models.IntegerField(default=0, help_text='Percentage 0-100')
    reporting_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_report_date = models.DateField(null=True, blank=True)
    
    # User-requested fields
    meeting_day = models.CharField(max_length=20, choices=WEEKDAY_CHOICES, null=True, blank=True)
    team_lead = models.ForeignKey('people.Member', on_delete=models.SET_NULL, null=True, blank=True, related_name='led_ministries')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50) # Sunday Service, Weekly Service
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField()
    ministry = models.ForeignKey(Ministry, on_delete=models.SET_NULL, null=True, blank=True)
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.start_date.date()})"

class SmallGroup(models.Model):
    name = models.CharField(max_length=255)
    semester = models.CharField(max_length=50) # e.g. "Spring 2025"
    leader_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default='active') # active, archived
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=255) # e.g. "Sunday Service"
    day_of_week = models.CharField(max_length=20, choices=Ministry.WEEKDAY_CHOICES, null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
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
