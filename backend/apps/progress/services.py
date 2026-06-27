from datetime import timedelta
from uuid import uuid4

from django.db.models import Avg, Count, ExpressionWrapper, F, FloatField, Max, Sum
from django.utils import timezone

from apps.lessons.models import Lesson
from apps.materials.models import LectureMaterial, PracticeMaterial, Resource
from apps.videos.models import VideoLesson, VideoWatchProgress

from .models import Certificate, LearningEvent, QuizResult, StudentProgress


PROGRESS_EVENT_FIELD = {
    LearningEvent.EventType.LECTURE_VIEWED: "lecture_viewed",
    LearningEvent.EventType.LECTURE_COMPLETED: "lecture_completed",
    LearningEvent.EventType.PDF_DOWNLOADED: "pdf_downloaded",
    LearningEvent.EventType.VIDEO_STARTED: "video_started",
    LearningEvent.EventType.VIDEO_COMPLETED: "video_completed",
    LearningEvent.EventType.PRACTICE_DOWNLOADED: "practice_downloaded",
    LearningEvent.EventType.PRACTICE_COMPLETED: "practice_completed",
    LearningEvent.EventType.QUIZ_ATTEMPTED: "quiz_attempted",
    LearningEvent.EventType.QUIZ_PASSED: "quiz_passed",
}


class ProgressService:
    @staticmethod
    def record_event(student, lesson, event_type: str, study_seconds: int = 0, metadata: dict | None = None) -> LearningEvent | None:
        if not student or not student.is_authenticated or not getattr(student, "is_student", False) or lesson is None:
            return None

        progress, _ = StudentProgress.objects.get_or_create(student=student, lesson=lesson)
        field = PROGRESS_EVENT_FIELD.get(event_type)
        if field:
            setattr(progress, field, True)
        progress.study_seconds = F("study_seconds") + max(study_seconds, 0)
        progress.last_activity_at = timezone.now()
        progress.save(update_fields=[*(field and [field] or []), "study_seconds", "last_activity_at", "completed", "completion_date", "updated_at"])
        progress.refresh_from_db()

        return LearningEvent.objects.create(
            student=student,
            course=lesson.course,
            lesson=lesson,
            event_type=event_type,
            study_seconds=max(study_seconds, 0),
            metadata=metadata or {},
        )

    @staticmethod
    def build_summary(student, course_id: int | None = None) -> dict:
        lessons = Lesson.objects.all()
        progress_rows = StudentProgress.objects.filter(student=student)
        completed_progress = progress_rows.filter(completed=True)
        results = QuizResult.objects.filter(student=student)

        if course_id:
            lessons = lessons.filter(course_id=course_id)
            progress_rows = progress_rows.filter(lesson__course_id=course_id)
            completed_progress = completed_progress.filter(lesson__course_id=course_id)
            results = results.filter(quiz__lesson__course_id=course_id)

        total_lessons = lessons.count()
        completed_lessons = completed_progress.count()
        percent_expr = ExpressionWrapper(100.0 * F("score") / F("total"), output_field=FloatField())
        average_score = results.annotate(percent=percent_expr).aggregate(avg=Avg("percent"))["avg"] or 0.0
        total_study_seconds = progress_rows.aggregate(total=Sum("study_seconds"))["total"] or 0
        last_progress = progress_rows.select_related("lesson").order_by("-last_activity_at", "-updated_at").first()
        recent_videos = VideoWatchProgress.objects.filter(student=student).select_related("video").order_by("-updated_at")[:5]
        recent_downloads = LearningEvent.objects.filter(student=student, event_type=LearningEvent.EventType.PDF_DOWNLOADED).order_by("-created_at")[:5]

        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "remaining_lessons": max(total_lessons - completed_lessons, 0),
            "completion_percentage": round((completed_lessons / total_lessons) * 100, 2) if total_lessons else 0.0,
            "quiz_attempts": results.aggregate(total=Count("id"))["total"] or 0,
            "average_score": round(float(average_score), 2),
            "total_study_seconds": total_study_seconds,
            "last_visited_lesson": {"id": last_progress.lesson_id, "title": last_progress.lesson.title} if last_progress else None,
            "current_streak": ProgressService.current_streak(student),
            "recently_watched_videos": [{"id": item.video_id, "title": item.video.title, "position": item.current_position, "percentage": item.watch_percentage} for item in recent_videos],
            "recently_downloaded_pdfs": [event.metadata for event in recent_downloads],
            "weekly_activity": ProgressService.weekly_activity(student),
        }

    @staticmethod
    def current_streak(student) -> int:
        dates = set(
            LearningEvent.objects.filter(student=student)
            .values_list("created_at__date", flat=True)
            .order_by("-created_at__date")[:60]
        )
        today = timezone.localdate()
        streak = 0
        while today - timedelta(days=streak) in dates:
            streak += 1
        return streak

    @staticmethod
    def weekly_activity(student) -> list[dict]:
        today = timezone.localdate()
        start = today - timedelta(days=6)
        rows = (
            LearningEvent.objects.filter(student=student, created_at__date__gte=start)
            .values("created_at__date")
            .annotate(seconds=Sum("study_seconds"), events=Count("id"))
        )
        bucket = {row["created_at__date"]: row for row in rows}
        return [
            {
                "date": (start + timedelta(days=offset)).isoformat(),
                "study_seconds": bucket.get(start + timedelta(days=offset), {}).get("seconds", 0) or 0,
                "events": bucket.get(start + timedelta(days=offset), {}).get("events", 0) or 0,
            }
            for offset in range(7)
        ]

    @staticmethod
    def student_analytics(student) -> dict:
        percent_expr = ExpressionWrapper(100.0 * F("score") / F("total"), output_field=FloatField())
        difficult_lessons = (
            QuizResult.objects.filter(student=student)
            .values("quiz__lesson_id", "quiz__lesson__title")
            .annotate(avg_score=Avg(percent_expr), attempts=Count("id"))
            .order_by("avg_score")[:5]
        )
        return {
            "daily_learning_time": ProgressService.weekly_activity(student)[-1]["study_seconds"],
            "weekly_learning_time": sum(day["study_seconds"] for day in ProgressService.weekly_activity(student)),
            "most_difficult_lessons": list(difficult_lessons),
            "average_quiz_score": round(float(QuizResult.objects.filter(student=student).annotate(percent=percent_expr).aggregate(avg=Avg("percent"))["avg"] or 0), 2),
            "learning_trend": ProgressService.weekly_activity(student),
        }

    @staticmethod
    def teacher_analytics() -> dict:
        percent_expr = ExpressionWrapper(100.0 * F("score") / F("total"), output_field=FloatField())
        return {
            "active_students": LearningEvent.objects.values("student").distinct().count(),
            "completed_courses": Certificate.objects.count(),
            "average_scores": round(float(QuizResult.objects.annotate(percent=percent_expr).aggregate(avg=Avg("percent"))["avg"] or 0), 2),
            "most_viewed_lecture": LectureMaterial.objects.order_by("-view_count").values("id", "title", "view_count").first(),
            "most_watched_video": VideoLesson.objects.annotate(progress_updates=Count("watch_progress")).order_by("-progress_updates").values("id", "title", "progress_updates").first(),
            "most_downloaded_pdf": LectureMaterial.objects.order_by("-download_count").values("id", "title", "download_count").first(),
            "quiz_statistics": list(
                QuizResult.objects.values("quiz_id", "quiz__title").annotate(attempts=Count("id"), average=Avg(percent_expr), latest=Max("created_at")).order_by("-attempts")[:10]
            ),
            "resource_downloads": list(Resource.objects.order_by("-download_count").values("id", "title", "download_count")[:10]),
            "practice_downloads": LearningEvent.objects.filter(event_type=LearningEvent.EventType.PRACTICE_DOWNLOADED).count(),
        }


