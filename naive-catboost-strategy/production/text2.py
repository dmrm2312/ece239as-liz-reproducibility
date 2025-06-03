import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests
from datetime import datetime
import pytz
import re

load_dotenv()

def send_text(subject: str, body: str) -> None:
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    sms_gateway = os.getenv("SMS_GATEWAY")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not all([email_address, email_password, sms_gateway, smtp_server, smtp_port]):
        raise ValueError("Missing one or more environment variables.")

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(email_address, email_password)

    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = sms_gateway
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    sms = msg.as_string()
    server.sendmail(email_address, sms_gateway, sms)
    server.quit()



def escape_markdown_v2(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


def send_telegram(subject: str, body: str, image_path: str = None) -> None:
    """Send a formatted Telegram message with optional image attachment."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing from environment.")

    # Format timestamp in PST
    tz = pytz.timezone("America/Los_Angeles")
    timestamp = datetime.now(tz).strftime("%y-%m-%d %I:%M:%S %p PST")

    raw_message = f"{subject}\n\n{body}\n\n{timestamp}"
    message = escape_markdown_v2(raw_message)


    if image_path and os.path.isfile(image_path):
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(image_path, "rb") as img:
            files = {"photo": img}
            data = {
                "chat_id": chat_id,
                "caption": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, data=data, files=files)
    else:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "MarkdownV2"
        }
        response = requests.post(url, json=payload)

    if not response.ok:
        raise RuntimeError(f"Telegram API error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    send_telegram("Backup Complete", "The backup completed successfully.")
