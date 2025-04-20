import re
from django.forms import ModelForm
from .models import Todo, UserTodo
from django.db import models
from django.core.validators import RegexValidator


class TodoForm(ModelForm):
    class Meta:
        model = Todo
        exclude = ["created_at", "updated_at", "deleted_at", "done"]


class EditTodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ["title", "content", "done"]


class UserForm(ModelForm):

    class Meta:
        model = UserTodo
        exclude = ["id", "account_id"]

    def is_valid(self):
        rgx_password = r"^[a-zA-Z0-9]{12}$"
        if re.match(rgx_password, self.data["password"]) == None:
            print(
                {
                    "password": self.data["password"],
                    "match": re.match(rgx_password, self.data["password"]),
                }
            )
            self.add_error(
                "password", "password must be content 12 alphanumics characters"
            )
            super().is_valid()
            return False
        if self.data["password"] != self.data["confirm_password"]:
            self.add_error("password", "password and confirm password must be the same")
            super().is_valid()
            return False
        return super().is_valid()
