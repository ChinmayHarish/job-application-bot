import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

class Scraper:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in env")
        self.app = FirecrawlApp(api_key=self.api_key)

    def scrape_job(self, url):
        """
        Scrapes job description from a URL using Firecrawl.
        """
        # LinkedIn/Indeed often block simple scrapers, so we'll use Firecrawl's scraping logic.
        if "linkedin.com" in url or "indeed.com" in url:
            # For these, we might need to prompt the user to use a specialized browser tool
            # or use Firecrawl's stealth modes if available.
            return "LINKEDIN_MARKER: Please use browser subagent to scrape this page."

        try:
            # The library use .scrape() with direct kwargs
            response = self.app.scrape(url, only_main_content=True, formats=['markdown'])
            
            # Handle response (Dict or Object)
            if hasattr(response, 'markdown'):
                 return response.markdown
            elif isinstance(response, dict) and 'markdown' in response:
                return response['markdown']
            return ""
        except Exception as e:
            print(f"Scrape error: {e}")
            return ""
