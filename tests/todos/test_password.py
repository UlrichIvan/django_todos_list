import bcrypt
from django.test import TestCase, Client
from django.urls import reverse

from todos.models import ResetPassword, UserTodo


class NewPasswordViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.login_credentials = {
            "code": "E193DA1F3",
            "password": "testazertyaa",
            "confirm_password": "testazertyaa",
        }
        self.user_form = {
            "first_name": "test1",
            "last_name": "test2",
            "email": "ab@gmail.com",
            "actived": True,
        }
        return super().setUp()

    def test_index(self):
        res = self.client.get(path=reverse("todo_list:todo_user_new_password"))
        self.assertEqual(res.status_code, 200)

    def test_post_pass(self):
        self.user = UserTodo(
            **self.user_form,
            password=bcrypt.hashpw(
                self.login_credentials["password"].encode(), bcrypt.gensalt()
            ).decode(),
        )
        self.user.save()
        self.user_password = ResetPassword(
            user=self.user, code=self.login_credentials["code"]
        )
        self.user_password.save()

        # Good credentials with redirection
        res = self.client.post(
            path=reverse("todo_list:todo_user_new_password"),
            data=self.login_credentials,
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, expected_url=reverse("todo_list:todo_user_login"))

    def test_post_fail(self):
        self.user_form["actived"] = False
        self.user = UserTodo(
            **self.user_form,
            password=bcrypt.hashpw(
                self.login_credentials["password"].encode(), bcrypt.gensalt()
            ).decode(),
        )
        self.user.save()
        self.user_password = ResetPassword(
            user=self.user, code=self.login_credentials["code"]
        )
        self.user_password.save()

        # Good credentials with redirection
        res = self.client.post(
            path=reverse("todo_list:todo_user_new_password"),
            data=self.login_credentials,
        )
        self.assertEqual(res.status_code, 401)


class ResetPasswordView(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.login_credentials = {
            "email": "ab@gmail.com",
            "password": "testazertyaa",
        }
        self.user_form = {
            "first_name": "test1",
            "last_name": "test2",
            "email": "ab@gmail.com",
            "actived": True,
        }
        return super().setUp()

    def test_index(self):
        res = self.client.get(path=reverse("todo_list:todo_user_reset_password"))
        self.assertEqual(res.status_code, 200)

    def test_post_pass(self):
        self.user = UserTodo(
            **self.user_form,
            password=bcrypt.hashpw(
                self.login_credentials["password"].encode(), bcrypt.gensalt()
            ).decode(),
        )
        self.user.save()
        self.user_password = ResetPassword(user=self.user)
        self.user_password.save()

        # Good credentials with redirection
        res = self.client.post(
            path=reverse("todo_list:todo_user_reset_password"),
            data=self.login_credentials,
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(
            res, expected_url=reverse("todo_list:todo_user_new_password")
        )

    def test_post_fail(self):
        self.user_form["actived"] = False
        self.user = UserTodo(
            **self.user_form,
            password=bcrypt.hashpw(
                self.login_credentials["password"].encode(), bcrypt.gensalt()
            ).decode(),
        )
        self.user.save()
        self.user_password = ResetPassword(user=self.user)
        self.user_password.save()

        # Good credentials with redirection
        res = self.client.post(
            path=reverse("todo_list:todo_user_reset_password"),
            data=self.login_credentials,
        )
        self.assertEqual(res.status_code, 401)
