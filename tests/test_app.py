from django.test import TestCase, Client
from django.urls import reverse


class AppTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        return super().setUp()

    def test_index(self):
        res = self.client.get(path=reverse("app_index"))
        self.assertEqual(res.status_code, 302)
