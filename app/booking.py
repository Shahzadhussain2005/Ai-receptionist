import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

HEADERS = ["Name", "Service", "Date", "Time", "Email", "Status", "Booked At"]

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.getenv("GOOGLE_CREDENTIALS_JSON"), SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1
    return sheet

def ensure_headers(sheet):
    first_row = sheet.row_values(1)
    if first_row != HEADERS:
        sheet.clear()
        sheet.append_row(HEADERS)

async def save_booking(booking_data: dict) -> bool:
    try:
        sheet = get_sheet()
        ensure_headers(sheet)
        row = [
            booking_data.get("name", "Unknown"),
            booking_data.get("service", "Unknown"),
            booking_data.get("date", "Unknown"),
            booking_data.get("time", "Unknown"),
            booking_data.get("email", "Not provided"),
            "Confirmed",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(row)
        print(f"Booking saved: {booking_data.get('name')}")
        return True
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        return False