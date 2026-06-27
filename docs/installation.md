# Installation Guide

## Local Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/initial_course.json
python manage.py createsuperuser
python manage.py runserver
```

## Local Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend: `http://localhost:5173`

Backend API: `http://localhost:8000/api/v1/`

Swagger: `http://localhost:8000/api/docs/`

## cPanel Static Build

Before deploying to Ahost, build the React app with static asset paths suitable for Django and WhiteNoise:

```bash
bash scripts/build_cpanel_static.sh
cd backend
python manage.py collectstatic --noinput
```

The build output is copied to `backend/templates/frontend/` and `backend/static/frontend/`.

## Quiz JSON Import

Teachers can import a quiz from the API or Swagger with `POST /api/v1/quizzes/import-json/` using multipart form field `file`.

```json
{
  "lesson": 1,
  "title": "AI Basics",
  "questions": [
    {
      "question": "What is AI?",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "explanation": "Explanation text"
    }
  ]
}
```
