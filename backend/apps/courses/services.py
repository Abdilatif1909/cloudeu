import csv
from io import StringIO

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from apps.lessons.models import Lesson

from .models import Course, CourseEnrollment


class EnrollmentService:
    @staticmethod
    @transaction.atomic
    def bulk_enroll(course: Course, student_ids: list[int], group=None, status: str = CourseEnrollment.Status.ACTIVE) -> dict:
        User = get_user_model()
        students = User.objects.filter(id__in=student_ids, role=User.Role.STUDENT)
        created = 0
        updated = 0
        for student in students:
            _, was_created = CourseEnrollment.objects.update_or_create(
                student=student,
                course=course,
                defaults={"group": group or student.academic_group, "status": status},
            )
            if was_created:
                created += 1
            else:
                updated += 1
        return {"created": created, "updated": updated, "missing": max(len(set(student_ids)) - students.count(), 0)}

    @staticmethod
    def import_csv(course: Course, uploaded_file) -> dict:
        try:
            content = uploaded_file.read().decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise serializers.ValidationError({"file": "CSV file must be UTF-8 encoded."}) from exc

        rows = csv.DictReader(StringIO(content))
        required = {"username"}
        if not required.issubset(set(rows.fieldnames or [])):
            raise serializers.ValidationError({"file": "CSV must include a username column."})

        User = get_user_model()
        student_ids = []
        for row in rows:
            username = (row.get("username") or "").strip()
            if not username:
                continue
            student = User.objects.filter(username=username, role=User.Role.STUDENT).first()
            if student:
                student_ids.append(student.id)
        return EnrollmentService.bulk_enroll(course, student_ids)


class CourseCloneService:
    @staticmethod
    @transaction.atomic
    def clone_course(course: Course, *, title: str | None = None, code: str | None = None, teacher=None) -> Course:
        clone = Course.objects.create(
            title=title or f"{course.title} Copy",
            code=code or f"{course.code}-COPY",
            description=course.description,
            department=course.department,
            academic_semester=course.academic_semester,
            teacher=teacher or course.teacher,
            semester=course.semester,
            credits=course.credits,
            image=course.image,
            is_active=False,
            is_published=False,
            is_archived=False,
        )
        for lesson in course.lessons.all().order_by("order"):
            Lesson.objects.create(
                course=clone,
                lesson_number=lesson.lesson_number,
                title=lesson.title,
                description=lesson.description,
                order=lesson.order,
            )
        return clone

    @staticmethod
    def duplicate_lesson(lesson: Lesson) -> Lesson:
        next_order = (Lesson.objects.filter(course=lesson.course).order_by("-order").values_list("order", flat=True).first() or 0) + 1
        next_number = (Lesson.objects.filter(course=lesson.course).order_by("-lesson_number").values_list("lesson_number", flat=True).first() or 0) + 1
        return Lesson.objects.create(
            course=lesson.course,
            lesson_number=next_number,
            title=f"{lesson.title} Copy",
            description=lesson.description,
            order=next_order,
        )
