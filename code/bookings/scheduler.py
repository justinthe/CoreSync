import json
import os
from datetime import datetime, timedelta, time
from django.conf import settings
from django.utils import timezone
from .models import Booking

# Path to the config file
CONFIG_PATH = os.path.join(settings.BASE_DIR, 'studio_config.json')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def is_holiday(date_obj, config):
    """Check if the given date falls within any holiday range."""
    for holiday in config.get('holidays', []):
        h_start = datetime.strptime(holiday['start'], '%Y-%m-%d').date()
        h_end = datetime.strptime(holiday['end'], '%Y-%m-%d').date()
        if h_start <= date_obj <= h_end:
            return True
    return False

def get_available_slots(target_date):
    """
    Returns a list of available start times (datetime objects) for a specific date.
    """
    config = load_config()
    
    # 1. Check for Holidays
    if is_holiday(target_date, config):
        return [] # Closed on holidays

    # 2. Get Schedule for the Day (e.g., "Monday")
    day_name = target_date.strftime('%A')
    day_schedule = config['weekly_schedule'].get(day_name)

    if not day_schedule:
        return [] # Closed this day

    # Parse config strings into time objects
    fmt = '%H:%M'
    start_time = datetime.strptime(day_schedule['start'], fmt).time()
    end_time = datetime.strptime(day_schedule['end'], fmt).time()
    
    break_start = None
    break_end = None
    if day_schedule.get('break'):
        break_start = datetime.strptime(day_schedule['break'][0], fmt).time()
        break_end = datetime.strptime(day_schedule['break'][1], fmt).time()

    session_duration = config['session_duration_minutes']
    
    # 3. Generate all theoretical slots
    available_slots = []
    current_dt = datetime.combine(target_date, start_time)
    end_dt = datetime.combine(target_date, end_time)

    # We need timezone aware objects for DB comparison
    current_dt = timezone.make_aware(current_dt)
    end_dt = timezone.make_aware(end_dt)

    while current_dt + timedelta(minutes=session_duration) <= end_dt:
        slot_end = current_dt + timedelta(minutes=session_duration)
        current_time = current_dt.time()

        # Check Break Collision
        in_break = False
        if break_start and break_end:
            # Simple overlap check: if slot starts before break ends AND slot ends after break starts
            if current_time < break_end and slot_end.time() > break_start:
                in_break = True
        
        if not in_break:
            available_slots.append(current_dt)

        # Move to next slot
        current_dt += timedelta(minutes=session_duration)

    # 4. Filter out slots already booked in Database
    # Find bookings for this day that are CONFIRMED
    existing_bookings = Booking.objects.filter(
        start_time__date=target_date,
        status='CONFIRMED'
    )

    final_slots = []
    for slot in available_slots:
        is_taken = False
        for booking in existing_bookings:
            # Check for exact match or overlap
            if booking.start_time == slot:
                is_taken = True
                break
        
        if not is_taken:
            final_slots.append(slot)

    return final_slots