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
from django.contrib import messages
from todos.utils import get_code
from .models import FactorAuth, Todo, UserTodo
from .forms import (
    TodoForm,
    EditTodoForm,
    UserActivationForm,
    UserFactAuthForm,
    UserForm,
    UserLoginForm,
    UserNewCodeForm,
)
import os
import bcrypt


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

                # create user after
                user = UserTodo(**data)
                f_auth = FactorAuth()
                f_auth.user = user

                # set code activation
                user.code = get_code()

                # hash password with bcrypt
                password_hashed = bcrypt.hashpw(
                    data.get("password").encode(), bcrypt.gensalt()
                )

                user.password = password_hashed.decode()

                user.save()
                f_auth.save()

                # send email
                send_mail(
                    subject="activation code account",
                    message="code activation account",
                    from_email=os.getenv("SMTP_USER"),
                    recipient_list=[user.email],
                    html_message=f"use this code : <b>{user.code}</b> to active your account.<br>",
                )

                messages.success(
                    request,
                    message="your account has been create successfully. Use theeee code in your emmail account to active your account",
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
    model = UserTodo

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:

        user_activation_form = UserActivationForm(request.POST)

        if user_activation_form.is_valid():

            data = user_activation_form.cleaned_data

            try:
                user = self.model.objects.get(code=data.get("code"))

                if user.actived:
                    return render(
                        request,
                        self.template_name,
                        {"errors": {"user_message": "your account already actived."}},
                    )
                else:
                    # hours count in the pass since the creation account for currentime
                    td = timezone.now() - user.updated_at
                    hours, _ = divmod(td.seconds, 3600)

                    if hours >= 1:
                        return render(
                            request,
                            self.template_name,
                            {
                                "errors": {
                                    "user_message": "your code have been expired."
                                }
                            },
                        )

                    user.actived = True

                    user.save()

                    # send email
                    send_mail(
                        subject="activation account done successfully",
                        message=f"Congratulation,{user.last_name} your account has been actived successfully",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user.email],
                        html_message=f"Dear <b>{user.last_name}</b>, your account has been actived successfully",
                    )

                    messages.success(
                        request, message="your account has been actived successfully"
                    )

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

                if user.actived == False:

                    user.code = get_code()
                    user.updated_at = timezone.now()
                    user.save()

                    #  send new code by email
                    send_mail(
                        subject="activation code account",
                        message="code activation account",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user.email],
                        html_message=f"use this code : <b>{user.code}</b> to actived your account.<br>This code will be expire in 1 hour",
                    )

                    messages.info(
                        request,
                        message="new code activation has been send to your email account successfully",
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
                    {"errors": {"user_message": "invalid email address or password"}},
                )
        except UserTodo.DoesNotExist as _:
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "invalid email address or password"}},
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

                if user.actived == True and bcrypt.checkpw(
                    data.get("password").encode(),
                    user.password.encode(),
                ):

                    f_auth = FactorAuth.objects.get(user=user)
                    f_auth.code = get_code()
                    f_auth.save()

                    # send email
                    send_mail(
                        subject="check your authentication",
                        message=f"new authentication on your account",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user.email],
                        html_message=f"Use this code <b>{f_auth.code}</b>, to valid your authentication.",
                    )

                    messages.info(
                        request,
                        message="use the code in your email account to verify your authentication",
                    )

                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_fact_auth")
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
                    {"errors": {"user_message": "invalid email or passwor"}},
                )
        except Exception as _:
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "an error occured please try again!"}},
            )


class UserFactAuth(View):
    template_name = "todos/user_fact_auth.html"
    context_object_name = "user"
    model = FactorAuth

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:

        user_fact_auth_form = UserFactAuthForm(request.POST)

        if user_fact_auth_form.is_valid():

            data = user_fact_auth_form.cleaned_data

            try:
                user_fact_auth = self.model.objects.get(code=data.get("code"))

                if user_fact_auth.user.actived == False:
                    return render(
                        request,
                        self.template_name,
                        {"errors": {"user_message": "your code is mistake"}},
                    )
                else:
                    # hours count in the pass since the creation account for currentime
                    td = timezone.now() - user_fact_auth.updated_at

                    seconds, _ = divmod(td.seconds, 60)

                    if seconds >= 60:
                        return render(
                            request,
                            self.template_name,
                            {
                                "errors": {
                                    "user_message": "your code have been expired."
                                }
                            },
                        )
                    user_fact_auth.is_auth = True
                    user_fact_auth.save()

                    # send email
                    send_mail(
                        subject="new connection on your account",
                        message=f"new connection",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user_fact_auth.user.email],
                        html_message=f"Dear <b>{user_fact_auth.user.last_name}</b>, your have a new connection on your Account",
                    )

                    return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))
            except self.model.DoesNotExist:
                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "invalid code authentication"}},
                )

        else:
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "invalid code activation"}},
            )


class UserNewCodeFactor(View):
    template_name = "todos/user_new_code_factor.html"
    context_object_name = "user"

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:
        user_code = UserNewCodeForm(request.POST)

        try:
            if user_code.is_valid():
                data = user_code.cleaned_data
                user = UserTodo.objects.get(email=data.get("email"))
                user_factor = FactorAuth.objects.get(user=user)

                if user.actived == True:
                    user_factor.code = get_code()
                    user_factor.updated_at = timezone.now()
                    user_factor.save()

                    #  send new code by email
                    send_mail(
                        subject="authentication code",
                        message="code authentication",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user.email],
                        html_message=f"use this code : <b>{user_factor.code}</b> to valid your authentication",
                    )

                    messages.info(
                        request,
                        message="new code authentication has been send to your email account successfully",
                    )

                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_fact_auth")
                    )

                return render(
                    request,
                    self.template_name,
                    {
                        "errors": {
                            "user_message": "unable to verify your authentication"
                        }
                    },
                )
            else:
                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "invalid email address or password"}},
                )
        except Exception as _:
            raise _
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "an error occured please try again!"}},
            )
