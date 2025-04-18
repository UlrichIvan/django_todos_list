from django.urls import path
from .views import TodosListView, Todos

app_name = "todo_list"
urlpatterns = [
    path("", TodosListView.as_view(), name="todo_index"),
    path("add", Todos.as_view(), name="todo_add"),
    path("save", Todos.as_view(), name="todo_save"),
]
