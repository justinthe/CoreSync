import json
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MessageLog, Customer
from .ai_service import analyze_message
from .processor import process_intent
from .whatsapp_utils import send_whatsapp_message

@csrf_exempt
def whatsapp_webhook(request):
    # 1. VERIFICATION (GET) - Used by Meta to check if URL is valid
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == os.environ.get('VERIFY_TOKEN'):
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('Error, wrong token', status=403)

    # 2. RECEIVE MESSAGE (POST)
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Check if this is a message (not a status update)
        try:
            entry = data['entry'][0]['changes'][0]['value']
            if 'messages' in entry:
                message = entry['messages'][0]
                sender_phone = message['from']
                text_body = message['text']['body']
                
                # A. Save Raw Log
                MessageLog.objects.create(
                    sender=sender_phone,
                    message_body=text_body,
                    direction='INCOMING'
                )

                # B. Ensure Customer Exists
                Customer.objects.get_or_create(phone_number=sender_phone)

                # C. Ask the Brain (Stage 4)
                ai_result = analyze_message(sender_phone, text_body)
                
                # D. Process Logic (Stage 5 processor)
                reply_text = process_intent(sender_phone, ai_result)
                
                # E. Reply (WhatsApp)
                send_whatsapp_message(sender_phone, reply_text)
                
                # F. Log the Reply
                MessageLog.objects.create(
                    sender=sender_phone,
                    message_body=reply_text,
                    direction='OUTGOING'
                )

        except (KeyError, IndexError):
            pass # Ignore status updates like "read" or "delivered"

        return HttpResponse('EVENT_RECEIVED', status=200)