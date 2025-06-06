# Generated by Django 5.2 on 2025-04-23 11:58

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0014_factorauth_is_auth'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResetPassword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=None, max_length=10, null=True, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='todos.usertodo')),
            ],
        ),
    ]
