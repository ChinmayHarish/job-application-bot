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
            self.creds = UserCredentials.from_authorized_user_file('token.json', SCOPES)
            print("Using OAuth 2.0 User Authentication.")
        else:
            self.creds = Credentials.from_service_account_file(self.credentials_path, scopes=SCOPES)
            print("Using Service Account Authentication.")
            
        self.client = gspread.authorize(self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheet = self.client.open_by_key(self.sheet_id).sheet1

    def get_or_create_subfolder(self, parent_id, folder_name):
        """Finds or creates a subfolder in Google Drive."""
        if not self.use_google or not self.drive_service:
            return None
        
        query = f"name = '{folder_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        try:
            results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            if files:
                return files[0]['id']
            
            # Create if not found
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
            print(f"📁 Created Drive Folder: {folder_name}")
            return folder.get('id')
        except Exception as e:
            print(f"Error managing subfolder '{folder_name}': {e}")
            return parent_id

    def upload_file(self, file_path, file_name, folder_id=None, make_shareable=True):
        """
        Generic file upload to Google Drive.
        :param folder_id: Optional Drive Folder ID. Defaults to self.drive_folder_id.
        :param make_shareable: Whether to set permissions to 'anyone with link'.
        """
        if not self.use_google:
            return os.path.abspath(file_path)

        if not self.drive_service:
            return None

        target_folder = folder_id if folder_id else self.drive_folder_id
        
        file_metadata = {
            'name': file_name,
            'parents': [target_folder] if target_folder else []
        }
        
        # Mimetype detection (basic)
        mimetype = 'application/pdf'
        if file_path.endswith('.tex'): mimetype = 'text/plain'
        elif file_path.endswith('.txt'): mimetype = 'text/plain'
        
        media = MediaFileUpload(file_path, mimetype=mimetype)
        
        try:
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink',
                supportsAllDrives=True
            ).execute()
            
            if make_shareable:
                self.drive_service.permissions().create(
                    fileId=file.get('id'),
                    body={'type': 'anyone', 'role': 'reader'},
                    supportsAllDrives=True
                ).execute()
            
            return file.get('webViewLink')
        except Exception as e:
            print(f"Drive Upload Error: {e}")
            return "Local Copy Only (Upload Failed)"

    def upload_resume(self, file_path, file_name, date_folder_name=None):
        """Legacy wrapper with optional date-based subfolder support."""
        target_folder = self.drive_folder_id
        if date_folder_name:
            target_folder = self.get_or_create_subfolder(self.drive_folder_id, date_folder_name)
            
        return self.upload_file(file_path, file_name, folder_id=target_folder, make_shareable=True)

    def log_application(self, date, company, role, portal, job_type, resume_link, location, compensation, status="Applied"):
        """Logs application details using the new 7+ column schema."""
        if self.use_google and self.sheet:
            # Schema: [Date, Job Role, Portal, Job Type, Resume Link, Location, Compensation, Status]
            row = [date, role, portal, job_type, resume_link, location, compensation, status]
            try:
                self.sheet.append_row(row)
                print(f"Logged to Sheet: {company} ({portal})")
            except Exception as e:
                print(f"Error logging to sheet: {e}")
        else:
            # Local CSV Logging
            if not hasattr(self, 'local_csv_path'):
                self.local_csv_path = "output/applications.csv"
            
            with open(self.local_csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                # Ensure header matches if file is new (handled in __init__ but just in case)
                writer.writerow([date, role, portal, job_type, resume_link, location, compensation, status])
            print(f"Logged to CSV: {company}")

    def create_golden_sheet(self, spreadsheet_name="Golden Tracking Sheet"):
        """Creates a new spreadsheet with the required Golden Schema."""
        if not self.use_google:
            return None
        
        try:
            sh = self.client.create(spreadsheet_name)
            self.sheet_id = sh.id
            self.sheet = sh.sheet1
            headers = ["Date", "Job Role", "Portal", "Job Type", "Resume Link", "Job Location", "Compensation", "Status"]
            self.sheet.insert_row(headers, 1)
            print(f"✨ Created NEW Golden Sheet: {sh.url}")
            return sh.id, sh.url
        except Exception as e:
            print(f"Error creating Golden Sheet: {e}")
            return None, None
