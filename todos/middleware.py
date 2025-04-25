from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.sessions.models import Session
from django.urls import reverse
from todos.utils import PROTECTED_VIEWS, get_route_name, token_verify


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request: HttpRequest, view_func, view_args, vkargs):
        try:
            if get_route_name(request) in PROTECTED_VIEWS:
                token = request.session.get("token")
                if token == None:
                    return HttpResponseRedirect(
                        redirect_to=reverse("todo_list:todo_user_login")
                    )
                else:
                    token_decoded = token_verify(token)
                    if token_decoded == False:
                        session_key = request.session.session_key
                        del request.session["token"]
                        Session.objects.get(session_key=session_key).delete()
                        return HttpResponseRedirect(
                            redirect_to=reverse("todo_list:todo_user_login")
                        )
                    else:
                        request.user_todo = token_decoded
                        return None
            return None
        except:
            print("An exception occurred")
