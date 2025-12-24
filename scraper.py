#!/usr/bin/env python3
"""
Australian Job Scraper - MVP
Fetches real job listings from GitHub curated lists, company career pages, and job boards.
"""

import os
import csv
import json
import hashlib
import re
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Company career pages from xdaybreakerx/australia-tech-jobs
COMPANY_CAREER_PAGES = {
    # Tier 0 - HFT
    "Jane Street": "https://www.janestreet.com/join-jane-street/open-roles/",
    "IMC Trading": "https://careers.imc.com/ap/en/search-results?qcountry=Australia",
    "Citadel": "https://www.citadel.com/careers/open-opportunities/engineering/",
    "Akuna Capital": "https://akunacapital.com/careers#careers",
    "VivCourt Trading": "https://www.vivcourt.com/careers/graduate-software-engineer/",
    # Tier 1 - Big Tech
    "Atlassian": "https://www.atlassian.com/company/careers/all-jobs?team=&location=Australia&search=",
    "Canva": "https://www.lifeatcanva.com/en/jobs/?page=1&team=Engineering&country=Australia&pagesize=20#results",
    "Google": "https://www.google.com/about/careers/applications/jobs/results/?location=Australia",
    "Apple": "https://jobs.apple.com/en-au/search?location=australia-AUSC",
    "Amazon": "https://www.amazon.jobs/en/search?base_query=&loc_query=Australia&country=AUS",
    "Microsoft": "https://jobs.careers.microsoft.com/global/en/search?lc=Australia&p=Software%20Engineering",
    "Spotify": "https://www.lifeatspotify.com/jobs?l=sydney",
    "MongoDB": "https://www.mongodb.com/company/careers/teams/engineering",
    # Tier 2
    "Adobe": "https://careers.adobe.com/us/en/search-results?qcountry=Australia",
    "Salesforce": "https://careers.salesforce.com/en/jobs/?search=&country=Australia&team=Software+Engineering",
    "Splunk": "https://www.splunk.com/en_us/careers/search-jobs.html?page=1&location=Australia&team=Products%20and%20Technology",
    "CloudFlare": "https://www.cloudflare.com/careers/jobs/?location=Australia",
    "SafetyCulture": "https://safetyculture.com/jobs/",
    "REA Group": "https://www.rea-group.com/careers/jobs/?team%5B0%5D=Tech_Other",
    "Databricks": "https://www.databricks.com/company/careers/open-positions?department=all&location=Australia",
    "Wisetech": "https://www.wisetechglobal.com/careers/current-openings/",
    "Immutable": "https://www.immutable.com/jobs",
    # Tier 3
    "Airwallex": "https://careers.airwallex.com/jobs/?team%5B%5D=engineering&location%5B%5D=melbourne&location%5B%5D=sydney",
    "Rokt": "https://www.rokt.com/careers/?teams=Engineering&location=Sydney",
    "Tyro": "https://tyro.wd3.myworkdayjobs.com/Tyro",
    "Xero": "https://jobs.lever.co/xero?department=Technology&location=Melbourne%2C%20AU",
    "WooliesX": "https://www.wowcareers.com.au/jobs/listing?expertise=Information+Technology&country=Australia&brand=WooliesX",
    "Domain": "https://www.domain.com.au/group/life-at-domain/careers/jobs/?keyword=software",
    "Sportsbet": "https://careers.sportsbet.com.au/jobs/search",
    "NAB": "https://careers.nab.com.au/en/filter/?category=software%20engineering",
    "SiteMinder": "https://www.siteminder.com/jobs/",
    "ANZ": "https://careers.anz.com/search/?optionsFacetsDD_customfield5=Engineering",
    # Tier 4
    "Freelancer": "https://www.freelancer.com.au/careers#vacancies",
    "Optus": "https://www.optus.com.au/about/careers",
    "MYOB": "https://careers.myob.com/explore-roles",
    "LinkTree": "https://linktr.ee/s/about/careers",
    "Culture Amp": "https://www.cultureamp.com/company/careers#open-roles",
    "Nine": "https://ninecareers.com.au/apply-now/?search=software",
    # Tier 5
    "Accenture": "https://www.accenture.com/au-en/careers/jobsearch?jk=software",
    "Thoughtworks": "https://www.thoughtworks.com/en-au/careers",
    "Telstra": "https://telstra.wd3.myworkdayjobs.com/Telstra_Careers",
    # VC Startups
    "Blackbird": "https://www.blackbird.vc/careers-at-blackbird#careers-collection",
    "Square Peg": "https://squarepeg.getro.com/jobs",
    "AirTree": "https://jobs.airtree.vc/jobs",
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
            job_url = match[1].strip()
            company = clean_text(match[2])
            location = clean_text(match[3])
            
            if not title or not job_url.startswith('http') or title.lower() in ['role', 'company']:
                continue
            
            jobs.append({
                'id': generate_job_id(title, company, job_url),
                'title': title,
                'company': company,
                'location': location if location else 'Australia',
                'salary': '',
                'url': job_url,
                'source': 'GitHub-AusJobs',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'scraped_at': datetime.now().isoformat(),
            })
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"  Found {len(jobs)} jobs")
    return jobs

