from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.scheduler import get_available_slots
import datetime

class Command(BaseCommand):
    help = 'Check available slots for a specific date (YYYY-MM-DD)'

    def add_arguments(self, parser):
        parser.add_argument('date', type=str, help='Date to check (YYYY-MM-DD)')

    def handle(self, *args, **options):
        date_str = options['date']
        target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        self.stdout.write(f"Checking slots for: {target_date}")
        
        slots = get_available_slots(target_date)
        
        if not slots:
            self.stdout.write(self.style.WARNING("No slots available (Holiday or Full)."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Found {len(slots)} slots:"))
            for slot in slots:
                # Local time print
                local_slot = timezone.localtime(slot)
                self.stdout.write(f"- {local_slot.strftime('%H:%M')}")