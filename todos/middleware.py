from django.http import HttpRequest, HttpResponseRedirect, HttpResponseServerError
from django.contrib.sessions.models import Session
from django.urls import reverse
from todos.utils import PROTECTED_VIEWS, EXCLUDED_VIEWS, get_route_name, token_verify


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request: HttpRequest, view_func, view_args, vkargs):
        try:
            token = request.session.get("token")
            route_name = get_route_name(request)
            if route_name in PROTECTED_VIEWS:
                if token == None:
                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_login")
                    )
                else:
                    token_decoded = token_verify(token)
                    if token_decoded == False:
                        request.session.clear()
                        return HttpResponseRedirect(
                            redirect_to=reverse("todo_list:todo_user_login")
                        )
                    else:
                        request.user_todo = token_decoded
                        return None

            elif route_name in EXCLUDED_VIEWS:
                return None
            else:
                if token != None:
                    token_decoded = token_verify(token)
                    if token_decoded == False:
                        request.session.clear()
                        return HttpResponseRedirect(
                            redirect_to=reverse("todo_list:todo_user_login")
                        )
                    else:
                        return HttpResponseRedirect(
                            redirect_to=reverse("todo_list:index")
                        )
                return None
        except Exception:
            return HttpResponseServerError(
                content="an error occured, please trai agin later!"
            )
