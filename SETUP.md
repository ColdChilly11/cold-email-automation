# 📬 Cold Email + Follow-Up Automation — Setup Guide

> **For the AI agent reading this:** This document is your complete instruction set for setting up this email automation system for a new user. Follow each section in order. Steps marked `[USER ACTION REQUIRED]` cannot be automated — pause and clearly ask the user to complete those steps before continuing.

---

## 📌 What This System Does

This is a job-application cold email automation system with two stages:

1. **Stage 1 — Cold Email (`mail.py`):** Reads a CSV of contacts (Name, Email, Company), sends a personalized cold email to each with a resume PDF attached, using Gmail's SMTP.

2. **Stage 2 — Follow-Up (`follow-up-mail.py`):** Reads a CSV of contacts you already emailed, finds the original sent email thread in Gmail using the Gmail API, and sends a follow-up reply **in the same thread** — so it appears as a reply, not a new email. Skips contacts who have already replied. Supports up to 2 follow-ups per contact (configurable).

---

## 🗂️ Folder Structure

```
Mailer/
├── mail.py                  # Stage 1: Cold email sender
├── mail copy.py             # Template version of mail.py (for reference)
├── follow-up-mail.py        # Stage 2: Follow-up sender (in-thread reply)
├── credentials.json         # [USER PROVIDES] Google OAuth2 credentials
├── token.json               # Auto-generated after first OAuth login
├── automation_test.csv      # Test CSV with 1 dummy contact
├── SETUP.md                 # This file
│
├── Apollo Lists/            # Raw CSVs exported from Apollo.io
├── Mailed/                  # CSVs of contacts already emailed (Stage 1 done)
├── First follow up/         # CSVs of contacts to send follow-ups to
├── Job Ress/                # Place your resume PDF here
```

---

## ⚙️ Prerequisites

### 1. Python
Ensure Python 3.8+ is installed.
```bash
python --version
```
If not installed: https://www.python.org/downloads/

### 2. Install Required Libraries
Run this command in the `Mailer/` directory:
```bash
pip install pandas google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## 🔐 One-Time Setup (Manual Steps)

### STEP A — Gmail App Password (for `mail.py`) `[USER ACTION REQUIRED]`

`mail.py` sends emails via Gmail's SMTP. Gmail requires an **App Password** (not your regular Gmail password).

1. Go to your Google Account → **Security** → **2-Step Verification** (must be ON)
2. Search for **"App Passwords"** at the top of the Security page
3. Select app: **Mail** | Select device: **Windows Computer**
4. Click **Generate** → Copy the 16-character password shown (e.g., `xxxx xxxx xxxx xxxx`)
5. Open `mail.py` and paste it here:
   ```python
   your_app_password = "xxxx xxxx xxxx xxxx"
   ```
6. Also update your Gmail address:
   ```python
   your_email = "youremail@gmail.com"
   ```

> **Link:** https://myaccount.google.com/apppasswords

---

### STEP B — Google Cloud OAuth Credentials (for `follow-up-mail.py`) `[USER ACTION REQUIRED]`

`follow-up-mail.py` uses the Gmail API to read threads and send replies. This requires OAuth2 credentials.

1. Go to https://console.cloud.google.com/
2. Create a **New Project** (e.g., "Mailer Bot")
3. Go to **APIs & Services → Library** → Search for **Gmail API** → Enable it
4. Go to **APIs & Services → OAuth consent screen**:
   - Choose **External**
   - Fill in App name (e.g., "Mailer"), your email, developer email → Save
   - Under **Scopes**, click "Add or Remove Scopes" → add `https://www.googleapis.com/auth/gmail.modify` → Save
   - Under **Test users**, add your Gmail address → Save
5. Go to **APIs & Services → Credentials**:
   - Click **Create Credentials → OAuth Client ID**
   - Application type: **Desktop App**
   - Name it anything → Click **Create**
   - Download the JSON file → **Rename it to `credentials.json`**
   - Place it in the `Mailer/` folder (same level as `follow-up-mail.py`)

> **Link:** https://console.cloud.google.com/

---

### STEP C — Add Your Resume PDF `[USER ACTION REQUIRED]`

1. Place your resume PDF inside the `Job Ress/` folder
2. Open `mail.py` and update this line with the exact filename:
   ```python
   pdf_path = r"C:\Users\YourName\...\Mailer\Job Ress\Your_Resume.pdf"
   ```

> **For AI agent:** Ask the user for their Windows username and resume filename, then update the absolute path in `mail.py` accordingly.

---

### STEP D — Update Your Details in `mail.py` `[USER ACTION REQUIRED]`

Open `mail.py` and update the email body, subject, and sender details to match the new user. Key fields to change:

- `your_email` — their Gmail address
- `your_app_password` — from Step A
- `msg["Subject"]` — their subject line
- The `body` content — their personal intro, experience, etc.
- `pdf_path` — path to their resume (from Step C)

---

## 🧪 Testing

