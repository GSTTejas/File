from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Uploaded_Image)
admin.site.register(UploadedDocument)
admin.site.register(UploadedPDF)
admin.site.register(Video)