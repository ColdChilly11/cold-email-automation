import smtplib
import pandas as pd
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

# ─────────────────────────────────────────────
# CONFIGURATION — Update these before running
# ─────────────────────────────────────────────

CSV_PATH = r'C:\Users\YourName\...\Mailer\Apollo Lists\YourFile.csv'  # Path to your contacts CSV
YOUR_EMAIL = "youremail@gmail.com"                                     # Your Gmail address
YOUR_APP_PASSWORD = ""                                                  # Your Gmail App Password (see SETUP.md Step A)
PDF_PATH = r'C:\Users\YourName\...\Mailer\Job Ress\Your_Resume.pdf'   # Path to your resume PDF

EMAIL_SUBJECT = "Requesting opportunity at {company}"                  # Customize your subject line

# ─────────────────────────────────────────────
# EMAIL BODY TEMPLATE
# Use {name} and {company} as placeholders
# ─────────────────────────────────────────────

EMAIL_BODY = """Hi {name},

My name is [Your Name] and I am a [your background]. I am currently seeking [role] opportunities.

I believe I can add value to {company} because [your reason].

Please find my resume attached. Looking forward to connecting.

Sincerely,
[Your Name]
"""

# ─────────────────────────────────────────────
# DO NOT EDIT BELOW THIS LINE
# ─────────────────────────────────────────────

def is_valid_email(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(regex, email)

df = pd.read_csv(CSV_PATH)

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)

for index, row in df.iterrows():
    recipient = row["Mail"]

    if not is_valid_email(recipient):
        print(f"❌ Skipped invalid email: {recipient}")
        continue

    msg = MIMEMultipart()
    msg["From"] = YOUR_EMAIL
    msg["To"] = recipient
    msg["Subject"] = EMAIL_SUBJECT.format(company=row['Company'])

    body = EMAIL_BODY.format(name=row['Name'], company=row['Company'])
    msg.attach(MIMEText(body, "plain"))

    if os.path.exists(PDF_PATH):
        with open(PDF_PATH, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="pdf")
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(PDF_PATH))
            msg.attach(part)
    else:
        print(f"⚠️  Resume PDF not found at: {PDF_PATH}")

    try:
        server.sendmail(YOUR_EMAIL, recipient, msg.as_string())
        print(f"✅ Sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send to {recipient}: {e}")

    time.sleep(4)  # ⏳ Delay between emails — keep at 4+ seconds

server.quit()
print("✅ All done.")