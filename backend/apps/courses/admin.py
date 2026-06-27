from django.contrib import admin

from .models import AcademicGroup, AcademicYear, Course, CourseEnrollment, Department, EducationDirection, Faculty, Semester, University


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "department", "academic_semester", "teacher", "semester", "credits", "is_published", "is_archived", "is_active")
    list_filter = ("department", "academic_semester", "teacher", "semester", "credits", "is_published", "is_archived", "is_active")
    search_fields = ("title", "code", "description", "department__name", "teacher__username", "teacher__email")
    autocomplete_fields = ("department", "academic_semester", "teacher")


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "address")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "university", "is_active")
    list_filter = ("university", "is_active")
    search_fields = ("name", "code", "university__name")
    autocomplete_fields = ("university",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "faculty", "is_active")
    list_filter = ("faculty", "is_active")
    search_fields = ("name", "code", "faculty__name")
    autocomplete_fields = ("faculty",)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "starts_on", "ends_on", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "number", "academic_year", "starts_on", "ends_on", "is_active")
    list_filter = ("academic_year", "number", "is_active")
    search_fields = ("name", "academic_year__name")
    autocomplete_fields = ("academic_year",)


@admin.register(EducationDirection)
class EducationDirectionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "faculty", "is_active")
    list_filter = ("faculty", "is_active")
    search_fields = ("name", "code", "faculty__name")
    autocomplete_fields = ("faculty",)


@admin.register(AcademicGroup)
class AcademicGroupAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "direction", "semester", "is_active")
    list_filter = ("direction", "semester", "is_active")
    search_fields = ("name", "code", "direction__name")
    autocomplete_fields = ("direction", "semester")


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "group", "status", "enrolled_at")
    list_filter = ("status", "course", "group")
    search_fields = ("student__username", "student__email", "course__title", "course__code", "group__name")
    autocomplete_fields = ("student", "course", "group")
