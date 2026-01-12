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
# Argument one is the excel sheet of faculty & supervisors with e-mails
# Argument two is the department directory

EXCEL_FILE = sys.argv[1]
file_destination = sys.argv[2]

FAR_DRAFT_PATH = "make_cv" +os.sep +"FAR_docx"
NSF_COA_PATH = "make_cv" +os.sep +"Collaborators" +os.sep +"collaborators.xlsx"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

AUTH_EMAIL = ""
AUTH_PASSWORD = ""  # Must be valid App Password

DELEGATED_EMAIL = "far@clarkson.edu"
DELEGATED_NAME = "FAR Team"
REPLY_TO_EMAIL = "far@clarkson.edu"

SUBJECT = "2025 Faculty Activity Report (FAR) Draft – Review & Submission Required"

# HTML body with bold text
HTML_BODY_TEMPLATE = """\
<html>
<body style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; line-height: 1.5;">
<p>Dear Prof. {name},</p>

<p>Attached please find a working draft of your <strong>2025 annual Faculty Activity Report (FAR)</strong>. This draft includes pre-populated information where available to support review and completion.</p>

<p>Please begin by reviewing the instructions provided at the beginning of the FAR, as they outline how the document is structured and how information should be reviewed and updated.</p>

<p><strong>What to Do</strong><br>
Please review the attached FAR carefully and:</p>

<ul>
  <li>Correct or update any pre-populated information</li>
  <li>Add any missing information as appropriate</li>
</ul>

<p>Please retain all section headers, even if a section does not apply to you. There is no need to add “N/A” under sections that are not relevant.<br>
<strong>Faculty are responsible for reviewing and verifying the accuracy and completeness</strong> of any information they edit or add to the FAR prior to submission.</p>

<p><strong>Submission Deadline</strong><br>
Please submit your completed, revised FAR by <strong>February 2</strong> to:</p>

<ul>
  <li>Your department chair or equivalent supervisor</li>
  <li>Your department administrator or designee</li>
  <li><strong>far@clarkson.edu</strong></li>
</ul>

<p><strong>What Happens Next</strong><br>
Department chairs or supervisors will conduct annual reviews and draft review letters as usual by <strong>February 27</strong>.</p>

<p><strong>Looking Ahead</strong><br>
We will continue to streamline and automate FAR information and processes where possible to support efficiency, accuracy, and consistent reporting across departments. Submitting revised FARs to far@clarkson.edu helps inform ongoing improvements to data collection and reporting.</p>

<p>If you have questions related to your FAR draft, please reach out to your department or email far@clarkson.edu.</p>

<p>Thank you for your time and attention to the FAR reporting and review process.</p>

<p>Best regards,<br>
FAR Team<br>
Brian Helenbrook<br>
Sidrah Yaqoob<br>
Akshay Kumar Thugudam<br>
Mohamed Fehmi Krifa<br>
</p>


<p style="font-style: italic;">P.S. For those of you who do NSF proposals, we have also included a file “collaborators.xlsx” which uses the grant, student, and publication information to create a collaborator list for NSF submissions.</p>
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

df["FacultyName"] = df["LAST_NAME"].astype(str) +', ' +df["FIRST_NAME"].astype(str)

os.chdir(file_destination)

for FacultyName in os.listdir("."):
    if FacultyName.find(",") > -1:
        print(f'Sending e-mail for {FacultyName}: ', end="")
        entries = df[df['FacultyName'] == FacultyName]
        if not entries.shape[0] == 1:
            print('Uh-oh' +FacultyName)
            skipped += 1
            continue
        recipient = entries["JJs Email list"].iloc[0]
        supervisor = entries["Supervisor Email"].iloc[0]
        greeting_name = entries["LAST_NAME"].iloc[0]
        shutil.copyfile(Path(FacultyName +os.sep +FAR_DRAFT_PATH +os.sep +"far.docx"), Path(FacultyName +os.sep +FAR_DRAFT_PATH +os.sep +FacultyName +" FAR.docx"))

        msg = EmailMessage()
        msg["From"] = f"{DELEGATED_NAME} <{DELEGATED_EMAIL}>"
        msg["To"] = recipient
        msg["Cc"] = supervisor
        msg["Reply-To"] = REPLY_TO_EMAIL
        msg["Subject"] = SUBJECT

        print(recipient)
        print(supervisor)
        
        html_body = HTML_BODY_TEMPLATE.format(name=greeting_name)
        msg.set_content(html_body, subtype="html")

        # -----------------------------
        # Attachments
        # -----------------------------
        
        attachments = [Path(FacultyName +os.sep +FAR_DRAFT_PATH +os.sep +FacultyName +" FAR.docx"),  Path(FacultyName +os.sep +NSF_COA_PATH)]
        
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