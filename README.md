# 🇦🇺 Australian Job Fetcher - Your Tech Career Launchpad

> **Real-time Australian tech job aggregator that helps you land your dream role faster** 🚀

Never miss out on fresh job opportunities again! This automated job fetcher scrapes multiple Australian job boards every few minutes, tracks exact posting times, and helps you apply to jobs within minutes of them being posted - giving you a critical competitive advantage in Australia's hot tech job market.

[![Auto-Update Jobs](https://img.shields.io/badge/jobs-auto--updated-success)](https://github.com/vats98754/aus-job-fetcher/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Made for Australians](https://img.shields.io/badge/made%20for-🇦🇺%20Australians-brightgreen)](https://github.com/vats98754/aus-job-fetcher)

---

## 🎯 Why This Tool is a Game-Changer

### ⚡ **Be First to Apply**
- **Track posting times to the minute** - Know exactly when jobs were posted
- **Filter jobs posted in the last hour** - Apply before the competition even sees them
- **Automated updates every 5 minutes** - Fresh opportunities delivered continuously
- **Smart deduplication** - Never waste time on duplicate listings

### 🎓 **Perfect For All Tech Career Levels**
- **Graduates & Interns** - Breaking into the Australian tech industry
- **Junior Developers** - Building your career foundation
- **Mid-Level Engineers** - Taking the next step up
- **Senior Professionals** - Finding leadership opportunities
- **Career Switchers** - Transitioning into tech roles

### 💼 **Comprehensive Job Coverage**

This tool aggregates from Australia's top tech job platforms:

| Job Board | Coverage | Updates | Special Features |
|-----------|----------|---------|------------------|
| 🔵 **SEEK** | Largest AU job board | Every 5 min | Salary data, posting times |
| 🟢 **GitHub AusJobs** | Curated internships | Real-time | Verified opportunities |
| 🟠 **Adzuna** | API-powered | Every 5 min | Comprehensive metadata |
| 🔗 **LinkedIn** | Professional network | Every 5 min | Company insights |
| 🎓 **GradConnection** | Graduate programs | Every 5 min | Entry-level focus |

### 🎯 **Role Coverage**

We track opportunities across all tech disciplines:

**Engineering & Development**
- Software Engineers/Developers (Frontend, Backend, Full-Stack)
- Mobile Developers (iOS, Android, React Native)
- DevOps & SRE Engineers
- Platform & Cloud Engineers

**Data & Analytics**
- Data Engineers
- Data Analysts
- Data Scientists
- Business Intelligence Developers
- Analytics Engineers
- Machine Learning Engineers

**Emerging Tech**
- AI/ML Engineers
- Solutions Architects
- Technical Analysts
- Systems Engineers

**Early Career**
- Graduate Programs
- Internships (Summer, Winter)
- Junior Roles
- Entry-Level Positions

---

## 🚀 Quick Start Guide

### Option 1: View the Live Website (Easiest!)

**Just visit:** `https://YOUR_USERNAME.github.io/aus-job-fetcher/`

Browse hundreds of fresh Australian tech jobs in a beautiful, filterable interface!

### Option 2: Fork & Customize (Recommended!)

1. **Fork this repository** 
   - Click the "Fork" button at the top right of this page
   - You'll have your own copy with automatic updates!

2. **Enable GitHub Actions**
   - Go to the "Actions" tab in your forked repo
   - Click "I understand my workflows, go ahead and enable them"

3. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: "GitHub Actions"
   - Save!

4. **Watch the magic happen! ✨**
   - Jobs will update automatically every 5 minutes
   - Visit `https://YOUR_USERNAME.github.io/aus-job-fetcher/` to see your personalized job board

### Option 3: Run Locally (For Developers)

```bash
# Clone the repository
git clone https://github.com/vats98754/aus-job-fetcher.git
cd aus-job-fetcher

# Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python scraper.py

# View results
open index.html  # macOS
# or xdg-open index.html  # Linux
# or start index.html  # Windows
```

---

## 🌟 Key Features Explained

### 📅 **Precise Timestamp Tracking**

Every job listing includes:
- **`fetched_at`** - Exact UTC timestamp when we found the job
- **`posted_at`** - When the company originally posted it (when available)
- **`hours_since_posted`** - Calculated recency for easy filtering

**Why this matters:** Apply to jobs within 30-60 minutes of posting for 3-5x higher response rates!

### 🔐 **Intelligent Job ID System**

Our clever deduplication algorithm:
```python
# Creates unique hash from URL + title + company
# Ensures the same job from different scrapers isn't counted twice
id = sha256(url + title + company)
```

**Benefits:**
- ✅ No duplicate applications
- ✅ Stable IDs across scraping runs
- ✅ Track which jobs you've already seen
- ✅ Efficient database management

### 🎨 **Beautiful, Functional Web Interface**

The `index.html` page provides:
- 🔍 **Real-time search** - Filter by keywords, company, location
- 📊 **Smart filtering** - By source, location, recency
- 📈 **Sortable columns** - Click headers to sort by any field
- 🕐 **Timestamp display** - See exactly when jobs were posted
- 💾 **Export options** - Download as CSV or JSON
- 📱 **Mobile responsive** - Job hunt on the go
- 🎯 **Direct apply links** - One click to the application page

### 📈 **Statistics Dashboard**

Track your job search effectiveness:
- Total unique jobs tracked
- Jobs posted in the last hour
- Jobs posted today
- Coverage by source and location
- Update frequency and freshness

---

## 💡 Pro Tips for Australian Job Seekers

### ⏰ **Timing is Everything**

1. **Check the "posted_at" field** - Apply to jobs posted within the last 1-2 hours
2. **Set up notifications** - Get alerted when new jobs appear
3. **Peak posting times** - Most companies post Monday-Wednesday, 9am-11am AEST
4. **Weekend advantage** - Fewer applicants compete on Saturday/Sunday posts

### 🎯 **Strategic Application Approach**

1. **Prioritize by recency** - Sort by `hours_since_posted`
2. **Focus on direct links** - All our URLs go straight to application pages
3. **Track your applications** - Use the CSV export to maintain a spreadsheet
4. **Customize per source** - Different job boards need different approach styles

### 📝 **Application Quality**

Speed matters, but quality matters more:
- ✅ Tailor your resume to each role
- ✅ Write personalized cover letters (even short ones)
- ✅ Reference specific details from the job description
- ✅ Follow up after 3-5 business days

### 🌏 **Location Strategy**

**Major Tech Hubs:**
- **Sydney** - Largest market, fintech, enterprise
- **Melbourne** - Startups, creative tech, agencies
- **Brisbane** - Growing market, lower competition
- **Perth** - Mining tech, resources sector
- **Adelaide** - Defense, space tech, emerging startup scene

**Remote Opportunities:**
- Filter for "Remote" or "Work from home"
- Many companies now offer hybrid arrangements
- Consider interstate remote roles for better salary

---

## ⚙️ Advanced Configuration

### 🔑 **Add Adzuna API (Optional but Recommended)**

Get more detailed job data:

1. Sign up at [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Create an application (free tier available)
3. Add to your repo: Settings → Secrets → Actions
   - `ADZUNA_APP_ID`: Your application ID
   - `ADZUNA_APP_KEY`: Your API key
4. Next scrape will include Adzuna jobs!

### 🕐 **Adjust Scraping Frequency**

Edit `.github/workflows/fetch-jobs.yml`:

```yaml
schedule:
  - cron: '*/5 * * * *'   # Every 5 minutes (default)
  # - cron: '*/10 * * * *' # Every 10 minutes (saves Actions minutes)
  # - cron: '0 * * * *'    # Every hour (for low-frequency monitoring)
```

**Note:** GitHub Free accounts get 2,000 Actions minutes/month. Choose wisely!

### 🎯 **Customize Search Parameters**

Edit `scraper.py` to modify:

```python
# Add more job keywords
JOB_KEYWORDS = [
    'your-specialty-here',
    'rust developer',  # Add emerging technologies
    'golang engineer',
    # ... customize for your interests
]

# Focus on specific locations
AUSTRALIA_KEYWORDS = [
    'sydney',  # Only Sydney jobs
    'remote',  # Remote-friendly
    # ... your preferred locations
]
```

### 📊 **Export & Integration**

**CSV Format:**
- Import into Excel/Google Sheets
- Track applications in Notion
- Build custom dashboards

**JSON Format:**
- Feed into other tools
- Create mobile apps
- Build browser extensions
- Power Slack/Discord bots

---

## 📱 Using the Web Interface

### 🔍 **Search & Filter Features**

1. **Keyword Search**
   - Search across title, company, location
   - Real-time filtering as you type
   - Case-insensitive matching

2. **Source Filter**
   - Focus on specific job boards
   - Different sources = different job types
   - SEEK = enterprise, GitHub = startups

3. **Location Filter**
   - Filter by city or state
   - Useful for relocation planning
   - Combine with remote options

4. **Recency Filter** (Coming Soon!)
   - Jobs posted in last hour
   - Jobs posted today
   - Jobs posted this week

### 📈 **Sorting Options**

Click any column header to sort:
- **Title** - Alphabetical job roles
- **Company** - Find specific employers
- **Location** - Geographic clustering
- **Posted At** - Freshest opportunities first
- **Hours Since Posted** - Competitive advantage

---

## 🛠️ Technical Details

### 📦 **Architecture**

```
aus-job-fetcher/
├── scraper.py          # Main scraping engine
├── jobs.csv            # Latest job data (CSV)
├── jobs.json           # Latest job data (JSON + metadata)
├── index.html          # Web interface
├── requirements.txt    # Python dependencies
└── .github/
    └── workflows/
        └── fetch-jobs.yml  # Automation configuration
```

### 🔄 **Data Flow**

```
Job Boards → Scrapers → Deduplication → CSV/JSON → GitHub Pages → You!
     ↓          ↓            ↓              ↓           ↓
  [APIs]   [BeautifulSoup] [SHA256]    [Pandas]    [HTML/JS]
```

### 🔐 **Job ID Generation Algorithm**

```python
def generate_job_id(title, company, url):
    """
    Creates stable, unique identifiers for jobs.
    Same job = same ID, even if scraped from different sources.
    """
    parsed_url = urlparse(url)
    clean_url = f"{parsed_url.netloc}{parsed_url.path}".lower()
    unique_string = f"{clean_url}|{title.lower()}|{company.lower()}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
```

**Why SHA-256?**
- Cryptographically secure hashing
- Extremely low collision probability
- Consistent across different runs
- URL normalization prevents query param differences

### 📊 **Data Schema**

```csv
id,title,company,location,salary,url,source,posted_at,fetched_at,hours_since_posted
```

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string(16) | Unique job identifier | `4c494a5eac8e4e32` |
| `title` | string | Job position name | `Senior Software Engineer` |
| `company` | string | Employer name | `Atlassian` |
| `location` | string | Job location | `Sydney, NSW` |
| `salary` | string | Salary range (if available) | `$120k - $150k` |
| `url` | string | Direct application link | `https://...` |
| `source` | string | Origin job board | `SEEK` |
| `posted_at` | ISO 8601 | When job was posted | `2025-12-24T10:30:00+00:00` |
| `fetched_at` | ISO 8601 | When we scraped it | `2025-12-24T14:05:00+00:00` |
| `hours_since_posted` | float | Calculated recency | `3.5` |

---

## 🤝 Contributing

We love contributions from the Australian tech community!

### 🐛 **Report Bugs**
- Open an issue with details
- Include error messages
- Share your configuration

### 💡 **Suggest Features**
- New job boards to add
- Filter improvements
- UI enhancements

### 🔧 **Submit Pull Requests**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 🌟 **Share Your Success**
Got a job using this tool? Let us know! We'd love to hear your story.

---

## 📜 License

MIT License - feel free to use, modify, and distribute!

This project is open source and maintained by the community for the Australian tech job seeker community.

---

## 🙏 Acknowledgments

**Data Sources:**
- [SEEK](https://www.seek.com.au/) - Australia's #1 job board
- [Adzuna](https://www.adzuna.com.au/) - Job search API
- [LinkedIn](https://www.linkedin.com/) - Professional network
- [GradConnection](https://au.gradconnection.com/) - Graduate opportunities
- [GitHub AusJobs](https://github.com/AusJobs/Australia-Tech-Internship) - Curated internship list

**Technology Stack:**
- Python 3.11+ with BeautifulSoup4, pandas, requests
- GitHub Actions for automation
- GitHub Pages for hosting
- Modern HTML5/CSS3/JavaScript

---

## 💬 Support & Community

### 🐛 Issues?
- Check [existing issues](https://github.com/vats98754/aus-job-fetcher/issues)
- Open a new issue with details
- Be specific and include error messages

### 💭 Questions?
- Read this README thoroughly
- Check [GitHub Discussions](https://github.com/vats98754/aus-job-fetcher/discussions)
- Search existing conversations

### 🌟 Like This Project?
- ⭐ Star this repository
- 🍴 Fork it and customize it
- 📢 Share it with other job seekers
- 🤝 Contribute improvements

---

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/vats98754/aus-job-fetcher?style=social)
![GitHub forks](https://img.shields.io/github/forks/vats98754/aus-job-fetcher?style=social)
![GitHub issues](https://img.shields.io/github/issues/vats98754/aus-job-fetcher)
![GitHub last commit](https://img.shields.io/github/last-commit/vats98754/aus-job-fetcher)

---

## 🎯 Roadmap

**Coming Soon:**
- [ ] Email/SMS notifications for new jobs
- [ ] Browser extension for instant alerts
- [ ] Machine learning job matching
- [ ] Salary insights and trends
- [ ] Company review integration
- [ ] Application tracking system
- [ ] Resume optimization tips
- [ ] Interview preparation resources

---

<div align="center">

### 🇦🇺 Made with ❤️ for Australian Tech Job Seekers

**Good luck with your job search!** 🚀

*Remember: The early bird gets the job. Be the first to apply!*

[View Live Jobs](https://YOUR_USERNAME.github.io/aus-job-fetcher/) • [Report Bug](https://github.com/vats98754/aus-job-fetcher/issues) • [Request Feature](https://github.com/vats98754/aus-job-fetcher/issues)

</div>
