# Generated by Django 4.1.13 on 2023-12-21 13:56

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("user_auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Alert",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("verb", models.CharField(blank=True, max_length=255, null=True)),
                ("target", models.CharField(blank=True, max_length=255, null=True)),
                ("content", models.CharField(blank=True, max_length=512, null=True)),
                ("read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "toUser",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alerts",
                        to="user_auth.user",
                    ),
                ),
            ],
            options={
                "db_table": "alert",
            },
        ),
    ]
