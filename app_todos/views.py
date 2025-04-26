from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponseRedirect


def redirect_to_todos(_):
    return HttpResponseRedirect(redirect_to=reverse("todo_list:todo_user_login"))


def not_found(request, _):
    return render(request, "404.html", status=404)


def interval_error(request):
    return render(request, "500.html", us=500)
