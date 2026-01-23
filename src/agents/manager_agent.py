"""
Manager Agent - Orchestrates the multi-agent workflow.

This is the "brain" of the system. It:
1. Receives a job URL
2. Delegates to Research Agent -> Tailor Agent -> Applier Agent
3. Handles errors and retries
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Try Phidata imports
try:
    from phi.agent import Agent
    from phi.model.google import Gemini
    PHIDATA_AVAILABLE = True
except ImportError:
    PHIDATA_AVAILABLE = False

# Import our agents
from src.agents.research_agent import research_job
from src.agents.tailor_agent import tailor_for_job
from src.agents.applier_agent import apply_and_log
from src.renderer import Renderer
from src.tracker import Tracker

from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize instances
_renderer = Renderer()
_tracker = Tracker(
    sheet_id=os.getenv("GOOGLE_SHEET_ID"),
    drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID")
)

def render_pdf(latex_content, company, output_dir):
    """Wrapper for Renderer class."""
    return _renderer.render_resume(latex_content, f"Chinmay Harish_{company}.pdf", output_pdf_dir=output_dir)

def upload_to_drive(pdf_path):
    """Wrapper for Tracker's upload method."""
    return _tracker.upload_resume(pdf_path, os.path.basename(pdf_path))


def create_manager_agent() -> Optional["Agent"]:
    """Create a Phidata Manager Agent for orchestration."""
    if not PHIDATA_AVAILABLE:
        return None

    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        return None

    agent = Agent(
        name="Manager Agent",
        role="Job Application Orchestrator",
        model=Gemini(id="gemini-2.0-flash", api_key=google_key),
        instructions=[
            "You are the orchestrator of a job application system.",
            "When given a job URL, you must coordinate these steps:",
            "1. Research: Scrape job details",
            "2. Tailor: Customize resume for the job",
            "3. Apply: Submit application and log status",
            "If any step fails, attempt recovery or escalate to the user."
        ],
        show_tool_calls=True,
        markdown=True
    )
    return agent


def run_pipeline(jd_text: str, is_url: bool = False) -> dict:
    """
    Execute the simplified job application pipeline.
    Input: Can be a Job URL or a raw Job Description.
    """
    results = {
        "status": "started",
        "steps": {}
    }

    # Step 1: Research / Metadata Extraction
    print(f"\n🔍 Step 1: Processing Job Content...")
    try:
        if is_url:
            research_result = research_job(jd_text)
            content = research_result.get("content", "")
            metadata = research_result.get("metadata", {})
        else:
            # Direct JD input
            content = jd_text
            from src.agents.tailor_agent import _tailor
            metadata = _tailor.extract_metadata(content)
        
        results["steps"]["research"] = {"status": "success", "metadata": metadata}
    except Exception as e:
        results["steps"]["research"] = {"status": "failed", "error": str(e)}
        results["status"] = "failed"
        return results

    # Step 2: Tailoring
    print("📝 Step 2: Tailoring resume (ATS keywords, no fabrication)...")
    try:
        from src.agents.tailor_agent import tailor_for_job
        tailor_result = tailor_for_job(content, metadata=metadata)
        latex_content = tailor_result.get("latex", "")
        results["steps"]["tailor"] = {"status": "success"}
    except Exception as e:
        results["steps"]["tailor"] = {"status": "failed", "error": str(e)}
        results["status"] = "failed"
        return results

    # Step 3: Render PDF
    now = datetime.now()
    date_str = now.strftime("%d %b %Y") # e.g., 23 Jan 2026
    
    company = metadata.get("company", "Unknown Company")
    safe_company = "".join([c for c in company if c.isalnum() or c in (' ', '_')]).strip()
    
    output_dir = os.path.expanduser(f"~/Desktop/job applications/{date_str}")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📄 Step 3: Rendering PDF to {output_dir}...")
    try:
        # Standard naming: Chinmay Harish_[Company Name].pdf
        pdf_path = render_pdf(latex_content, safe_company, output_dir)
        results["steps"]["render"] = {"status": "success", "path": pdf_path}
    except Exception as e:
        results["steps"]["render"] = {"status": "failed", "error": str(e)}
        results["status"] = "failed"
        return results

    # Step 4: Upload to Drive (Synchronized Folder Logic)
    print("☁️ Step 4: Uploading to Drive (Syncing folder structure)...")
    try:
        # We pass date_str to ensure subfolder mirroring: job applications/[Date]/
        drive_link = _tracker.upload_resume(pdf_path, os.path.basename(pdf_path), date_folder_name=date_str)
        results["steps"]["upload"] = {"status": "success", "link": drive_link}
    except Exception as e:
        results["steps"]["upload"] = {"status": "failed", "error": str(e)}
        # Non-fatal

    # Step 5: Log to Golden Tracking Sheet
    print("📊 Step 5: Logging to Golden Tracking Sheet...")
    try:
        # Schema: [Date, Role, Portal, Job Type, Resume Link, Location, Compensation, Status]
        _tracker.log_application(
            date=date_str,
            company=company,
            role=metadata.get("role", "Applicant"),
            portal=metadata.get("portal", "Other"),
            job_type=metadata.get("job_type", "Full-time"),
            resume_link=drive_link,
            location=metadata.get("location", "Unknown"),
            compensation=metadata.get("compensation", "Not Specified"),
            status="Applied"
        )
    except Exception as e:
        print(f"Logging error: {e}")

    results["status"] = "completed"
    results["metadata"] = metadata
    print(f"\n✅ Resume prepared for {company}")
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
        is_url = input_data.startswith("http")
        result = run_pipeline(input_data, is_url=is_url)
        # Final summary for the user
        if result["status"] == "completed":
            print(f"\n🚀 Success!")
            print(f"📁 Local PDF: {result['steps']['render'].get('path')}")
            print(f"🔗 Drive Link: {result['steps']['upload'].get('link')}")
    else:
        print("Usage: python src/agents/manager_agent.py \"<JOB_URL_OR_JD_TEXT>\"")
