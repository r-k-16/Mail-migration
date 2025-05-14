#!/usr/bin/python3

"""
Usage: python3 mail-down.py --> Download all folders
        --folder INBOX --> Download only specific folder (INBOX - local folder name)
        --list --> Only display folders in the server
"""

import os
import re
import sys
import argparse
from datetime import datetime
from imapclient import IMAPClient

# --- Configuration ---
SOURCE_HOST = 'example.com' # Old server host name
SOURCE_USER = 'test@example.com'
SOURCE_PASS = 'hBrAHiHqKw{j'

EMAILS_PATH = '/tmp/emails_backup'
os.makedirs(EMAILS_PATH, exist_ok=True)

def safe_folder_name(name):
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)

def download_emails(folder_filter=None):
    BATCH_SIZE = 10  # Customize batch size as needed

    with IMAPClient(SOURCE_HOST, ssl=True) as source:
        source.login(SOURCE_USER, SOURCE_PASS)
        folders = source.list_folders()

        all_folders = [f[2].decode() if isinstance(f[2], bytes) else f[2] for f in folders]

        print("\n📂 Available folders on server:")
        for f in all_folders:
            print(f"  - {f}")

        folders_to_process = [folder_filter] if folder_filter else all_folders
        total_downloaded = 0

        for folder_name in folders_to_process:
            if folder_name not in all_folders:
                print(f"\n⛔ Folder '{folder_name}' not found on server. Skipping.")
                continue

            print(f"\n📥 Downloading folder: {folder_name}")
            try:
                source.select_folder(folder_name, readonly=True)
                uids = source.search('ALL')
                if not uids:
                    print("  (No messages)")
                    continue

                safe_folder = safe_folder_name(folder_name)
                folder_path = os.path.join(EMAILS_PATH, safe_folder)
                os.makedirs(folder_path, exist_ok=True)

                total = len(uids)
                print(f"  ✉️ {total} messages found. Downloading in batches of {BATCH_SIZE}...")

                downloaded = 0
                for batch_start in range(0, total, BATCH_SIZE):
                    batch_uids = uids[batch_start:batch_start + BATCH_SIZE]

                    for idx, uid in enumerate(batch_uids, start=batch_start + 1):
                        try:
                            msg_data = source.fetch([uid], ['RFC822', 'INTERNALDATE', 'FLAGS'])
                            data = msg_data[uid]

                            eml = data[b'RFC822']
                            msg_time = data[b'INTERNALDATE']
                            flags = data.get(b'FLAGS', [])

                            timestamp_str = msg_time.strftime('%Y-%m-%dT%H-%M-%S')
                            status = 'read' if b'\\Seen' in flags else 'unread'
                            file_name = f"{timestamp_str}_{uid}_{status}.eml"
                            file_path = os.path.join(folder_path, file_name)

                            if os.path.exists(file_path):
                                print(f"  ⚠️ [{idx}/{total}] Skipped (exists): {file_name}")
                                continue

                            with open(file_path, 'wb') as f:
                                f.write(eml)

                            print(f"  ✅ [{idx}/{total}] Saved: {file_name}")
                            downloaded += 1

                        except Exception as e:
                            print(f"  ❌ [{idx}/{total}] Failed to download UID {uid}: {e}")

                print(f"  📦 Done: {downloaded} new emails saved to '{safe_folder}'")
                total_downloaded += downloaded

            except Exception as e:
                print(f"  ❌ Error downloading '{folder_name}': {e}")

        print(f"\n✅ Download complete. Total new emails saved: {total_downloaded}")

def list_folders():
    with IMAPClient(SOURCE_HOST, ssl=True) as source:
        source.login(SOURCE_USER, SOURCE_PASS)
        folders = source.list_folders()
        all_folders = [f[2].decode() if isinstance(f[2], bytes) else f[2] for f in folders]
        print("\n📂 Available folders on server:")
        for f in all_folders:
            print(f"  - {f}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download emails from IMAP server.')
    parser.add_argument('--folder', help='Download a specific folder only')
    parser.add_argument('--list', action='store_true', help='List folders on the server and exit')

    args = parser.parse_args()

    if args.list:
        list_folders()
        sys.exit(0)

    download_emails(folder_filter=args.folder)
