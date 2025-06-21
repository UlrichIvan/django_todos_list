from django.contrib import admin
from django.urls import path, include
from .views import redirect_to_todos

app_name = "todo_app"
urlpatterns = [
    path("", redirect_to_todos, name="app_index"),
    path("admin/", admin.site.urls),
    path("todos/", include("todos.urls"), name="todos"),
    path("auth/", include("google.urls"), name="google"),
]

handler400 = "app_todos.views.not_found"

handler500 = "app_todos.views.interval_error"
