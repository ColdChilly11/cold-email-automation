import base64
import csv
import os
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --------------------- CONFIGURATION ---------------------

CSV_FILE_PATH = r'path\to\your\YourFollowUpList.csv'  # Your CSV file with Name, Mail, Company

FOLLOW_UP_BODY = """Hi {{Name}}, 

Just gently following up on my earlier email regarding the opportunity at {{Company}}. I’d love to hear your thoughts when you have a moment.

Regards, 
[Your Name]
"""

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'credentials.json'

# ---------------------------------------------------------

def authenticate():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_message(to, body, thread_id=None, subject=None, references=None):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject or "Follow-up"
    
    # Critical for threading: set In-Reply-To and References headers
    if references:
        # In-Reply-To should be the most recent message
        message['In-Reply-To'] = references[-1]
        # References should be all previous messages
        message['References'] = ' '.join(references)
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    msg = {'raw': raw}
    
    # Set threadId for Gmail API
    if thread_id:
        msg['threadId'] = thread_id
    
    print(f"Thread ID: {thread_id}")
    print(f"References: {references}")
    print(f"Subject: {subject}")
    
    return msg

def search_sent_thread(service, recipient):
    three_days_ago = (datetime.utcnow() - timedelta(days=7)).strftime('%Y/%m/%d')
    query = f"to:{recipient} after:{three_days_ago}"
    results = service.users().messages().list(userId='me', labelIds=['SENT'], q=query).execute()
    messages = results.get('messages', [])
    if messages:
        # Get the most recent message (first one in the list)
        return messages[0]['threadId'], messages[0]['id']
    else:
        return None, None

def get_all_message_ids_in_thread(service, thread_id, my_email):
    """Get all message IDs from me in this thread in chronological order"""
    try:
        thread = service.users().threads().get(userId='me', id=thread_id).execute()
        messages = thread['messages']
        
        my_message_ids = []
        
        # Go through messages in order (oldest first)
        for msg in messages:
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            from_email = headers.get('From', '')
            
            # Check if this message is from me
            if my_email.lower() in from_email.lower():
                # Get the actual Message-ID header
                msg_headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                message_id = msg_headers.get('Message-ID')
                if message_id:
                    my_message_ids.append(message_id)
        
        return my_message_ids
        
    except Exception as e:
        print(f"Error getting thread message IDs: {e}")
        return []

# Configuration: Maximum number of follow-ups to send
MAX_FOLLOWUPS = 2  # Set this to your desired limit

def count_my_messages_in_thread(service, thread_id, my_email):
    """Count how many messages I've sent in this thread"""
    thread = service.users().threads().get(userId='me', id=thread_id).execute()
    messages = thread['messages']
    
    count = 0
    for msg in messages:
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        from_email = headers.get('From', '')
        
        # Check if this message is from me
        if my_email.lower() in from_email.lower():
            count += 1
    
    return count

def get_thread_message_metadata(service, message_id):
    try:
        print(f"Trying to get metadata for message ID: {message_id}")
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        msg_id = headers.get('Message-ID')
        subject = headers.get('Subject')
        
        print(f"Retrieved Message-ID: {msg_id}")
        print(f"Retrieved Subject: {subject}")
        
        return msg_id, subject
        
    except Exception as e:
        print(f"Error getting message metadata: {e}")
        return None, None

def has_reply(service, thread_id, my_email):
    thread = service.users().threads().get(userId='me', id=thread_id).execute()
    messages = thread['messages']
    
    # Skip the first message (original) and check if any subsequent message is from someone else
    for msg in messages[1:]:
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        from_email = headers.get('From', '')
        
        # Check if the message is not from you (indicating a reply)
        if my_email.lower() not in from_email.lower():
            return True
    return False

def send_message(service, message):
    return service.users().messages().send(userId='me', body=message).execute()

def personalize(template, name, company):
    return template.replace("{{Name}}", name).replace("{{Company}}", company)

def get_my_email(service):
    profile = service.users().getProfile(userId='me').execute()
    return profile['emailAddress']

def main():
    service = authenticate()
    my_email = get_my_email(service)
    print(f"Authenticated as: {my_email}")

    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['Name']
            email = row['Mail']
            company = row['Company']

            print(f"\nProcessing {email}...")

            thread_id, msg_id = search_sent_thread(service, email)

            if not thread_id:
                print(f"[SKIP] No mail found for {email} in the last 3 days")
                continue

            if has_reply(service, thread_id, my_email):
                print(f"[SKIP] Reply already received from {email}")
                continue

            # Check if we've already sent too many follow-ups
            my_message_count = count_my_messages_in_thread(service, thread_id, my_email)
            if my_message_count >= MAX_FOLLOWUPS + 1:  # +1 for original message
                print(f"[SKIP] Already sent {my_message_count - 1} follow-ups to {email}")
                continue

            # Get all message IDs from me in this thread
            my_message_ids = get_all_message_ids_in_thread(service, thread_id, my_email)
            
            if not my_message_ids:
                print(f"[ERROR] Could not find any Message-IDs from me in thread {thread_id}")
                continue
            
            print(f"Found {len(my_message_ids)} messages from me in thread")
            
            # For subject, get the original subject from the first message in the thread
            thread = service.users().threads().get(userId='me', id=thread_id).execute()
            first_message = thread['messages'][0]
            first_headers = {h['name']: h['value'] for h in first_message['payload']['headers']}
            original_subject = first_headers.get('Subject', 'Follow-up')
            
            # Ensure proper subject formatting for threading
            if original_subject:
                if not original_subject.lower().startswith("re:"):
                    subject = f"Re: {original_subject}"
                else:
                    subject = original_subject
            else:
                subject = "Re: Follow-up"

            follow_up = personalize(FOLLOW_UP_BODY, name, company)
            msg = create_message(email, follow_up, thread_id=thread_id, subject=subject, references=my_message_ids)
            
            try:
                send_message(service, msg)
                print(f"[SENT] Follow-up sent to {email} in thread {thread_id}")
            except Exception as e:
                print(f"[ERROR] Failed to send to {email}: {str(e)}")

            time.sleep(1)

if __name__ == '__main__':
    main()