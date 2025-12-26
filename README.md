# 🧘‍♀️ CoreSync: Pilates Studio Booking Assistant

CoreSync is an AI-powered booking management system designed for Pilates studios. It acts as a virtual receptionist on **WhatsApp**, allowing clients to book sessions, check availability, and cancel appointments using natural language.

**Key Features:**
* **AI-Powered:** Uses DeepSeek LLM to understand English and Indonesian (Bahasa Indonesia).
* **Smart Scheduling:** Reads availability from a JSON config (hours, breaks, holidays) and the database.
* **Google Calendar Sync:** Automatically pushes confirmed bookings to the studio's calendar.
* **Conflict Prevention:** Handles double-booking and "ambiguous cancellation" scenarios safely.

---

## 🚀 How to Run

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* [Ngrok](https://ngrok.com/) (for exposing local server to WhatsApp).

### 1. Setup Environment
1.  Clone this repository.
2.  Create a `.env` file in the root folder (see "Secrets" section below).
3.  Place your Google Service Account key in `config/google_credentials.json` (see "Secrets" section below).

### 2. Start the Server
Run the following command to build and start the containers:
```bash
docker-compose up --build
````

- The app will run at `http://localhost:8000`.    
- The Django Admin is at `http://localhost:8000/admin`.    

### 3. Testing Locally (The "Brain" Simulator)
You don't need WhatsApp to test the logic. We included a CLI tool to simulate user messages directly in your terminal.

**Test Booking:**
Bash
```
docker-compose exec web python manage.py test_ai "Booking besok jam 10 pagi"
```
**Test Cancellation:**
Bash
```
docker-compose exec web python manage.py test_ai "Batalin dong"
```

---

## ⚙️ Configuration (`studio_config.json`)

All business logic is stored in `studio_config.json`. You can edit this file to change your operating hours without touching code.

**Location:** Root directory.
**How to manage:**
- **`weekly_schedule`**: Define start/end times and break times for each day.    
- **`holidays`**: Add date ranges where the studio is closed. The scheduler will automatically block these dates.    
- **`session_duration_minutes`**: Defines the length of a single booking block.    

**Example:**
JSON
```
{
  "session_duration_minutes": 45,
  "weekly_schedule": {
    "Monday": { "start": "08:00", "end": "20:00", "break": ["12:00", "13:00"] },
    ...
  },
  "holidays": [
    { "start": "2025-01-01", "end": "2025-01-04" }
  ]
}
```

---

## 🔐 Secrets & Tokens
This app requires sensitive keys to function. **Never commit these files to Git.**
### 1. The `.env` File
Create a file named `.env` in the root folder. Copy the template below and fill in your keys.
#### **Template:**
Ini, YAML
```
# --- DJANGO ---
SECRET_KEY=django-insecure-change-me-to-something-random
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# --- DATABASE ---
POSTGRES_DB=coresync_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# --- DEEPSEEK AI ---
# Get API Key: [https://platform.deepseek.com/](https://platform.deepseek.com/)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# --- WHATSAPP (META) ---
# Get these from Meta Developer Dashboard -> WhatsApp -> API Setup
WHATSAPP_TOKEN=EABWxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_ID=10xxxxxxxxxxxxx
# This is a password you invent yourself for the webhook verification
VERIFY_TOKEN=my_secret_password_123

# --- GOOGLE CALENDAR ---
# Do not change the path (it maps to the docker container)
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxxxxxx=
# Your ACTUAL email address that you shared the calendar with
CALENDAR_ID=your.email@gmail.com
```

### 2. Google Service Account (`google_credentials.json`)
You need a JSON key file to allow the bot to edit your calendar.
#### **How to Generate:**
1. Go to **[Google Cloud Console](https://console.cloud.google.com/?authuser=4)**.    
2. Create a project -> Search for **"Google Calendar API"** -> Enable it.    
3. Go to **Credentials** -> **Create Credentials** -> **Service Account**.    
4. Click on the newly created email (e.g., `bot@project.iam.gserviceaccount.com`).    
5. Go to **Keys** tab -> **Add Key** -> **Create New Key** -> **JSON**.    
6. Rename the downloaded file to `google_credentials.json` and move it to the `CoreSync/config/` folder.
#### **Crucial Step: Sharing**
1. Open the JSON file and copy the `client_email` address.    
2. Go to [Google Calendar](https://calendar.google.com/?authuser=4).    
3. Go to **Settings and sharing** for your primary calendar.    
4. Scroll to **"Share with specific people"** -> Add the client email.    
5. **Permission:** Select **"Make changes to events"**.

---

## 🌐 Going Live (Connecting WhatsApp)

To connect the real WhatsApp app to your local code:
1. Start **Ngrok**:    
    Bash    
    ```
    ngrok http 8000
   ```
    
2. Copy the HTTPS URL (e.g., `https://xyz.ngrok-free.app`).    
3. Go to **Meta Developer Dashboard** -> WhatsApp -> Configuration.    
4. **Edit Webhook:**    
    - **Callback URL:** `https://xyz.ngrok-free.app/whatsapp/webhook/`        
    - **Verify Token:** The `VERIFY_TOKEN` you set in your `.env`.        
5. Save and Verify.