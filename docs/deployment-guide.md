# Deployment Guide

## Requirements

- Ahost cPanel Python Application with Passenger
- Python 3.12
- Domain with HTTPS enabled in cPanel
- Strong `.env` values based on `.env.example`

## Production Start

```bash
cd /home/cloudeu2/lms
git pull origin main
source /home/cloudeu2/virtualenv/lms/3.12/bin/activate
pip install -r backend/requirements.txt
cd backend
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
```

Restart the Python application from cPanel after updating code or dependencies.

## Health Checks

- `/live/` process liveness
- `/ready/` database readiness
- `/health/` basic application health
- `/version/` deployed application version

## Backups

```bash
BACKUP_DIR=/backups/db ./scripts/backup_db.sh
./scripts/restore_db.sh /backups/db/lms-YYYYMMDD-HHMMSS.dump
BACKUP_DIR=/backups/media MEDIA_ROOT=./backend/media ./scripts/backup_media.sh
./scripts/restore_media.sh /backups/media/media-YYYYMMDD-HHMMSS.tar.gz
```

## Verification

```bash
python manage.py check
python manage.py collectstatic --noinput
python -c "import sys; sys.path.insert(0, '..'); import passenger_wsgi; print(passenger_wsgi.application)"
```

Use [../DEPLOYMENT.md](../DEPLOYMENT.md) as the authoritative Ahost deployment checklist.
