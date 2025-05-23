# Generated by Django 5.1.6 on 2025-03-01 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_uploaded_image_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='documents/')),
                ('password', models.CharField(max_length=20)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
