
# img

from django.db import models


class Uploaded_Image(models.Model):
    user = models.CharField(max_length=200)
    random_id = models.CharField(max_length=200)
    key = models.CharField(max_length=200)
    encrypted_paths = models.TextField()
    encrypted_password = models.CharField(max_length=200)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.random_id

# doc
 
from django.db import models

class UploadedDocument(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    password = models.CharField(max_length=20)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

# pdf

from django.db import models

class UploadedPDF(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")  # ✅ Stores file path
    upload_date = models.DateTimeField(auto_now_add=True)
    security_pin = models.CharField(max_length=6)  # ✅ Stores PIN for security

    def __str__(self):
        return self.filename

# video

from django.db import models

# Image Model
class UploadedImage(models.Model):  # Renamed to follow Python naming conventions
    user = models.CharField(max_length=200)
    random_id = models.CharField(max_length=200, unique=True)
    key = models.CharField(max_length=200)
    encrypted_paths = models.TextField()  # Stores encrypted image paths
    encrypted_password = models.CharField(max_length=200)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.random_id}"  # More descriptive

# Document Model
class UploadedDocument(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    password = models.CharField(max_length=20)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

# PDF Model
class UploadedPDF(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="pdfs/")  # Changed folder to "pdfs/" for clarity
    upload_date = models.DateTimeField(auto_now_add=True)
    security_pin = models.CharField(max_length=6)

    def __str__(self):
        return self.filename

# Video Model

class Video(models.Model):
    file = models.FileField(upload_to="videos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    pin = models.CharField(max_length=10)
    split_files = models.JSONField(default=list)

    def __str__(self):
        return f"Video {self.id} - {self.file.name}"



