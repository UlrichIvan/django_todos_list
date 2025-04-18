from django.utils import timezone
from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False, unique=False)
    content = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(default=None, null=True)
