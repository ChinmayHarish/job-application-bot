from src.tracker import Tracker
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("Checking Sheet...")
    tracker = Tracker(sheet_id=os.getenv("GOOGLE_SHEET_ID"))
    
    if tracker.use_google:
        print("Auth Success. Fetching rows...")
        rows = tracker.sheet.get_all_values()
        print(f"Total Rows: {len(rows)}")
        if len(rows) > 0:
            print(f"Last Row: {rows[-1]}")
    else:
        print("Tracker is in Local Mode (Auth failed?)")
except Exception as e:
    print(f"Check failed: {e}")
