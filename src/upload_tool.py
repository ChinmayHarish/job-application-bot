import os
import sys
from src.tracker import Tracker
from dotenv import load_dotenv

load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/upload_tool.py <FILE_PATH> [FOLDER_ID] [MAKE_SHAREABLE:true/false]")
        return

    file_path = sys.argv[1]
    folder_id = sys.argv[2] if len(sys.argv) > 2 else None
    make_shareable = sys.argv[3].lower() != 'false' if len(sys.argv) > 3 else True

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    tracker = Tracker(
        sheet_id=os.getenv("GOOGLE_SHEET_ID"),
        drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    )

    print(f"📤 Uploading {os.path.basename(file_path)}...")
    link = tracker.upload_file(file_path, os.path.basename(file_path), folder_id=folder_id, make_shareable=make_shareable)
    
    if link and "Local Copy" not in link:
        print(f"✅ Success!")
        print(f"🔗 Link: {link}")
    else:
        print(f"❌ Upload Failed. Check your Drive API quota or credentials.")

if __name__ == "__main__":
    main()
