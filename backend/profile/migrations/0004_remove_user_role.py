# Generated by Django 4.2.1 on 2024-09-12 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("profile", "0003_alter_user_full_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="role",
        ),
    ]
