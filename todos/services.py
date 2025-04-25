from todos.models import Todo


def get_todos(
    query: dict,
    start=0,
    end=100,
) -> list:
    """get todos list between start and end interval

    Args:
        query (dict): _description_
        start (int, optional): start index. Defaults to 0.
        end (int, optional): end index. Defaults to 100.

    Returns:
        list: list of todos
    """
    todos = Todo.objects.filter(**query)[start:end]
    return [todo for todo in todos]
