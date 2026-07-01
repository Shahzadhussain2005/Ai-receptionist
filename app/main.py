from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import hmac
import hashlib
import os
from dotenv import load_dotenv
from app.booking import save_booking
from app.email_sender import send_client_email
from app.notify import send_owner_email

load_dotenv()

app = FastAPI()

VAPI_SECRET = os.getenv("VAPI_WEBHOOK_SECRET", "")

def extract_booking_data(payload: dict) -> dict | None:
    structured = payload.get("message", {}).get("artifact", {}).get("structuredData", {})
    
    if not structured:
        transcript = payload.get("message", {}).get("artifact", {}).get("transcript", "")
        return {
            "name": structured.get("name", "Unknown"),
            "service": structured.get("service", "Unknown"),
            "date": structured.get("date", "Unknown"),
            "time": structured.get("time", "Unknown"),
            "email": structured.get("email", ""),
            "transcript": transcript
        }

    return {
        "name": structured.get("name", "Unknown"),
        "service": structured.get("service", "Unknown"),
        "date": structured.get("date", "Unknown"),
        "time": structured.get("time", "Unknown"),
        "email": structured.get("email", ""),
        "transcript": payload.get("message", {}).get("artifact", {}).get("transcript", "")
    }

@app.get("/")
async def root():
    return {"status": "Glow Studio AI Receptionist is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/webhook")
async def vapi_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    message_type = payload.get("message", {}).get("type", "")

    if message_type != "end-of-call-report":
        return JSONResponse(content={"status": "ignored", "type": message_type})

    booking_data = extract_booking_data(payload)

    if not booking_data:
        return JSONResponse(content={"status": "no booking data found"})

    sheet_success = await save_booking(booking_data)

    if booking_data.get("email"):
        await send_client_email(booking_data)
        await send_owner_email(booking_data)

    return JSONResponse(content={
        "status": "success",
        "booking": booking_data,
        "saved_to_sheet": sheet_success
    })