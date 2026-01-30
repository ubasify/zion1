"""
Script to recalculate total_count for all existing Attendance records.
Run this after updating the Attendance model to use the new calculation formula:
Total = Adults + Children + First Timers

Usage:
    python manage.py shell < fix_attendance_totals.py
"""

from operations.models import Attendance

# Get all attendance records
attendance_records = Attendance.objects.all()
count = attendance_records.count()

print(f"Found {count} attendance records to update...")

# Update each record (the save() method will auto-calculate total_count)
updated = 0
for record in attendance_records:
    old_total = record.total_count
    # Just call save() - the model's save() method will recalculate total_count
    record.save()
    new_total = record.total_count
    
    if old_total != new_total:
        updated += 1
        print(f"Updated {record.date} {record.service_type}: {old_total} -> {new_total}")

print(f"\nCompleted! Updated {updated} out of {count} records.")
