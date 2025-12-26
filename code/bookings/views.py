import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MessageLog, Customer
from .ai_service import analyze_message
from .processor import process_intent
from .whatsapp_utils import send_whatsapp_message

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        print("\n--- INCOMING TWILIO DATA ---")
        
        # 1. Try to read standard Form Data (Default Twilio)
        data = request.POST.dict()
        
        # 2. If empty, try to read JSON (Edge case config)
        if not data:
            try:
                data = json.loads(request.body.decode('utf-8'))
                print("DEBUG: Received JSON Data")
            except json.JSONDecodeError:
                pass

        print(f"DEBUG DATA: {data}")
        print("----------------------------\n")

        # 3. Extract Fields safely
        raw_sender = data.get('From', '')
        message_body = data.get('Body', '').strip()
        sender_phone = raw_sender.replace('whatsapp:', '')

        # 4. Handle "Empty" messages (e.g., Status updates or Media w/o caption)
        if not message_body:
            print("WARNING: Empty message body received (Sticker? Image? Status update?)")
            # We return 200 OK to tell Twilio "We got it, stop retrying" even if we ignore it
            return HttpResponse("OK", status=200)

        # --- CORE LOGIC STARTS ---
        
        # A. Save Log
        MessageLog.objects.create(
            sender=sender_phone,
            message_body=message_body,
            direction='INCOMING'
        )

        # B. Ensure Customer
        Customer.objects.get_or_create(phone_number=sender_phone)

        # C. AI Processing
        ai_result = analyze_message(sender_phone, message_body)
        
        # D. Business Logic
        reply_text = process_intent(sender_phone, ai_result)
        
        # E. Reply
        send_whatsapp_message(sender_phone, reply_text)
        
        # F. Log Reply
        MessageLog.objects.create(
            sender=sender_phone,
            message_body=reply_text,
            direction='OUTGOING'
        )

        return HttpResponse("OK", status=200)

    return HttpResponse("Only POST allowed", status=405)