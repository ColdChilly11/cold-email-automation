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

CSV_PATH = r'C:\Users\YourName\...\Mailer\YourContactList.csv'  # Path to your contacts CSV (columns: Name, Mail, Company)
YOUR_EMAIL = "youremail@gmail.com"                               # Your Gmail address
YOUR_APP_PASSWORD = ""                                           # Your Gmail App Password (see SETUP.md Step A)
PDF_PATH = r'C:\Users\YourName\...\Mailer\Your_Resume.pdf'      # Path to your resume PDF (leave empty string to skip)

# Subject line — {company} will be replaced with the recipient's company name
# 💡 TIP: Keep {company} in the subject — personalised subjects are less likely to be flagged as spam
EMAIL_SUBJECT = "Requesting opportunity at {company}"

# ─────────────────────────────────────────────
# EMAIL BODY TEMPLATE
# Available placeholders: {name}, {company}
# ─────────────────────────────────────────────

EMAIL_BODY = """Hi {name},

My name is [Your Name] and I am a [your background, e.g. recent graduate from XYZ University]. I am currently seeking [role, e.g. entry-level APM / Product Analyst / Growth] opportunities.

My experience has been impactful and I'd love to bring the same energy to {company}:

- [Experience 1 — e.g. Product Intern at Company X working on Y]
- [Experience 2 — e.g. PM Intern at Company Z building products for ...]
- [Experience 3 — e.g. Research project / internship / achievement]
- [Experience 4 — add or remove bullet points as needed]

Thank you so much, and please let me know if you have any questions or if you'd like to look at my resume. Looking forward to an opportunity.

Sincerely,
[Your Name]

[Your portfolio/LinkedIn URL]
Find my resume attached below:
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

    if PDF_PATH and os.path.exists(PDF_PATH):
        with open(PDF_PATH, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="pdf")
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(PDF_PATH))
            msg.attach(part)
    elif PDF_PATH:
        print(f"⚠️  Resume PDF not found at: {PDF_PATH}")

    try:
        server.sendmail(YOUR_EMAIL, recipient, msg.as_string())
        print(f"✅ Sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send to {recipient}: {e}")

    time.sleep(4)  # ⏳ Delay between emails — keep at 4+ seconds to avoid rate limits

server.quit()
print("✅ All done.")