#! /usr/bin/env python3

import pandas as pd
import smtplib
from email.message import EmailMessage
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
EXCEL_FILE = "emails.xlsx"
ATTACHMENT_PATH = "attachment.pdf"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Gmail app password

SUBJECT = "Automated Message"
BODY_TEMPLATE = """\
Hello {name},

This is an automated email sent using Python.

Best regards,
Brian
"""

# -----------------------------
# Load spreadsheet
# -----------------------------
df = pd.read_excel(EXCEL_FILE)

# -----------------------------
# Connect to SMTP server
# -----------------------------
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(SENDER_EMAIL, SENDER_PASSWORD)

# -----------------------------
# Send emails
# -----------------------------
attachment_path = Path(ATTACHMENT_PATH)

for _, row in df.iterrows():
    recipient = row["Email"]
    name = row.get("Name", "Colleague")

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg["Subject"] = SUBJECT
    msg.set_content(BODY_TEMPLATE.format(name=name))

    # Attach file
    with open(attachment_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename=attachment_path.name
        )

    server.send_message(msg)
    print(f"Sent email to {recipient}")

# -----------------------------
# Cleanup
# -----------------------------
server.quit()
