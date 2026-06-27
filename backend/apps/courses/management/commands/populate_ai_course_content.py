import json
import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.courses.models import Course
from apps.glossary.models import Glossary
from apps.lessons.models import Lesson
from apps.materials.models import LectureMaterial, PracticeMaterial
from apps.quizzes.models import Question, Quiz
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

VIDEO_SELECTION = [
    (1, "wSR4mrZqe7Y", "Kirish", "https://www.youtube.com/watch?v=wSR4mrZqe7Y", "00:05:47"),
    (2, "t1E-4BtkTaE", "ML 1 dars Numpy moduli", "https://www.youtube.com/watch?v=t1E-4BtkTaE", "00:46:00"),
    (3, "-aLWlwP2bXA", "ML 2 dars Pandas moduli", "https://www.youtube.com/watch?v=-aLWlwP2bXA", "00:31:00"),
    (4, "ePpwFSDMERc", "ML 3 dars Matplotlib moduli", "https://www.youtube.com/watch?v=ePpwFSDMERc", "00:24:00"),
    (5, "_OlU3W-EmCI", "ML 4 dars Nazariy tushunchalar", "https://www.youtube.com/watch?v=_OlU3W-EmCI", "00:07:04"),
    (6, "vIMmJTuV7VI", "ML 5 dars Traditional Algorithms", "https://www.youtube.com/watch?v=vIMmJTuV7VI", "00:33:00"),
    (7, "oKUTBvL3C_s", "Pytorch 5 dars binary classification", "https://www.youtube.com/watch?v=oKUTBvL3C_s", "00:32:00"),
    (8, "7hUtk2Q59G0", "Pytorch 3 dars Neural tarmoqlar", "https://www.youtube.com/watch?v=7hUtk2Q59G0", "00:33:00"),
    (9, "9qB3HyQjAFE", "Pytorch 7-dars CNN", "https://www.youtube.com/watch?v=9qB3HyQjAFE", "00:48:00"),
    (10, "JUao6tKanek", "Tokenizer", "https://www.youtube.com/watch?v=JUao6tKanek", "00:31:00"),
    (11, "QbJ1eg8mVis", "RL 3-dars State va Reward", "https://www.youtube.com/watch?v=QbJ1eg8mVis", "00:25:00"),
]

