import bcrypt
from django.test import TestCase, Client
from django.urls import reverse

from todos.forms import UserLoginForm
from todos.models import FactorAuth, UserTodo


class LoginTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.login_credentials = {"email": "ab@gmail.com", "password": "testazertyaa"}
        self.user_form = {
            "first_name": "test1",
            "last_name": "test2",
            "email": "ab@gmail.com",
            "actived": True,
        }
        return super().setUp()

    def test_index(self):
        res = self.client.get(path=reverse("todo_list:init"))
        self.assertEqual(res.status_code, 302)

    def test_get_method(self):
        res = self.client.get(path=reverse("todo_list:todo_user_login"))
        self.assertEqual(res.status_code, 200)

    def test_login_form(self):
        form = UserLoginForm(self.login_credentials)
        self.assertTrue(form.is_valid())

    def test_login_user(self):

        # good crendentials
        self.user = UserTodo(
            **self.user_form,
            password=bcrypt.hashpw(
                self.login_credentials["password"].encode(), bcrypt.gensalt()
            ).decode(),
        )
        self.user.save()
        self.user_factor = FactorAuth(user=self.user)
        self.user_factor.save()

        # Good credentials with redirection
        res = self.client.post(
            path=reverse("todo_list:todo_user_login"),
            data=self.login_credentials,
        )
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, expected_url=reverse("todo_list:todo_user_fact_auth"))
        
        # Bad credentials with unauthorization
        res = self.client.post(
            path=reverse("todo_list:todo_user_login"),
            data={**self.login_credentials, "password": "testazertyab"},
        )
        self.assertEqual(res.status_code, 401)

        # error server
        self.user.delete()
        res = self.client.post(
            path=reverse("todo_list:todo_user_login"),
            data={**self.login_credentials, "password": "testazertyab"},
        )
        self.assertEqual(res.status_code, 501)
