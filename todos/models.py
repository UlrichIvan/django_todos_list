from django.utils import timezone
from django.db import models
import uuid


class Todo(models.Model):
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=255, null=False, blank=False, unique=False)
    content = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(default=None, null=True)

    def get_fields(self):
        fields = []
        for field in Todo._meta.fields:
            if field.name == "id":
                continue
            elif field.name == "done":
                fields.append(
                    (field.name, "yes" if getattr(self, field.name) else "no")
                )
            elif field.name in ["created_at", "updated_at"]:
                fields.append((field.name.strip("_at"), getattr(self, field.name)))
            elif field.name in ["deleted_at"]:
                fields.append(
                    (
                        field.name.strip("_at"),
                        (
                            getattr(self, field.name)
                            if getattr(self, field.name)
                            else "never"
                        ),
                    )
                )
            else:
                fields.append((field.name, getattr(self, field.name)))

        return fields
