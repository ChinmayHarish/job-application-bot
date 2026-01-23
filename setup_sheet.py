import os
from src.tracker import Tracker
from dotenv import load_dotenv

load_dotenv()

def setup():
    print("🚀 Initializing Golden Tracking Infrastructure...")
    
    # Initialize tracker with existing IDs to get the service connection
    tracker = Tracker(
        sheet_id=os.getenv("GOOGLE_SHEET_ID"),
        drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    )
    
    if not tracker.use_google:
        print("❌ Google Authentication failed. Check token.json or credentials.json.")
        return

    # 1. Create Root Folder in Drive
    print("\n📁 Creating 'job applications' root folder in Drive...")
    file_metadata = {
        'name': 'job applications',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = tracker.drive_service.files().create(body=file_metadata, fields='id').execute()
    folder_id = folder.get('id')
    print(f"✅ Created Folder ID: {folder_id}")

    # 2. Create Golden Tracking Sheet
    print("\n📊 Creating 'Golden Tracking Sheet'...")
    # Initialize a temporary tracker with the NEW folder ID to create the sheet
    tracker.drive_folder_id = folder_id 
    sheet_id, sheet_url = tracker.create_golden_sheet("Golden Tracking Sheet")
    
    if sheet_id:
        print(f"✅ Created Sheet ID: {sheet_id}")
        print(f"🔗 View Sheet: {sheet_url}")
        
        print("\n" + "="*50)
        print("⚠️ ACTION REQUIRED: Update your .env file with these values:")
        print(f"GOOGLE_SHEET_ID={sheet_id}")
        print(f"GOOGLE_DRIVE_FOLDER_ID={folder_id}")
        print("="*50)
    else:
        print("❌ Failed to create Golden Sheet.")

if __name__ == "__main__":
    setup()
