# Scheduling Daily Stock Analysis

This guide shows how to automatically run the stock analyzer every morning at 9am ET and receive a summary report.

## Quick Setup

### Step 1: Configure the Daily Runner

```bash
cd stock_analyzer

# Copy the example config
cp daily_config.json.example daily_config.json

# Edit the config file
nano daily_config.json  # or use any text editor
```

**Edit `daily_config.json`:**
```json
{
  "universe": "sp500",
  "max_stocks": 500,
  "top_n_stocks": 20,
  "output_directory": "daily_reports",

  "email_enabled": true,
  "email_from": "your_email@gmail.com",
  "email_to": ["your_email@gmail.com"],
  "email_password": "your_app_password",
  "send_csv": true
}
```

### Step 2: Test the Daily Runner

```bash
python daily_runner.py --config daily_config.json
```

This will:
- Analyze the stocks (takes 30-60 minutes for S&P 500)
- Save results to `daily_reports/` folder
- Send an email report (if enabled)

### Step 3: Set Up Scheduling

Choose the method for your operating system:

---

## Method 1: Linux/Mac - Cron Job (Recommended)

### Setup Cron Job

1. **Get the full path to Python and the script:**
```bash
which python3
# Output: /usr/bin/python3 (or similar)

pwd
# Output: /home/user/random/stock_analyzer
```

2. **Open crontab editor:**
```bash
crontab -e
```

3. **Add this line for 9am ET (adjust timezone as needed):**

**If your system is in ET timezone:**
```bash
0 9 * * * cd /home/user/random/stock_analyzer && /usr/bin/python3 daily_runner.py >> daily_reports/cron.log 2>&1
```

**If your system is in UTC (convert 9am ET to UTC):**
- 9am ET = 2pm UTC (during EST)
- 9am ET = 1pm UTC (during EDT)

```bash
# During EST (November - March)
0 14 * * * cd /home/user/random/stock_analyzer && /usr/bin/python3 daily_runner.py >> daily_reports/cron.log 2>&1

# During EDT (March - November)
0 13 * * * cd /home/user/random/stock_analyzer && /usr/bin/python3 daily_runner.py >> daily_reports/cron.log 2>&1
```

4. **Save and exit** (Ctrl+X, then Y, then Enter in nano)

5. **Verify cron job is set:**
```bash
crontab -l
```

### Cron Time Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └── Day of week (0-7, 0 and 7 = Sunday)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
│ └──────── Hour (0-23)
└────────── Minute (0-59)
```

**Examples:**
```bash
# Every day at 9am
0 9 * * *

# Weekdays only at 9am
0 9 * * 1-5

# Monday, Wednesday, Friday at 9am
0 9 * * 1,3,5

# Every 6 hours
0 */6 * * *
```

### Check Cron Logs

```bash
# View the log file
tail -f daily_reports/cron.log

