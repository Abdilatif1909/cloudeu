from django.contrib import admin

from .models import Glossary


@admin.register(Glossary)
class GlossaryAdmin(admin.ModelAdmin):
    list_display = ("term", "category")
    list_filter = ("category",)
    search_fields = ("term", "definition", "category")
