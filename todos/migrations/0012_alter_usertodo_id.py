# Generated by Django 5.2 on 2025-04-23 08:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0011_remove_usertodo_account_id_usertodo_actived_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertodo',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True),
        ),
    ]
