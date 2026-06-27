import re
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.courses.models import Course
from apps.lessons.models import Lesson
from apps.materials.models import LectureMaterial, PracticeMaterial
from apps.videos.models import VideoLesson


COURSE_TITLE = "Sun'iy intellekt asoslari"
COURSE_CODE = "AI101"

LESSON_TOPICS = {
    1: "Sun'iy intellektga kirish va muammoni shakllantirish",
    2: "Ma'lumotlar bilan ishlash: NumPy va massivlar",
    3: "Pandas, jadval ma'lumotlari va tayyorlash",
    4: "Vizual tahlil va Matplotlib",
    5: "Machine Learning nazariy asoslari",
    6: "An'anaviy ML algoritmlari",
    7: "Klassifikatsiya va baholash",
    8: "Neyron tarmoqlar va PyTorch asoslari",
    9: "CNN va kompyuter ko'rish",
    10: "NLP, tokenizatsiya va til modellari",
    11: "Reinforcement Learning va intellektual agentlar",
}

VIDEO_LINKS = [
    (1, "Kirish", "https://www.youtube.com/watch?v=wSR4mrZqe7Y", "00:05:47"),
    (2, "ML 1 dars Numpy moduli", "https://www.youtube.com/watch?v=t1E-4BtkTaE", "00:46:00"),
    (3, "ML 2 dars Pandas moduli", "https://www.youtube.com/watch?v=-aLWlwP2bXA", "00:31:00"),
    (4, "ML 3 dars Matplotlib moduli", "https://www.youtube.com/watch?v=ePpwFSDMERc", "00:24:00"),
    (5, "ML 4 dars Nazariy tushunchalar", "https://www.youtube.com/watch?v=_OlU3W-EmCI", "00:07:04"),
    (6, "ML 5 dars Traditional Algorithms", "https://www.youtube.com/watch?v=vIMmJTuV7VI", "00:33:00"),
    (7, "Pytorch 5 dars binary classification", "https://www.youtube.com/watch?v=oKUTBvL3C_s", "00:32:00"),
    (8, "Pytorch 3 dars Neural tarmoqlar", "https://www.youtube.com/watch?v=7hUtk2Q59G0", "00:33:00"),
    (9, "Pytorch 7-dars CNN", "https://www.youtube.com/watch?v=9qB3HyQjAFE", "00:48:00"),
    (10, "Tokenizer", "https://www.youtube.com/watch?v=JUao6tKanek", "00:31:00"),
    (11, "RL 3-dars State va Reward", "https://www.youtube.com/watch?v=QbJ1eg8mVis", "00:25:00"),
]


@dataclass
class ImportStats:
    courses_before: int = 0
    lessons_before: int = 0
    lectures_before: int = 0
    practices_before: int = 0
    videos_before: int = 0
    courses_created: int = 0
    lessons_created: int = 0
    lectures_created: int = 0
    lectures_updated: int = 0
    practices_created: int = 0
    practices_updated: int = 0
    videos_created: int = 0
    videos_updated: int = 0
    skipped_files: int = 0
    warnings: list[str] = field(default_factory=list)


