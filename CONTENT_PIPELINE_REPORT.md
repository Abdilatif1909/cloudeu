# Content Pipeline Report

## Actual Model Names

- Lecture PDF model: `apps.materials.models.LectureMaterial`
- Practice PDF model: `apps.materials.models.PracticeMaterial`
- Video model: `apps.videos.models.VideoLesson`

The following imports are intentionally invalid because these models do not exist:

- `from apps.materials.models import Lecture`
- `from apps.videos.models import Video`

## Import Command Verification

Command:

```bash
python manage.py import_ai_course_content
```

Verified behavior:

- Scans `pdf/maruza`
- Scans `pdf/amaliy`
- Creates or updates `Course`
- Creates or updates `Lesson`
- Creates `LectureMaterial` rows
- Creates `PracticeMaterial` rows
- Creates `VideoLesson` rows
- Attaches PDF files into `backend/media`

Fresh SQLite import result:

- Courses: 1
- Lessons: 11
- Lecture materials: 11
- Practice materials: 4
- Videos: 11

## Serializer Verification

Verified serializers:

- `LectureMaterialSerializer` exposes `id`, `lesson`, `course_id`, `title`, `lecture_number`, `pdf_file`, and metadata fields.
- `PracticeMaterialSerializer` exposes `id`, `lesson`, `course_id`, `title`, `pdf_file`, `difficulty`, and timing fields.
- `VideoLessonSerializer` exposes `id`, `lesson`, `course_id`, `title`, `youtube_url`, `video_id`, `duration`, `thumbnail`, and `speaker`.
- `LessonSerializer` now exposes nested read-only `lecture_materials`, `practice_materials`, `videos`, `resources`, and `quizzes`.

## API Verification

Verified API calls with the same filters used by the frontend:

```text
/api/v1/courses/                                  -> 1 course
/api/v1/lessons/?course=1&ordering=order          -> 11 lessons
/api/v1/lecture-materials/?lesson__course=1       -> 11 lecture PDFs
/api/v1/practice-materials/?lesson__course=1      -> 4 practice PDFs
/api/v1/videos/?lesson__course=1                  -> 11 YouTube videos
```

Verified nested lesson payload:

- First lesson includes `lecture_materials: 1`
- First lesson includes `practice_materials: 1`
- First lesson includes `videos: 1`
- First lecture includes a `pdf_file` URL
- First video includes `video_id: wSR4mrZqe7Y`

## Frontend Verification

Course Detail page now consumes content through two compatible paths:

- Primary path: nested `lesson.lecture_materials`, `lesson.practice_materials`, and `lesson.videos`
- Secondary path: separate `/lecture-materials/`, `/practice-materials/`, and `/videos/` endpoint responses

The page deduplicates records by `id`, groups them by `lesson`, and displays:

```text
Course -> Lesson -> Lecture PDF
Course -> Lesson -> Practice PDF
Course -> Lesson -> Video
```

Sidebar totals now use the grouped content actually rendered on the page.

## Build And Check Results

Verified commands:

```bash
python manage.py check
python manage.py import_ai_course_content
npm run build
powershell -ExecutionPolicy Bypass -File scripts/build_cpanel_static.ps1
```

The cPanel build updated:

- `backend/templates/frontend/index.html`
- `backend/static/frontend/`

## Resolution

The backend data existed and the individual API endpoints returned records. The frontend was made resilient by exposing and consuming nested lesson content, removing reliance on separate resource requests as the only source for rendering PDFs and videos.