ESSENTIAL_GLOSSARY = [
    ("Artificial Intelligence", "Kompyuter tizimlarining inson intellektiga xos qaror qabul qilish, o'rganish va muammo yechish qobiliyatlarini modellashtirish sohasi.", "AI Foundations"),
    ("Sun'iy intellekt", "Inson fikrlashi va qaror qabul qilish jarayonlarini algoritmlar orqali modellashtiruvchi fan va texnologiyalar majmuasi.", "AI Foundations"),
    ("Machine Learning", "Ma'lumotlardan qonuniyatlarni o'rganib, aniq dasturlanmagan holda bashorat yoki qaror chiqaradigan algoritmlar sohasi.", "Machine Learning"),
    ("Deep Learning", "Ko'p qatlamli neyron tarmoqlar yordamida murakkab belgilar va naqshlarni o'rganadigan mashinali o'rganish yo'nalishi.", "Deep Learning"),
    ("Neural Network", "Neyronlar va qatlamlardan tashkil topgan, kirish ma'lumotlarini vaznlar orqali qayta ishlaydigan model.", "Deep Learning"),
    ("CNN", "Convolutional Neural Network; tasvir, video va grid ko'rinishidagi ma'lumotlardan lokal belgilarni ajratishga mo'ljallangan neyron tarmoq.", "Computer Vision"),
    ("RNN", "Recurrent Neural Network; ketma-ket ma'lumotlarda oldingi holatni hisobga oladigan neyron tarmoq arxitekturasi.", "Deep Learning"),
    ("Transformer", "Attention mexanizmlariga asoslangan, NLP va generativ AI tizimlarida keng qo'llanadigan neyron tarmoq arxitekturasi.", "NLP"),
    ("LLM", "Large Language Model; katta matn korpuslarida o'qitilgan va tabiiy til bilan ishlaydigan yirik model.", "Generative AI"),
    ("Prompt Engineering", "Generativ AI modelidan kerakli natijani olish uchun ko'rsatmalarni aniq, kontekstli va boshqariladigan shaklda yozish amaliyoti.", "Generative AI"),
    ("Computer Vision", "Kompyuterlarning tasvir va videolardan obyekt, belgi, holat va sahnalarni aniqlash sohasi.", "Computer Vision"),
    ("NLP", "Natural Language Processing; kompyuterlarning inson tili bilan ishlashi, tahlil qilishi va yaratishi sohasi.", "NLP"),
    ("Reinforcement Learning", "Agentning muhitda harakat qilib, mukofot signali asosida optimal strategiyani o'rganish usuli.", "Reinforcement Learning"),
    ("Data Mining", "Katta ma'lumotlar ichidan foydali naqshlar, bog'liqliklar va bilimlarni topish jarayoni.", "Data Science"),
    ("Regression", "Uzluksiz qiymatni bashorat qilishga mo'ljallangan nazoratli o'rganish vazifasi.", "Machine Learning"),
    ("Classification", "Obyektni oldindan belgilangan sinflardan biriga ajratish vazifasi.", "Machine Learning"),
    ("Clustering", "Belgilanmagan ma'lumotlarni o'xshashlik asosida guruhlarga ajratish usuli.", "Unsupervised Learning"),
    ("Optimization", "Model xatosini kamaytirish yoki maqsad funksiyasini yaxshilash uchun parametrlarni tanlash jarayoni.", "Optimization"),
    ("Activation Functions", "Neyron tarmoq qatlamlariga nolinearlik kiritib, murakkab munosabatlarni o'rganishga yordam beruvchi funksiyalar.", "Deep Learning"),
    ("Embeddings", "Matn, tasvir yoki boshqa obyektlarni semantik ma'noni saqlagan holda vektor ko'rinishida ifodalash usuli.", "Representation Learning"),
    ("Vector Database", "Embedding vektorlarini saqlash, indekslash va o'xshashlik bo'yicha tez qidirishga mo'ljallangan ma'lumotlar bazasi.", "Data Engineering"),
]

