# Database Schema

## accounts_user

Custom Django user based on `AbstractUser`.

| Field | Type | Notes |
| --- | --- | --- |
| id | bigint | Primary key |
| username | varchar | Unique username |
| email | email | Unique email |
| role | varchar | `super_admin`, `teacher`, `student` |
| avatar | image | Optional |
| phone | varchar | Optional |

## courses_course

| Field | Type | Notes |
| --- | --- | --- |
| id | bigint | Primary key |
| title | varchar(255) | Course title |
| code | varchar(32) | Unique course code |
| description | text | Course description |
| semester | smallint | University semester |
| credits | smallint | Credit value |
| image | image | Optional |
| is_active | boolean | Publication flag |

## lessons_lesson

| Field | Type | Notes |
| --- | --- | --- |
| id | bigint | Primary key |
| course_id | fk | `courses_course.id` |
| lesson_number | smallint | Unique per course |
| title | varchar(255) | Lesson title |
| description | text | Optional |
| order | smallint | Unique per course |

## materials_lecturematerial

Lecture content is managed from admin/API and tracks preview/download usage.

| Field | Type | Notes |
| --- | --- | --- |
| id | bigint | Primary key |
| lesson_id | fk | `lessons_lesson.id` |
| title | varchar | Lecture title |
| lecture_number | smallint | Sort/navigation number |
| pdf_file | file | PDF only |
| description | text | Optional |
| cover_image | image | Optional |
| estimated_reading_time | smallint | Minutes |
| download_count | int | Auto-incremented |
| view_count | int | Auto-incremented |
| is_published | boolean | Visibility flag |

## materials_practicematerial

| Field | Type | Notes |
| --- | --- | --- |
| id | bigint | Primary key |
| lesson_id | fk | `lessons_lesson.id` |
| title | varchar | Practice title |
| pdf_file | file | PDF only |
| example_files | file | ZIP/RAR examples |
| source_code_files | file | Source archive/file |
| description | text | Optional |
| difficulty | varchar | `easy`, `medium`, `hard` |
| estimated_time | smallint | Minutes |

## materials_resource

| Field | Type | Notes |
| --- | --- | --- |
| id | bigint | Primary key |
| course_id | fk | Optional course |
| lesson_id | fk | Optional lesson |
| title | varchar | Resource title |
| description | text | Optional |
| category | varchar | Books, Articles, Datasets, Code, Presentation, Assignment, Other |
| file | file | PDF, DOCX, PPTX, ZIP, RAR, image, CSV, Python, notebook |
| download_count | int | Auto-incremented |
| is_published | boolean | Visibility flag |

## videos_videolesson

| Field | Type | Notes |
| --- | --- | --- |
| id | bigint | Primary key |
| lesson_id | fk | `lessons_lesson.id` |
| title | varchar | Video title |
| youtube_url | url | YouTube URL |
| video_id | varchar | Auto-extracted |
| duration | interval | Video duration |
| thumbnail | url | Auto-generated YouTube thumbnail URL |
| speaker | varchar | Optional |
| description | text | Optional |

## quizzes_quiz / quizzes_question

`Quiz` belongs to a lesson. `Question` belongs to a quiz and stores answer options in JSON.

| Field | Type | Notes |
| --- | --- | --- |
| question | text | Prompt |
| options | jsonb | List of options |
| correct_answer | varchar | Must match one option |
| explanation | text | Optional |

## progress_studentprogress / progress_quizresult

Tracks lesson completion and quiz attempts by student.

| Field | Type | Notes |
| --- | --- | --- |
| student_id | fk | `accounts_user.id` |
| lesson_id | fk | `lessons_lesson.id` |
| completed | boolean | Completion state |
| completion_date | datetime | Auto-set when completed |
| quiz_id | fk | `quizzes_quiz.id` |
| score | smallint | Earned points |
| total | smallint | Total points |
| duration | interval | Attempt duration |

## glossary_glossary

| Field | Type | Notes |
| --- | --- | --- |
| term | varchar(255) | Unique |
| definition | text | Description |
| category | varchar(128) | Optional grouping |
