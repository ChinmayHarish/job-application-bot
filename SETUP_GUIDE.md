# Setup Guide: Job Application Workspace

This guide is for initializing a new **Anti-Gravity Workspace** (e.g., "job application") and connecting it to this automation engine.

## 1. Environment Setup
Clone your private repository and install dependencies:
```bash
git clone <YOUR_PRIVATE_REPO_URL>
pip install -r requirements.txt
# Ensure tectonic is installed: brew install tectonic
```

## 2. Authentication
Ensure the following files are in the root directory (never commit these!):
- `.env`: Contains `GOOGLE_API_KEY`, `GOOGLE_SHEET_ID`, etc.
- `token.json`: Your authenticated Google OAuth 2.0 token.

## 3. Running a "Single JD" Job
Whenever you find a job description you like, simply pass the text to the `manager_agent.py`:

```bash
export PYTHONPATH=.
python3 src/agents/manager_agent.py "We are looking for a Senior Product Manager..."
```

## 4. Where are my files?
- **Local PDF**: `~/Desktop/job applications/[Today's Date]/`
- **Link**: The terminal will output a Google Drive link for easy access/sharing.
- **Tracker**: Your Google Sheet will automatically log the new entry.

---
**Agent Instruction**: 
When this workspace is opened, read the `.antigravity/` folder to resume full context.
