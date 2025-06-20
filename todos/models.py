from typing import Iterable
from django.utils import timezone
from django.db import models
from django.core.validators import RegexValidator
import uuid


class UserTodo(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    first_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        error_messages={"max_length": "invalid length first name"},
    )
    last_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        error_messages={"max_length": "invalid length last name"},
    )
    email = models.EmailField(
        max_length=255,
        null=False,
        unique=True,
        error_messages={"unique": "email already taken"},
    )
    password = models.CharField(null=False, blank=False, max_length=128)
    code = models.CharField(max_length=10, null=False, default=None, unique=True)
    actived = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class Todo(models.Model):
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    title = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=False,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z ]{1,255}$",
                message="title must be contains at least 1 alphabetics characters",
            )
        ],
    )
    content = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
    expired_at = models.DateTimeField(default=None, null=True, blank=True)
    user_id = models.ForeignKey(to=UserTodo, on_delete=models.SET_NULL, null=True)

    def get_expired(self) -> str | None:
        return self.expired_at.strftime("%Y-%m-%dT%H:%M") if self.expired_at else None

    def get_fields(self):
        fields = []
        for field in Todo._meta.fields:
            if field.name in ["id", "user_id"]:
                continue
            elif field.name == "done":
                fields.append(
                    (field.name, "yes" if getattr(self, field.name) else "no")
                )
            elif field.name in ["created_at", "updated_at", "expired_at"]:
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


class FactorAuth(models.Model):
    code = models.CharField(max_length=10, null=True, default=None, unique=True)
    user = models.OneToOneField(to=UserTodo, on_delete=models.SET_NULL, null=True)
    is_auth = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class ResetPassword(models.Model):
    code = models.CharField(max_length=10, null=True, default=None, unique=True)
    user = models.OneToOneField(to=UserTodo, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
