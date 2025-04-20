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
from .models import Account, Todo, UserTodo
from .forms import TodoForm, EditTodoForm, UserForm
import os
import random
import uuid
import bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


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
                account.code = str(uuid.uuid4())[0 : random.randint(8, 10)].upper()
                account.save()

                # create user after
                user = UserTodo(**data)  # spread operator for dict object

                # password hash
                password_hashed = bcrypt.hashpw(
                    bytes(data["password"], encoding="UTF-8"), bcrypt.gensalt(15)
                )

                ob = AES.new(os.getenv("KEY_ENCRPYT").encode("UTF-8"), AES.MODE_CBC)

                password_hashed_encrypt = ob.encrypt(
                    pad(password_hashed, AES.block_size)
                )

                # encrypt password with cipher object
                user.password = password_hashed_encrypt

                user.account_id = account

                user.save()

                # send email

                send_mail(
                    subject="code actiovation",
                    message="code activation account",
                    from_email=os.getenv("SMTP_USER"),
                    recipient_list=[user.email],
                    html_message=f"use this code : <b>{account.code}</b> to actived your account.<br>This code will be expire in 1 hour",
                )

                return render(
                    request,
                    self.template_name,
                    {
                        "errors": {"user_message": "user created successfully"},
                    },
                )

                # return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))
            else:
                return render(
                    request,
                    self.template_name,
                    {"errors": user_form.errors, "user": user_form},
                )
        except Exception as _:
            raise _
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
