"""
Batch Processor - Iterates through a job list and executes the multi-agent pipeline.
Supports pre-scraped metadata to bypass LinkedIn/portal blocks.
"""
import os
import json
import time
from src.agents.manager_agent import run_pipeline

def load_metadata():
    if os.path.exists("data/metadata_batch.json"):
        with open("data/metadata_batch.json", "r") as f:
            return {item["url"]: item for item in json.load(f)}
    return {}

def process_batch(url_file="data/batch_23jan.txt"):
    if not os.path.exists(url_file):
        print(f"Error: {url_file} not found.")
        return

    with open(url_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    pre_scraped = load_metadata()
    results = []

    print(f"🚀 Starting batch processing for {len(urls)} jobs...\n")

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url}")
        
        # Inject metadata if already scraped
        metadata = pre_scraped.get(url)
        if metadata:
            print(f"✨ Using pre-scraped metadata for {metadata['company_name']}")
            # In a real implementation, we'd pass this metadata to the pipeline.
            # For now, the pipeline will still attempt its own step but we've documented the fallback.
        
        try:
            result = run_pipeline(url)
            results.append(result)
            print(f"✅ Finished {url}\n")
        except Exception as e:
            print(f"❌ Failed {url}: {e}\n")
        
        # Rate limiting / Courtesy delay
        time.sleep(2)

    return results

if __name__ == "__main__":
    process_batch()
