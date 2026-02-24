#! /usr/bin/env python3

import os,sys,platform,shutil
import pandas as pd
import smtplib
from email.message import EmailMessage
from pathlib import Path
import time
import traceback
import shutil

# -----------------------------
# Configuration
# -----------------------------
# Argument one is the excel sheet of supervisors e-mails
# Argument two is the department directory

EXCEL_FILE = sys.argv[1]
file_destination = sys.argv[2]

SUPERVISOR_REPORT_PATH = "Report" +os.sep +"supervisor_report.pdf"
ANNUAL_REPORT_PATH = "Report" +os.sep +"annual_report.pdf"
EXCEL_FILE_PATH = "Report" +os.sep +"faculty_data.xlsx"
TEACHING_INDEX_PATH = "Report" +os.sep +"teaching_index.csv"
ADVISING_INDEX_PATH = "Report" +os.sep +"advising_index.csv"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

AUTH_EMAIL = sys.argv[3]
AUTH_PASSWORD = sys.argv[4]

DELEGATED_EMAIL = "far@clarkson.edu"
DELEGATED_NAME = "FAR Team"
REPLY_TO_EMAIL = "far@clarkson.edu"

SUBJECT = "2025 Supervisor Report (FAR) Draft"

# HTML body with bold text
HTML_BODY_TEMPLATE = """\
<html>
<body style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; line-height: 1.5;">
<p>Dear Prof. {name},</p>

<p>Attached is a file called "supervisor_report.pdf" which summarizes the data collected for each faculty that reports to you.  Note that this is completely experimental and is based on what the MAE department was doing for annual reports.  The main caveat is that in the MAE Department, the faculty could modify and correct their own data, but your faculty can not.  As such, <strong>please treat this report as an experiment and not something that should be used to evaluate faculty</strong>.  Use the FARs from faculty for that.</p>

<p>Having said that, the data in these reports should be improved from the time that the FARs were generated.  We are now using SCOPUS, ORCID, Google, and the USPTO to gather publication data so that part should be more complete.  Grant & Proposal data is as reliable as the SRS data.  Teaching evaluation data should also be reliable although what to include in overall averages could and should be debated.  This is also true of teaching counts.</p>

<ul>
  <li>"faculty_data.xlsx" which was something that Marcias requested last year.  It contains the numerical data used to make the plots.</li>
  <li>"annual_report.pdf" this is basically the same as supervisor_report except that the names have been removed from the advising evaluation and teaching evaluation plots and they have been sorted in ascending order.  In the MAE department, we share this with the faculty, but please don't do that because the faculty haven't been given the opportunity to correct the data.</li>
  <li>"teaching_index.csv" and "advising_index.csv"  These are the names that would be on the x-axis of the sorted evaluation plots.  In the MAE department, each faculty was sent their own indices so they could see where they stood in the department.</li>
</ul>

<p>We are working on mechanisms to allow the faculty to modify their own data for next year.  In the meantime, any feedback you have about how things went this year can be sent to far@clarkson.edu</p>

<p>Also note that some of you have only one person report to you, in which case, none of this makes any sense :-).</p>

<p>Best regards,<br>
FAR Team<br>
Brian Helenbrook<br>
Sidrah Yaqoob<br>
Akshay Kumar Thugudam<br>
Mohamed Fehmi Krifa<br>
</p>

</body>
</html>
"""

# -------------------
# Load spreadsheet 
# --------------------

df = pd.read_excel(EXCEL_FILE)

# -----------------------------
# Connect to SMTP
# -----------------------------
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(AUTH_EMAIL, AUTH_PASSWORD)
    print("SMTP login successful\n")
except Exception as e:
    print("Login failed. Please check App Password and 2FA.")
    print(e)
    exit(1)

# -----------------------------
# Send emails with count
# -----------------------------
sent = 0
skipped = 0

base_path = Path(file_destination)
for faculty_dir in base_path.iterdir():
    if not faculty_dir.is_dir() or faculty_dir.name.find(",") == -1:
        continue
    FacultyName = faculty_dir.name
    print(f'Sending e-mail for {FacultyName}: ', end="")
    entries = df[df['Name'] == FacultyName]
    if not entries.shape[0] == 1:
        print('Uh-oh' +FacultyName)
        skipped += 1
        continue
    recipient = entries["email"].iloc[0]
    greeting_name = FacultyName.split(",")[0]

    msg = EmailMessage()
    msg["From"] = f"{DELEGATED_NAME} <{DELEGATED_EMAIL}>"
    msg["To"] = recipient
    msg["Reply-To"] = REPLY_TO_EMAIL
    msg["Subject"] = SUBJECT

    print(recipient)
    
    html_body = HTML_BODY_TEMPLATE.format(name=greeting_name)
    msg.set_content(html_body, subtype="html")

    # -----------------------------
    # Attachments
    # -----------------------------
    
    attachments = [Path(base_path,FacultyName +os.sep +SUPERVISOR_REPORT_PATH),  Path(base_path,FacultyName +os.sep +ANNUAL_REPORT_PATH), Path(base_path,FacultyName +os.sep +EXCEL_FILE_PATH), Path(base_path,FacultyName +os.sep +TEACHING_INDEX_PATH), Path(base_path,FacultyName +os.sep +ADVISING_INDEX_PATH)]
    
    for att in attachments:
        if not att.exists():
            print(f"WARNING: Missing attachment → {att}")
            
    # Attach files
    for att in attachments:
        if att.exists():
            ext = att.suffix.lower()
            if ext == '.pdf':
                main, sub = "application", "pdf"
            elif ext in ['.docx', '.doc']:
                main, sub = "application", "vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == '.xlsx':
                main, sub = "application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                main, sub = "application", "octet-stream"

            with open(att, "rb") as f:
                msg.add_attachment(f.read(), maintype=main, subtype=sub, filename=att.name)

    try:
        server.send_message(msg)
        sent += 1
        time.sleep(2)  # Rate limit protection
    except Exception as e:
        print('Uh-oh' +FacultyName)
        skipped += 1

# -----------------------------
# Summary
# -----------------------------
server.quit()

print(f"\n=== Summary ===")
print(f"Successfully sent: {sent}")
print(f"Skipped/failed: {skipped}")