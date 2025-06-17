from django.core.management.base import BaseCommand
from django.utils import timezone
from employee.models import Attendance
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check today\'s attendance records'

    def handle(self, *args, **options):
        try:
            # Get current time in different timezones
            utc_now = timezone.now()
            kolkata_tz = pytz.timezone('Asia/Kolkata')
            kolkata_now = utc_now.astimezone(kolkata_tz)
            
            self.stdout.write("\nTime Information:")
            self.stdout.write("-" * 80)
            self.stdout.write(f"UTC Time: {utc_now}")
            self.stdout.write(f"Kolkata Time: {kolkata_now}")
            self.stdout.write(f"System Timezone: {timezone.get_current_timezone()}")
            self.stdout.write(f"USE_TZ setting: {timezone.is_aware(utc_now)}")
            
            # Get all attendance records for today
            today = timezone.now().date()
            today_records = Attendance.objects.filter(date=today)
            
            self.stdout.write(f"\nToday's date: {today}")
            self.stdout.write(f"Total records for today: {today_records.count()}")
            
            if today_records.exists():
                self.stdout.write("\nAttendance Records:")
                self.stdout.write("-" * 100)
                self.stdout.write(f"{'Employee ID':<15} {'Clock In (UTC)':<25} {'Clock In (Kolkata)':<25} {'Status':<10}")
                self.stdout.write("-" * 100)
                
                for record in today_records:
                    clock_in_utc = record.time_in
                    clock_in_kolkata = clock_in_utc.astimezone(kolkata_tz)
                    self.stdout.write(
                        f"{record.eId:<15} "
                        f"{clock_in_utc.strftime('%Y-%m-%d %H:%M:%S'):<25} "
                        f"{clock_in_kolkata.strftime('%Y-%m-%d %H:%M:%S'):<25} "
                        f"{record.status:<10}"
                    )
            else:
                self.stdout.write(self.style.WARNING("\nNo attendance records found for today."))
                
            # Check if there are any attendance records at all
            all_records = Attendance.objects.all().order_by('-date')[:5]
            if all_records.exists():
                self.stdout.write("\nLast 5 Attendance Records (Any Date):")
                self.stdout.write("-" * 100)
                self.stdout.write(f"{'Employee ID':<15} {'Date':<12} {'Clock In (UTC)':<25} {'Clock In (Kolkata)':<25} {'Status':<10}")
                self.stdout.write("-" * 100)
                
                for record in all_records:
                    clock_in_utc = record.time_in
                    clock_in_kolkata = clock_in_utc.astimezone(kolkata_tz)
                    self.stdout.write(
                        f"{record.eId:<15} "
                        f"{record.date.strftime('%Y-%m-%d'):<12} "
                        f"{clock_in_utc.strftime('%Y-%m-%d %H:%M:%S'):<25} "
                        f"{clock_in_kolkata.strftime('%Y-%m-%d %H:%M:%S'):<25} "
                        f"{record.status:<10}"
                    )
            else:
                self.stdout.write(self.style.WARNING("\nNo attendance records found in the system."))
                
        except Exception as e:
            logger.error(f"Check attendance error: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error checking attendance: {str(e)}')
            ) 