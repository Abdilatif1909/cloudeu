# Sun'iy intellekt asoslari LMS

Production-ready LMS for the university course **Sun'iy intellekt asoslari**, packaged for Ahost cPanel Python Hosting with Passenger.

## Stack

- Django 5, Django REST Framework, SQLite production fallback, PostgreSQL support, JWT, CORS, drf-spectacular
- React, Vite, React Router, Axios, Bootstrap 5
- WhiteNoise static serving and cPanel Passenger WSGI

## CMS Features

- Admin-managed lectures with PDF preview, counters, publishing, and previous/next navigation
- Practical materials with PDF, examples, source files, difficulty, and estimated time
- YouTube lessons with automatic video ID and thumbnail extraction
- Resource library for PDFs, Office files, archives, images, CSV, Python, and notebooks
- Teacher JSON quiz importer with validation and duplicate prevention
- Admin dashboard cards, latest uploads, recent activity, global search, and statistics API

## Structure

```text
backend/
  api/
  apps/
    accounts/ courses/ lessons/ materials/ videos/ quizzes/ progress/ glossary/ common/
  config/
  media/
frontend/
  src/
    components/ pages/ layouts/ services/ hooks/ assets/
docs/
passenger_wsgi.py
.htaccess
```

## Quick Start

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Build frontend assets for Django:

```bash
cd frontend
npm install
npm run build:cpanel
```

Open:

- Admin: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/api/docs/`

## Documentation

- [Database schema](docs/database-schema.md)
- [API endpoints](docs/api-endpoints.md)
- [Installation guide](docs/installation.md)
- [Ahost deployment](DEPLOYMENT.md)
