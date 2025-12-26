import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service_account.json'

def get_calendar_service():

    # --- DEBUG PRINTS ---
    target_calendar = os.environ.get('CALENDAR_ID')
    print(f"DEBUG: .env variable CALENDAR_ID is: '{target_calendar}'")
    
    if not target_calendar:
        print("WARNING: No CALENDAR_ID found. Defaulting to 'primary' (The Bot's Calendar).")
        calendar_id = 'primary'
    else:
        calendar_id = target_calendar
    # --------------------
    
    """
    Takes an Order object and adds it to Google Calendar.
    """
    # 1. Authenticate
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Error: service_account.json not found.")
        return False

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
        
    return build('calendar', 'v3', credentials=creds)

def create_calendar_event(booking):
    """
    Creates an event in Google Calendar.
    Returns the Google Event ID.
    """
    try:
        service = get_calendar_service()
        calendar_id = os.environ.get("CALENDAR_ID", "primary")

        # Define the event body
        event_body = {
            'summary': f"Pilates: {booking.customer.first_name or 'Client'} {booking.customer.phone_number}",
            'description': f"Booking via CoreSync.\nPhone: {booking.customer.phone_number}",
            'start': {
                'dateTime': booking.start_time.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'end': {
                'dateTime': booking.end_time.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
        }

        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        return event.get('id')
    
    except Exception as e:
        print(f"GOOGLE CALENDAR ERROR (Create): {e}")
        return None

def cancel_calendar_event(google_event_id):
    """
    Deletes an event from Google Calendar.
    """
    if not google_event_id:
        return

    try:
        service = get_calendar_service()
        calendar_id = os.environ.get("CALENDAR_ID", "primary")

        service.events().delete(calendarId=calendar_id, eventId=google_event_id).execute()
        print(f"Successfully deleted event {google_event_id}")
        
    except Exception as e:
        print(f"GOOGLE CALENDAR ERROR (Delete): {e}")