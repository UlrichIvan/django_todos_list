from django.shortcuts import render, Http404
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Todo
from .forms import TodoForm, EditTodoForm


class TodosListView(ListView):
    template_name = "todos/index.html"
    context_object_name = "todos"

    def get_queryset(self):
        todos_done = Todo.objects.filter(done=True)[:100]
        todos_not_done = Todo.objects.filter(done=False)[:100]
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
        try:
            todo = Todo.objects.get(pk=id)
            edit_todo = EditTodoForm(instance=todo)
            return render(
                request, self.template_name, {"edit_todo": edit_todo, "todo": todo}
            )
        except Todo.DoesNotExist:
            return HttpResponseNotFound(content="unable to edit todo")

    def post(self, request, id) -> HttpResponse | None:
        try:
            edit_form = EditTodoForm(request.POST)
            todo = Todo.objects.get(pk=id)
            if edit_form.is_valid():
                data = edit_form.cleaned_data
                todo.title = data.get("title", todo.title)
                todo.content = data.get("content", todo.content)
                todo.done = data.get("done", todo.done)
                todo.save(force_update=True)
                return HttpResponseRedirect(redirect_to=reverse("todo_list:index"))

            return render(
                request,
                self.template_name,
                {"errors": edit_form.errors, "edit_todo": edit_form, "todo": todo},
            )

        except Todo.DoesNotExist:
            return HttpResponseNotFound(content="unable to edit todo")
