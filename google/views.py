import datetime
import os
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.core.mail import send_mail
from todos.models import UserTodo
from todos.utils import (
    get_jwt_token,
    get_oauth_token,
    get_oauth_url_token,
    get_oauth_user,
    get_user_info_url,
)

# import requests

# Create your views here.


class GoogleAuth(View):

    user = {}

    def get(self, request: HttpRequest):
        try:
            code = request.GET.get("code") or ""
            data = get_oauth_token(code=code)
            result = get_oauth_user(token=f"Bearer {data.get("access_token")}")
            self.user = result
            u = UserTodo.objects.get(email=result.get("email"))

            if u and u.actived == True:
                request.session["token"] = get_jwt_token(
                    payload={
                        "is_auth": True,
                        "user_id": str(u.id),
                        "user_name": u.last_name,
                        "exp": datetime.datetime.now() + datetime.timedelta(days=365),
                    }
                )
                # send email
                send_mail(
                    subject="new connection on your account",
                    message=f"new connection",
                    from_email=os.getenv("SMTP_USER"),
                    recipient_list=[u.email],
                    html_message=f"Dear <b>{u.last_name}</b>, you have a new connection on your Account",
                )

                return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))

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
