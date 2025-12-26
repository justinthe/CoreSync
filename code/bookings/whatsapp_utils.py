import os
from twilio.rest import Client

def send_whatsapp_message(to_phone_number, message_text):
    """
    Sends a WhatsApp message using Twilio.
    Ensures both 'from' and 'to' numbers have the 'whatsapp:' prefix.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    # Get the raw number from .env
    raw_from = os.environ.get("TWILIO_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    # FORCE 'whatsapp:' prefix on the SENDER
    if not raw_from.startswith("whatsapp:"):
        from_number = f"whatsapp:{raw_from}"
    else:
        from_number = raw_from

    # FORCE 'whatsapp:' prefix on the RECEIVER
    if not to_phone_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_phone_number}"
    else:
        to_number = to_phone_number

    print(f"DEBUG: Attempting to send from '{from_number}' to '{to_number}'")

    try:
        message = client.messages.create(
            from_=from_number,
            body=message_text,
            to=to_number
        )
        print(f"Twilio Message Sent: {message.sid}")
    except Exception as e:
        print(f"Error sending Twilio message: {e}")