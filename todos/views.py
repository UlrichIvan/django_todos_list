from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from .models import Todo
from .forms import TodoForm, EditTodoForm


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