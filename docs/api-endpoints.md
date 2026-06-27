# API Endpoints

Swagger UI is available at `/api/docs/`, ReDoc at `/api/redoc/`, and OpenAPI JSON at `/api/schema/`.

## Auth

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/auth/login/` | Login and receive access/refresh JWT |
| POST | `/api/v1/auth/refresh/` | Refresh access token |
| POST | `/api/v1/auth/logout/` | Blacklist refresh token |
| GET/PATCH | `/api/v1/auth/profile/` | Current user profile |
| POST | `/api/v1/auth/change-password/` | Change password |

## LMS Resources

All list endpoints support pagination. Most support `search`, `ordering`, and declared filter fields.

| Resource | Endpoint |
| --- | --- |
| Courses | `/api/v1/courses/` |
| Lessons | `/api/v1/lessons/` |
| Lecture PDFs | `/api/v1/lecture-materials/` |
| Practice PDFs | `/api/v1/practice-materials/` |
| Resource library | `/api/v1/resources/` |
| YouTube videos | `/api/v1/videos/` |
| Quizzes | `/api/v1/quizzes/` |
| Questions | `/api/v1/questions/` |
| Student progress | `/api/v1/progress/` |
| Quiz results | `/api/v1/quiz-results/` |
| Progress summary | `/api/v1/progress-summary/` |
| Glossary | `/api/v1/glossary/` |
| Global search | `/api/v1/search/?q=ai` |
| Statistics | `/api/v1/statistics/` |

## CMS Actions

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/lecture-materials/{id}/preview/` | Preview PDF and increment view counter |
| GET | `/api/v1/lecture-materials/{id}/download/` | Download PDF and increment download counter |
| GET | `/api/v1/lecture-materials/{id}/navigation/` | Previous and next lecture |
| GET | `/api/v1/practice-materials/{id}/files/` | Attached PDF/example/source file URLs |
| GET | `/api/v1/resources/{id}/download/` | Download library resource |
| GET | `/api/v1/videos/{id}/related/` | Related videos in the same course |
| GET | `/api/v1/videos/{id}/navigation/` | Previous and next video |
| POST | `/api/v1/videos/{id}/watch-progress/` | Save watch progress |
| POST | `/api/v1/quizzes/import-json/` | Import or update quiz questions from `quiz.json` |

Teachers and super admins can create, update, and delete course content. Students can read content and manage only their own progress and quiz results.
