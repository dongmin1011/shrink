# Generated by Django 4.1.13 on 2024-01-02 16:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("report", "0006_alter_report_status_like"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="unit",
            field=models.CharField(max_length=10, null=True),
        ),
    ]
