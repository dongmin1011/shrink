# Generated by Django 4.1.13 on 2024-01-05 00:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0014_remove_productanalysis_result_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(blank=True, upload_to="product/image/"),
        ),
    ]
