# Generated by Django 4.1.13 on 2023-12-27 07:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProductAnalysis",
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
                ("image", models.ImageField(blank=True, upload_to="")),
                ("result", models.CharField(max_length=100, null=True)),
                ("weight", models.CharField(max_length=50, null=True)),
                ("create_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
