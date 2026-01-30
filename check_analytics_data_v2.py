import os
import django
import json
from django.db.models import Avg, Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from operations.models import Attendance, MemberAttendance

def check():
    print("Checking Analytics Data V2 Logic...")
    today = timezone.now().date()
    year_ago = today - timedelta(days=365)
    
    # 1. Attendance Trend Logic
    attendance_records = Attendance.objects.filter(date__gte=year_ago).annotate(
        real_count=Count('details') # details is MemberAttendance
    ).values('date', 'real_count')
    
    print(f"Found {len(attendance_records)} attendance records in last year.")
    if len(attendance_records) > 0:
        print(f"Sample First Record: {attendance_records[0]}")
    
    att_map = {}
    for r in attendance_records:
        m_str = r['date'].strftime('%b %Y')
        att_map.setdefault(m_str, []).append(r['real_count'])
        
    att_labels = []
    att_data = []
    
    curr = year_ago.replace(day=1)
    end = today.replace(day=1)
    
    while curr <= end:
        m_label = curr.strftime('%b %Y')
        att_labels.append(m_label)
        counts = att_map.get(m_label, [])
        avg = sum(counts) / len(counts) if counts else 0
        att_data.append(round(avg))
        
        if curr.month == 12:
            curr = curr.replace(year=curr.year + 1, month=1)
        else:
            curr = curr.replace(month=curr.month + 1)
            
    print(f"Labels: {json.dumps(att_labels)}")
    print(f"Data: {json.dumps(att_data)}")

if __name__ == '__main__':
    check()
