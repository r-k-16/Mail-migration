# 📧 Email Backup & Restore Scripts (IMAP)

These Python scripts help you **download** and **upload** emails via the IMAP protocol for backup and migration purposes.

- `mail-down.py`: Download emails from a source IMAP server.
- `mail-up.py`: Upload emails to a destination IMAP server.

---

## 🛠 Requirements

- Python 3.6+
- [`imapclient`](https://pypi.org/project/IMAPClient/)

Install with:

```bash
pip install IMAPClient
```

---

## 📥 `mail-down.py` – Download Emails

Downloads emails from an IMAP server to local `.eml` files in structured folders.

### 🔧 Configuration

Edit the top of the script:
```python
SOURCE_HOST = 'example.com'
SOURCE_USER = 'test@example.com'
SOURCE_PASS = 'your_password'
EMAILS_PATH = '/tmp/emails_backup'
```

### 📦 Features

- Downloads all or specific folders
- Saves emails as `.eml` with timestamp, UID, and read/unread flag
- Skips emails already downloaded
- Batch processing for large inboxes

### 📋 Usage

```bash
python3 mail-down.py                     # Download all folders
python3 mail-down.py --folder INBOX      # Download only INBOX
python3 mail-down.py --list              # List available folders on the server
```

---

## 📤 `mail-up.py` – Upload Emails

Uploads previously downloaded `.eml` files to a new IMAP server.

### 🔧 Configuration

Edit the top of the script:
```python
DEST_HOST = 'host.example.com'
DEST_USER = 'test@example.com'
DEST_PASS = 'your_password'
EMAILS_PATH = '/tmp/emails_backup'
```

### 📦 Features

- Uploads all or specific folders
- Maintains read/unread status and original timestamps
- Can upload a specific `.eml` file
- Prevents uploads to unmapped or missing folders

### 📁 Folder Mapping

Update `FOLDER_MAP` in the script to map local folder names to server folder names:
```python
FOLDER_MAP = {
    "INBOX": "INBOX",
    "Sent_Items": "Sent",
    "Deleted_Items": "Trash",
    ...
}
```

### 📋 Usage

```bash
python3 mail-up.py                         # Upload all folders
python3 mail-up.py --folder INBOX          # Upload specific folder
python3 mail-up.py --folder INBOX --file YYYY-MM-DDTHH-mm-ss_123_123_read.eml  # Upload a single email(/tmp/emails_backup/INBOX)
python3 mail-up.py --list                  # List folders on the server
```

---

## 📦 Backup Folder Structure

Emails are stored as:
```
/tmp/emails_backup/
  └── INBOX/
        ├── YYYY-MM-DDTHH-mm-ss_123_read.eml
        └── YYYY-MM-DDTHH-mm-ss_124_unread.eml
```
