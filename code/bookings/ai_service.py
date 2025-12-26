import os
import json
from datetime import datetime
from django.utils import timezone
from openai import OpenAI

# Initialize the client using DeepSeek's base URL
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def analyze_message(user_phone, user_message):
    """
    Sends the user message to DeepSeek and returns a structured Python dict.
    """
    
    # We must provide the current time so the AI understands "tomorrow" or "besok"
    now_local = timezone.localtime(timezone.now())
    current_context = f"Today is {now_local.strftime('%A, %Y-%m-%d')}. Current time is {now_local.strftime('%H:%M')}."

    system_prompt = f"""
    You are the AI brain of a Pilates Studio booking system.
    {current_context}
    
    You understand English and Indonesian (Bahasa Indonesia).
    Your job is to extract the user's INTENT, DATE, and TIME from their message.
    
    RULES:
    1. INTENT must be one of: ['check_availability', 'book', 'cancel', 'unknown'].
    2. DATE must be in format 'YYYY-MM-DD'. 
       - Calculate relative dates (e.g., "besok", "lusa", "Selasa depan") based on "Today".
       - If user asks for availability without a date (e.g., "Ada slot kosong?"), assume they mean "Today" or the nearest relevant date.
    3. TIME must be in format 'HH:MM' (24-hour).
    4. CANCELLATION LOGIC:
       - If user says "Cancel" or "Batalin" without a date, set DATE/TIME to null.
    
    EXAMPLES (Indonesian Context):
    
    User: "Besok ada slot kosong gak?" (Is there a slot tomorrow?)
    Output: {{"intent": "check_availability", "date": "2025-xx-xx", "time": null}}

    User: "Cek jadwal hari Kamis dong" (Check Thursday schedule)
    Output: {{"intent": "check_availability", "date": "2025-xx-xx", "time": null}}

    User: "Saya mau latihan besok jam 2 siang"
    Output: {{"intent": "book", "date": "2025-xx-xx", "time": "14:00"}}
    
    User: "Mba, tolong batalin ya"
    Output: {{"intent": "cancel", "date": null, "time": null}}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            stream=False,
            temperature=0.0
        )

        raw_content = response.choices[0].message.content
        clean_content = raw_content.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_content)

    except Exception as e:
        print(f"AI Error: {e}")
        return {"intent": "unknown", "error": str(e)}