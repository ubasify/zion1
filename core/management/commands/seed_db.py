import random
from datetime import timedelta, date, timezone
from django.core.management.base import BaseCommand
from django.utils import timezone as django_timezone
from faker import Faker
from core.models import User
from ministry.models import Parish, Ministry, Event
from people.models import Member, Volunteer
from operations.models import Attendance, MemberAttendance, Finance, AuditLog, Notification

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds database with large scale data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database...')
        
        # 1. Clear Data
        self.stdout.write('Cleaning old data...')
        # Dependents first
        Notification.objects.all().delete()
        AuditLog.objects.all().delete()
        Finance.objects.all().delete()
        MemberAttendance.objects.all().delete()
        Attendance.objects.all().delete()
        Volunteer.objects.all().delete()
        Member.objects.all().delete()
        Event.objects.all().delete()
        User.objects.all().delete()
        Ministry.objects.all().delete()
        Parish.objects.all().delete()

        # 2. Parishes (10)
        parishes = []
        for _ in range(10):
            parishes.append(Parish(
                name=f"{fake.city()} Parish",
                address=fake.address(),
                pastor_name=fake.name(),
                contact_email=fake.email()
            ))
        Parish.objects.bulk_create(parishes)
        all_parishes = list(Parish.objects.all())

        # 3. Ministries (8)
        ministry_names = ['Choir', 'Ushering', 'Prayer', 'Evangelism', 'Children', 'Youth', 'Media', 'Welfare']
        ministries = []
        for name in ministry_names:
            ministries.append(Ministry(
                name=name,
                description=fake.sentence(),
                parish=random.choice(all_parishes)
            ))
        Ministry.objects.bulk_create(ministries)
        all_ministries = list(Ministry.objects.all())

        # 4. Users (20)
        # Admin
        User.objects.create_superuser('admin', 'admin@zynchurch.com', 'password123', role_id=1)
        users = []
        for i in range(19):
            users.append(User(
                username=f"{fake.user_name()}{i}",
                email=fake.email(),
                role_id=random.randint(2, 4),
                ministry=random.choice(all_ministries),
                parish=random.choice(all_parishes)
            ))
        # User create_user logic handles hashing, so bulk_create is tricky for passwords unless we hash manually or loop.
        # For speed in dev, we'll loop.
        for u in users:
            u.set_password('password123')
            u.save()
        all_users = list(User.objects.all())

        # 5. Members (5000)
        self.stdout.write('Seeding 5000 members...')
        members = []
        for _ in range(5000):
            members.append(Member(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number()[:20],
                address=fake.address(),
                dob=fake.date_of_birth(minimum_age=10, maximum_age=90),
                membership_date=fake.date_between(start_date='-5y', end_date='today'),
                status='active',
                member_type='Member',
                ministry=random.choice(all_ministries),
                parish=random.choice(all_parishes)
            ))
        Member.objects.bulk_create(members, batch_size=1000)
        all_members = list(Member.objects.all()) # Need IDs

        # 6. Events (100)
        events = []
        for _ in range(100):
            events.append(Event(
                name='Sunday Service' if random.random() < 0.6 else fake.catch_phrase(),
                type='Sunday Service' if random.random() < 0.6 else 'Weekly Service',
                description=fake.sentence(),
                start_date=fake.date_time_between(start_date='-5y', end_date='now', tzinfo=timezone.utc),
                ministry=random.choice(all_ministries),
                parish=random.choice(all_parishes)
            ))
        Event.objects.bulk_create(events)
        all_events = list(Event.objects.all())

        # 7. Attendance (5000 summaries)
        self.stdout.write('Seeding Attendance...')
        attendances = []
        for _ in range(5000):
            attendances.append(Attendance(
                date=fake.date_between(start_date='-5y', end_date='today'),
                service_type='Sunday Service',
                event=random.choice(all_events),
                total_count=random.randint(50, 500),
                ministry=random.choice(all_ministries),
                parish=random.choice(all_parishes)
            ))
        Attendance.objects.bulk_create(attendances, batch_size=1000)
        
        # 8. Audit Logs (150k)
        self.stdout.write('Seeding 150k Logs (this may take a moment)...')
        logs = []
        for _ in range(150000):
            logs.append(AuditLog(
                user=random.choice(all_users),
                action=random.choice(['LOGIN', 'UPDATE', 'CREATE', 'DELETE']),
                entity_type=random.choice(['MEMBER', 'USER', 'EVENT']),
                entity_id=random.randint(1, 1000),
                details=fake.sentence()
            ))
        AuditLog.objects.bulk_create(logs, batch_size=5000)

        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))
