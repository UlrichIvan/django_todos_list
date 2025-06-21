from django.urls import path, include

from google.views import GoogleAuth

app_name = "google_app"
urlpatterns = [
    path("google", GoogleAuth.as_view(), name="auth"),  
]

handler400 = "app_todos.views.not_found"

handler500 = "app_todos.views.interval_error"