class Command(BaseCommand):
    help = "Import the AI course lessons, lecture PDFs, practice PDFs, and YouTube links from the repository."

    def add_arguments(self, parser):
        parser.add_argument("--pdf-root", default=None, help="Folder containing maruza and amaliy subfolders.")
        parser.add_argument("--report", default=None, help="Report output path.")

    @transaction.atomic
    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parents[5]
        pdf_root = Path(options["pdf_root"]).resolve() if options["pdf_root"] else project_root / "pdf"
        report_path = Path(options["report"]).resolve() if options["report"] else project_root / "DATABASE_IMPORT_REPORT.md"

        stats = self.initial_stats()
        course = self.ensure_course(stats)
        lessons = self.ensure_lessons(course, stats)

        self.import_lecture_pdfs(pdf_root / "maruza", lessons, stats)
        self.import_practice_pdfs(pdf_root / "amaliy", lessons, stats)
        self.import_videos(lessons, stats)
        self.write_report(report_path, project_root, pdf_root, course, stats)

        self.stdout.write(self.style.SUCCESS("AI course database import completed."))
        self.stdout.write(f"Report written to {report_path}")

    def initial_stats(self):
        return ImportStats(
            courses_before=Course.objects.count(),
            lessons_before=Lesson.objects.count(),
            lectures_before=LectureMaterial.objects.count(),
            practices_before=PracticeMaterial.objects.count(),
            videos_before=VideoLesson.objects.count(),
        )

    def ensure_course(self, stats):
        course = Course.objects.filter(code=COURSE_CODE).first() or Course.objects.filter(title__iexact=COURSE_TITLE).first()
        if course:
            changed = False
            if course.title != COURSE_TITLE:
                course.title = COURSE_TITLE
                changed = True
            if not course.is_active or not course.is_published or course.is_archived:
                course.is_active = True
                course.is_published = True
                course.is_archived = False
                changed = True
            if changed:
                course.save(update_fields=["title", "is_active", "is_published", "is_archived", "updated_at"])
            return course

        stats.courses_created += 1
        return Course.objects.create(
            title=COURSE_TITLE,
            code=COURSE_CODE,
            description=(
                "Axborot Texnologiyalari va Menejment Universiteti uchun "
                "sun'iy intellekt asoslari bo'yicha ma'ruza, amaliy material, video va testlar."
            ),
            semester=1,
            credits=6,
            is_active=True,
            is_published=True,
            is_archived=False,
        )

    def ensure_lessons(self, course, stats):
        lessons = {}
        for number, title in LESSON_TOPICS.items():
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                lesson_number=number,
                defaults={
                    "title": title,
                    "description": f"{COURSE_TITLE}: {title}",
                    "order": number,
                },
            )
            if created:
                stats.lessons_created += 1
            else:
                updates = {}
                if lesson.title != title:
                    updates["title"] = title
                if lesson.order != number:
                    updates["order"] = number
                if not lesson.description:
                    updates["description"] = f"{COURSE_TITLE}: {title}"
                if updates:
                    for field, value in updates.items():
                        setattr(lesson, field, value)
                    lesson.save(update_fields=[*updates.keys(), "updated_at"])
            lessons[number] = lesson
        return lessons

    def import_lecture_pdfs(self, folder, lessons, stats):
        for path in self.pdf_files(folder, stats):
            number = self.lesson_number(path)
            lesson = lessons.get(number)
            if not lesson:
                stats.skipped_files += 1
                stats.warnings.append(f"No lesson mapping for lecture PDF: {path.name}")
                continue

            material, created = LectureMaterial.objects.get_or_create(
                lesson=lesson,
                lecture_number=number,
                defaults={
                    "title": self.title_from_pdf(path),
                    "description": f"{lesson.title} mavzusi bo'yicha ma'ruza materiali.",
                    "estimated_reading_time": 20,
                    "is_published": True,
                },
            )
            if created:
                stats.lectures_created += 1
            self.attach_pdf(material, path, stats, "lectures_updated", created)

    def import_practice_pdfs(self, folder, lessons, stats):
        for index, path in enumerate(self.pdf_files(folder, stats), start=1):
            number = self.lesson_number(path) or index
            lesson = lessons.get(number) or lessons.get(index)
            if not lesson:
                stats.skipped_files += 1
                stats.warnings.append(f"No lesson mapping for practice PDF: {path.name}")
                continue

            title = self.title_from_pdf(path)
            material, created = PracticeMaterial.objects.get_or_create(
                lesson=lesson,
                title=title,
                defaults={
                    "description": f"{lesson.title} mavzusi bo'yicha amaliy mashg'ulot materiali.",
                    "difficulty": PracticeMaterial.Difficulty.MEDIUM,
                    "estimated_time": 90,
                },
            )
            if created:
                stats.practices_created += 1
            self.attach_pdf(material, path, stats, "practices_updated", created)

    def import_videos(self, lessons, stats):
        for number, title, url, duration in VIDEO_LINKS:
            lesson = lessons[number]
            video = VideoLesson.objects.filter(youtube_url=url).first()
            created = False
            if not video:
                video = VideoLesson(lesson=lesson, youtube_url=url)
                created = True

            changed = created
            for field_name, value in {
                "lesson": lesson,
                "title": title,
                "duration": self.parse_duration(duration),
                "speaker": "Machine Mind",
                "description": f"{lesson.title} mavzusiga mos YouTube video.",
            }.items():
                if getattr(video, field_name) != value:
                    setattr(video, field_name, value)
                    changed = True

            if changed:
                video.save()
                if created:
                    stats.videos_created += 1
                else:
                    stats.videos_updated += 1

    def pdf_files(self, folder, stats):
        if not folder.exists():
            stats.warnings.append(f"PDF folder not found: {folder}")
            return []
        return sorted(folder.glob("*.pdf"), key=lambda path: (self.lesson_number(path), path.name.lower()))

    def lesson_number(self, path):
        match = re.search(r"\d+", path.stem)
        return int(match.group(0)) if match else 0

    def title_from_pdf(self, path):
        title = re.sub(r"^\s*\d+\s*[\)\-._]?\s*", "", path.stem).strip()
        return title or path.stem

    def attach_pdf(self, material, path, stats, updated_field, created):
        current_path = Path(settings.MEDIA_ROOT) / material.pdf_file.name if material.pdf_file else None
        file_missing = bool(current_path and not current_path.exists())

        if material.pdf_file and not file_missing:
            return

        with path.open("rb") as opened:
            material.pdf_file.save(path.name, File(opened), save=True)
        if not created:
            setattr(stats, updated_field, getattr(stats, updated_field) + 1)

    def parse_duration(self, value):
        parts = [int(part) for part in value.split(":")]
        if len(parts) == 3:
            return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
        return timedelta(minutes=parts[0], seconds=parts[1])

    def display_path(self, project_root, path):
        try:
            return path.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError:
            return str(path)

    def write_report(self, report_path, project_root, pdf_root, course, stats):
        lessons = Lesson.objects.filter(course=course)
        lectures = LectureMaterial.objects.filter(lesson__course=course)
        practices = PracticeMaterial.objects.filter(lesson__course=course)
        videos = VideoLesson.objects.filter(lesson__course=course)

        lesson_lines = []
        for lesson in lessons.order_by("order"):
            lesson_lines.append(
                f"- Lesson {lesson.lesson_number}: {lesson.title} "
                f"({lesson.lecture_materials.count()} lectures, "
                f"{lesson.practice_materials.count()} practices, "
                f"{lesson.videos.count()} videos)"
            )

        report = f"""# Database Import Report

## Source

- Lecture PDFs: `{self.display_path(project_root, pdf_root / "maruza")}`
- Practice PDFs: `{self.display_path(project_root, pdf_root / "amaliy")}`
- Course: `{course.code} - {course.title}`

## Database Records Before Import

- Courses: {stats.courses_before}
- Lessons: {stats.lessons_before}
- Lecture materials: {stats.lectures_before}
- Practice materials: {stats.practices_before}
- Videos: {stats.videos_before}

## Imported Or Updated In This Run

- Courses created: {stats.courses_created}
- Lessons created: {stats.lessons_created}
- Lecture materials created: {stats.lectures_created}
- Lecture PDF files attached or repaired: {stats.lectures_updated}
- Practice materials created: {stats.practices_created}
- Practice PDF files attached or repaired: {stats.practices_updated}
- YouTube videos created: {stats.videos_created}
- YouTube videos updated: {stats.videos_updated}
- PDF files skipped: {stats.skipped_files}

## Current AI Course Totals

- Lessons: {lessons.count()}
- Lecture materials: {lectures.count()}
- Practice materials: {practices.count()}
- Videos: {videos.count()}

## Course Page Verification Data

{chr(10).join(lesson_lines) if lesson_lines else "- No lessons found"}

## Warnings

{chr(10).join(f"- {warning}" for warning in stats.warnings) if stats.warnings else "- None"}
"""
        report_path.write_text(report, encoding="utf-8")
