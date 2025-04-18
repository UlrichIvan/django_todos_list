from django.forms import ModelForm
from .models import Todo


class TodoForm(ModelForm):
    class Meta:
        model = Todo
        exclude = ["created_at", "updated_at", "deleted_at", "done"]


class EditTodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ["title", "content", "done"]
