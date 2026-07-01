import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def build_client_email(booking_data: dict) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Appointment is Confirmed — Glow Studio ✨"
    msg["From"] = GMAIL_SENDER
    msg["To"] = booking_data.get("email")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #c9a96e; font-size: 28px; margin: 0;">✨ Glow Studio</h1>
            <p style="color: #888; margin: 5px 0;">Permanent Makeup & Beauty Artistry</p>
        </div>

        <div style="background: #fff8f0; border-radius: 12px; padding: 24px; margin: 20px 0;">
            <h2 style="color: #333; margin-top: 0;">Your Appointment is Confirmed!</h2>
            <p style="color: #555;">Hi {booking_data.get("name", "there")},</p>
            <p style="color: #555;">We're excited to see you! Here are your booking details:</p>

            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="border-bottom: 1px solid #f0e0d0;">
                    <td style="padding: 12px 0; color: #888; width: 40%;">Service</td>
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
                <tr>
                    <td style="padding: 12px 0; color: #888;">Deposit</td>
                    <td style="padding: 12px 0; color: #333; font-weight: bold;">$100 due on arrival</td>
                </tr>
            </table>
        </div>

        <div style="background: #f9f9f9; border-radius: 12px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #333; margin-top: 0;">Important Reminders</h3>
            <ul style="color: #555; padding-left: 20px; line-height: 1.8;">
                <li>Please arrive 10 minutes early</li>
                <li>Cancel at least 48 hours in advance to keep your deposit</li>
                <li>Avoid alcohol 24 hours before your appointment</li>
                <li>Come with a clean face — no heavy makeup on the treatment area</li>
            </ul>
        </div>

        <div style="text-align: center; padding: 20px 0; color: #555;">
            <p>📍 123 Beauty Lane, Suite 5</p>
            <p>📞 (555) 123-4567</p>
        </div>

        <div style="text-align: center; padding: 20px 0; border-top: 1px solid #f0e0d0;">
            <p style="color: #888; font-size: 14px;">See you soon!</p>
            <p style="color: #c9a96e; font-weight: bold;">Maya & The Glow Studio Team</p>
        </div>

    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))
    return msg

async def send_client_email(booking_data: dict) -> bool:
    try:
        msg = build_client_email(booking_data)
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=465,
            username=GMAIL_SENDER,
            password=GMAIL_PASSWORD,
            use_tls=True
        )
        print(f"Confirmation email sent to {booking_data.get('email')}")
        return True
    except Exception as e:
        print(f"Error sending client email: {e}")
        return False