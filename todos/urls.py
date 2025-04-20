from django.urls import path
from .views import TodosListView, AddTodo, EditTodo, TodoDetails, TodoDelete, UserCreate

app_name = "todo_list"
urlpatterns = [
    path("", TodosListView.as_view(), name="index"),
    path("add", AddTodo.as_view(), name="add_todo"),
    path("edit/<uuid:id>", EditTodo.as_view(), name="edit_todo"),
    path("details/<uuid:pk>", TodoDetails.as_view(), name="details_todo"),
    path("delete/<uuid:id>", TodoDelete.as_view(), name="delete_todo"),
    path("account", UserCreate.as_view(), name="todo_user_account"),
]
