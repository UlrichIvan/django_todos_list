import datetime
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic.detail import DetailView
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.sessions.models import Session
from todos.services import get_todos
from django.forms.models import model_to_dict
from todos.utils import get_code, get_jwt_token
from .models import FactorAuth, ResetPassword, Todo, UserTodo
from .forms import (
    TodoForm,
    EditTodoForm,
    UserActivationForm,
    UserFactAuthForm,
    UserForm,
    UserLoginForm,
    UserNewCodeForm,
    UserNewPasswordForm,
)
import os
import bcrypt


class TodosListView(View):
    template_name = "todos/index.html"

    def get(self, request: HttpRequest):
        try:
            user_todo: dict = getattr(request, "user_todo")
            t_done = Todo.objects.filter(
                done=True, deleted_at__isnull=True, user_id__id=user_todo.get("user_id")
            )[0:100]
            t_not_done = Todo.objects.filter(
                done=False,
                deleted_at__isnull=True,
                user_id__id=user_todo.get("user_id"),
            )[0:100]

            return render(
                request,
                self.template_name,
                {
                    "todos": {
                        "todos_done": t_done,
                        "todos_not_done": t_not_done,
                    },
                    "user_name": user_todo.get("user_name"),
                },
            )
        except Exception as e:
            return render(
                request,
                "500.html",
            )


class AddTodo(View):

    template_name = "todos/add_todo.html"

    def get(self, request) -> HttpResponse:
        form_todo = TodoForm()
        return render(
            request,
            self.template_name,
            {"form_todo": form_todo, "user_name": request.user_todo.get("user_name")},
        )

    def post(self, request) -> HttpResponse | None:
        todo_form = TodoForm(request.POST)
        try:
            user_todo = request.user_todo
            if todo_form.is_valid():
                data = todo_form.cleaned_data
                todo = Todo(**data)
                todo.user_id = UserTodo.objects.get(id=user_todo.get("user_id"))
                todo.save()
                messages.success(
                    request,
                    message="todo has been created successfully. create another todo if you want",
                )
                return render(
                    request,
                    self.template_name,
                    {"user_name": request.user_todo.get("user_name")},
                )

            messages.error(
                request,
                message="invalid form data",
            )

            return render(
                request,
                self.template_name,
                {
                    "errors": todo_form.errors,
                    "todo": todo_form,
                    "user_name": request.user_todo.get("user_name"),
                },
            )

        except (ValidationError, Exception):
            messages.error(
                request,
                message="An occurred, please try again, later",
            )

            return render(
                request,
                self.template_name,
                {
                    "errors": todo_form.errors,
                    "todo": todo_form,
                    "user_name": request.user_todo.get("user_name"),
                },
            )


class EditTodo(View):

    template_name = "todos/edit_todo.html"

    def get(self, request, id) -> HttpResponse:

        todo = get_object_or_404(Todo, pk=id)
        user_todo = request.user_todo

        return render(
            request,
            self.template_name,
            {
                "todo": {
                    **model_to_dict(todo),
                    "id": id,
                    "expired_at": todo.get_expired(),
                },
                "user_name": user_todo.get("user_name"),
            },
        )

    def post(self, request, id) -> HttpResponse | None:

        todo = get_object_or_404(Todo, pk=id)

        edit_form = TodoForm(request.POST)

        user_name = request.user_todo.get("user_name")
        if edit_form.is_valid():
            data = edit_form.cleaned_data
            todo.title = data.get("title", todo.title)
            todo.content = data.get("content", todo.content)
            todo.done = data.get("done", todo.done)
            todo.updated_at = timezone.now()
            todo.expired_at = data.get("expired_at", todo.expired_at)
            todo.save()
            return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))

        return render(
            request,
            self.template_name,
            {
                "errors": edit_form.errors,
                "todo": {
                    **model_to_dict(todo),
                    "id": id,
                    "expired_at": todo.get_expired(),
                },
                "user_name": user_name,
            },
        )


class TodoDetails(DetailView):
    template_name = "todos/details.html"
    context_object_name = "todo"
    model = Todo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_todo: dict = getattr(self.request, "user_todo")
        context["user_name"] = user_todo.get("user_name")
        return context


