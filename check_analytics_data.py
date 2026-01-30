import os
import django
import json
from django.db.models import Avg, Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from people.models import Member
from operations.models import Attendance, Finance, Expense

def check():
    print("Checking Analytics Data Logic...")
    today = timezone.now().date()
    year_ago = today - timedelta(days=365)
    
    # 1. Attendance
    attendance_qs = Attendance.objects.filter(date__gte=year_ago).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        avg_count=Avg('total_count')
    ).order_by('month')
    
    att_data = []
    for entry in attendance_qs:
        att_data.append(round(entry['avg_count']))
        
    print(f"Attendance Data Points: {len(att_data)}")
    print(f"Attendance Data: {att_data}")
    
    # 2. Gender
    gender_data = list(Member.objects.values('gender').annotate(count=Count('id')))
    print(f"\nGender Raw Data: {gender_data}")
    
    g_labels = [x['gender'] or 'Unknown' for x in gender_data]
    g_series = [x['count'] for x in gender_data]
    print(f"Gender Labels: {json.dumps(g_labels)}")
    print(f"Gender Series: {json.dumps(g_series)}")

    # 3. Finance
    six_months_ago = today - timedelta(days=180)
    income_qs = Finance.objects.filter(date__gte=six_months_ago).count()
    print(f"\nFinance Records (last 6 months): {income_qs}")

if __name__ == '__main__':
    check()
