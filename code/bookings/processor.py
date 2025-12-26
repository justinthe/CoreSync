from datetime import datetime, timedelta
from django.utils import timezone
from .models import Booking, Customer
from .scheduler import get_available_slots, load_config
from .google_service import create_calendar_event, cancel_calendar_event

def process_intent(user_phone, ai_data):
    intent = ai_data.get('intent')
    date_str = ai_data.get('date')
    time_str = ai_data.get('time')

    customer = Customer.objects.get(phone_number=user_phone)

    # 1. CHECK AVAILABILITY
    if intent == 'check_availability':
        if not date_str:
            return "Untuk tanggal berapa ya kak?"
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = get_available_slots(target_date)
        
        if not slots:
            return f"Maaf kak, tanggal {date_str} penuh atau kami libur."
        
        slot_strings = [timezone.localtime(s).strftime('%H:%M') for s in slots]
        return f"Slot kosong untuk {date_str}:\n" + ", ".join(slot_strings)

    # 2. BOOKING
    elif intent == 'book':
        if not date_str or not time_str:
            return "Boleh diinfo tanggal dan jamnya kak?"
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        target_time = datetime.strptime(time_str, '%H:%M').time()
        start_dt = timezone.make_aware(datetime.combine(target_date, target_time))
        
        # Validation
        available_slots = get_available_slots(target_date)
        if start_dt not in available_slots:
            return f"Waduh, jam {time_str} di tanggal {date_str} tidak tersedia."

        # Config & Save
        config = load_config()
        duration = config.get('session_duration_minutes', 45)
        end_dt = start_dt + timedelta(minutes=duration) 
        
        new_booking = Booking.objects.create(
            customer=customer,
            start_time=start_dt,
            end_time=end_dt,
            status='CONFIRMED'
        )

        # Google Sync
        g_event_id = create_calendar_event(new_booking)
        if g_event_id:
            new_booking.google_event_id = g_event_id
            new_booking.save()
        
        return f"Siap! Booking terkonfirmasi untuk {date_str} jam {time_str}. Sudah masuk kalender kami!"

    # 3. CANCELLATION (UPDATED LOGIC)
    elif intent == 'cancel':
        # Get ALL active bookings for this user
        active_bookings = Booking.objects.filter(
            customer=customer,
            status='CONFIRMED',
            start_time__gte=timezone.now()
        ).order_by('start_time')

        count = active_bookings.count()

        # Scenario A: No bookings at all
        if count == 0:
            return "Kakak belum ada booking aktif yang bisa dibatalkan."

        booking_to_cancel = None

        # Scenario B: User Provided a Specific Date
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            # Filter matches on that day
            matches = [b for b in active_bookings if b.start_time.date() == target_date]
            
            if not matches:
                return f"Kakak tidak punya booking di tanggal {date_str}."
            
            if len(matches) > 1 and not time_str:
                return f"Ada {len(matches)} sesi di tanggal {date_str}. Tolong sebutkan jamnya ya?"
            
            # If we narrowed it down to 1, pick it
            booking_to_cancel = matches[0]

        # Scenario C: User did NOT provide a date
        else:
            if count == 1:
                # If they only have one, safe to auto-cancel
                booking_to_cancel = active_bookings.first()
            else:
                # NEW REQUIREMENT: Multiple bookings exist, ambiguity!
                msg = "Kakak punya beberapa booking aktif. Mohon sebutkan tanggal/jam yang mau dibatalkan:\n"
                for b in active_bookings:
                    local_dt = timezone.localtime(b.start_time)
                    msg += f"- {local_dt.strftime('%d %b %Y jam %H:%M')}\n"
                return msg

        # Perform the Cancellation if a target was identified
        if booking_to_cancel:
            if booking_to_cancel.google_event_id:
                cancel_calendar_event(booking_to_cancel.google_event_id)

            booking_to_cancel.status = 'CANCELLED'
            booking_to_cancel.save()
            
            local_time = timezone.localtime(booking_to_cancel.start_time)
            return f"Baik kak, booking untuk {local_time.strftime('%Y-%m-%d %H:%M')} sudah dibatalkan."
        
        return "Maaf, saya bingung booking mana yang dimaksud."

    else:
        return "Maaf saya kurang paham. Bisa diulang?"