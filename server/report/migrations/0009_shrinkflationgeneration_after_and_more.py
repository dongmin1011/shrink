# Generated by Django 4.1.13 on 2024-01-03 02:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("report", "0008_shrinkflationgeneration"),
    ]

    operations = [
        migrations.AddField(
            model_name="shrinkflationgeneration",
            name="after",
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="shrinkflationgeneration",
            name="before",
            field=models.CharField(max_length=10, null=True),
        ),
    ]