class CertificateService:
    @staticmethod
    def eligible(student, course) -> tuple[bool, dict]:
        summary = ProgressService.build_summary(student, course.id)
        return summary["completion_percentage"] >= 100 and summary["average_score"] >= 70, summary

    @staticmethod
    def issue(student, course) -> Certificate:
        is_eligible, summary = CertificateService.eligible(student, course)
        if not is_eligible:
            raise ValueError(f"Certificate requires 100% completion and >=70% quiz average. Current: {summary}")
        certificate, _ = Certificate.objects.get_or_create(
            student=student,
            course=course,
            defaults={
                "certificate_id": f"CERT-{course.code}-{student.pk}-{uuid4().hex[:10].upper()}",
                "verification_code": uuid4().hex,
            },
        )
        return certificate

    @staticmethod
    def render_pdf(certificate: Certificate) -> bytes:
        student_name = certificate.student.get_full_name() or certificate.student.username
        lines = [
            "Course Completion Certificate",
            f"Student: {student_name}",
            f"Course: {certificate.course.title}",
            f"Completion date: {certificate.issued_at.date().isoformat()}",
            f"Certificate ID: {certificate.certificate_id}",
            f"QR verification code: {certificate.verification_code}",
        ]
        return CertificateService.render_pdf_text("Course Completion Certificate", "\\n".join(lines))

    @staticmethod
    def render_pdf_text(title: str, body: str) -> bytes:
        text = f"{title}\\n\\n{body}".replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 22 Tf 72 740 Td ({text}) Tj ET".encode("latin-1", errors="ignore")
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        ]
        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n".encode())
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")
        xref_offset = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode())
        pdf.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode())
        return bytes(pdf)
