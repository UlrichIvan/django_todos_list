import datetime
import bcrypt
from django.test import TestCase, Client
from django.urls import reverse

from todos.models import UserTodo
from todos.utils import get_jwt_token


class TodosListViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.code = "97D08BB6"
        self.user_form = {
            "first_name": "test1",
            "last_name": "test2",
            "email": "ab@gmail.com",
            "actived": False,
            "code": self.code,
        }
        self.password = "testazertyaa"

    def create_user(self):
        self.user = UserTodo(
            **self.user_form,
            password=bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode(),
        )
        self.user.save()
        self.token = get_jwt_token(
            payload={
                "is_auth": True,
                "user_id": str(self.user.id),
                "user_name": self.user.last_name,
                "photo": None,
                "iat": datetime.datetime.now(),
                "exp": datetime.datetime.now() + datetime.timedelta(days=365),
            }
        )

    def test_index_pass(self):
        self.create_user()
        session = self.client.session
        session["token"] = self.token
        session.save()
        res = self.client.get(path=reverse("todo_list:index"))
        self.assertEqual(res.status_code, 200)

    def test_index_fail(self):
        res = self.client.get(path=reverse("todo_list:index"))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("todo_list:todo_user_login"))


class AddTodoViewTest(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.code = "97D08BB6"
        self.user_form = {
            "first_name": "test1",
            "last_name": "test2",
            "email": "ab@gmail.com",
            "actived": False,
            "code": self.code,
        }
        self.password = "testazertyaa"
        self.create_user()

    def create_user(self):
        self.user = UserTodo(
            **self.user_form,
            password=bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode(),
        )
        self.user.save()
        self.token = get_jwt_token(
            payload={
                "is_auth": True,
                "user_id": str(self.user.id),
                "user_name": self.user.last_name,
                "photo": None,
                "iat": datetime.datetime.now(),
                "exp": datetime.datetime.now() + datetime.timedelta(days=365),
            }
        )
        session = self.client.session
        session["token"] = self.token
        session.save()

    def test_add_todo_get(self):
        res = self.client.get(path=reverse("todo_list:add_todo"))
        self.assertEqual(res.status_code, 200)

    def test_add_todo_pass(self):
        res = self.client.post(
            path=reverse("todo_list:add_todo"),
            data={
                "title": "Test Todo",
                "content": "This is a test todo item.",
                "done": False,
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        messages = list(res.context["messages"])
        self.assertTrue(any("todo has been created successfully. create another todo if you want" in str(m) for m in messages))
    def test_add_todo_fail(self):
        res = self.client.post(
            path=reverse("todo_list:add_todo"),
            data={
                "title": "",
                "content": "This is a test todo item.",
                "done": False,
            },
            follow=True,
        )
        self.assertEqual(res.status_code, 200)
        messages = list(res.context["messages"])
        self.assertTrue(any("invalid form data" in str(m) for m in messages))
