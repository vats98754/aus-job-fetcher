#!/usr/bin/env python3
"""
Australian Tech Job Scraper
Only fetches REAL job postings with exact URLs for Australian positions.
"""

import os
import csv
import json
import hashlib
import re
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import pandas as pd
from dateutil import parser as date_parser
import pytz

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-AU,en;q=0.9",
}

# Job title keywords - must match at least one
JOB_KEYWORDS = [
    'software engineer', 'software developer', 'swe', 'sde',
    'data engineer', 'data developer', 'data analyst', 'data analytics',
    'data scientist', 'machine learning', 'ml engineer', 'ai engineer',
    'backend', 'back-end', 'frontend', 'front-end', 'fullstack', 'full-stack', 'full stack',
    'devops', 'sre', 'site reliability', 'platform engineer', 'cloud engineer',
    'bi developer', 'business intelligence', 'data reporting', 'reporting analyst',
    'python developer', 'java developer', 'javascript developer', 'typescript',
    'web developer', 'mobile developer', 'ios developer', 'android developer',
    'database', 'dba', 'etl', 'data warehouse', 'analytics engineer',
    'graduate', 'intern', 'junior', 'entry level',
    'solutions engineer', 'technical analyst', 'systems engineer',
]

# Australia location keywords - must match at least one
AUSTRALIA_KEYWORDS = [
    'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
    'canberra', 'hobart', 'darwin', 'gold coast', 'newcastle', 'wollongong',
    'geelong', 'cairns', 'townsville', 'aus', 'nsw', 'vic', 'qld', 'wa', 'sa', 'tas', 'nt', 'act',
    'new south wales', 'victoria', 'queensland', 'western australia',
]

def generate_job_id(title, company, url):
    """Generate unique ID for deduplication using URL, title, and company.
    This prevents duplicate jobs from being stored.
    """
    # Normalize URL by removing query parameters and fragments for better deduplication
    parsed_url = urlparse(url)
    clean_url = f"{parsed_url.netloc}{parsed_url.path}".lower()
    
    # Create a unique hash combining all three elements
    unique_string = f"{clean_url}|{title.lower()}|{company.lower()}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

def parse_relative_time(time_str):
    """Parse relative time strings like '2 hours ago', '1 day ago' into datetime.
    Returns ISO format timestamp or empty string if cannot parse.
    """
    if not time_str:
        return ""
    
    time_str_lower = time_str.lower().strip()
    now = datetime.now(timezone.utc)
    
    # Match patterns like "2 hours ago", "1 day ago", "30 minutes ago"
    patterns = [
        (r'(\d+)\s*min(?:ute)?s?\s*ago', 'minutes'),
        (r'(\d+)\s*hour?s?\s*ago', 'hours'),
        (r'(\d+)\s*day?s?\s*ago', 'days'),
        (r'(\d+)\s*week?s?\s*ago', 'weeks'),
        (r'(\d+)\s*month?s?\s*ago', 'months'),
    ]
    
    for pattern, unit in patterns:
        match = re.search(pattern, time_str_lower)
        if match:
            value = int(match.group(1))
            if unit == 'minutes':
                posted_time = now - timedelta(minutes=value)
            elif unit == 'hours':
                posted_time = now - timedelta(hours=value)
            elif unit == 'days':
                posted_time = now - timedelta(days=value)
            elif unit == 'weeks':
                posted_time = now - timedelta(weeks=value)
            elif unit == 'months':
                posted_time = now - timedelta(days=value * 30)
            return posted_time.isoformat()
    
    # Try parsing as absolute date
    try:
        parsed_date = date_parser.parse(time_str)
        # If no timezone, assume UTC
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
        return parsed_date.isoformat()
    except:
        pass
    
    # If "today" or "just now"
    if 'today' in time_str_lower or 'just now' in time_str_lower or 'recently' in time_str_lower:
        return now.isoformat()
    
    return ""

def calculate_hours_since_posted(posted_at_iso):
    """Calculate hours since job was posted.
    Returns float of hours or None if cannot calculate.
    """
    if not posted_at_iso:
        return None
    
    try:
        posted_time = date_parser.parse(posted_at_iso)
        now = datetime.now(timezone.utc)
        
        # Ensure both are timezone-aware
        if posted_time.tzinfo is None:
            posted_time = posted_time.replace(tzinfo=timezone.utc)
        
        delta = now - posted_time
        hours = delta.total_seconds() / 3600
        return round(hours, 1)
    except:
        return None

def get_current_timestamp():
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()

