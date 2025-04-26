from django.contrib import admin
from django.urls import path, include
from .views import redirect_to_todos

app_name = "todo_app"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("todos/", include("todos.urls"), name="todos"),
    path("", redirect_to_todos, name="app_index"),
]

handler400 = "app_todos.views.not_found"

handler500 = "app_todos.views.interval_error"
