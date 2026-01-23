"""
Tailor Agent - Handles resume customization.

This agent is responsible for:
1. Taking a JD and extracting keywords
2. Mapping skills to resume sections
3. Generating a tailored LaTeX resume
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Try Phidata imports
try:
    from phi.agent import Agent
    from phi.model.google import Gemini
    from phi.tools.file import FileTools
    PHIDATA_AVAILABLE = True
except ImportError:
    PHIDATA_AVAILABLE = False

# Fallback imports
from src.tailor import Tailor

_tailor = Tailor()

def tailor_resume(jd: str, metadata: dict) -> str:
    """Wrapper for the Tailor class's tailor_resume method."""
    return _tailor.tailor_resume(jd, "")

def extract_metadata(jd: str) -> dict:
    """Wrapper for the Tailor class's extract_metadata method."""
    return _tailor.extract_metadata(jd)


def create_tailor_agent() -> Optional["Agent"]:
    """Create a Phidata Tailor Agent with file manipulation tools."""
    if not PHIDATA_AVAILABLE:
        return None

    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        print("Warning: GOOGLE_API_KEY not set. Tailor agent limited.")
        return None

    agent = Agent(
        name="Tailor Agent",
        role="Expert Resume Strategist",
        model=Gemini(id="gemini-2.0-flash", api_key=google_key),
        tools=[FileTools()],
        instructions=[
            "You are an expert at tailoring resumes for specific job applications.",
            "When given a job description, extract the 5 most important skills.",
            "Then, rewrite the resume's experience section to highlight those skills.",
            "Never fabricate experience. Only emphasize existing skills.",
            "Output the final resume in valid LaTeX format."
        ],
        show_tool_calls=True,
        markdown=True
    )
    return agent


def tailor_for_job(jd_text: str, base_resume_path: str = "data/resume_base.tex", metadata: Optional[dict] = None) -> dict:
    """
    Main entry point for resume tailoring.
    Uses Phidata agent if available, otherwise falls back to existing tailor.
    """
    # Use agentic approach with Gemini Pro
    agent = create_tailor_agent()

    # Load base resume
    with open(base_resume_path, "r") as f:
        base_resume_content = f.read()

    if agent:
        try:
            prompt = f"""
            You are an expert Resume Strategist. 
            Tailor the following LaTeX resume to match the Job Description (JD) perfectly.
            
            Job Description:
            ---
            {jd_text}
            ---
            
            Base Resume (LaTeX):
            ---
            {base_resume_content}
            ---
            
            Instructions:
            - Focus on the Company and Role if provided.
            - Output ONLY the modified LaTeX code.
            """
            response = agent.run(prompt)
            latex = response.content
            
            # Metadata might be passed in or we extract it
            if not metadata:
                metadata = _tailor.extract_metadata(jd_text)
                
            return {
                "source": "phidata", 
                "latex": latex, 
                "metadata": metadata
            }
        except Exception as e:
            print(f"Tailor agent error: {e}. Falling back to core tailor.")
    
    # Fallback to core tailor (which now also uses AI)
    if not metadata:
        metadata = _tailor.extract_metadata(jd_text)
    latex = _tailor.tailor_resume(jd_text, base_resume_content)
    return {"source": "core_ai", "latex": latex, "metadata": metadata}


if __name__ == "__main__":
    test_jd = "We are looking for a Product Manager with SQL and Python skills."
    result = tailor_for_job(test_jd)
    print(result.get("source"))
