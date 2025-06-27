import bcrypt
from django.test import TestCase, Client
from django.urls import reverse

from todos.models import UserTodo


class UserCreateTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.password = "testazertyaa"
        self.user_form = {
            "first_name": "test1",
            "last_name": "test2",
            "email": "ab@gmail.com",
        }
        return super().setUp()

    def test_index(self):
        res = self.client.get(path=reverse("todo_list:todo_user_account"))
        self.assertEqual(res.status_code, 200)

    def test_post_pass(self):
        # user creation with valid data
        res = self.client.post(
            path=reverse("todo_list:todo_user_account"),
            data={
                **self.user_form,
                "password": self.password,
                "confirm_password": self.password,
            },
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(
            res, expected_url=reverse("todo_list:todo_user_active_account")
        )

    def test_post_fail(self):
        # user creation with invalid data
        res = self.client.post(
            path=reverse("todo_list:todo_user_account"),
            data={
                **self.user_form,
                "password": "testazert",
                "confirm_password": "testazert",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "password must be content 12 alphanumics characters")

        # user creation with existing email
        UserTodo.objects.create(
            **self.user_form,
            password=bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode(),
        )
        res = self.client.post(
            path=reverse("todo_list:todo_user_account"),
            data={
                **self.user_form,
                "password": self.password,
                "confirm_password": self.password,
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "email already taken")


class UserActiveAccountTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.code = "97D08BB6"
        self.password = "testazertyaa"
        self.user_form = {
            "first_name": "test1",
            "last_name": "test2",
            "email": "ab@gmail.com",
            "actived": False,
            "code": self.code,
        }

    def test_index(self):
        res = self.client.get(path=reverse("todo_list:todo_user_active_account"))
        self.assertEqual(res.status_code, 200)

    def create_user(self):
        self.user = UserTodo(
            **self.user_form,
            password=bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode(),
        )
        self.user.save()

    def test_post_pass(self):
        self.create_user()
        res = self.client.post(
            path=reverse("todo_list:todo_user_active_account"),
            data={"code": self.code},
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, expected_url=reverse("todo_list:todo_user_login"))

    def test_post_fail(self):
        self.user_form["actived"] = True
        self.create_user()

        # user already activated
        self.user.actived = True
        self.user.save()
        res = self.client.post(
            path=reverse("todo_list:todo_user_active_account"),
            data={"code": self.code},
        )
        self.assertEqual(res.status_code, 401)
