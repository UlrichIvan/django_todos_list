from django.shortcuts import render
from django.views import View
from django.http import HttpResponse


# Create your views here.
class Todos(View):

    template_name = "todos/index.html"

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)
