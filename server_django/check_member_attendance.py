import os
import django
from django.db.models import Count

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operations.models import MemberAttendance, Attendance

print(f"Total MemberAttendance records: {MemberAttendance.objects.count()}")
print(f"Total Attendance records: {Attendance.objects.count()}")

# Check recent
from django.utils import timezone
from datetime import timedelta
year_ago = timezone.now().date() - timedelta(days=365)
recent_ma = MemberAttendance.objects.filter(attendance__date__gte=year_ago).count()
print(f"Recent MemberAttendance (last year): {recent_ma}")

# Check annotation
qs = Attendance.objects.filter(date__gte=year_ago).annotate(real_count=Count('details'))
print("Sample aggregated counts:")
for q in qs[:5]:
    print(f"{q.date}: TotalCount field={q.total_count}, RealCount(MemberAttendance)={q.real_count}")
