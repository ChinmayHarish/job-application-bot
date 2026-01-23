"""
Applier Agent - Handles browser automation & logging.

This agent is responsible for:
1. Navigating to job portals (Naukri, LinkedIn, etc.)
2. Filling out application forms
3. Logging application status to Google Sheets
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Try Phidata imports
try:
    from phi.agent import Agent
    from phi.model.openai import OpenAI
    PHIDATA_AVAILABLE = True
except ImportError:
    PHIDATA_AVAILABLE = False

# Fallback imports
from src.applier import Applier

_applier = Applier()

def apply_to_job(url: str) -> dict:
    """Wrapper for the Applier class's apply method."""
    result = _applier.apply(url, "")
    return {"status": result}
from src.tracker import Tracker
import os
from dotenv import load_dotenv

load_dotenv()

_tracker = Tracker(
    sheet_id=os.getenv("GOOGLE_SHEET_ID"),
    drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID")
)

def log_to_sheet(date, company, role, url, resume_link, status):
    """Wrapper for the Tracker class's log_application method."""
    _tracker.log_application(date, company, role, url, resume_link, status)
    return {"status": "logged"}


def create_applier_agent() -> Optional["Agent"]:
    """Create a Phidata Applier Agent for browser tasks."""
    if not PHIDATA_AVAILABLE:
        return None

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        return None

    # NOTE: Full browser tools (Playwright MCP) would be added here.
    # For now, we wrap our existing functions as "tools".
    agent = Agent(
        name="Applier Agent",
        role="Job Application Specialist",
        model=OpenAI(id="gpt-4o-mini", api_key=openai_key),
        instructions=[
            "You are an expert at applying to jobs on various portals.",
            "When given a job URL, determine the platform (Naukri, LinkedIn, etc.).",
            "Execute the appropriate application steps for that platform.",
            "Log the result (Applied/Failed/Pending) to the tracking sheet."
        ],
        show_tool_calls=True,
        markdown=True
    )
    return agent


def apply_and_log(job_url: str, pdf_path: str, metadata: dict) -> dict:
    """
    Main entry point for job application.
    Combines browser automation with sheet logging.
    """
    # Use existing applier logic (already works well)
    apply_result = apply_to_job(job_url)

    # Log to Google Sheet
    log_result = log_to_sheet(
        date=metadata.get("date", ""),
        company=metadata.get("company", "Unknown"),
        role=metadata.get("role", "Applicant"),
        url=job_url,
        resume_link=metadata.get("resume_link", ""),
        status=apply_result.get("status", "Initiated")
    )

    return {
        "apply_result": apply_result,
        "log_result": log_result
    }


if __name__ == "__main__":
    print("Applier Agent module loaded.")