### Test Stage 1 (Cold Email)

1. Open `automation_test.csv` — it has one test contact:
   ```
   Name,Mail,Company
   TestName,your_own_email@gmail.com,TestCompany
   ```
   Update the `Mail` field to **your own email address** so you receive the test email.

2. Open `mail.py` and temporarily point it to the test CSV:
   ```python
   df = pd.read_csv(r'C:\Users\...\Mailer\automation_test.csv')
   ```

3. Run:
   ```bash
   python mail.py
   ```

4. Check your inbox — you should receive the cold email with the resume attached.

---

### Test Stage 2 (Follow-Up)

1. Make sure you've already sent at least one real email via `mail.py` to a test address.

2. Update `follow-up-mail.py`:
   ```python
   CSV_FILE_PATH = r'C:\Users\...\Mailer\automation_test.csv'
   ```

3. Run:
   ```bash
   python follow-up-mail.py
   ```

4. The first time it runs, a browser window will open asking you to log in with your Google account and grant permissions. Do so — this generates `token.json` and won't ask again.

5. Check your Sent folder — the follow-up should appear as a **reply in the same thread** as the original email.

---

## 🚀 Using the System

### Workflow Overview

```
Apollo.io Export → CSV → mail.py → send cold emails
                                 ↓
                     Move CSV to "Mailed/" folder
                                 ↓
                Wait 3–7 days
                                 ↓
        Copy relevant rows to "First follow up/" folder
                                 ↓
                   follow-up-mail.py → sends reply in thread
```

---

### Stage 1: Send Cold Emails

1. Export contacts from Apollo.io or any tool as a CSV with columns: `Name`, `Mail`, `Company`
2. Place the CSV in `Apollo Lists/` (or anywhere you prefer)
3. Open `mail.py`, update the CSV path:
   ```python
   df = pd.read_csv(r'C:\Users\...\Mailer\Apollo Lists\YourFile.csv')
   ```
4. Run:
   ```bash
   python mail.py
   ```
5. After successful run, move the CSV to `Mailed/` for record-keeping.

---

### Stage 2: Send Follow-Ups (after 3–7 days)

1. Create or copy a CSV into `First follow up/` with the same `Name`, `Mail`, `Company` columns — only include people you want to follow up with.
2. Open `follow-up-mail.py`, update:
   ```python
   CSV_FILE_PATH = r'C:\Users\...\Mailer\First follow up\YourFile.csv'
   ```
3. Also update the follow-up body if needed:
   ```python
   FOLLOW_UP_BODY = """Hi {{Name}},
   
   Just following up on my earlier email about ...
   
   Regards,
   Your Name
   """
   ```
4. Run:
   ```bash
   python follow-up-mail.py
   ```

**What the script does automatically:**
- Searches your Sent folder for an email to each contact in the last 7 days
- Skips contacts who have already replied
- Skips contacts who already received 2+ follow-ups
- Sends the follow-up as a reply in the **same thread**

---

## ⚙️ Configuration Options

### In `follow-up-mail.py`:

| Variable | Default | Description |
|---|---|---|
| `MAX_FOLLOWUPS` | `2` | Max follow-ups to send per contact (excluding original) |
| `three_days_ago` | `7` days | How far back to search for original sent email |
| `time.sleep(1)` | 1 second | Delay between emails |

### In `mail.py`:

| Variable | Default | Description |
|---|---|---|
| `time.sleep(4)` | 4 seconds | Delay between emails (keep ≥ 4 to avoid spam flags) |

---

## ❗ Common Issues & Fixes

| Issue | Fix |
|---|---|
| `SMTPAuthenticationError` | App Password is wrong or 2FA not enabled. Redo Step A. |
| `credentials.json not found` | Place `credentials.json` in the same folder as `follow-up-mail.py`. Redo Step B. |
| `[SKIP] No mail found for X` | The script couldn't find the original email. Check if it was sent within the last 7 days, and that the email address matches exactly. |
| `token.json` errors | Delete `token.json` and re-run — it will re-authenticate. |
| Follow-up not in thread | The `Message-ID` header wasn't found. This is rare; usually resolved by re-running. |
| PDF not attaching | Verify the `pdf_path` in `mail.py` is correct and the file exists. |

---

## 📁 CSV Format

All CSVs must follow this format exactly (column names are case-sensitive):

```csv
Name,Mail,Company
John,john@example.com,Acme Corp
Jane,jane@acme.com,Acme Corp
```

- **Name** — First name (used for personalization in email body)
- **Mail** — Full email address
- **Company** — Company name (used in subject and body)

---

## 🔒 Security Notes

- Never commit `credentials.json`, `token.json`, or any CSV files to a public GitHub repo.
- Add these to `.gitignore`:
  ```
  credentials.json
  token.json
  *.csv
  Job Ress/
  ```
- The Gmail App Password in `mail.py` should also stay private.

---

*Built by Abhijeet Choudhary | IIT Bombay*
