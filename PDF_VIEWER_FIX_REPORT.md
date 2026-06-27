# PDF Viewer Fix Report

## Root Cause

Django was serving media PDFs correctly from `/media/...`, but the frontend was not consistently opening those direct media URLs.

The Course Detail page linked lecture and practice rows to React SPA routes:

- `/lectures/:id`
- `/practices/:id`

The Lecture page embedded PDFs through the API preview route:

- `/api/v1/lecture-materials/:id/preview/`

Those routes can work as application pages, but they are not the verified direct PDF resources. The reliable PDF resources are the serializer-provided `pdf_file` values under `/media/...`.

## Components Audited

- `frontend/src/pages/CourseDetailPage.jsx`
- `frontend/src/pages/LecturePage.jsx`
- `frontend/src/pages/PracticePage.jsx`
- `frontend/src/services/lmsService.js`
- `frontend/src/App.jsx`

## Actual PDF URL Source

The API serializers expose direct media URLs:

- `LectureMaterialSerializer.pdf_file`
- `PracticeMaterialSerializer.pdf_file`
- `PracticeMaterialViewSet.files().pdf_file`

Example verified API payload values:

```text
http://localhost/media/materials/lectures/1-mavzu.pdf
http://localhost/media/materials/practices/1_Maqsad_va_muammoni_shakllantirish.pdf
```

The frontend now normalizes these to same-origin paths:

```text
/media/materials/lectures/1-mavzu.pdf
/media/materials/practices/1_Maqsad_va_muammoni_shakllantirish.pdf
```

## Fix

Added:

- `frontend/src/utils/mediaUrl.js`

Updated:

- Course Detail lecture rows now open `item.pdf_file` directly in a new browser tab.
- Course Detail practice rows now open `item.pdf_file` directly in a new browser tab.
- Lecture iframe now uses `lecture.pdf_file` instead of the API preview route.
- Lecture primary PDF button now opens the direct media PDF in a new browser tab.
- Practice iframe now uses `practice.pdf_file`.
- Practice file links now use direct normalized media URLs and open in a new browser tab.

## Router And SPA Interception Check

React Router still owns application pages:

- `/lectures/:lectureId`
- `/practices/:practiceId`
- `/videos/:videoId`

PDF links now use normal anchors with:

```jsx
target="_blank"
rel="noreferrer"
```

Because the link `href` is `/media/...`, the request goes directly to the server media path and is not handled by React Router.

## iframe/embed/object/window.open Audit

- Lecture PDF iframe: uses direct `/media/...` URL.
- Practice PDF iframe: uses direct `/media/...` URL.
- No `<embed>` usage found.
- No `<object>` usage found.
- No `window.open()` usage found.

## Verification

Commands run:

```bash
python manage.py check
python manage.py migrate --noinput
python manage.py import_ai_course_content
python manage.py collectstatic --noinput
npm ci
powershell -ExecutionPolicy Bypass -File scripts/build_cpanel_static.ps1
```

URL normalization verified:

```text
https://cloude.uz/media/materials/lectures/1-mavzu.pdf
-> /media/materials/lectures/1-mavzu.pdf

http://localhost/media/materials/practices/1.pdf
-> /media/materials/practices/1.pdf
```

Production bundle verified:

- `backend/templates/frontend/index.html` points to the rebuilt frontend asset.
- `backend/static/frontend/assets/LecturePage-*.js` contains direct PDF open behavior.
- `backend/static/frontend/assets/CourseDetailPage-*.js` contains direct media link behavior.

## Expected Browser Behavior

Clicking a lecture PDF row on the course detail page opens the direct PDF URL in a new tab:

```text
/media/materials/lectures/<file>.pdf
```

Clicking a practice PDF row opens:

```text
/media/materials/practices/<file>.pdf
```

These URLs are served by Django/cPanel media handling as `application/pdf`.
