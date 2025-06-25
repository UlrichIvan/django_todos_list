from django.http import HttpRequest, HttpResponseRedirect, HttpResponseServerError
from django.urls import reverse
from todos.utils import PROTECTED_VIEWS, token_verify


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request: HttpRequest, view_func, view_args, vkargs):
        try:
            token = request.session.get("token", "")
            token_decoded = token_verify(token)

            if token_decoded:
                if request.path_info.startswith(PROTECTED_VIEWS):
                    setattr(request, "user_todo", token_decoded)
                    return None
                else:
                    return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))
            else:
                if request.path_info.startswith(PROTECTED_VIEWS):
                    request.session.clear()
                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_login")
                    )
                else:
                    return None

        except Exception as e:
            return HttpResponseServerError(
                content="An error occured, please try agin later!"
            )
