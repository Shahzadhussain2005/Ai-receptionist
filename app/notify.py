import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", os.getenv("GMAIL_SENDER"))

def build_owner_email(booking_data: dict) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🆕 New Booking — {booking_data.get('name', 'Unknown')} — Glow Studio"
    msg["From"] = GMAIL_SENDER
    msg["To"] = OWNER_EMAIL

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">

        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #c9a96e; font-size: 24px; margin: 0;">✨ Glow Studio</h1>
            <p style="color: #888; margin: 5px 0;">New Booking Alert</p>
        </div>

        <div style="background: #f0fff4; border-left: 4px solid #48bb78; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h2 style="color: #276749; margin-top: 0;">🆕 New Appointment Booked!</h2>
            <p style="color: #555;">A new booking was just made via your AI receptionist Maya.</p>
        </div>

        <div style="background: #fff8f0; border-radius: 12px; padding: 24px; margin: 20px 0;">
            <h3 style="color: #333; margin-top: 0;">Booking Details</h3>

            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #f0e0d0;">
                    <td style="padding: 12px 0; color: #888; width: 40%;">Client Name</td>
                    <td style="padding: 12px 0; color: #333; font-weight: bold;">{booking_data.get("name", "Unknown")}</td>
                </tr>
                <tr style="border-bottom: 1px solid #f0e0d0;">
                    <td style="padding: 12px 0; color: #888;">Service</td>
                    <td style="padding: 12px 0; color: #333; font-weight: bold;">{booking_data.get("service", "Unknown")}</td>
                </tr>
                <tr style="border-bottom: 1px solid #f0e0d0;">
                    <td style="padding: 12px 0; color: #888;">Date</td>
                    <td style="padding: 12px 0; color: #333; font-weight: bold;">{booking_data.get("date", "Unknown")}</td>
                </tr>
                <tr style="border-bottom: 1px solid #f0e0d0;">
                    <td style="padding: 12px 0; color: #888;">Time</td>
                    <td style="padding: 12px 0; color: #333; font-weight: bold;">{booking_data.get("time", "Unknown")}</td>
                </tr>
                <tr style="border-bottom: 1px solid #f0e0d0;">
                    <td style="padding: 12px 0; color: #888;">Client Email</td>
                    <td style="padding: 12px 0; color: #333; font-weight: bold;">{booking_data.get("email", "Not provided")}</td>
                </tr>
            </table>
        </div>

        <div style="background: #f9f9f9; border-radius: 12px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #333; margin-top: 0;">Call Transcript</h3>
            <p style="color: #555; font-size: 13px; line-height: 1.6; white-space: pre-wrap;">{booking_data.get("transcript", "No transcript available")}</p>
        </div>

        <div style="text-align: center; padding: 20px 0; border-top: 1px solid #f0e0d0;">
            <p style="color: #888; font-size: 13px;">Check your Google Sheet for full booking history</p>
            <p style="color: #c9a96e; font-weight: bold;">Glow Studio AI Receptionist</p>
        </div>

    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))
    return msg

async def send_owner_email(booking_data: dict) -> bool:
    try:
        msg = build_owner_email(booking_data)
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=465,
            username=GMAIL_SENDER,
            password=GMAIL_PASSWORD,
            use_tls=True
        )
        print(f"Owner notification sent to {OWNER_EMAIL}")
        return True
    except Exception as e:
        print(f"Error sending owner email: {e}")
        return False