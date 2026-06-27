# Folder Structure

```text
backend/
  api/                 DRF router and API URL registration
  apps/accounts/       User model, auth, profile
  apps/common/         shared pagination, permissions, audit, health, search, stats
  apps/courses/        university hierarchy, courses, enrollment, cloning
  apps/lessons/        lesson ordering and duplication
  apps/materials/      lectures, practices, resources, upload validation
  apps/videos/         YouTube lessons and watch progress
  apps/quizzes/        quizzes, questions, JSON importer
  apps/progress/       student progress, notes, bookmarks, certificates, analytics
  config/              Django settings and root URLs
frontend/
  src/components/      reusable UI components
  src/layouts/         application layout
  src/pages/           route pages
  src/services/        API clients
docs/                  guides and diagrams
scripts/               backup and restore scripts
passenger_wsgi.py      cPanel Passenger WSGI entry point
.htaccess              cPanel rewrite/static routing rules
```