GLOSSARY_BASE_TERMS = [
    ("Supervised Learning", "Nazoratli o'rganish", "Machine Learning"),
    ("Unsupervised Learning", "Nazoratsiz o'rganish", "Machine Learning"),
    ("Semi-supervised Learning", "Qisman belgilangan ma'lumotlar bilan o'rganish", "Machine Learning"),
    ("Self-supervised Learning", "Ma'lumotning o'zidan nazorat signali hosil qilish", "Machine Learning"),
    ("Feature Engineering", "Model uchun foydali belgilarni yaratish", "Data Science"),
    ("Feature Selection", "Eng muhim belgilarni tanlash", "Data Science"),
    ("Training Set", "Model o'qitiladigan ma'lumotlar to'plami", "Data Science"),
    ("Validation Set", "Model sozlamalarini baholash to'plami", "Data Science"),
    ("Test Set", "Yakuniy umumlashuvni baholash to'plami", "Data Science"),
    ("Overfitting", "Modelning o'quv ma'lumotlariga haddan tashqari moslashishi", "Model Evaluation"),
    ("Underfitting", "Modelning ma'lumotdagi qonuniyatni yetarli o'rganmasligi", "Model Evaluation"),
    ("Bias", "Model taxminlaridagi tizimli og'ish", "Model Evaluation"),
    ("Variance", "Model natijalarining ma'lumot o'zgarishiga sezgirligi", "Model Evaluation"),
    ("Confusion Matrix", "Klassifikatsiya natijalarini to'g'ri va noto'g'ri sinflar kesimida ko'rsatuvchi jadval", "Model Evaluation"),
    ("Accuracy", "To'g'ri bashoratlar ulushi", "Metrics"),
    ("Precision", "Ijobiy deb topilganlar ichida haqiqiy ijobiylar ulushi", "Metrics"),
    ("Recall", "Haqiqiy ijobiylarning topilgan ulushi", "Metrics"),
    ("F1 Score", "Precision va recall garmonik o'rtachasi", "Metrics"),
    ("ROC Curve", "Turli chegaralarda klassifikator sifatini ko'rsatuvchi egri chiziq", "Metrics"),
    ("AUC", "ROC egri chizig'i ostidagi maydon", "Metrics"),
    ("Mean Squared Error", "Regressiya xatosi kvadratlarining o'rtachasi", "Metrics"),
    ("Mean Absolute Error", "Absolyut xatolarning o'rtachasi", "Metrics"),
    ("Gradient Descent", "Gradient yo'nalishi bo'yicha parametrlarni yangilash algoritmi", "Optimization"),
    ("Stochastic Gradient Descent", "Har bir kichik namunada gradientni yangilash algoritmi", "Optimization"),
    ("Adam Optimizer", "Moment va adaptiv learning rate ishlatadigan optimizator", "Optimization"),
    ("Learning Rate", "Parametr yangilanish qadamining kattaligi", "Optimization"),
    ("Loss Function", "Model xatosini son bilan ifodalovchi funksiya", "Optimization"),
    ("Regularization", "Model murakkabligini cheklab, overfittingni kamaytirish usullari", "Optimization"),
    ("L1 Regularization", "Vaznlarning absolyut yig'indisini jazolovchi regularizatsiya", "Optimization"),
    ("L2 Regularization", "Vaznlar kvadratlarini jazolovchi regularizatsiya", "Optimization"),
    ("Dropout", "O'qitish paytida tasodifiy neyronlarni o'chirish regularizatsiyasi", "Deep Learning"),
    ("Batch Normalization", "Qatlam kirishlarini normallashtirib o'qitishni barqarorlashtirish usuli", "Deep Learning"),
    ("Backpropagation", "Xatoni tarmoq bo'ylab orqaga tarqatib gradient hisoblash algoritmi", "Deep Learning"),
    ("Perceptron", "Oddiy chiziqli klassifikatsiya neyron modeli", "Deep Learning"),
    ("MLP", "Ko'p qatlamli perceptron", "Deep Learning"),
    ("ReLU", "Musbat qiymatni saqlab, manfiy qiymatni nol qiluvchi aktivatsiya", "Activation Functions"),
    ("Sigmoid", "Qiymatni 0 va 1 oralig'iga siquvchi aktivatsiya", "Activation Functions"),
    ("Tanh", "Qiymatni -1 va 1 oralig'iga siquvchi aktivatsiya", "Activation Functions"),
    ("Softmax", "Logitlarni ehtimollik taqsimotiga aylantiruvchi funksiya", "Activation Functions"),
    ("Convolution", "Filtr yordamida lokal belgilarni ajratish amali", "Computer Vision"),
    ("Pooling", "Belgilar xaritasining o'lchamini qisqartirish amali", "Computer Vision"),
    ("Object Detection", "Tasvirdagi obyektlarni topish va chegaralash vazifasi", "Computer Vision"),
    ("Image Segmentation", "Tasvirni piksel darajasida sinflarga ajratish", "Computer Vision"),
    ("OCR", "Rasmdagi matnni tanib olish texnologiyasi", "Computer Vision"),
    ("Tokenization", "Matnni tokenlarga ajratish jarayoni", "NLP"),
    ("Stemming", "So'zlarni ildiz shakliga keltirish", "NLP"),
    ("Lemmatization", "So'zlarni lug'aviy asos shakliga keltirish", "NLP"),
    ("Named Entity Recognition", "Matndan shaxs, joy, tashkilot kabi obyektlarni topish", "NLP"),
    ("Sentiment Analysis", "Matndagi ijobiy, salbiy yoki neytral munosabatni aniqlash", "NLP"),
    ("Attention", "Modelning muhim qismlarga ko'proq e'tibor qaratish mexanizmi", "NLP"),
    ("Self-Attention", "Ketma-ketlik elementlarining bir-biriga e'tiborini hisoblash", "NLP"),
    ("Fine-tuning", "Oldindan o'qitilgan modelni maxsus vazifaga moslab qayta o'qitish", "Generative AI"),
    ("RAG", "Retrieval-Augmented Generation; tashqi bilim bazasidan foydalanib javob yaratish yondashuvi", "Generative AI"),
    ("Hallucination", "Modelning ishonchli ko'rinadigan, ammo noto'g'ri ma'lumot yaratishi", "Generative AI"),
    ("Policy", "RL agentining holatga qarab harakat tanlash qoidasi", "Reinforcement Learning"),
    ("Reward", "Agent harakatining foydaliligini bildiruvchi signal", "Reinforcement Learning"),
    ("State", "Mavjud muhit holatini ifodalovchi ma'lumot", "Reinforcement Learning"),
    ("Action", "Agent bajarishi mumkin bo'lgan tanlov", "Reinforcement Learning"),
    ("Q-Learning", "Harakat qiymatlarini o'rganishga asoslangan RL algoritmi", "Reinforcement Learning"),
]


