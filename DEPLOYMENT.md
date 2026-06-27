# Ahost cPanel Passenger Deployment

This repository is production-only for Ahost cPanel Python Hosting with Passenger.

It does not use GitHub Pages, Cloudflare Pages, or GitHub Actions deployment.

## Target Layout

Clone path on Ahost:

```text
/home/cloudeu2/lms
```

Python application:

```text
Python: 3.12.13
Virtualenv: /home/cloudeu2/virtualenv/lms/3.12/
Application root: /home/cloudeu2/lms
Startup file: passenger_wsgi.py
Entry point: application
```

## Files Used By Passenger

```text
passenger_wsgi.py
backend/config/wsgi.py
backend/config/settings.py
```

The root `.htaccess` keeps `/static/*` and `/media/*` out of the SPA fallback and maps static files to:

```text
backend/staticfiles/
```

## Environment

Create `/home/cloudeu2/lms/backend/.env`.

Minimum SQLite production configuration:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=cloude.uz,www.cloude.uz,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://cloude.uz,https://www.cloude.uz
DJANGO_CORS_ALLOWED_ORIGINS=https://cloude.uz,https://www.cloude.uz
DJANGO_CORS_ALLOW_CREDENTIALS=True
DJANGO_TIME_ZONE=Asia/Tashkent
DJANGO_LOG_LEVEL=INFO
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
DJANGO_CACHE_LOCATION=cloudeuz-cache
DJANGO_CACHE_TIMEOUT=300
DB_ENGINE=django.db.backends.sqlite3
SQLITE_NAME=/home/cloudeu2/lms/backend/db.sqlite3
POSTGRES_CONNECT_TIMEOUT=3
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
PASSWORD_MIN_LENGTH=10
LOGIN_LOCKOUT_ATTEMPTS=5
LOGIN_LOCKOUT_SECONDS=900
MAX_UPLOAD_SIZE=52428800
FILE_UPLOAD_MAX_MEMORY_SIZE=10485760
DATA_UPLOAD_MAX_MEMORY_SIZE=20971520
DRF_THROTTLE_ANON=100/hour
DRF_THROTTLE_USER=1000/hour
DRF_THROTTLE_LOGIN=10/minute
DRF_THROTTLE_UPLOAD=60/hour
```

PostgreSQL remains supported. To enable it, set `DATABASE_URL` or all PostgreSQL variables in `.env`.

## Install / Update

From cPanel Terminal or SSH:

```bash
cd /home/cloudeu2/lms
git pull origin main
source /home/cloudeu2/virtualenv/lms/3.12/bin/activate
pip install -r backend/requirements.txt
```

## Build Frontend For Django

If Node.js is available on hosting:

```bash
cd /home/cloudeu2/lms
bash scripts/build_cpanel_static.sh
```

If Node.js is not available on hosting, use the committed build already included under:

```text
backend/templates/frontend/index.html
backend/static/frontend/
```

## Database And Static Files

Run from the backend directory:

```bash
cd /home/cloudeu2/lms/backend
python manage.py check
python manage.py migrate
python manage.py import_ai_course_content
python manage.py collectstatic --noinput
```

`import_ai_course_content` scans the committed `pdf/maruza` and `pdf/amaliy` folders, creates the AI course lessons/material rows if the database is empty, attaches PDFs into `backend/media`, and imports the curated YouTube links.

## Restart Passenger

In cPanel:

1. Open **Setup Python App**.
2. Select the application for `cloude.uz`.
3. Click **Restart**.

Alternatively, touch Passenger restart file if supported:

```bash
mkdir -p /home/cloudeu2/lms/tmp
touch /home/cloudeu2/lms/tmp/restart.txt
```

## Verify

```bash
curl -I https://cloude.uz/static/frontend/assets/index-CkPxsyms.js
curl https://cloude.uz/health/
```

Expected static asset headers:

```text
HTTP/2 200
content-type: application/javascript
```

Expected health response:

```json
{"status":"ok"}
```

Expected home page title:

```text
Cloud Education Platform | cloude.uz
```

## Important cPanel Notes

- The domain document root must read the root `.htaccess` in `/home/cloudeu2/lms`, or the same `.htaccess` rules must be copied into the actual cPanel document root.
- Do not enable GitHub Pages for this repository.
- Do not add `CNAME` files.
- Do not add GitHub Actions deployment workflows.
- Static files must be served from `backend/staticfiles` after `collectstatic`.
