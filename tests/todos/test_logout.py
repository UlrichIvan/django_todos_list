import datetime
import bcrypt
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from todos.models import UserTodo
from todos.utils import get_jwt_token


class LogoutTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user_form = {
            "first_name": "test1",
            "last_name": "test2",
            "email": "ab@gmail.com",
            "actived": True,
            "code": "97D08BB6",
        }
        self.password = "testazertyaa"

    def create_user(self):
        self.user = UserTodo(
            **{
                "first_name": "test1",
                "last_name": "test2",
                "email": "ab@gmail.com",
                "actived": True,
                "code": "97D08BB6",
            },
        )
        self.user.save()
        self.token = get_jwt_token(
            payload={
                "is_auth": True,
                "user_id": str(self.user.id),
                "user_name": self.user.last_name,
                "photo": None,
                "iat": datetime.datetime.now(),
                "exp": timezone.now() + datetime.timedelta(days=365),
            }
        )
        session = self.client.session
        session["token"] = self.token
        session.save()

    def test_logout_user_index(self):
        self.create_user()
        res = self.client.get(path=reverse("todo_list:logout"))
        self.assertEqual(res.status_code, 200)

    def test_logout_user_pass(self):
        self.create_user()
        res = self.client.post(path=reverse("todo_list:logout"), data=None)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("todo_list:todo_user_login"))
    