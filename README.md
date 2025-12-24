# 🇦🇺 Australian Job Scraper

An automated job aggregator that scrapes Australian job boards every 3 minutes and displays them on a GitHub Pages website.

![Jobs](https://img.shields.io/badge/dynamic/json?color=success&label=Total%20Jobs&query=length&url=https://YOUR_USERNAME.github.io/au-job-scraper/jobs.json)
![Workflow](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/au-job-scraper/scrape-jobs.yml?label=Scraper)

## 🎯 Features

- **Multi-Board Scraping**: Aggregates jobs from 6+ Australian job boards
- **Real-Time Updates**: Runs every 3 minutes via GitHub Actions
- **Beautiful UI**: Modern, responsive GitHub Pages website
- **Search & Filter**: Filter by source, location, and keywords
- **Export Options**: Download as CSV or JSON
- **Deduplication**: Automatically removes duplicate listings
- **Free Hosting**: Uses GitHub Pages for free hosting

## 📋 Supported Job Boards

| Source | Method | Status |
|--------|--------|--------|
| **SEEK** | Web Scraping | ✅ Active |
| **Indeed Australia** | RSS Feed | ✅ Active |
| **Adzuna** | Official API | ✅ Active (requires API key) |
| **Jora** | Web Scraping | ✅ Active |
| **LinkedIn** | JobSpy | ⚠️ Optional |
| **Glassdoor** | JobSpy | ⚠️ Optional |
| **Google Jobs** | JobSpy | ⚠️ Optional |

## 🚀 Quick Setup

### 1. Fork This Repository

Click the **Fork** button at the top right of this page.

### 2. Enable GitHub Pages

1. Go to your forked repo → **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: **GitHub Actions**
3. Save

### 3. Enable GitHub Actions

1. Go to **Actions** tab
2. Click "I understand my workflows, go ahead and enable them"

### 4. (Optional) Add Adzuna API Keys

For more job listings, add Adzuna API credentials:

1. Sign up at [Adzuna Developer](https://developer.adzuna.com/)
2. Create an application and get your API keys
3. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
4. Add two secrets:
   - `ADZUNA_APP_ID`: Your Adzuna App ID
   - `ADZUNA_APP_KEY`: Your Adzuna App Key

### 5. Run the Scraper

1. Go to **Actions** tab
2. Select "Scrape Australian Jobs"
3. Click "Run workflow"
4. Wait ~2 minutes for it to complete

### 6. View Your Jobs

Visit: `https://YOUR_USERNAME.github.io/au-job-scraper/`

## ⚙️ Configuration

### Customize Search Queries

Edit the workflow file `.github/workflows/scrape-jobs.yml`:

```yaml
inputs:
  queries:
    default: 'software engineer,developer,python,data engineer,devops'
  locations:
    default: 'Sydney,Melbourne,Brisbane,Perth,Adelaide'
```

### Change Scraping Frequency

The default is every 3 minutes. To change:

```yaml
schedule:
  - cron: '*/3 * * * *'  # Every 3 minutes
  # - cron: '*/5 * * * *'  # Every 5 minutes
  # - cron: '0 * * * *'    # Every hour
```

> ⚠️ **Note**: GitHub Actions has a limit of 2,000 minutes/month for free accounts. Running every 3 minutes uses ~1,440 minutes/day. Consider reducing frequency if you hit limits.

### Add More Job Boards

Edit `scraper.py` to add custom scrapers:

```python
class CustomScraper:
    def search(self, query: str, location: str = "") -> list[Job]:
        # Your scraping logic here
        pass
```

## 📊 Output Files

| File | Description |
|------|-------------|
| `jobs.csv` | All jobs in CSV format |
| `jobs.json` | All jobs in JSON format |
| `index.html` | Interactive web interface |

### CSV Schema

| Column | Description |
|--------|-------------|
| `id` | Unique job identifier |
| `title` | Job title |
| `company` | Company name |
| `location` | Job location |
| `url` | Direct link to job posting |
| `source` | Job board source |
| `salary` | Salary range (if available) |
| `date_posted` | When the job was posted |
| `job_type` | Full-time, part-time, contract, etc. |
| `description` | Job description snippet |
| `scraped_at` | When we scraped this job |

## 🔧 Local Development

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/au-job-scraper.git
cd au-job-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python scraper.py --queries "software engineer" "python developer" --locations "Sydney" "Melbourne"

# View results
open index.html  # On macOS
# or xdg-open index.html on Linux
# or start index.html on Windows
```

### Environment Variables

```bash
export ADZUNA_APP_ID="your_app_id"
export ADZUNA_APP_KEY="your_app_key"
```

## 📈 Usage Tips

### Finding Jobs Faster

1. **Customize queries**: Add specific technologies you know (React, Rust, AWS, etc.)
2. **Filter by source**: Different boards have different job types
3. **Use location filters**: Focus on cities where you can work
4. **Check frequently**: Jobs are updated every 3 minutes

### Applying Quickly

1. Click the "Apply →" button to go directly to the job posting
2. Keep your resume ready
3. Customize your cover letter based on the job description
4. Track applications in a spreadsheet

## ⚠️ Rate Limiting & Ethics

This scraper is designed for personal use. Please:

- Don't run excessively (the 3-minute default is reasonable)
- Respect robots.txt where applicable
- Don't use for commercial purposes without permission
- Be mindful of API rate limits

## 🐛 Troubleshooting

### No jobs appearing?

1. Check the Actions tab for errors
2. Verify API keys are set correctly
3. Try running manually with `workflow_dispatch`

### Rate limited?

- Reduce scraping frequency
- Add delays between requests in `scraper.py`
- Use proxies (for advanced users)

### Stale data?

- GitHub Actions caches may cause delays
- Manually trigger a workflow run
- Check the "Last updated" timestamp on the page

## 📝 License

MIT License - feel free to use and modify for personal use.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch
3. Submit a pull request

## 🔗 Related Resources

- [Adzuna API Documentation](https://developer.adzuna.com/)
- [SEEK](https://www.seek.com.au/)
- [Indeed Australia](https://au.indeed.com/)
- [Jora](https://au.jora.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

Made with ❤️ for Australian job seekers
