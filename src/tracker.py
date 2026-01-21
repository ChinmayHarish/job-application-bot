import os
import csv
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class Tracker:
    def __init__(self, credentials_path="credentials.json", sheet_id=None, drive_folder_id=None):
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.drive_folder_id = drive_folder_id
        
        self.use_google = False
        self.creds = None
        self.client = None
        self.sheet = None
        self.drive_service = None

        if os.path.exists(self.credentials_path) and sheet_id:
            try:
                self.authenticate()
                self.use_google = True
                print("Connected to Google Services.")
            except Exception as e:
                print(f"Google Auth failed: {e}. Switching to Local Mode.")
                self.use_google = False
        else:
            print("Credentials not found. Using Local CSV Mode.")
            self.use_google = False
            
        # Ensure output directory for local CSV exists if in local mode
        if not self.use_google:
            if not os.path.exists("output"):
                os.makedirs("output")
            self.local_csv_path = "output/applications.csv"
            if not os.path.exists(self.local_csv_path):
                with open(self.local_csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Date", "Company", "Role", "Job URL", "Resume Path", "Status"])

    def authenticate(self):
        # Prefer OAuth 2.0 User Token (token.json) if available
        if os.path.exists('token.json'):
            from google.oauth2.credentials import Credentials as UserCredentials
            self.creds = UserCredentials.from_authorized_user_file(token_file='token.json', scopes=SCOPES)
            print("Using OAuth 2.0 User Authentication.")
        else:
            self.creds = Credentials.from_service_account_file(self.credentials_path, scopes=SCOPES)
            print("Using Service Account Authentication.")
            
        self.client = gspread.authorize(self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheet = self.client.open_by_key(self.sheet_id).sheet1

    def upload_resume(self, file_path, file_name):
        if not self.use_google:
            # Local mode: just return absolute path
            return os.path.abspath(file_path)

        if not self.drive_service:
            return None

        file_metadata = {
            'name': file_name,
            'parents': [self.drive_folder_id] if self.drive_folder_id else []
        }
        media = MediaFileUpload(file_path, mimetype='application/pdf')
        
        try:
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink',
                supportsAllDrives=True
            ).execute()
            
            # Make it shareable
            self.drive_service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'},
                supportsAllDrives=True
            ).execute()
            
            return file.get('webViewLink')
        except Exception as e:
            # If Drive fails (e.g. Quota), return a friendly local status
            return "Local Copy Only (Drive Quota Exceeded)"

    def log_application(self, date, company, role, job_url, resume_link, status="Applied"):
        if self.use_google and self.sheet:
            row = [date, company, role, job_url, resume_link, status]
            try:
                self.sheet.append_row(row)
                print(f"Logged to Sheet: {company}")
            except Exception as e:
                print(f"Error logging to sheet: {e}")
        else:
            # Local CSV Logging
            with open(self.local_csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([date, company, role, job_url, resume_link, status])
            print(f"Logged to CSV: {company}")
