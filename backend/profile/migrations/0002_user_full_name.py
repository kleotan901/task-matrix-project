# Generated by Django 4.2.1 on 2024-09-06 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profile", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="full_name",
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]