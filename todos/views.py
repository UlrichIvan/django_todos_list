from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import Todo
from .forms import TodoForm


class TodosListView(ListView):
    template_name = "todos/index.html"
    context_object_name = "todos"

    def get_queryset(self):
        return Todo.objects.all()[:100]


class Todos(View):

    template_name = "todos/add_todo.html"

    def get(self, request) -> HttpResponse:
        form_todo = TodoForm()
        return render(request, self.template_name, {"form_todo": form_todo})

    def post(self, request) -> HttpResponse:
        todo_form = TodoForm(request.POST)
        try:
            if todo_form.is_valid():
                return HttpResponse(content="todo valided", status=200)

            return HttpResponse(content="todo not valided", status=404)
        except ValidationError:
            return HttpResponse(content="An exception occurred", status=500)
