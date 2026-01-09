
import pandas as pd
import smtplib
from email.message import EmailMessage
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------
EXCEL_FILE = '/Users/akshaythugudam/Documents/GitHub/University Data/email_test.xlsx'
ATTACHMENT_PATH = '/Users/akshaythugudam/Documents/GitHub/Departments/Arts Culture Technology Dept/Ball, Jennifer/make_cv/FAR_docx/far.docx'

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Account you authenticate with
AUTH_EMAIL = "thuguda@clarkson.edu"
AUTH_PASSWORD = "kichjbhkyhukldci"

# Delegated "Send As" address
DELEGATED_EMAIL = "far@clarkson.edu"
DELEGATED_NAME = "TEAM FAR"

SUBJECT = "Automated Message"
BODY_TEMPLATE = """\
Hello {name},

This message is sent from a delegated departmental account.

Best regards,
FAR
"""

# -----------------------------
# Load spreadsheet
# -----------------------------
df = pd.read_excel(EXCEL_FILE)

# -----------------------------
# Connect to Gmail
# -----------------------------
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(AUTH_EMAIL, AUTH_PASSWORD)

attachment_path = Path(ATTACHMENT_PATH)

# -----------------------------
# Send emails
# -----------------------------
for _, row in df.iterrows():
    recipient = row["Email"]
    name = row.get("Name", "Colleague")

    msg = EmailMessage()
    msg["From"] = f"{DELEGATED_NAME} <{DELEGATED_EMAIL}>"
    msg["To"] = recipient
    msg["Subject"] = SUBJECT
    msg.set_content(BODY_TEMPLATE.format(name=name))

    with open(attachment_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename=attachment_path.name
        )

    server.send_message(msg)
    print(f"Sent delegated email to {recipient}")

server.quit()
