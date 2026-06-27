from rest_framework import serializers

from .models import (
    AcademicGroup,
    AcademicYear,
    Course,
    CourseEnrollment,
    Department,
    EducationDirection,
    Faculty,
    Semester,
    University,
)


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = "__all__"


class FacultySerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source="university.name", read_only=True)

    class Meta:
        model = Faculty
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)

    class Meta:
        model = Department
        fields = "__all__"


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class SemesterSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = Semester
        fields = "__all__"


class EducationDirectionSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)

    class Meta:
        model = EducationDirection
        fields = "__all__"


class AcademicGroupSerializer(serializers.ModelSerializer):
    direction_name = serializers.CharField(source="direction.name", read_only=True)

    class Meta:
        model = AcademicGroup
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(source="lessons.count", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    semester_name = serializers.CharField(source="academic_semester.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    enrollments_count = serializers.IntegerField(source="enrollments.count", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "code",
            "description",
            "department",
            "department_name",
            "academic_semester",
            "semester_name",
            "teacher",
            "teacher_name",
            "semester",
            "credits",
            "image",
            "is_active",
            "is_published",
            "is_archived",
            "lessons_count",
            "enrollments_count",
        ]


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = ["id", "student", "student_name", "course", "course_title", "group", "group_name", "status", "enrolled_at", "created_at", "updated_at"]
        read_only_fields = ["enrolled_at", "created_at", "updated_at"]


class BulkEnrollmentSerializer(serializers.Serializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    students = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    group = serializers.PrimaryKeyRelatedField(queryset=AcademicGroup.objects.all(), required=False, allow_null=True)
    status = serializers.ChoiceField(choices=CourseEnrollment.Status.choices, default=CourseEnrollment.Status.ACTIVE)


class CSVEnrollmentImportSerializer(serializers.Serializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.lower().endswith(".csv"):
            raise serializers.ValidationError("Only CSV files are supported for enrollment import.")
        return value
