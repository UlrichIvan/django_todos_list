from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend

from todos.utils import get_code
from .models import Account, Todo, UserTodo
from .forms import (
    TodoForm,
    EditTodoForm,
    UserActivationForm,
    UserForm,
    UserLoginForm,
    UserNewCodeForm,
)
import os
import random
import uuid
import bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class TodosListView(ListView):
    template_name = "todos/index.html"
    context_object_name = "todos"

    def get_queryset(self):
        todos_done = Todo.objects.filter(done=True, deleted_at__isnull=True)[:100]
        todos_not_done = Todo.objects.filter(done=False, deleted_at__isnull=True)[:100]
        return {"todos_done": todos_done, "todos_not_done": todos_not_done}


class AddTodo(View):

    template_name = "todos/add_todo.html"

    def get(self, request) -> HttpResponse:
        form_todo = TodoForm()
        return render(request, self.template_name, {"form_todo": form_todo})

    def post(self, request) -> HttpResponse | None:
        todo_form = TodoForm(request.POST)
        try:
            if todo_form.is_valid():
                todo_form.save()
                return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))

            return render(
                request,
                self.template_name,
                {"errors": todo_form.errors, "todo": todo_form},
            )

        except ValidationError:
            return HttpResponse(content="An exception occurred", status=500)


class EditTodo(View):

    template_name = "todos/edit_todo.html"

    def get(self, request, id) -> HttpResponse:

        todo = get_object_or_404(Todo, pk=id)

        edit_todo = EditTodoForm(instance=todo)

        return render(
            request, self.template_name, {"edit_todo": edit_todo, "todo": todo}
        )

    def post(self, request, id) -> HttpResponse | None:

        todo = get_object_or_404(Todo, pk=id)

        edit_form = EditTodoForm(request.POST)

        if edit_form.is_valid():
            data = edit_form.cleaned_data
            todo.title = data.get("title", todo.title)
            todo.content = data.get("content", todo.content)
            todo.done = data.get("done", todo.done)
            todo.updated_at = timezone.now()
            todo.save(force_update=True)
            return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))

        return render(
            request,
            self.template_name,
            {"errors": edit_form.errors, "edit_todo": edit_form, "todo": todo},
        )


class TodoDetails(DetailView):
    template_name = "todos/details.html"
    context_object_name = "todo"
    model = Todo


class TodoDelete(View):
    template_name = "todos/delete.html"
    context_object_name = "todo"

    def get(self, request, id) -> HttpResponse:
        todo = get_object_or_404(Todo, pk=id)
        return render(request, self.template_name, {"todo": todo})

    def post(self, _, id) -> HttpResponse | None:
        todo = get_object_or_404(Todo, pk=id)
        todo.deleted_at = timezone.now()
        todo.save()
        return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))


class UserCreate(View):
    template_name = "todos/user_account.html"
    context_object_name = "user"

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:

        user_form = UserForm(request.POST)

        try:
            if user_form.is_valid():

                data = user_form.cleaned_data

                # create account first
                account = Account()
                account.code = get_code()
                account.save()

                # create user after
                user = UserTodo(**data)

                # encrypt password with cipher object
                password_hashed = bcrypt.hashpw(
                    data.get("password").encode(), bcrypt.gensalt(15)
                )

                user.password = password_hashed.decode()

                user.account_id = account

                user.save()

                # send email
                send_mail(
                    subject="activation code account",
                    message="code activation account",
                    from_email=os.getenv("SMTP_USER"),
                    recipient_list=[user.email],
                    html_message=f"use this code : <b>{account.code}</b> to active your account.<br>This code will be expire in 1 hour",
                )

                return HttpResponseRedirect(
                    redirect_to=reverse("todo_list:todo_user_active_account")
                )
            else:
                return render(
                    request,
                    self.template_name,
                    {"errors": user_form.errors, "user": user_form},
                )
        except Exception as _:
            return render(
                request,
                self.template_name,
                {
                    "errors": {
                        **user_form.errors,
                        "user_message": "an error occured please try again",
                    },
                    "user": user_form,
                },
            )


class UserActiveAccount(View):
    template_name = "todos/user_active_account.html"
    context_object_name = "user"
    model = Account

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:

        user_activation_form = UserActivationForm(request.POST)

        if user_activation_form.is_valid():

            data = user_activation_form.cleaned_data

            try:
                account = self.model.objects.get(code=data.get("code"))

                if account.actived:
                    return render(
                        request,
                        self.template_name,
                        {"errors": {"user_message": "your account already actived."}},
                    )
                else:
                    # hours count in the pass since the creation account for currentime
                    td = timezone.now() - account.updated_at
                    hours, _ = divmod(td.seconds, 3600)

                    if hours >= 1:
                        return render(
                            request,
                            self.template_name,
                            {"errors": {"user_message": "your code had been expired."}},
                        )
                    account.actived = True
                    account.save()
                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_login")
                    )
            except self.model.DoesNotExist:
                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "unable to active your account"}},
                )

        else:
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "invalid code activation"}},
            )


class UserNewCode(View):
    template_name = "todos/user_new_code.html"
    context_object_name = "user"

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:
        user_code = UserNewCodeForm(request.POST)

        try:
            if user_code.is_valid():
                data = user_code.cleaned_data
                user = UserTodo.objects.get(email=data.get("email"))

                if user.account_id.actived == False:

                    account = user.account_id
                    account.code = str(uuid.uuid4())[0 : random.randint(8, 10)].upper()
                    account.updated_at = timezone.now()
                    account.save()

                    #  send new code by email
                    send_mail(
                        subject="activation code account",
                        message="code activation account",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user.email],
                        html_message=f"use this code : <b>{account.code}</b> to actived your account.<br>This code will be expire in 1 hour",
                    )

                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_active_account")
                    )

                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "unable to activate your account"}},
                )
            else:
                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "invalid email address"}},
                )
        except Exception as _:
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "an error occured please try again!"}},
            )


class UserLogin(View):
    template_name = "todos/user_login.html"
    context_object_name = "user"
    model = UserTodo

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:
        login_form = UserLoginForm(request.POST)

        try:
            if login_form.is_valid():
                data = login_form.cleaned_data
                user = UserTodo.objects.get(email=data.get("email"))

                if user.account_id.actived == True and bcrypt.checkpw(
                    data.get("password").encode(),
                    user.password.encode(),
                ):
                    return render(
                        request,
                        self.template_name,
                        {"errors": {"user_message": "user valided successfully!"}},
                    )
                else:
                    return render(
                        request,
                        self.template_name,
                    )
            else:
                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "invalid email or password address"}},
                )
        except Exception as _:
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "an error occured please try again!"}},
            )
