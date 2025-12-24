#!/usr/bin/env python3
"""
Australian Job Scraper - MVP
Fetches real job listings from GitHub curated list and job boards.
"""

import os
import csv
import json
import hashlib
import re
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def generate_job_id(title, company, url):
    return hashlib.md5(f"{title}|{company}|{url}".encode()).hexdigest()[:12]

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', str(text)).strip()

def scrape_github_ausjobs():
    """Scrape the curated AusJobs GitHub repository."""
    print("🔍 Scraping GitHub AusJobs repository...")
    jobs = []
    
    try:
        url = "https://raw.githubusercontent.com/AusJobs/Australia-Tech-Internship/main/README.md"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        content = response.text
        
        # Parse markdown table: | [Role](URL) | Company | Location | Notes | Date |
        pattern = r'\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*([^|]+)\|'
        matches = re.findall(pattern, content)
        
        for match in matches:
            title = clean_text(match[0])
            url = match[1].strip()
            company = clean_text(match[2])
            location = clean_text(match[3])
            
            if not title or not url.startswith('http') or title.lower() in ['role', 'company']:
                continue
            
            jobs.append({
                'id': generate_job_id(title, company, url),
                'title': title,
                'company': company,
                'location': location if location else 'Australia',
                'salary': '',
                'url': url,
                'source': 'GitHub-AusJobs',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'scraped_at': datetime.now().isoformat(),
            })
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def scrape_seek_intern():
    """Scrape SEEK for intern/graduate positions."""
    print("🔍 Scraping SEEK...")
    jobs = []
    
    searches = [
        "software-engineer-intern-jobs",
        "graduate-software-developer-jobs", 
        "junior-developer-jobs",
        "data-engineer-intern-jobs",
    ]
    
    for search in searches:
        try:
            url = f"https://www.seek.com.au/{search}"
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find job listings
            articles = soup.find_all('article', {'data-card-type': 'JobCard'})
            
            for article in articles[:10]:
                try:
                    title_elem = article.find('a', {'data-automation': 'jobTitle'})
                    if not title_elem:
                        continue
                    
                    title = clean_text(title_elem.get_text())
                    link = title_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = f"https://www.seek.com.au{link}"
                    
                    company_elem = article.find('a', {'data-automation': 'jobCompany'})
                    location_elem = article.find('a', {'data-automation': 'jobLocation'})
                    salary_elem = article.find('span', {'data-automation': 'jobSalary'})
                    
                    company = clean_text(company_elem.get_text()) if company_elem else "Unknown"
                    location = clean_text(location_elem.get_text()) if location_elem else "Australia"
                    salary = clean_text(salary_elem.get_text()) if salary_elem else ""
                    
                    if title and link:
                        jobs.append({
                            'id': generate_job_id(title, company, link),
                            'title': title,
                            'company': company,
                            'location': location,
                            'salary': salary,
                            'url': link,
                            'source': 'SEEK',
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'scraped_at': datetime.now().isoformat(),
                        })
                except Exception:
                    continue
        except Exception as e:
            print(f"  SEEK error for {search}: {e}")
            continue
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def scrape_adzuna_api():
    """Scrape Adzuna API if credentials available."""
    print("🔍 Checking Adzuna API...")
    jobs = []
    
    app_id = os.environ.get('ADZUNA_APP_ID', '')
    app_key = os.environ.get('ADZUNA_APP_KEY', '')
    
    if not app_id or not app_key:
        print("  Adzuna API credentials not found, skipping")
        return jobs
    
    searches = ["software intern", "graduate developer", "junior engineer"]
    
    for search in searches:
        try:
            url = "https://api.adzuna.com/v1/api/jobs/au/search/1"
            params = {
                'app_id': app_id,
                'app_key': app_key,
                'results_per_page': 20,
                'what': search,
                'sort_by': 'date',
                'max_days_old': 30,
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code != 200:
                continue
            
            data = response.json()
            
            for result in data.get('results', []):
                title = clean_text(result.get('title', ''))
                company = clean_text(result.get('company', {}).get('display_name', 'Unknown'))
                location = clean_text(result.get('location', {}).get('display_name', 'Australia'))
                link = result.get('redirect_url', '')
                
                salary = ""
                if result.get('salary_min') and result.get('salary_max'):
                    salary = f"${int(result['salary_min']):,} - ${int(result['salary_max']):,}"
                
                if title and link:
                    jobs.append({
                        'id': generate_job_id(title, company, link),
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'url': link,
                        'source': 'Adzuna',
                        'posted_date': result.get('created', '')[:10] if result.get('created') else datetime.now().strftime('%Y-%m-%d'),
                        'scraped_at': datetime.now().isoformat(),
                    })
        except Exception as e:
            print(f"  Adzuna error: {e}")
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def main():
    print("=" * 50)
    print("🇦🇺 Australian Tech Job Scraper - MVP")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    all_jobs = []
    
    # Scrape all sources
    all_jobs.extend(scrape_github_ausjobs())
    all_jobs.extend(scrape_seek_intern())
    all_jobs.extend(scrape_adzuna_api())
    
    print(f"\n📊 Total jobs scraped: {len(all_jobs)}")
    
    if not all_jobs:
        print("⚠️ No jobs found!")
        return
    
    # Create DataFrame and deduplicate
    df = pd.DataFrame(all_jobs)
    df = df.drop_duplicates(subset=['id'], keep='first')
    df = df.sort_values('scraped_at', ascending=False)
    
    # Load existing and merge
    if os.path.exists('jobs.csv'):
        try:
            existing = pd.read_csv('jobs.csv')
            df = pd.concat([df, existing], ignore_index=True)
            df = df.drop_duplicates(subset=['id'], keep='first')
            print(f"📂 Merged with existing data")
        except Exception:
            pass
    
    # Save CSV
    df.to_csv('jobs.csv', index=False, quoting=csv.QUOTE_ALL)
    print(f"✅ Saved {len(df)} jobs to jobs.csv")
    
    # Save JSON
    with open('jobs.json', 'w') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'total_jobs': len(df),
            'jobs': df.to_dict(orient='records')
        }, f, indent=2)
    print(f"✅ Saved {len(df)} jobs to jobs.json")
    
    print("\n🏁 Done!")

if __name__ == '__main__':
    main()
