# sbir-tracker
SBIR/STTR Active Topics Scraper
This project automatically collects and saves all currently active SBIR/STTR topics from the DoD SBIR/STTR Topics App.

Overview
The DoD SBIR/STTR Topics website loads content dynamically with JavaScript, so traditional HTTP requests can't access the data. This scraper uses Playwright (a headless browser automation tool) to:

Load the webpage fully
Wait for the topics table to appear
Extract and parse the table data
Save results to CSV files
Features
Automated scraping using GitHub Actions
Saves both timestamped and latest versions of the data
Runs on a configurable schedule (daily by default)
Can be triggered manually via GitHub Actions
Includes error handling and logging
Files
sbir_scraper.py - Main Python scraper script
.github/workflows/scrape_topics.yml - GitHub Actions workflow
requirements.txt - Python dependencies
active_sbir_topics.csv - Latest scraped data (auto-generated)
active_sbir_topics_YYYYMMDD_HHMMSS.csv - Timestamped versions (auto-generated)
Setup
Local Development
Clone the repository:
bash
git clone [your-repo-url]
cd [repo-name]
Install Python dependencies:
bash
pip install -r requirements.txt
Install Playwright browsers:
bash
playwright install chromium
playwright install-deps
Run the scraper:
bash
python sbir_scraper.py
GitHub Actions Setup
Copy the workflow file to .github/workflows/scrape_topics.yml
The workflow will automatically run:
Daily at 6 AM UTC (configurable in the workflow file)
On every push to the main branch
When manually triggered from the Actions tab
Configuration
Adjusting the Schedule
Edit the cron expression in .github/workflows/scrape_topics.yml:

yaml
schedule:
  - cron: '0 6 * * *'  # Daily at 6 AM UTC
Use crontab.guru to help create custom schedules.

Manual Trigger
Go to the Actions tab in your GitHub repository
Select "Scrape SBIR/STTR Topics"
Click "Run workflow"
Output
The scraper saves data in CSV format with:

All columns from the original topics table
An additional scrape_timestamp column
Both a timestamped file and active_sbir_topics.csv (latest version)
Troubleshooting
If the scraper fails:

Check if the website structure has changed
Verify the table selector in the script
Increase timeout values if the site loads slowly
Check GitHub Actions logs for specific error messages
Future Enhancements
Track award statuses (not implemented in current version)
Add data validation and cleaning
Email notifications for new topics
Historical data analysis
License
[Your chosen license]

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

