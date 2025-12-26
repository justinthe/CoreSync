from django.core.management.base import BaseCommand
from bookings.ai_service import analyze_message
from bookings.processor import process_intent
from bookings.models import Customer
import json

class Command(BaseCommand):
    help = 'Test the full flow: AI -> Processor -> DB'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='The simulated user message')

    def handle(self, *args, **options):
        message = options['message']
        # Use a dummy phone number for testing
        test_phone = "+628123456789"

        # 1. SETUP: Ensure a test customer exists (Processor needs this)
        customer, created = Customer.objects.get_or_create(
            phone_number=test_phone,
            defaults={'first_name': 'Test', 'last_name': 'User'}
        )

        self.stdout.write(f"--- Incoming Message from {test_phone} ---")
        self.stdout.write(f"'{message}'")
        self.stdout.write("-" * 30)

        # 2. STAGE 4: The AI Brain (Extract Intent)
        ai_result = analyze_message(test_phone, message)
        
        self.stdout.write(self.style.WARNING("DEBUG - AI JSON:"))
        self.stdout.write(json.dumps(ai_result, indent=2))
        self.stdout.write("-" * 30)

        # 3. STAGE 5: The Processor (Check Rules & Save to DB)
        reply_text = process_intent(test_phone, ai_result)

        # 4. RESULT: The Bot's Reply
        self.stdout.write(self.style.SUCCESS("--- BOT REPLY ---"))
        self.stdout.write(reply_text)