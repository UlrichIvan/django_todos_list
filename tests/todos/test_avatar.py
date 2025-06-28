import datetime
from io import BytesIO
import os
import shutil
from PIL import Image
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from todos.models import UserAvatar, UserTodo
from todos.utils import get_jwt_token
from django.core.files.uploadedfile import SimpleUploadedFile


class AvatarTestCase(TestCase):
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

        #  CREATE TEMP MEDIA ROOT
        self.temp_media_root = os.path.join(settings.BASE_DIR, "test_media")
        if not os.path.exists(self.temp_media_root):
            os.makedirs(self.temp_media_root)
        self.old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.temp_media_root

    def tearDown(self):
        # cleanup the temporary media root
        if os.path.exists(self.temp_media_root):
            shutil.rmtree(self.temp_media_root)
        settings.MEDIA_ROOT = self.old_media_root

    def create_in_memory_image(
        self, name="test_image.png", format="PNG", size=(100, 100), color=(255, 0, 0)
    ):
        """Crée une image PNG en mémoire pour les tests."""
        image_buffer = BytesIO()
        image = Image.new("RGB", size=size, color=color)
        image.save(image_buffer, format=format)
        image_buffer.seek(0)
        return SimpleUploadedFile(
            name=name,
            content=image_buffer.getvalue(),
            content_type=f"image/{format.lower()}",
        )

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

    def test_avatar_upload_get(self):
        self.create_user()
        res = self.client.get(
            path=reverse("todo_list:user_profile", kwargs={"pk": self.user.id})
        )
        self.assertEqual(res.status_code, 200)

    def test_avatar_upload_post_with_avatar_exists(self):
        self.create_user()
        self.user_avatar = UserAvatar.objects.create(user=self.user, avatar=None)
        # Créer un fichier image simulé
        image = self.create_in_memory_image(
            name="test_avatar.jpg", format="JPEG", size=(150, 150), color=(0, 255, 0)
        )

        res = self.client.post(
            path=reverse("todo_list:user_profile", kwargs={"pk": self.user.id}),
            data={"avatar": image},
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("todo_list:index"))

    def test_avatar_upload_post_with_avatar_not_exists(self):

        self.create_user()

        # Créer un fichier image simulé
        image = self.create_in_memory_image(
            name="test_avatar.jpg", format="JPEG", size=(150, 150), color=(0, 255, 0)
        )

        res = self.client.post(
            path=reverse("todo_list:user_profile", kwargs={"pk": self.user.id}),
            data={"avatar": image},
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("todo_list:index"))
        self.assertEqual(UserAvatar.objects.count(), 1)
        image = UserAvatar.objects.first()
        self.assertEqual(image.user, self.user)
        print(image.avatar.name)
        self.assertTrue(image.avatar.name.startswith(f"_{image.i}/"))
        # self.assertTrue(image.avatar.name.endswith(".jpeg"))
        self.assertEqual(image.height, 150)
        self.assertEqual(image.width, 150)