def clean_text(text):
    """Clean whitespace from text."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', str(text)).strip()

def is_valid_job_title(title):
    """Check if title matches our target job keywords."""
    if not title:
        return False
    title_lower = title.lower()
    return any(kw in title_lower for kw in JOB_KEYWORDS)

def is_australia_location(location, title="", url=""):
    """Check if location is in Australia."""
    check_text = f"{location} {title} {url}".lower()
    return any(kw in check_text for kw in AUSTRALIA_KEYWORDS)

def is_direct_job_url(url):
    """Check if URL is a direct job posting, not a generic careers page."""
    if not url:
        return False
    url_lower = url.lower()
    
    # Must have job identifiers in URL
    job_patterns = [
        r'/job[s]?/',
        r'/position[s]?/',
        r'/opening[s]?/',
        r'/requisition',
        r'/req\d+',
        r'/jid/',
        r'/jobid/',
        r'/job-\d+',
        r'/apply/',
        r'jobid=',
        r'job_id=',
        r'positionid=',
        r'id=\d+',
        r'/\d{5,}',  # Long numeric ID
        r'greenhouse\.io/.+/jobs/',
        r'lever\.co/.+/',
        r'workday\.com/.+/job/',
        r'myworkdayjobs\.com/.+/job/',
        r'smartrecruiters\.com/.+/\d+',
        r'seek\.com\.au/job/',
        r'indeed\.com/.+/viewjob',
        r'linkedin\.com/jobs/view/',
    ]
    
    # Generic pages to reject
    generic_patterns = [
        r'^https?://[^/]+/?$',  # Just domain
        r'/careers/?$',
        r'/jobs/?$',
        r'/about/?$',
        r'/company/?$',
        r'/teams?/?$',
        r'/culture/?$',
    ]
    
    # Reject generic pages
    for pattern in generic_patterns:
        if re.search(pattern, url_lower):
            return False
    
    # Accept if has job identifier
    for pattern in job_patterns:
        if re.search(pattern, url_lower):
            return True
    
    # Otherwise reject
    return False

def scrape_github_ausjobs():
    """Scrape the curated AusJobs GitHub repository - already vetted Australia internships."""
    print("🔍 Scraping GitHub AusJobs repository...")
    jobs = []
    
    try:
        url = "https://raw.githubusercontent.com/AusJobs/Australia-Tech-Internship/main/README.md"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        content = response.text
        
        current_time = get_current_timestamp()
        
        # Parse markdown table: | [Role](URL) | Company | Location | Notes | Date |
        pattern = r'\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*([^|]+)\|'
        matches = re.findall(pattern, content)
        
        for match in matches:
            title = clean_text(match[0])
            job_url = match[1].strip()
            company = clean_text(match[2])
            location = clean_text(match[3])
            
            # Skip headers
            if title.lower() in ['role', 'company', 'position'] or '---' in title:
                continue
            
            # Must be valid URL
            if not job_url.startswith('http'):
                continue
            
            # This repo is curated for Australian internships, trust it
            jobs.append({
                'id': generate_job_id(title, company, job_url),
                'title': title,
                'company': company,
                'location': location if location else 'Australia',
                'salary': '',
                'url': job_url,
                'source': 'GitHub-AusJobs',
                'posted_at': '',  # Not available from this source
                'fetched_at': current_time,
                'hours_since_posted': None,
            })
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def scrape_seek():
    """Scrape SEEK for Australian tech jobs - exact job posting URLs."""
    print("🔍 Scraping SEEK Australia...")
    jobs = []
    
    current_time = get_current_timestamp()
    
    # Specific searches for our target roles
    searches = [
        ("data-engineer", "data engineer"),
        ("data-analyst", "data analyst"),
        ("data-scientist", "data scientist"),
        ("software-engineer", "software engineer"),
        ("software-developer", "software developer"),
        ("backend-developer", "backend developer"),
        ("frontend-developer", "frontend developer"),
        ("full-stack-developer", "full stack developer"),
        ("devops-engineer", "devops engineer"),
        ("machine-learning-engineer", "ml engineer"),
        ("python-developer", "python developer"),
        ("graduate-software", "graduate developer"),
        ("junior-developer", "junior developer"),
        ("intern-software", "intern"),
        ("bi-developer", "bi developer"),
        ("analytics-engineer", "analytics engineer"),
    ]
    
    for search_slug, search_name in searches:
        try:
            url = f"https://www.seek.com.au/{search_slug}-jobs/in-All-Australia"
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'lxml')
            articles = soup.find_all('article', {'data-card-type': 'JobCard'})
            
            for article in articles[:15]:  # Top 15 per search
                try:
                    title_elem = article.find('a', {'data-automation': 'jobTitle'})
                    if not title_elem:
                        continue
                    
                    title = clean_text(title_elem.get_text())
                    link = title_elem.get('href', '')
                    
                    # Build full SEEK job URL
                    if link and not link.startswith('http'):
                        link = f"https://www.seek.com.au{link}"
                    
                    # Verify it's a direct job URL (has /job/ in path)
                    if '/job/' not in link:
                        continue
                    
                    company_elem = article.find('a', {'data-automation': 'jobCompany'})
                    location_elem = article.find('a', {'data-automation': 'jobLocation'})
                    salary_elem = article.find('span', {'data-automation': 'jobSalary'})
                    time_elem = article.find('span', {'data-automation': 'jobListingDate'})
                    
                    company = clean_text(company_elem.get_text()) if company_elem else ""
                    location = clean_text(location_elem.get_text()) if location_elem else ""
                    salary = clean_text(salary_elem.get_text()) if salary_elem else ""
                    
                    # Parse posting time
                    posted_at = ""
                    if time_elem:
                        time_text = clean_text(time_elem.get_text())
                        posted_at = parse_relative_time(time_text)
                    
                    hours_since = calculate_hours_since_posted(posted_at)
                    
                    # Skip if no company
                    if not company:
                        continue
                    
                    # Verify Australia location
                    if not is_australia_location(location):
                        continue
                    
                    jobs.append({
                        'id': generate_job_id(title, company, link),
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'url': link,
                        'source': 'SEEK',
                        'posted_at': posted_at,
                        'fetched_at': current_time,
                        'hours_since_posted': hours_since,
                    })
                except Exception:
                    continue
        except Exception as e:
            continue
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def scrape_adzuna_api():
    """Scrape Adzuna API for Australian tech jobs."""
    print("🔍 Checking Adzuna API...")
    jobs = []
    
    app_id = os.environ.get('ADZUNA_APP_ID', '')
    app_key = os.environ.get('ADZUNA_APP_KEY', '')
    
    if not app_id or not app_key:
        print("  Adzuna API credentials not found, skipping")
        return jobs
    
    current_time = get_current_timestamp()
    
    searches = [
        "data engineer",
        "data analyst", 
        "data scientist",
        "software engineer",
        "software developer",
        "devops engineer",
        "machine learning",
        "python developer",
        "graduate developer",
        "junior developer",
    ]
    
    for search in searches:
        try:
            api_url = "https://api.adzuna.com/v1/api/jobs/au/search/1"
            params = {
                'app_id': app_id,
                'app_key': app_key,
                'results_per_page': 25,
                'what': search,
                'where': 'Australia',
                'sort_by': 'date',
                'max_days_old': 14,
            }
            
            response = requests.get(api_url, params=params, timeout=15)
            if response.status_code != 200:
                continue
            
            data = response.json()
            
            for result in data.get('results', []):
                title = clean_text(result.get('title', ''))
                company = clean_text(result.get('company', {}).get('display_name', ''))
                location = clean_text(result.get('location', {}).get('display_name', ''))
                link = result.get('redirect_url', '')
                
                # Skip if missing essential fields
                if not title or not company or not link:
                    continue
                
                # Verify job title matches our criteria
                if not is_valid_job_title(title):
                    continue
                
                # Verify Australia location
                if not is_australia_location(location, title):
                    continue
                
                salary = ""
                if result.get('salary_min') and result.get('salary_max'):
                    salary = f"${int(result['salary_min']):,} - ${int(result['salary_max']):,}"
                elif result.get('salary_min'):
                    salary = f"${int(result['salary_min']):,}+"
                
                # Parse posting time from Adzuna's created field
                posted_at = ""
                if result.get('created'):
                    posted_at = parse_relative_time(result.get('created'))
                
                hours_since = calculate_hours_since_posted(posted_at)
                
                jobs.append({
                    'id': generate_job_id(title, company, link),
                    'title': title,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'url': link,
                    'source': 'Adzuna',
                    'posted_at': posted_at,
                    'fetched_at': current_time,
                    'hours_since_posted': hours_since,
                })
        except Exception as e:
            continue
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def scrape_linkedin_public():
    """Scrape LinkedIn public job listings for Australian tech jobs."""
    print("🔍 Scraping LinkedIn public listings...")
    jobs = []
    
    current_time = get_current_timestamp()
    
    searches = [
        ("data%20engineer", "Australia"),
        ("data%20analyst", "Australia"),
        ("software%20engineer", "Australia"),
        ("python%20developer", "Australia"),
        ("graduate%20software", "Australia"),
    ]
    
    for search, location in searches:
        try:
            # LinkedIn public job search
            url = f"https://www.linkedin.com/jobs/search?keywords={search}&location={location}&f_TPR=r604800"
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'lxml')
            job_cards = soup.find_all('div', class_='base-card')
            
            for card in job_cards[:10]:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    time_elem = card.find('time', class_='job-search-card__listdate')
                    
                    if not all([title_elem, company_elem, link_elem]):
                        continue
                    
                    title = clean_text(title_elem.get_text())
                    company = clean_text(company_elem.get_text())
                    location = clean_text(location_elem.get_text()) if location_elem else ""
                    link = link_elem.get('href', '')
                    
                    # Parse posting time
                    posted_at = ""
                    if time_elem:
                        time_text = time_elem.get('datetime', '') or clean_text(time_elem.get_text())
                        posted_at = parse_relative_time(time_text)
                    
                    hours_since = calculate_hours_since_posted(posted_at)
                    
                    # Verify it's a direct job URL
                    if '/jobs/view/' not in link:
                        continue
                    
                    # Verify Australia
                    if not is_australia_location(location, title, link):
                        continue
                    
                    # Verify job title
                    if not is_valid_job_title(title):
                        continue
                    
                    jobs.append({
                        'id': generate_job_id(title, company, link),
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': '',
                        'url': link.split('?')[0],  # Clean URL
                        'source': 'LinkedIn',
                        'posted_at': posted_at,
                        'fetched_at': current_time,
                        'hours_since_posted': hours_since,
                    })
                except Exception:
                    continue
        except Exception:
            continue
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def scrape_gradconnection():
    """Scrape GradConnection for Australian graduate tech jobs."""
    print("🔍 Scraping GradConnection...")
    jobs = []
    
    current_time = get_current_timestamp()
    
    try:
        url = "https://au.gradconnection.com/graduate-jobs/information-technology/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return jobs
        
        soup = BeautifulSoup(response.text, 'lxml')
        job_cards = soup.find_all('div', class_='job-card')
        
        for card in job_cards[:30]:
            try:
                title_elem = card.find('a', class_='job-title')
                company_elem = card.find('span', class_='company-name')
                location_elem = card.find('span', class_='location')
                time_elem = card.find('span', class_='job-posted-date')
                
                if not title_elem:
                    continue
                
                title = clean_text(title_elem.get_text())
                link = title_elem.get('href', '')
                company = clean_text(company_elem.get_text()) if company_elem else ""
                location = clean_text(location_elem.get_text()) if location_elem else "Australia"
                
                # Parse posting time
                posted_at = ""
                if time_elem:
                    time_text = clean_text(time_elem.get_text())
                    posted_at = parse_relative_time(time_text)
                
                hours_since = calculate_hours_since_posted(posted_at)
                
                if not link.startswith('http'):
                    link = f"https://au.gradconnection.com{link}"
                
                # Must be direct job URL
                if not is_direct_job_url(link) and '/graduate-jobs/' not in link:
                    continue
                
                # Verify Australia
                if not is_australia_location(location, title):
                    continue
                
                jobs.append({
                    'id': generate_job_id(title, company, link),
                    'title': title,
                    'company': company,
                    'location': location,
                    'salary': '',
                    'url': link,
                    'source': 'GradConnection',
                    'posted_at': posted_at,
                    'fetched_at': current_time,
                    'hours_since_posted': hours_since,
                })
            except Exception:
                continue
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def scrape_careerjet():
    """Scrape CareerJet Australia for tech jobs."""
    print("🔍 Scraping CareerJet Australia...")
    jobs = []
    
    current_time = get_current_timestamp()
    
    searches = [
        "data engineer",
        "data analyst",
        "data scientist",
        "software engineer",
        "software developer",
        "backend developer",
        "frontend developer",
        "full stack developer",
        "devops engineer",
        "machine learning engineer",
        "python developer",
        "graduate software",
        "junior developer",
    ]
    
    for search in searches:
        try:
            search_encoded = search.replace(' ', '+')
            url = f"https://www.careerjet.com.au/search/jobs?s={search_encoded}&l=Australia&sort=date"
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'lxml')
            job_cards = soup.find_all('article', class_='job')
            
            for card in job_cards[:10]:  # Top 10 per search
                try:
                    # Get title
                    title_elem = card.find('h2')
                    if not title_elem:
                        continue
                    title = clean_text(title_elem.get_text())
                    
                    # Get link
                    link_elem = title_elem.find('a')
                    if not link_elem:
                        continue
                    link = link_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = 'https://www.careerjet.com.au' + link
                    
                    # Get company
                    company_elem = card.find('p', class_='company')
                    company = clean_text(company_elem.get_text()) if company_elem else ""
                    
                    # Get location
                    loc_elem = card.find('ul', class_='location')
                    location = clean_text(loc_elem.get_text()) if loc_elem else "Australia"
                    
                    # Get salary if available
                    salary_elem = card.find('li', class_='salary')
                    salary = clean_text(salary_elem.get_text()) if salary_elem else ""
                    
                    # Get posted date
                    date_elem = card.find('ul', class_='date')
                    posted_at = ""
                    if date_elem:
                        date_text = clean_text(date_elem.get_text())
                        posted_at = parse_relative_time(date_text)
                    
                    hours_since = calculate_hours_since_posted(posted_at)
                    
                    # Skip if no company
                    if not company:
                        continue
                    
                    # Verify job title
                    if not is_valid_job_title(title):
                        continue
                    
                    # Verify Australia location
                    if not is_australia_location(location, title):
                        continue
                    
                    jobs.append({
                        'id': generate_job_id(title, company, link),
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'url': link,
                        'source': 'CareerJet',
                        'posted_at': posted_at,
                        'fetched_at': current_time,
                        'hours_since_posted': hours_since,
                    })
                except Exception:
                    continue
        except Exception as e:
            continue
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def main():
    print("=" * 60)
    print("🇦🇺 Australian Tech Job Scraper - Detailed Edition")
    print(f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    print("Filters: Australia only | Tech/Data roles | Direct job URLs")
    print("Features: Precise timestamps | Deduplication | Recency tracking")
    print("=" * 60)
    
    merge_mode = '--merge' in sys.argv
    
    all_jobs = []
    
    # Scrape all sources
    all_jobs.extend(scrape_github_ausjobs())
    all_jobs.extend(scrape_seek())
    all_jobs.extend(scrape_careerjet())  # Added CareerJet as SEEK alternative
    all_jobs.extend(scrape_adzuna_api())
    all_jobs.extend(scrape_linkedin_public())
    all_jobs.extend(scrape_gradconnection())
    
    print(f"\n📊 Total jobs scraped: {len(all_jobs)}")
    
    if not all_jobs:
        print("⚠️ No jobs found!")
        return
    
    # Create DataFrame and deduplicate
    df = pd.DataFrame(all_jobs)
    print(f"📋 Jobs before deduplication: {len(df)}")
    
    df = df.drop_duplicates(subset=['id'], keep='first')
    print(f"✨ Jobs after deduplication: {len(df)}")
    
    # Sort by fetched_at (most recent first)
    df = df.sort_values('fetched_at', ascending=False)
    
    # Load existing and merge
    if merge_mode and os.path.exists('jobs.csv'):
        try:
            existing = pd.read_csv('jobs.csv')
            print(f"📂 Loading {len(existing)} existing jobs")
            df = pd.concat([df, existing], ignore_index=True)
            df = df.drop_duplicates(subset=['id'], keep='first')
            print(f"🔄 After merge: {len(df)} unique jobs")
        except Exception as e:
            print(f"⚠️ Could not merge with existing data: {e}")
    
    # Calculate statistics
    jobs_with_timestamp = df['posted_at'].notna().sum()
    jobs_very_recent = df[df['hours_since_posted'].notna() & (df['hours_since_posted'] <= 1)].shape[0]
    jobs_recent = df[df['hours_since_posted'].notna() & (df['hours_since_posted'] <= 24)].shape[0]
    
    print(f"\n📈 Statistics:")
    print(f"  • Total unique jobs: {len(df)}")
    print(f"  • Jobs with posting timestamps: {jobs_with_timestamp}")
    print(f"  • Jobs posted within 1 hour: {jobs_very_recent}")
    print(f"  • Jobs posted within 24 hours: {jobs_recent}")
    
    # Save CSV with all new fields
    df.to_csv('jobs.csv', index=False, quoting=csv.QUOTE_ALL)
    print(f"\n✅ Saved {len(df)} jobs to jobs.csv")
    
    # Save JSON with metadata
    with open('jobs.json', 'w') as f:
        json.dump({
            'last_updated': get_current_timestamp(),
            'total_jobs': len(df),
            'jobs_with_timestamps': int(jobs_with_timestamp),
            'jobs_within_1_hour': int(jobs_very_recent),
            'jobs_within_24_hours': int(jobs_recent),
            'jobs': df.to_dict(orient='records')
        }, f, indent=2)
    print(f"✅ Saved {len(df)} jobs to jobs.json")
    
    print("\n🏁 Scraping complete!")
    print(f"🔗 View your jobs at: https://vats98754.github.io/aus-job-fetcher/")

if __name__ == '__main__':
    main()
