
from django.contrib import admin 
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',views.index, name="index"),
    path('register',views.register, name="register"),
    path('log_in',views.log_in, name="log_in"),
    path('dashboard',views.dashboard, name="dashboard"),

    path('upload_image',views.upload_image, name="upload_image"),
    path('download_merged_image',views.download_merged_image, name="download_merged_image"),
    path('log_out',views.log_out, name="log_out"),

    path("upload_doc/", views.upload_doc, name="upload_doc"),  # Upload & split DOCX
    path("merge-doc/", views.merge_word_documents, name="merge_word_documents"),  # Merge & download DOCX
    path("download/<int:doc_id>/", views.download_doc, name="download_doc"),  # Download DOCX with PIN
    
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),  # Uploading PDFs
    path('download_pdf/<int:pdf_id>/', views.download_pdf, name='download_pdf'),  # Downloading with PIN authentication
    path('merge_pdf_documents/', views.merge_pdf_documents, name='merge_pdf_documents'),  


    path("upload_video/", views.upload_video, name="upload_video"),
    path("list_videos/", views.list_videos, name="list_videos"),
    path("download_video/<int:video_id>/", views.download_video, name="download_video"),


    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)