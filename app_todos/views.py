from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect


def redirect_to_todos(_):
    return HttpResponseRedirect(redirect_to=reverse("todo_list:todo_user_account"))
