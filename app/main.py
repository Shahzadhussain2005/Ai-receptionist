from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import json
import requests
from dotenv import load_dotenv
from app.booking import save_booking
from app.email_sender import send_client_email
from app.notify import send_owner_email

load_dotenv()

app = FastAPI()
VAPI_API_KEY = os.getenv("VAPI_API_KEY")

def get_structured_data_from_vapi(call_id: str) -> dict:
    url = f"https://api.vapi.ai/call/{call_id}"
    headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch call: {response.status_code}")
        return {}
    
    call_data = response.json()
    print("=== VAPI CALL DATA ===")
    print(json.dumps(call_data.get("analysis", {}), indent=2))
    
    structured = call_data.get("analysis", {}).get("structuredData", {})
    
    for key, value in structured.items():
        if isinstance(value, dict) and "result" in value:
            return value["result"]
    
    return {}

def extract_booking_data(payload: dict) -> dict:
    message = payload.get("message", {})
    artifact = message.get("artifact", {})
    transcript = artifact.get("transcript", "")
    call_id = message.get("call", {}).get("id", "")

    print(f"Call ID: {call_id}")

    booking = get_structured_data_from_vapi(call_id) if call_id else {}

    print(f"=== BOOKING FROM VAPI API ===")
    print(json.dumps(booking, indent=2))

    return {
        "name": booking.get("name", "Unknown"),
        "service": booking.get("service", "Unknown"),
        "date": booking.get("date", "Unknown"),
        "time": booking.get("time", "Unknown"),
        "email": booking.get("email", ""),
        "transcript": transcript
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
    print(f"Webhook received — type: {message_type}")

    if message_type != "end-of-call-report":
        return JSONResponse(content={"status": "ignored", "type": message_type})

    booking_data = extract_booking_data(payload)
    print(f"Final booking: {booking_data}")

    sheet_success = await save_booking(booking_data)

    if booking_data.get("email"):
        await send_client_email(booking_data)
        await send_owner_email(booking_data)

    return JSONResponse(content={
        "status": "success",
        "booking": booking_data,
        "saved_to_sheet": sheet_success
    })