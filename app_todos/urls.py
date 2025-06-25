from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from .views import redirect_to_todos
from django.conf.urls.static import static

app_name = "todo_app"
urlpatterns = [
    path("", redirect_to_todos, name="app_index"),
    path("admin/", admin.site.urls, name="admin"),
    path("todos/", include("todos.urls"), name="todos"),
    path("auth/", include("google.urls"), name="google"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "app_todos.views.not_found"

handler500 = "app_todos.views.interval_error"
