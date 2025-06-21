from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.contrib import messages
from todos.models import UserTodo
from todos.utils import (
    get_oauth_token,
    get_oauth_url_token,
    get_oauth_user,
    get_user_info_url,
)

# import requests

# Create your views here.


class GoogleAuth(View):

    user = {}

    def get(self, request):
        try:
            code = request.GET["code"]
            data = get_oauth_token(code=code)
            result = get_oauth_user(token=f"Bearer {data.get("access_token")}")
            self.user = result
            UserTodo.objects.get(email=result.get("email"))

            messages.info(
                request,
                message="account already exists, log into your account",
            )

            return HttpResponseRedirect(
                redirect_to=reverse("todo_list:todo_user_login")
            )
        except UserTodo.DoesNotExist:
            data = {
                "company": "google",
                "first_name": self.user.get("family_name"),
                "last_name": self.user.get("given_name"),
                "actived": True,
                "email": self.user.get("email"),
            }
            user = UserTodo(**data)
            user.save()
            messages.info(
                request,
                message="account has been created successfully, log into your account",
            )
            return HttpResponseRedirect(
                redirect_to=reverse("todo_list:todo_user_login")
            )
        except Exception:
            return render(
                request,
                "500.html",
            )
