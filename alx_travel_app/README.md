# CRM Celery Tasks Setup Guide

This guide provides step-by-step instructions for setting up and running Celery tasks in the CRM application.

## 📋 Prerequisites

- Python 3.8+
- Django 4.2+
- Redis Server
- Virtual environment (recommended)

---

## 🚀 Installation Steps

### Step 1: Install Redis

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### On macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

#### On Windows:
Download and install Redis from: https://github.com/microsoftarchive/redis/releases

Or use WSL (Windows Subsystem for Linux) and follow Ubuntu instructions.

#### Verify Redis is Running:
```bash
redis-cli ping
# Should return: PONG
```

---

### Step 2: Install Python Dependencies

```bash
# Activate your virtual environment (if using one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

**Required packages include:**
- `celery>=5.3.0`
- `django-celery-beat>=2.5.0`
- `redis>=5.0.0`

---

### Step 3: Run Django Migrations

```bash
python manage.py migrate
```

This will create the necessary database tables for:
- Django Celery Beat schedules
- Periodic tasks
- Other CRM models

---

## 🎯 Running Celery

You need to run **three separate processes** (in different terminal windows/tabs):

### Terminal 1: Django Development Server
```bash
python manage.py runserver
```

### Terminal 2: Celery Worker
```bash
celery -A crm worker -l info
```

**What this does:**
- Starts the Celery worker process
- Processes asynchronous tasks
- Logs task execution and results
- `-A crm` specifies the Celery app
- `-l info` sets logging level to INFO

### Terminal 3: Celery Beat Scheduler
```bash
celery -A crm beat -l info
```

**What this does:**
- Starts the Celery Beat scheduler
- Triggers periodic tasks based on schedule
- Runs `generate_crm_report` every Monday at 6:00 AM
- `-l info` sets logging level to INFO

---

## 📊 Scheduled Tasks

### Weekly CRM Report

**Task:** `crm.tasks.generate_crm_report`

**Schedule:** Every Monday at 6:00 AM

**What it does:**
1. Queries GraphQL endpoint for:
   - Total number of customers
   - Total number of orders
   - Total revenue (sum of order amounts)
2. Generates a report with timestamp
3. Logs to `/tmp/crm_report_log.txt`

**Log Format:**
```
YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue.
```

---

## 🧪 Testing

### Test the Celery Worker

```bash
# In Python shell
python manage.py shell
```

```python
from crm.tasks import generate_crm_report

# Run task synchronously (for testing)
result = generate_crm_report()
print(result)
```

### Test the Celery Beat Schedule

```bash
# Run Celery Beat in foreground to see schedules
celery -A crm beat -l debug
```

You should see output like:
```
Scheduler: Sending due task generate-crm-report (crm.tasks.generate_crm_report)
```

### Manually Trigger the Task

```bash
# In Python shell
python manage.py shell
```

```python
from crm.tasks import generate_crm_report

# Queue the task
result = generate_crm_report.delay()
print(f"Task ID: {result.id}")
```

---

## 📝 Verify Logs

### Check CRM Report Log

```bash
cat /tmp/crm_report_log.txt
```

**Expected output:**
```
2026-01-11 06:00:00 - Report: 150 customers, 342 orders, 45678.90 revenue.
2026-01-18 06:00:00 - Report: 165 customers, 389 orders, 52341.25 revenue.
```

### Monitor in Real-Time

```bash
# Watch the log file for updates
tail -f /tmp/crm_report_log.txt
```

---

## 🔧 Troubleshooting

### Redis Connection Error

**Error:** `Error 111 connecting to localhost:6379. Connection refused.`

**Solution:**
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Start Redis if not running
sudo systemctl start redis-server

# Or on macOS
brew services start redis
```

### Celery Worker Not Processing Tasks

**Check:**
1. Ensure Redis is running
2. Verify Celery worker is running: `celery -A crm worker -l info`
3. Check for errors in worker logs
4. Verify task is registered:
   ```bash
   celery -A crm inspect registered
   ```

### Task Not Executing on Schedule

**Check:**
1. Ensure Celery Beat is running: `celery -A crm beat -l info`
2. Verify schedule in settings.py
3. Check Beat logs for schedule execution
4. Run migrations: `python manage.py migrate`

### GraphQL Endpoint Not Responding

**Check:**
1. Django development server is running
2. GraphQL endpoint is accessible at `http://localhost:8000/graphql`
3. Schema is properly configured in settings.py

### Permission Denied for Log File

**Solution:**
```bash
# Create log file with proper permissions
sudo touch /tmp/crm_report_log.txt
sudo chmod 666 /tmp/crm_report_log.txt
```

---

## 🛠️ Production Deployment

### Using Supervisor (Recommended)

Install Supervisor:
```bash
sudo apt-get install supervisor
```

Create configuration file `/etc/supervisor/conf.d/crm-celery.conf`:
```ini
[program:crm-celery-worker]
command=/path/to/venv/bin/celery -A crm worker -l info
directory=/path/to/alx-backend-graphql_crm
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.error.log

[program:crm-celery-beat]
command=/path/to/venv/bin/celery -A crm beat -l info
directory=/path/to/alx-backend-graphql_crm
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.error.log
```

Reload Supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### Using Systemd

Create service files:

`/etc/systemd/system/crm-celery-worker.service`:
```ini
[Unit]
Description=CRM Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/alx-backend-graphql_crm
ExecStart=/path/to/venv/bin/celery -A crm worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/crm-celery-beat.service`:
```ini
[Unit]
Description=CRM Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/alx-backend-graphql_crm
ExecStart=/path/to/venv/bin/celery -A crm beat -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable crm-celery-worker crm-celery-beat
sudo systemctl start crm-celery-worker crm-celery-beat
```

---

## 📚 Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django-Celery-Beat Documentation](https://django-celery-beat.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html#tips-and-best-practices)

---

## ✅ Quick Start Checklist

- [ ] Redis installed and running
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Migrations run (`python manage.py migrate`)
- [ ] Django server running (`python manage.py runserver`)
- [ ] Celery worker running (`celery -A crm worker -l info`)
- [ ] Celery beat running (`celery -A crm beat -l info`)
- [ ] Log file created and accessible (`/tmp/crm_report_log.txt`)
- [ ] GraphQL endpoint accessible (`http://localhost:8000/graphql`)

---

**Happy Task Scheduling! 🎉**
