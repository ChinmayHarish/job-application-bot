import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class Tailor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in env")
        
        genai.configure(api_key=self.api_key)
        # Use explicit model name
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def tailor_resume(self, job_description, current_resume_latex):
        """
        Actually tailors the resume using Gemini.
        """
        prompt = f"""
        You are an expert Resume Strategist. 
        Your goal is to tailor the following LaTeX resume to match the Job Description (JD) perfectly.
        
        Job Description:
        ---
        {job_description}
        ---
        
        Base Resume (LaTeX):
        ---
        {current_resume_latex}
        ---
        
        Instructions:
        1. Extract 5-7 critical keywords/skills from the JD.
        2. subtly integrate these keywords into the Experience and Summary sections of the resume.
        3. Do NOT fabricate experience. Only rephrase or emphasize relevant accomplishments.
        4. Ensure the LaTeX remains valid and compilable.
        5. Output ONLY the modified LaTeX code. Nothing else.
        """
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                # Clean up markdown if AI includes it
                text = response.text.strip()
                if text.startswith("```latex"):
                    text = text[8:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                return text.strip()
            return current_resume_latex # Fallback to original if AI fails
        except Exception as e:
            print(f"Tailoring error: {e}")
            return current_resume_latex

    def extract_metadata(self, jd_text):
        """
        Extracts Company, Role, Job Type, Location, and Compensation from JD text using Gemini.
        Deduces portal based on content keywords.
        """
        prompt = f"""
        Extract the following details from this job description:
        1. Company Name
        2. Job Title (Role)
        3. Job Type (Full-time, Internship, Contract, etc.)
        4. Job Location
        5. Compensation (Salary/Range, if mentioned)
        
        If you can't find a specific detail, use 'Unknown' or 'Not Specified'.
        
        JD Text:
        ---
        {jd_text}
        ---
        
        Return JSON format: 
        {{
            "company": "...", 
            "role": "...", 
            "job_type": "...", 
            "location": "...", 
            "compensation": "..."
        }}
        Output ONLY the JSON.
        """
        # Deduce Portal (Simple keyword matching)
        portal = "Other"
        jd_lower = jd_text.lower()
        if "linkedin" in jd_lower: portal = "LinkedIn"
        elif "naukri" in jd_lower: portal = "Naukri"
        elif "wellfound" in jd_lower: portal = "Wellfound"
        elif "indeed" in jd_lower: portal = "Indeed"
        elif "lever" in jd_lower or "greenhouse" in jd_lower: portal = "Company Website"

        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                data = json.loads(response.text.strip().strip("```json").strip("```"))
                data["portal"] = portal # Add portal
                return data
            return {
                "company": "Unknown Company", "role": "Applicant", 
                "job_type": "Full-time", "location": "Remote", 
                "compensation": "Not Specified", "portal": portal
            }
        except Exception as e:
            print(f"Metadata extraction error: {e}")
            return {
                "company": "Unknown Company", "role": "Applicant", 
                "job_type": "Full-time", "location": "Remote", 
                "compensation": "Not Specified", "portal": portal
            }
