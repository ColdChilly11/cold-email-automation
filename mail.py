import smtplib
import pandas as pd
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication  # <-- Added for PDF attachment
import os

# Read your CSV
df = pd.read_csv(r'C:\Users\pc\OneDrive\Desktop\Mailer\Mailed\1st September.csv')  # Columns: Name, Mail, Company

# Your Gmail credentials
your_email = "abhiabhii9001jk@gmail.com" #add your email here
your_app_password = "kjcz wbbl hmei muls" #generate your app password and add here

# Email validation function
def is_valid_email(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(regex, email)

# Setup SMTP connection
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(your_email, your_app_password)

# Loop through each row and send mail
for index, row in df.iterrows():
    recipient = row["Mail"]

    if not is_valid_email(recipient):
        print(f"❌ Skipped invalid email: {recipient}")
        continue  # skip to next email

    msg = MIMEMultipart()
    msg["From"] = your_email
    msg["To"] = recipient
    msg["Subject"] = f"IIT Bombay | PM @ Fi Money | ex-Gupshup, UC (Requesting opportunity at {row['Company']})"

    body = f"""Hi {row['Name']},

My name is Abhijeet and I am a recent graduate from IIT Bombay. I am currently seeking an entry-level job opportunities as APM, Product Analyst or Growth roles.

My experience at different places has been nothing short of impactful and want to do the same at {row['Company']}:

- Currently a Product Intern at Fi Money in the User Risk Team where I am actively working on AI and LLM-based models, focusing on improving internal products, heavy data analysis, LLM prompt and context design, evaluation, and understanding model behavior.
- Completed 1 year of Product Management intern at Gupshup building products for clients worldwide in the Bot Studio and Journey Builder Team
- Did a remote research project on customer centricity and marketing at Solvay Brussels School
- Completed 2.5 months on-site internship as data analyst under BDA profile at Urban Company in Mumbai Salon Division
- Came 1st in Product Challenge at PM School and have participated in various others

Thank you so much, and please let me know if you have any questions or if you'd like to look at my resume. Looking forward to an opportunity.

Sincerely,
Abhijeet Choudhary

My portfolio website for virtual handshake – https://abhijeetchoudhary.super.site/
Find my resume attached below:
"""
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF (common for all or customize per recipient)
    pdf_path = r"C:\Users\pc\OneDrive\Desktop\Mailer\Job Ress\Abhijeet_Choudhary_Resume.pdf"  # Change if needed
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="pdf")
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
            msg.attach(part)

    try:
        server.sendmail(your_email, recipient, msg.as_string())
        print(f"✅ Sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send to {recipient}: {e}")

    time.sleep(4)  # ⏳ Delay between mails

server.quit()

# https://tinyurl.com/abhijeet03
#kjcz wbbl hmei muls