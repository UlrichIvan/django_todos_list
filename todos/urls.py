from django.urls import path
from .views import Todos

urlpatterns = [
    path("", Todos.as_view(), name="todo_index"),
]