class TodoDelete(View):
    template_name = "todos/delete.html"
    context_object_name = "todo"

    def get(self, request, id) -> HttpResponse:
        todo = get_object_or_404(Todo, pk=id)
        user_todo = request.user_todo
        return render(
            request,
            self.template_name,
            {"todo": todo, "user_name": user_todo.get("user_name")},
        )

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

                # init 2f auht and reset password
                f_auth = FactorAuth()
                r_password = ResetPassword()
                f_auth.user = user
                r_password.user = user

                # set code activation
                user.code = get_code()

                # hash password with bcrypt
                password_hashed = bcrypt.hashpw(
                    str(data.get("password")).encode(), bcrypt.gensalt()
                )

                user.password = password_hashed.decode()

                user.save()
                f_auth.save()
                r_password.save()

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
                    message="your account has been create successfully. Use this code in your email account to active your account",
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
            except Exception:
                return render(
                    request,
                    self.template_name,
                    {
                        "errors": {
                            "user_message": "an error occured please try again later"
                        }
                    },
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
                    data.get("password", "").encode(),
                    user.password.encode(),
                ):
                    f_auth = UserTodo.objects.get(factorauth__user=user)
                    f_auth.code = get_code()
                    f_auth.updated_at = timezone.now()
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
                    {"errors": {"user_message": "invalid email or password"}},
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
                user_fact_auth: FactorAuth = self.model.objects.get(
                    code=data.get("code")
                )
                user: UserTodo | None = user_fact_auth.user
                if user and user.actived == False:
                    return render(
                        request,
                        self.template_name,
                        {"errors": {"user_message": "your code is mistake"}},
                    )
                elif user and user.actived == True:
                    # hours count in the pass since the creation account for currentime
                    td = timezone.now() - user_fact_auth.updated_at

                    minutes, _ = divmod(td.total_seconds(), 60)

                    if minutes > 1:
                        return render(
                            request,
                            self.template_name,
                            {
                                "errors": {
                                    "user_message": "your code have been expired."
                                }
                            },
                        )
                    user_fact_auth.save()

                    request.session["token"] = get_jwt_token(
                        payload={
                            "is_auth": True,
                            "user_id": str(user.id),
                            "user_name": user.last_name,
                            "exp": datetime.datetime.now()
                            + datetime.timedelta(days=365),
                        }
                    )
                    # send email
                    send_mail(
                        subject="new connection on your account",
                        message=f"new connection",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user.email],
                        html_message=f"Dear <b>{user.last_name}</b>, your have a new connection on your Account",
                    )

                    return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))
            except self.model.DoesNotExist:
                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "invalid code authentication"}},
                )

            except Exception:
                return render(
                    request,
                    self.template_name,
                    {
                        "errors": {
                            "user_message": "error occured, please try again later"
                        }
                    },
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
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "an error occured please try again!"}},
            )


class ResetPasswordView(View):
    template_name = "todos/user_reset_password.html"
    context_object_name = "user"

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:
        user_code = UserNewCodeForm(request.POST)

        try:
            if user_code.is_valid():
                data = user_code.cleaned_data
                user = UserTodo.objects.get(email=data.get("email"))
                rpwd = ResetPassword.objects.get(user=user)

                if user.actived == True:

                    rpwd.code = get_code()
                    rpwd.updated_at = timezone.now()
                    rpwd.save()

                    #  send new code by email
                    send_mail(
                        subject="reset code account",
                        message="code to reset account",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user.email],
                        html_message=f"use this code : <b>{rpwd.code}</b> to reset your account.<br>",
                    )

                    messages.info(
                        request,
                        message="new code has been send to reset your password",
                    )

                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_new_password")
                    )

                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "unable to reset your account"}},
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


class NewPasswordView(View):
    template_name = "todos/user_new_password.html"
    context_object_name = "user"

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request) -> HttpResponse | None:

        user_form = UserNewPasswordForm(request.POST)

        try:
            if user_form.is_valid():
                data = user_form.cleaned_data
                rpwd = ResetPassword.objects.get(code=data.get("code"))
                user = rpwd.user
                if user and user.actived == True:

                    # hours count in the pass since the creation account for currentime
                    td = timezone.now() - rpwd.updated_at
                    hours, _ = divmod(td.seconds, 3600)

                    if hours >= 1:
                        return render(
                            request,
                            self.template_name,
                            {
                                "errors": {
                                    "user_message": "your code have been expired, get new code to reset your password"
                                }
                            },
                        )

                    # hash password with bcrypt
                    password_hashed = bcrypt.hashpw(
                        str(data.get("password")).encode(), bcrypt.gensalt()
                    )

                    user.password = password_hashed.decode()
                    user.updated_at = timezone.now()
                    user.save()

                    #  send new code by email
                    send_mail(
                        subject="your password has reset successfully",
                        message="password reset",
                        from_email=os.getenv("SMTP_USER"),
                        recipient_list=[user.email],
                        html_message=f"your password has reset successfully",
                    )

                    messages.success(
                        request,
                        message="password reset successfully",
                    )

                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_login")
                    )

                return render(
                    request,
                    self.template_name,
                    {"errors": {"user_message": "unable to reset your account"}},
                )
            else:
                return render(
                    request,
                    self.template_name,
                    {"errors": user_form.errors, "user": user_form},
                )
        except ResetPassword.DoesNotExist:
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "invalid code"}},
            )
        except Exception as _:
            return render(
                request,
                self.template_name,
                {"errors": {"user_message": "an error occured please try again!"}},
            )


class LogOut(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            request.session.clear()
            return HttpResponseRedirect(
                redirect_to=reverse("todo_list:todo_user_login")
            )
        except (Session.DoesNotExist, Exception):
            return HttpResponseRedirect(
                redirect_to=reverse("todo_list:todo_user_login")
            )