# Check system cron logs
grep CRON /var/log/syslog  # Ubuntu/Debian
grep CRON /var/log/cron    # CentOS/RedHat
```

---

## Method 2: Windows - Task Scheduler

### Step 1: Create a Batch Script

Create `run_daily_analysis.bat` in the `stock_analyzer` folder:

```batch
@echo off
cd /d C:\path\to\random\stock_analyzer
python daily_runner.py --config daily_config.json >> daily_reports\windows.log 2>&1
```

### Step 2: Open Task Scheduler

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task" in the right panel

### Step 3: Configure the Task

**General Tab:**
- Name: `Daily Stock Analysis`
- Description: `Runs stock market analysis at 9am ET daily`
- Run whether user is logged on or not: ✓

**Triggers Tab:**
- Click "New"
- Begin the task: `On a schedule`
- Daily, Recur every: `1 days`
- Start: `9:00:00 AM`
- Time zone: `(UTC-05:00) Eastern Time (US & Canada)`
- Enabled: ✓

**Actions Tab:**
- Click "New"
- Action: `Start a program`
- Program/script: `C:\path\to\random\stock_analyzer\run_daily_analysis.bat`
- Start in: `C:\path\to\random\stock_analyzer`

**Conditions Tab:**
- Uncheck "Start the task only if the computer is on AC power" (if laptop)

**Settings Tab:**
- Allow task to be run on demand: ✓
- Run task as soon as possible after a scheduled start is missed: ✓

### Step 4: Test the Task

Right-click the task → "Run"

Check `daily_reports\windows.log` for output.

---

## Method 3: Python Scheduler (Cross-Platform)

For a pure Python solution that runs continuously:

### Create `scheduler_daemon.py`:

```python
#!/usr/bin/env python3
"""Continuous scheduler for daily stock analysis."""
import schedule
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_analysis():
    """Run the daily analysis."""
    logging.info("Starting daily stock analysis...")
    try:
        result = subprocess.run(
            ['python', 'daily_runner.py', '--config', 'daily_config.json'],
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout
        )
        logging.info(f"Analysis completed with return code {result.returncode}")
        if result.returncode != 0:
            logging.error(f"Error output: {result.stderr}")
    except Exception as e:
        logging.error(f"Failed to run analysis: {e}")

# Schedule the job
schedule.every().day.at("09:00").do(run_analysis)

logging.info("Stock Analysis Scheduler started")
logging.info("Scheduled to run daily at 09:00 ET")

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

### Install schedule library:
```bash
pip install schedule
```

### Run as a background service:

**Linux/Mac:**
```bash
# Run in background
nohup python scheduler_daemon.py &

# Check if running
ps aux | grep scheduler_daemon

# View logs
tail -f scheduler.log
```

**Windows:**
```batch
# Run in background (PowerShell)
Start-Process python -ArgumentList "scheduler_daemon.py" -WindowStyle Hidden
```

### Make it persistent (Linux systemd):

Create `/etc/systemd/system/stock-analyzer.service`:

```ini
[Unit]
Description=Daily Stock Analysis Scheduler
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/random/stock_analyzer
ExecStart=/usr/bin/python3 scheduler_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable stock-analyzer
sudo systemctl start stock-analyzer
sudo systemctl status stock-analyzer
```

---

## Method 4: Cloud/Server Deployment

### Deploy to a Cloud Server (AWS EC2, DigitalOcean, etc.)

1. **Launch a small Linux server** (t2.micro is sufficient)

2. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3-pip git -y
```

3. **Clone your repository:**
```bash
git clone https://github.com/younghub23/random.git
cd random
git checkout claude/cyberpunk-snake-game-01MwcFeUDrX9i9oB8ckFEequ
cd stock_analyzer
```

4. **Install Python packages:**
```bash
pip3 install -r requirements.txt
```

5. **Configure daily runner:**
```bash
cp daily_config.json.example daily_config.json
nano daily_config.json
```

6. **Set up cron job:**
```bash
crontab -e
```

Add (9am ET = 2pm UTC):
```
0 14 * * * cd /home/ubuntu/random/stock_analyzer && /usr/bin/python3 daily_runner.py
```

7. **Ensure server stays running** (set instance to not stop)

---

## Email Setup (Gmail)

### Generate App Password for Gmail:

1. Go to Google Account settings: https://myaccount.google.com/
2. Security → 2-Step Verification (enable if not already)
3. Security → App passwords
4. Select app: "Mail", Select device: "Other"
5. Enter "Stock Analyzer" → Generate
6. Copy the 16-character password
7. Use this in `daily_config.json` as `email_password`

### Configuration Example:

```json
{
  "email_enabled": true,
  "email_from": "your.email@gmail.com",
  "email_to": ["your.email@gmail.com", "another@example.com"],
  "email_password": "xxxx xxxx xxxx xxxx",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```

### Other Email Providers:

**Outlook/Hotmail:**
```json
{
  "smtp_server": "smtp-mail.outlook.com",
  "smtp_port": 587
}
```

**Yahoo:**
```json
{
  "smtp_server": "smtp.mail.yahoo.com",
  "smtp_port": 587
}
```

**Custom SMTP:**
```json
{
  "smtp_server": "smtp.yourprovider.com",
  "smtp_port": 587
}
```

---

## Customizing the Report

### Quick Settings in `daily_config.json`:

```json
{
  // Analyze only top 100 stocks (faster)
  "max_stocks": 100,

  // Show top 50 stocks in report
  "top_n_stocks": 50,

  // Only include stocks scoring >= 70
  "min_score": 70,

  // Use NASDAQ 100 instead of S&P 500
  "universe": "nasdaq100",

  // Faster analysis (may hit rate limits)
  "delay": 0.2,

  // Don't attach CSV to email
  "send_csv": false
}
```

### Universe Options:

- `"sp500"` - S&P 500 (~500 stocks)
- `"sp1000"` - Russell 1000 (~1000 stocks)
- `"nasdaq100"` - NASDAQ 100 (~100 tech stocks)

---

## Output Files

Each day's run creates:

```
daily_reports/
├── daily_analysis_20240115.json           # Full data
├── daily_analysis_20240115.csv            # All stocks spreadsheet
├── daily_analysis_20240115_top50.csv      # Top 50 only
├── daily_summary_20240115.txt             # Text summary
└── cron.log                                # Execution logs
```

---

## Monitoring & Troubleshooting

### Check if the job ran:

**Linux/Mac:**
```bash
ls -lt daily_reports/
tail daily_reports/cron.log
```

**Windows:**
```batch
dir daily_reports\ /O-D
type daily_reports\windows.log
```

### Common Issues:

**1. Python not found:**
- Use full path: `/usr/bin/python3` instead of `python3`
- Check: `which python3`

**2. Cron job not running:**
- Check cron service: `sudo systemctl status cron`
- Check logs: `grep CRON /var/log/syslog`
- Test manually: `/usr/bin/python3 /full/path/to/daily_runner.py`

**3. Email not sending:**
- Verify app password (not regular password)
- Check Gmail "Less secure app access" is OFF (use App Password instead)
- Test SMTP: `telnet smtp.gmail.com 587`

**4. Yahoo Finance 403 errors:**
- Increase delay in config: `"delay": 1.0`
- Reduce max_stocks: `"max_stocks": 100`
- Run at different times to avoid peak hours

**5. Script timeout:**
- For 500+ stocks, increase system timeout
- Or split into multiple smaller runs

---

## Tips for Production Use

1. **Start small:** Test with 50 stocks before scaling to 500+
2. **Monitor first week:** Check logs daily to ensure it runs correctly
3. **Backup config:** Keep `daily_config.json` backed up
4. **Rotate logs:** Set up log rotation to prevent disk fill
5. **Set alerts:** Monitor that you receive the email each day
6. **Handle holidays:** Script runs every day - decide if you want weekends/holidays only

---

## Advanced: Weekdays Only

**Cron (weekdays only):**
```bash
# Monday-Friday at 9am
0 9 * * 1-5 cd /home/user/random/stock_analyzer && python3 daily_runner.py
```

**Windows Task Scheduler:**
- In Triggers → Weekly
- Check: Monday, Tuesday, Wednesday, Thursday, Friday

**Python scheduler:**
```python
# Only run on weekdays
schedule.every().monday.at("09:00").do(run_analysis)
schedule.every().tuesday.at("09:00").do(run_analysis)
schedule.every().wednesday.at("09:00").do(run_analysis)
schedule.every().thursday.at("09:00").do(run_analysis)
schedule.every().friday.at("09:00").do(run_analysis)
```

---

## Support

If you encounter issues:
1. Check the logs first
2. Test the script manually
3. Verify your config file is valid JSON
4. Check that all dependencies are installed

For detailed batch analysis options, see [BATCH_ANALYZER_GUIDE.md](BATCH_ANALYZER_GUIDE.md)
