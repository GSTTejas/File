# Generated by Django 5.1.2 on 2025-02-11 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_uploaded_image_delete_countmodel_delete_myimagemodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploaded_image',
            name='user',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
