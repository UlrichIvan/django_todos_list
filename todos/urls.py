from django.urls import path
from .views import TodosListView, AddTodo, EditTodo

app_name = "todo_list"
urlpatterns = [
    path("", TodosListView.as_view(), name="index"),
    path("add", AddTodo.as_view(), name="add_todo"),
    path("edit/<int:id>", EditTodo.as_view(), name="edit_todo"),
]
