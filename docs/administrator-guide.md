# Administrator Guide

## Responsibilities
- Manage universities, faculties, departments, academic years, semesters, education directions, groups, users, courses, lessons, resources, videos, quizzes, enrollments, audit logs, and certificates from Django Admin.
- Assign each course to a department, semester, and teacher.
- Assign students to faculty, direction, academic group, and current semester.
- Monitor audit logs for login, upload, edit, delete, import, and export activity.

## Daily Operations
1. Create or update academic structure.
2. Create teacher and student accounts.
3. Create courses and assign responsible teachers.
4. Enroll students manually, in bulk, or via CSV.
5. Review dashboard counts, latest uploads, recent activity, and audit logs.
6. Use `/api/docs/` for API verification.

## Security Operations
- Keep `DJANGO_DEBUG=False` in production.
- Rotate `DJANGO_SECRET_KEY` and database passwords through environment variables.
- Review `/admin/common/auditlog/` regularly.
- Enforce HTTPS in cPanel and keep trusted origins aligned with the production domain.
