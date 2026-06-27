from django.db import models

from apps.common.models import TimeStampedModel


class Glossary(TimeStampedModel):
    term = models.CharField(max_length=255, unique=True)
    definition = models.TextField()
    category = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["term"]
        verbose_name_plural = "glossary terms"

    def __str__(self) -> str:
        return self.term