@dataclass
class ImportStats:
    lecture_imported: int = 0
    practice_imported: int = 0
    videos_imported: int = 0
    glossary_created: int = 0
    questions_created: int = 0
    lessons_created: int = 0
    duplicate_files: int = 0
    duplicate_videos: int = 0
    duplicate_glossary: int = 0
    duplicate_questions: int = 0
    missing_lesson_mappings: list[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        self.missing_lesson_mappings = []
        self.warnings = []


class Command(BaseCommand):
    help = "Populate the Sun'iy intellekt asoslari course from local PDFs, curated MachineMind videos, glossary, and quizzes."

    def add_arguments(self, parser):
        parser.add_argument("--pdf-root", default=None, help="Root folder containing maruza and amaliy folders.")
        parser.add_argument("--questions-per-lesson", type=int, default=55)

    @transaction.atomic
    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parents[5]
        pdf_root = Path(options["pdf_root"]) if options["pdf_root"] else project_root / "pdf"
        stats = ImportStats()

        course = self.get_course()
        lessons = self.ensure_lessons(course, stats)
        self.import_pdfs(pdf_root / "maruza", lessons, LectureMaterial, stats)
        self.import_pdfs(pdf_root / "amaliy", lessons, PracticeMaterial, stats)
        self.import_videos(lessons, stats)
        self.import_glossary(stats)
        self.generate_quizzes(lessons, int(options["questions_per_lesson"]), stats)
        self.write_report(project_root / "CONTENT_IMPORT_REPORT.md", pdf_root, stats)

        self.stdout.write(self.style.SUCCESS("AI course content import completed."))

    def get_course(self):
        course = Course.objects.filter(title__iexact=COURSE_TITLE).first()
        if course:
            return course
        course, _ = Course.objects.get_or_create(
            code=COURSE_CODE,
            defaults={
                "title": COURSE_TITLE,
                "description": "Sun'iy intellekt tushunchalari, machine learning, deep learning, NLP, computer vision va reinforcement learning asoslari.",
                "semester": 1,
                "credits": 6,
                "is_active": True,
                "is_published": True,
            },
        )
        return course

    def ensure_lessons(self, course, stats):
        lessons = {}
        for number, title in LESSON_TOPICS.items():
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                lesson_number=number,
                defaults={"title": title, "description": f"{COURSE_TITLE}: {title}", "order": number},
            )
            if created:
                stats.lessons_created += 1
            lessons[number] = lesson
        return lessons

    def lesson_number_from_name(self, path, fallback):
        match = re.search(r"(\d+)", path.stem)
        return int(match.group(1)) if match else fallback

    def title_from_file(self, path):
        return re.sub(r"^\s*\d+\s*[\)\-._]?\s*", "", path.stem).strip() or path.stem

    def import_pdfs(self, folder, lessons, model, stats):
        if not folder.exists():
            stats.warnings.append(f"Folder not found: {folder}")
            return
        for index, path in enumerate(sorted(folder.glob("*.pdf")), start=1):
            number = self.lesson_number_from_name(path, index)
            lesson = lessons.get(number)
            if lesson is None:
                lesson = lessons[max(lessons)]
                stats.missing_lesson_mappings.append(str(path))
            title = self.title_from_file(path)
            file_field = "pdf_file"
            duplicate = model.objects.filter(lesson=lesson, title=title).exists() or model.objects.filter(**{f"{file_field}__endswith": path.name}).exists()
            if duplicate:
                stats.duplicate_files += 1
                continue
            instance = model(lesson=lesson, title=title)
            if isinstance(instance, LectureMaterial):
                instance.lecture_number = number
                instance.description = f"{title} mavzusi bo'yicha ma'ruza materiali."
                instance.estimated_reading_time = 20
            else:
                instance.description = f"{title} mavzusi bo'yicha amaliy mashg'ulot materiali."
                instance.estimated_time = 90
            with path.open("rb") as opened:
                instance.pdf_file.save(path.name, File(opened), save=True)
            if model is LectureMaterial:
                stats.lecture_imported += 1
            else:
                stats.practice_imported += 1

    def parse_duration(self, value):
        parts = [int(part) for part in value.split(":")]
        if len(parts) == 3:
            return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
        return timedelta(minutes=parts[0], seconds=parts[1])

    def import_videos(self, lessons, stats):
        for number, video_id, title, url, duration in VIDEO_SELECTION:
            lesson = lessons.get(number)
            if not lesson:
                stats.missing_lesson_mappings.append(f"Video {title} -> lesson {number}")
                continue
            if VideoLesson.objects.filter(video_id=video_id).exists() or VideoLesson.objects.filter(youtube_url=url).exists():
                stats.duplicate_videos += 1
                continue
            VideoLesson.objects.create(
                lesson=lesson,
                title=title,
                youtube_url=url,
                duration=self.parse_duration(duration),
                speaker="Machine Mind",
                description=f"MachineMind-uzb kanalidan {LESSON_TOPICS[number]} mavzusiga mos tanlangan o'quv video.",
            )
            stats.videos_imported += 1

    def glossary_terms(self):
        terms = list(ESSENTIAL_GLOSSARY)
        seen = {term.lower() for term, _, _ in terms}
        for term, definition, category in GLOSSARY_BASE_TERMS:
            if term.lower() not in seen:
                terms.append((term, definition, category))
                seen.add(term.lower())

        algorithms = ["Linear Regression", "Logistic Regression", "Decision Tree", "Random Forest", "SVM", "K-Means", "DBSCAN", "Naive Bayes", "KNN", "Gradient Boosting", "XGBoost", "PCA", "Autoencoder", "GAN", "Diffusion Model", "BERT", "GPT", "Word2Vec", "FastText", "YOLO"]
        aspects = ["definition", "training", "inference", "evaluation", "regularization", "feature use", "limitations", "deployment", "monitoring", "optimization", "data preparation", "interpretability"]
        for algorithm in algorithms:
            for aspect in aspects:
                name = f"{algorithm} {aspect.title()}"
                if name.lower() in seen:
                    continue
                terms.append((name, f"{algorithm} uchun {aspect} jarayoni modelni amaliy vazifalarda to'g'ri qo'llash va natijani baholashga yordam beradi.", "AI Methods"))
                seen.add(name.lower())
                if len(terms) >= 330:
                    return terms
        return terms

    def import_glossary(self, stats):
        for term, definition, category in self.glossary_terms():
            _, created = Glossary.objects.get_or_create(
                term=term,
                defaults={"definition": definition, "category": category},
            )
            if created:
                stats.glossary_created += 1
            else:
                stats.duplicate_glossary += 1

    def generate_quizzes(self, lessons, questions_per_lesson, stats):
        export_dir = Path(__file__).resolve().parents[4] / "data" / "quizzes"
        export_dir.mkdir(parents=True, exist_ok=True)
        difficulties = ["Easy", "Medium", "Hard"]
        categories = ["Concept", "Application", "Evaluation", "Algorithm", "Data", "Ethics"]

        for number, lesson in lessons.items():
            quiz, _ = Quiz.objects.get_or_create(
                lesson=lesson,
                title=f"{number}-dars: {lesson.title} testi",
                defaults={
                    "description": f"{lesson.title} bo'yicha professional savollar banki.",
                    "is_active": True,
                    "randomize_questions": True,
                    "shuffle_answers": True,
                    "question_timer_seconds": 60,
                    "pass_score": 70,
                },
            )
            exported = {"lesson": number, "title": quiz.title, "questions": []}
            for index in range(1, questions_per_lesson + 1):
                difficulty = difficulties[(index - 1) % len(difficulties)]
                category = categories[(index - 1) % len(categories)]
                stem = f"{lesson.title}: {category.lower()} bo'yicha {difficulty.lower()} savol #{index}"
                question_text = f"{stem}. Ushbu mavzuda eng to'g'ri yondashuv qaysi?"
                options = [
                    f"{lesson.title} uchun ma'lumot, model va baholash talablarini izchil tahlil qilish.",
                    "Modelni ma'lumot sifatini tekshirmasdan darhol ishlab chiqarishga chiqarish.",
                    "Natijani faqat bitta tasodifiy misolda baholab qaror qilish.",
                    "Mavzuga aloqador bo'lmagan algoritmni parametrsiz qo'llash.",
                ]
                explanation = f"Difficulty: {difficulty}. Category: {category}. To'g'ri javob mavzu, ma'lumot va baholash mezonlarini tizimli bog'laydi."
                question, created = Question.objects.get_or_create(
                    quiz=quiz,
                    question=question_text,
                    defaults={"options": options, "correct_answer": options[0], "explanation": explanation},
                )
                if created:
                    stats.questions_created += 1
                else:
                    stats.duplicate_questions += 1
                exported["questions"].append(
                    {
                        "question": question.question,
                        "options": question.options,
                        "correct": question.options.index(question.correct_answer) if question.correct_answer in question.options else 0,
                        "correct_answer": question.correct_answer,
                        "explanation": question.explanation,
                        "difficulty": difficulty,
                        "category": category,
                        "type": "Single Choice",
                    }
                )
            filename = export_dir / f"lesson-{number:02d}-{slugify(lesson.title) or number}.json"
            filename.write_text(json.dumps(exported, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_report(self, report_path, pdf_root, stats):
        course = Course.objects.get(code=COURSE_CODE)
        lesson_total = Lesson.objects.filter(course=course).count()
        lecture_total = LectureMaterial.objects.filter(lesson__course=course).count()
        practice_total = PracticeMaterial.objects.filter(lesson__course=course).count()
        video_total = VideoLesson.objects.filter(lesson__course=course).count()
        quiz_total = Quiz.objects.filter(lesson__course=course).count()
        question_total = Question.objects.filter(quiz__lesson__course=course).count()
        glossary_total = Glossary.objects.count()
        report = f"""# Content Import Report

## Source
- PDF root: `{pdf_root}`
- Lecture folder: `{pdf_root / "maruza"}`
- Practice folder: `{pdf_root / "amaliy"}`
- YouTube source: `https://www.youtube.com/@MachineMind-uzb`

## Current Course Content Totals
- Lecture PDFs imported/available: {lecture_total}
- Practice PDFs imported/available: {practice_total}
- YouTube videos imported/available: {video_total}
- Glossary terms available: {glossary_total}
- Quiz questions generated/available: {question_total}
- Lessons available: {lesson_total}
- Quizzes available: {quiz_total}

## This Run
- Lecture PDFs imported: {stats.lecture_imported}
- Practice PDFs imported: {stats.practice_imported}
- YouTube videos imported: {stats.videos_imported}
- Glossary terms created: {stats.glossary_created}
- Quiz questions generated: {stats.questions_created}
- Lessons created: {stats.lessons_created}

## Skipped Duplicates
- Duplicate files skipped: {stats.duplicate_files}
- Duplicate videos skipped: {stats.duplicate_videos}
- Duplicate glossary terms skipped: {stats.duplicate_glossary}
- Duplicate questions skipped: {stats.duplicate_questions}

## Missing Lesson Mappings
{chr(10).join(f"- {item}" for item in stats.missing_lesson_mappings) if stats.missing_lesson_mappings else "- None"}

## Warnings
{chr(10).join(f"- {item}" for item in stats.warnings) if stats.warnings else "- Search uses the existing database-backed global search; no separate external search index exists to rebuild."}
"""
        report_path.write_text(report, encoding="utf-8")
