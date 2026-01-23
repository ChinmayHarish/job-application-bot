"""
Research Agent - Handles JD scraping and company analysis.

This agent is responsible for:
1. Scraping job descriptions from URLs (Naukri, LinkedIn, etc.)
2. Extracting structured metadata (Company, Role, Requirements)
3. Optionally researching company culture for personalization
"""
import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Try Phidata imports, fallback to simple function if not available
try:
    from phi.agent import Agent
    from phi.model.google import Gemini
    from phi.tools.firecrawl import FirecrawlTools
    PHIDATA_AVAILABLE = True
except ImportError:
    PHIDATA_AVAILABLE = False
    print("Phidata not installed. Using fallback scraper.")

# Fallback: Use existing scraper logic
from src.scraper import Scraper

_scraper = Scraper()

def scrape_job_description(url: str) -> str:
    """Wrapper for the Scraper class's scrape_job method."""
    return _scraper.scrape_job(url)


def create_research_agent() -> Optional["Agent"]:
    """Create a Phidata Research Agent with web scraping tools."""
    if not PHIDATA_AVAILABLE:
        return None
    
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_key:
        print("Warning: GOOGLE_API_KEY not set. Research agent limited.")
        return None

    agent = Agent(
        name="Research Agent",
        role="Senior Job Market Researcher",
        model=Gemini(id="gemini-2.0-flash", api_key=google_key),
        tools=[FirecrawlTools(api_key=firecrawl_key)] if firecrawl_key else [],
        instructions=[
            "You are an expert at extracting job details from career pages.",
            "Always extract: Company Name, Role Title, Location, Key Skills, Description.",
            "If a website is blocked, try to find alternative sources for the job.",
        ],
        show_tool_calls=True,
        markdown=True
    )
    return agent


def research_job(url: str) -> dict:
    """
    Main entry point for job research.
    Uses Phidata agent if available, otherwise falls back to Firecrawl.
    Checks for pre-scraped metadata first.
    """
    # Check for pre-scraped metadata
    if os.path.exists("data/metadata_batch.json"):
        try:
            with open("data/metadata_batch.json", "r") as f:
                metadata_list = json.load(f)
                for item in metadata_list:
                    if item["url"] == url:
                        print(f"✨ Found pre-scraped data for {url}")
                        content = f"Company: {item.get('company_name')}\nRole: {item.get('job_title')}\nDescription: {item.get('job_description_summary')}"
                        return {
                            "source": "metadata_cache", 
                            "content": content,
                            "metadata": {
                                "company": item.get("company_name"),
                                "role": item.get("job_title")
                            }
                        }
        except Exception as e:
            print(f"Metadata cache read error: {e}")

    # Use agentic approach with Gemini Pro
    agent = create_research_agent()
    
    if agent:
        try:
            # If LinkedIn, we might need to handle it differently 
            # (e.g., providing a prompt that acknowledges LinkedIn's structure)
            prompt = f"Scrape and extract all details from this job posting: {url}. "
            if "linkedin.com" in url:
                prompt += "Focus on extracting Company Name, Role, and Job Description keywords even if the full text is tricky to scrape."
            
            response = agent.run(prompt)
            content = response.content
            
            # Use the fixed extract_metadata from Tailor to get structured fields
            metadata = _tailor.extract_metadata(content)
            
            return {
                "source": "phidata", 
                "content": content,
                "metadata": metadata
            }
        except Exception as e:
            print(f"Agent error: {e}. Falling back to simple scraper.")
    
    # Fallback to existing scraper
    jd_text = scrape_job_description(url)
    metadata = _tailor.extract_metadata(jd_text)
    return {"source": "firecrawl", "content": jd_text, "metadata": metadata}


if __name__ == "__main__":
    # Quick test
    test_url = "https://www.naukri.com/job-listings-product-manager-test"
    result = research_job(test_url)
    print(result)
