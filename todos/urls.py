from django.urls import path
from .views import (
    LogOut,
    TodosListView,
    AddTodo,
    EditTodo,
    TodoDetails,
    TodoDelete,
    UserCreate,
    UserActiveAccount,
    UserNewCode,
    UserLogin,
    UserFactAuth,
    UserNewCodeFactor,
    ResetPasswordView,
    NewPasswordView,
)

app_name = "todo_list"
urlpatterns = [
    path("", TodosListView.as_view(), name="index"),
    path("add", AddTodo.as_view(), name="add_todo"),
    path("edit/<uuid:id>", EditTodo.as_view(), name="edit_todo"),
    path("details/<uuid:pk>", TodoDetails.as_view(), name="details_todo"),
    path("delete/<uuid:id>", TodoDelete.as_view(), name="delete_todo"),
    path("account", UserCreate.as_view(), name="todo_user_account"),
    path(
        "active/account", UserActiveAccount.as_view(), name="todo_user_active_account"
    ),
    path("new/code", UserNewCode.as_view(), name="todo_user_new_code"),
    path("login", UserLogin.as_view(), name="todo_user_login"),
    path("fact/auth", UserFactAuth.as_view(), name="todo_user_fact_auth"),
    path(
        "code/fact/auth",
        UserNewCodeFactor.as_view(),
        name="todo_user_new_code_fact_auth",
    ),
    path(
        "reset/password",
        ResetPasswordView.as_view(),
        name="todo_user_reset_password",
    ),
    path("newpassword", NewPasswordView.as_view(), name="todo_user_new_password"),
    path("logout", LogOut.as_view(), name="logout"),
]