def scrape_xdaybreakerx_repo():
    """Scrape the xdaybreakerx/australia-tech-jobs GitHub repo for company career links."""
    print("🔍 Scraping xdaybreakerx/australia-tech-jobs repository...")
    jobs = []
    
    try:
        url = "https://raw.githubusercontent.com/xdaybreakerx/australia-tech-jobs/main/readme.md"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        content = response.text
        
        # Parse markdown table: | Company | [Link Text](URL) |
        pattern = r'\|\s*([^|]+?)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|'
        matches = re.findall(pattern, content)
        
        for match in matches:
            company = clean_text(match[0])
            link_text = clean_text(match[1])
            job_url = match[2].strip()
            
            # Skip header rows
            if company.lower() in ['company', '---', '']:
                continue
            
            if not job_url.startswith('http'):
                continue
                
            jobs.append({
                'id': generate_job_id(link_text, company, job_url),
                'title': link_text,
                'company': company,
                'location': 'Australia',
                'salary': '',
                'url': job_url,
                'source': 'GitHub-TechJobs',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'scraped_at': datetime.now().isoformat(),
            })
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"  Found {len(jobs)} career pages")
    return jobs

def scrape_company_careers():
    """Scrape individual company career pages for actual job listings."""
    print("🔍 Scraping company career pages...")
    jobs = []
    
    for company, url in COMPANY_CAREER_PAGES.items():
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Generic job link patterns - look for job/career/position links
            job_links = soup.find_all('a', href=True)
            
            for link in job_links[:20]:  # Limit per company
                href = link.get('href', '')
                text = clean_text(link.get_text())
                
                # Skip navigation/footer links, look for job-like links
                if len(text) < 5 or len(text) > 150:
                    continue
                
                # Match job-related keywords in link text or URL
                job_keywords = ['engineer', 'developer', 'software', 'intern', 'graduate', 'data', 'analyst', 'devops', 'cloud', 'full stack', 'backend', 'frontend', 'sre', 'platform']
                text_lower = text.lower()
                
                if not any(kw in text_lower for kw in job_keywords):
                    continue
                
                # Build full URL
                if href.startswith('/'):
                    parsed = urlparse(url)
                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                elif not href.startswith('http'):
                    continue
                
                jobs.append({
                    'id': generate_job_id(text, company, href),
                    'title': text,
                    'company': company,
                    'location': 'Australia',
                    'salary': '',
                    'url': href,
                    'source': f'Company-{company}',
                    'posted_date': datetime.now().strftime('%Y-%m-%d'),
                    'scraped_at': datetime.now().isoformat(),
                })
        except Exception:
            continue  # Silent fail for individual companies
    
    print(f"  Found {len(jobs)} jobs from company pages")
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
    
    merge_mode = '--merge' in sys.argv
    
    all_jobs = []
    
    # Scrape all sources
    all_jobs.extend(scrape_github_ausjobs())
    all_jobs.extend(scrape_xdaybreakerx_repo())
    all_jobs.extend(scrape_company_careers())
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
    if merge_mode and os.path.exists('jobs.csv'):
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
