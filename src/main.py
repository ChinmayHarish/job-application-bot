import argparse
import os
from datetime import datetime
from scraper import Scraper
from tailor import Tailor
from renderer import Renderer
from tracker import Tracker
from applier import Applier
from utils import extract_jobs

def process_job(url, role_override=None, company_override=None, resume_path="data/resume_base.tex"):
    print(f"\n--- Processing: {url} ---")
    
    # 1. Scrape
    print("Scraping Job Description...")
    scraper = Scraper()
    jd_text = scraper.scrape_job(url)
    
    # MOCK REMOVED - Using Real Scraper
    
    if not jd_text:
        print("Failed to scrape JD.")
        return

    # Metadata Extraction (Improved)
    print("Extracting Metadata...")
    tailor = Tailor()
    meta = tailor.extract_metadata(jd_text)
    
    company_name = company_override or meta.get('company', "Unknown_Company")
    role_name = role_override or meta.get('role', "Applicant")
    
    # 2. Tailor
    print("Tailoring Resume...")
    
    with open(resume_path, 'r') as f:
        base_resume = f.read()
        
    tailored_content = tailor.tailor_resume(jd_text, base_resume)
    
    # 3. Render
    print("Rendering PDF...")
    renderer = Renderer()
    
    # Create filename-friendly strings
    # Naming convention: "Chinmay Harish - Company Name.pdf"
    # Filter safe characters for filename
    safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '_', '-')).strip()
    output_filename = f"Chinmay Harish - {safe_company}.pdf"
    
    # Desktop Output Directory
    # Format: [Day]st/nd/rd/th Jan (e.g., 21st Jan)
    now_dt = datetime.now()
    day = now_dt.day
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    date_folder = now_dt.strftime(f"{day}{suffix} %b") # e.g., "21st Jan"
    
    desktop_output = os.path.expanduser(f"~/Desktop/Application/{date_folder}")
    if not os.path.exists(desktop_output):
        os.makedirs(desktop_output)
    
    pdf_path = renderer.render_resume(tailored_content, filename=os.path.join(desktop_output, output_filename))
    
    # 4. Upload & Log
    # 4. Upload & Log
    from dotenv import load_dotenv
    load_dotenv()
    tracker = Tracker(sheet_id=os.getenv("GOOGLE_SHEET_ID"), drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID"))
    if pdf_path:
        if tracker.use_google:
            print("Uploading to Drive...")
        else:
            print("Saving locally...")
            
        link = tracker.upload_resume(pdf_path, output_filename)
        
        if link:
            print(f"Resume Ready: {link}")
            tracker.log_application(
                date=datetime.now().strftime("%d %b %Y"),
                company=company_name,
                role=role_name,
                job_url=url,
                resume_link=link,
                status="Applied (Bot)"
            )
            
            # 5. LIVE APPLICATION (Bot)
            applier = Applier()
            print("Starting Live Application Bot...")
            # We don't call applier.apply as a blocking python call here, 
            # instead we'll handle the browser_subagent interaction in the next step.
            # For now, let's keep it as a placeholder.
            result = applier.apply(url, pdf_path)
            print(f"Application Result: {result}")
            
    else:
        print("PDF Generation Failed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Single Job URL to process")
    parser.add_argument("--file", help="File containing list of jobs")
    parser.add_argument("--resume", default="data/resume_base.tex", help="Path to base resume LaTeX file")
    parser.add_argument("--start", type=int, default=1, help="Start index (1-based)")
    parser.add_argument("--end", type=int, default=None, help="End index (inclusive)")
    
    args = parser.parse_args()
    
    if args.url:
        process_job(args.url, resume_path=args.resume)
    elif args.file:
        with open(args.file, 'r') as f:
            raw_text = f.read()
            
        all_jobs = extract_jobs(raw_text)
        
        start_idx = max(0, args.start - 1)
        end_idx = args.end if args.end is not None else len(all_jobs)
        jobs = all_jobs[start_idx:end_idx]
        
        print(f"Found {len(all_jobs)} jobs. Processing indices {args.start} to {end_idx if args.end else len(all_jobs)}.")
        
        for job in jobs:
            # job is a dict: {'company':..., 'role':..., 'url':...}
            role = job.get('role')
            link = job.get('url')
            company = job.get('company')
            
            if link:
                process_job(link, role_override=role, company_override=company, resume_path=args.resume)
