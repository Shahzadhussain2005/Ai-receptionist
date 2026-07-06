# Glow Studio AI Voice Receptionist

An AI-powered voice receptionist system for salons and med spas. Handles inbound phone calls 24/7, collects appointment bookings through natural conversation, persists data to Google Sheets, and sends automated HTML email confirmations via Gmail SMTP — all without human intervention.

## Architecture

```
Inbound Call → Vapi (Voice AI Platform)
                    ↓
              Groq API (LLaMA 3.1 8B Instant)
              [STT: Deepgram | TTS: Vapi Native]
                    ↓
              End-of-Call Webhook (POST /webhook)
                    ↓
              FastAPI Server (Python 3.11+)
               ├── Google Sheets API v4  → persists booking row
               ├── Gmail SMTP (TLS 465)  → client confirmation email
               └── Gmail SMTP (TLS 465)  → owner alert + transcript
```

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Voice AI Platform | Vapi | Inbound call handling, STT, TTS |
| LLM | Groq — LLaMA 3.1 8B Instant | Natural language understanding & response |
| Speech to Text | Deepgram (via Vapi) | Converts caller speech to text |
| Text to Speech | Vapi Native Voice | Converts Maya's replies to voice |
| Backend | FastAPI + Uvicorn | Async webhook server |
| Database | Google Sheets API v4 | Booking persistence |
| Auth | Google Service Account + oauth2client | Sheets authentication |
| Email Transport | aiosmtplib (async SMTP) | Non-blocking email dispatch |
| Email Format | MIME Multipart HTML | Rich HTML email templates |
| Hosting | Railway | Cloud deployment |

## Features

- 24/7 inbound call handling via Vapi voice AI platform
- Natural language booking flow collecting name, service, date, time, email
- Sub-second AI response latency via Groq LLaMA 3.1 8B Instant model
- Real-time Google Sheets row append per confirmed booking
- Async HTML email confirmation to client via Gmail SMTP over TLS port 465
- Async HTML email alert to salon owner including full call transcript
- Dynamic email templates with f-string interpolation of booking data
- Graceful escalation handling for medical questions and complaints
- Webhook type filtering — only processes end-of-call-report events
- Safe key extraction with default fallbacks — never crashes on missing data

## Email System — Technical Details

The email system uses **aiosmtplib** for fully asynchronous SMTP delivery, meaning emails are sent without blocking the webhook response back to Vapi.

### Transport Layer
```
Protocol  : SMTP over TLS
Host      : smtp.gmail.com
Port      : 465 (SMTPS — implicit TLS)
Auth      : Gmail App Password (not account password)
Library   : aiosmtplib (async, non-blocking)
```

### Email Format
```
MIME Type : multipart/alternative
Body      : text/html
Encoding  : UTF-8
Template  : Python f-string with dynamic booking data injection
```

### Two Emails Sent Per Booking

**1. Client Confirmation Email**
```
To      : client email collected during call
Subject : Your Appointment is Confirmed — Glow Studio ✨
Content :
  - Personalized greeting with client name
  - Full booking summary table (service, date, time, deposit)
  - Pre-appointment reminders
  - Salon address and contact info
  - Branded HTML template with inline CSS
```

**2. Owner Alert Email**
```
To      : owner Gmail (OWNER_EMAIL env var)
Subject : 🆕 New Booking — {client name} — Glow Studio
Content :
  - Full booking details table
  - Complete call transcript (white-space preserved)
  - Timestamp of booking
  - Reference to Google Sheet for history
```

### Email Authentication Flow
```
Gmail Account → Enable 2-Step Verification
             → Generate App Password (16 chars)
             → Use as SMTP password (not account password)
             → Gmail accepts connection on port 465 with TLS
```

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI server + Vapi webhook handler
│   ├── booking.py         # Google Sheets API integration
│   ├── email_sender.py    # Async client confirmation email
│   └── notify.py          # Async owner alert email with transcript
├── .env.example           # Environment variable template
├── requirements.txt       # Python dependencies
└── README.md
```

## Environment Variables

```bash
VAPI_API_KEY=              # Vapi dashboard private API key
VAPI_ASSISTANT_ID=         # Vapi assistant UUID
GROQ_API_KEY=              # Groq API key (free tier)
GOOGLE_SHEET_ID=           # Google Sheets document ID (from URL)
GOOGLE_CREDENTIALS_JSON=   # Path to service account JSON keyfile
GMAIL_SENDER=              # Gmail address used as SMTP sender
GMAIL_APP_PASSWORD=        # 16-char Gmail app-specific password
OWNER_EMAIL=               # Recipient for owner alert emails
PORT=8000                  # Uvicorn server port
```

## Local Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/glow-studio-ai-receptionist.git
cd glow-studio-ai-receptionist

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in your API keys in .env
# Place credentials.json in root folder

# Run the server
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check — server status |
| GET | `/health` | Railway health probe |
| POST | `/webhook` | Vapi end-of-call webhook receiver |

## Webhook Payload

Vapi sends a POST request to `/webhook` on call end:

```json
{
  "message": {
    "type": "end-of-call-report",
    "artifact": {
      "transcript": "full conversation transcript",
      "structuredData": {
        "name": "Sarah Johnson",
        "service": "Microblading",
        "date": "January 20",
        "time": "2:00 PM",
        "email": "sarah@gmail.com"
      }
    }
  }
}
```

Server extracts structured data → appends Google Sheets row → dispatches both emails asynchronously.

## Google Sheets Schema

| Column | Value |
|---|---|
| A | Client Name |
| B | Service |
| C | Date |
| D | Time |
| E | Email |
| F | Status (Confirmed) |
| G | Booked At (timestamp) |

## Deployment on Railway

```bash
# Railway auto-deploys from GitHub main branch
# Set all environment variables in Railway dashboard
# Start command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Point Vapi webhook URL to:
```
https://your-railway-app.railway.app/webhook
```

## Scalability — White Label Model

Designed as a multi-tenant white-label solution. Each salon client gets:
- Their own Vapi assistant with custom system prompt and voice
- Their own Google Sheet for isolated booking data
- Custom branded HTML email templates
- Dedicated webhook endpoint per deployment

Onboarding a new salon client takes under 30 minutes using the existing template.

## Dependencies

```
fastapi==0.115.0          # async web framework
uvicorn==0.30.6           # ASGI server
python-dotenv==1.0.1      # env var loader
python-multipart==0.0.12  # form data parsing
httpx==0.27.2             # async HTTP client
requests==2.32.3          # sync HTTP client
gspread==6.1.2            # Google Sheets client
oauth2client==4.1.3       # Google service account auth
aiosmtplib==3.0.1         # async SMTP email sender
email-validator==2.1.1    # email format validation
```

## License

MIT
