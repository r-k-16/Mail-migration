#!/usr/bin/python3

"""
Usage: python3 mail-up.py --> upload all folders
        --folder INBOX --> upload only specific folder (INBOX - local folder name)
        --file email-backup-file.eml --> combine with folder to upload only specific file
        --list --> Only display folders in the server
"""

import os
import sys
import argparse
from datetime import datetime
from imapclient import IMAPClient

# Configuration
DEST_HOST = 'host.example.com' # New Server details
DEST_USER = 'test@example.com'
DEST_PASS = 'hBrAHiHqKw{j'

EMAILS_PATH = '/tmp/emails_backup'

# Folder mapping: Downloaded mail folders name → new server folder
# If you're not sure about the new server folder names, then create a test mail 
#and update the login details and run the script. You will the server folders.

FOLDER_MAP = {
    "Deleted_Items": "Trash",
    "Drafts": "Drafts",
    "INBOX": "INBOX",
    "Junk_E-mail": "Junk",
    "Sent_Items": "Sent",
}

def extract_date_from_filename(filename):
    try:
        timestamp_str = filename.split('_')[0]
        return datetime.strptime(timestamp_str, '%Y-%m-%dT%H-%M-%S')
    except Exception as e:
        print(f"⚠️ Could not extract date from '{filename}': {e}")
        return None

def detect_read_status(filename):
    if '_read.eml' in filename:
        return True
    elif '_unread.eml' in filename:
        return False
    return None

def upload_eml_file(dest, eml_path, dest_folder, file_count, file_index, total_files):
    with open(eml_path, 'rb') as f:
        eml_data = f.read()

    filename = os.path.basename(eml_path)
    msg_time = extract_date_from_filename(filename) or datetime.now()
    is_read = detect_read_status(filename)
    flags = [b'\\Seen'] if is_read else []

    try:
        dest.append(dest_folder, eml_data, flags=flags, msg_time=msg_time)
        file_count['uploaded'] += 1
        print(f"✅ [{file_index+1}/{total_files}] Saved: {filename} → {dest_folder} ({'read' if is_read else 'unread'})")
    except Exception as e:
        print(f"❌ Upload failed for {filename}: {e}")

def upload_folder(dest, local_folder, dest_folder, file_count):
    folder_path = os.path.join(EMAILS_PATH, local_folder)
    if not os.path.isdir(folder_path):
        print(f"⛔ Folder not found: {folder_path}")
        return

    print(f"\n📁 Uploading folder: {local_folder} → {dest_folder}")
    dest.select_folder(dest_folder)

    total_files = len([f for f in os.listdir(folder_path) if f.endswith('.eml')])
    if total_files == 0:
        print("  (No emails to upload)")
        return 0

    uploaded = 0
    for index, f in enumerate(os.listdir(folder_path)):
        if f.endswith('.eml'):
            upload_eml_file(dest, os.path.join(folder_path, f), dest_folder, file_count, index, total_files)
            uploaded += 1

    print(f"  📦 {uploaded} emails uploaded to '{dest_folder}'")
    return uploaded

def validate_folders(local_folders, server_folders):
    matched = []
    unmatched = []

    print("\n🔍 Validating folders:")

    for folder in local_folders:
        mapped = FOLDER_MAP.get(folder)

        if not mapped:
            print(f" ❌ No mapping for local folder: {folder}")
            unmatched.append(folder)

        elif mapped not in server_folders:
            print(f" ❌ Server folder '{mapped}' for '{folder}' not found on server.")
            unmatched.append(folder)
        else:
            print(f"✅ Matched: {folder} → {mapped}")
            matched.append((folder, mapped))

    if unmatched:
        print("\n❌ Upload aborted due to unmatched folders.")
        for uf in unmatched_folders:
            print(f"  - {uf}")
        sys.exit(1)
    return matched

def main(folder=None, filename=None, list_only=False):
    total_uploaded = 0  # Initialize the total uploaded count
    folder_uploaded_count = {}  # Dictionary to keep track of uploads per folder

    with IMAPClient(DEST_HOST, ssl=True) as dest:
        dest.login(DEST_USER, DEST_PASS)
        server_folders = [f[2] if isinstance(f[2], str) else f[2].decode() for f in dest.list_folders()]

        # List all server folders
        print("\n📂 Server folders:")
        for f in server_folders:
            print(f" - {f}")

        if list_only:
            return

        print("\n⚠️  If the mail already exists, duplicate mail will be created")

        if folder:
            mapped = FOLDER_MAP.get(folder)
            if not mapped or mapped not in server_folders:
                print(f"❌ Folder '{folder}' not mapped or missing on server.")
                sys.exit(1)

            if filename:
                eml_path = os.path.join(EMAILS_PATH, folder, filename)
                if not os.path.isfile(eml_path):
                    print(f"❌ File not found: {eml_path}")
                    sys.exit(1)
                dest.select_folder(mapped)
                upload_eml_file(dest, eml_path, mapped, {'uploaded': 0}, 0, 1)
                total_uploaded += 1
            else:
                folder_upload_count = upload_folder(dest, folder, mapped, {'uploaded': 0})
                total_uploaded += folder_upload_count
        else:
            all_local_folders = [f for f in os.listdir(EMAILS_PATH)
                                 if os.path.isdir(os.path.join(EMAILS_PATH, f))]
            matched = validate_folders(all_local_folders, server_folders)
            for local_folder, dest_folder in matched:
                folder_upload_count = upload_folder(dest, local_folder, dest_folder, {'uploaded': 0})
                folder_uploaded_count[local_folder] = folder_upload_count
                total_uploaded += folder_upload_count

        # Print the total uploaded summary
        print(f"\n✅ Upload complete. Total emails uploaded: {total_uploaded}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', help='Folder to upload')
    parser.add_argument('--file', help='Specific file to upload')
    parser.add_argument('--list', action='store_true', help='List server folders only')

    args = parser.parse_args()
    main(folder=args.folder, filename=args.file, list_only=args.list)
