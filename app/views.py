from django.shortcuts import render , redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .auth import authentication
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .process import *
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
from .models import *
from datetime import datetime
from tempfile import NamedTemporaryFile
import os 
import random
from cryptography.fernet import Fernet
import numpy as np
import glob
from io import BytesIO
from django.http import HttpResponse
import json

import cv2
import numpy as np
from PIL import Image

def merge_segmented_images(image_paths):
    """
    Merges segmented images into a single image that exactly matches the original uploaded image.
    :param image_paths: List of paths to segmented images.
    :return: Merged image as a PIL Image object.
    """
    image_paths = eval(image_paths) if isinstance(image_paths, str) else image_paths
    if not image_paths or len(image_paths) == 0:
        print("Error: No segmented images found!")
        return None

    # Sort the image paths to maintain correct order
    image_paths = sorted(image_paths)

    # Load the first image for reference dimensions
    first_img = cv2.imread(image_paths[0], cv2.IMREAD_UNCHANGED)
    if first_img is None:
        print("Error: Unable to load first image!")
        return None

    height, width, channels = first_img.shape
    merged_img = np.zeros_like(first_img, dtype=np.uint8)  # Create blank canvas

    # Merge segmented images using bitwise OR to restore original pixel values
    for img_path in image_paths:
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            continue

        # Ensure the image size matches the original
        if img.shape[:2] != (height, width):
            img = cv2.resize(img, (width, height), interpolation=cv2.INTER_NEAREST)

        # Perform bitwise OR operation to reconstruct original image
        merged_img = cv2.bitwise_or(merged_img, img)

    # Convert to PIL format for Django response
    merged_pil = Image.fromarray(
        cv2.cvtColor(merged_img, cv2.COLOR_BGRA2RGBA) if channels == 4 else cv2.cvtColor(merged_img, cv2.COLOR_BGR2RGB)
    )
    return merged_pil



from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Uploaded_Image
from cryptography.fernet import Fernet
from io import BytesIO

def download_merged_image(request):
    """
    Handles the request to merge segmented images and return as a downloadable file.
    Ensures that the merged image is identical to the originally uploaded image.
    """
    if request.method == "POST":
        file_id = request.POST.get('file_id')
        password = request.POST.get('password')

        try:
            image_data = Uploaded_Image.objects.get(random_id=file_id)
        except Uploaded_Image.DoesNotExist:
            return HttpResponse("Error: File not found!", content_type="text/plain")

        # Decrypt paths and password
        cipher_suite = Fernet(image_data.key.encode())

        try:
            decrypted_paths = cipher_suite.decrypt(eval(image_data.encrypted_paths)).decode()
            decrypted_password = cipher_suite.decrypt(eval(image_data.encrypted_password)).decode()
        except Exception as e:
            return HttpResponse(f"Decryption error: {str(e)}", content_type="text/plain")

        if password == decrypted_password:
            # Convert decrypted paths from string to list
            image_paths = decrypted_paths.strip("[]").replace("'", "").split(", ")

            # Merge the segmented images
            merged_img = merge_segmented_images(image_paths)

            if merged_img:
                img_io = BytesIO()
                merged_img.save(img_io, format="PNG")
                img_io.seek(0)

                response = HttpResponse(img_io, content_type="image/png")
                response['Content-Disposition'] = 'attachment; filename="merged_output.png"'
                return response
            else:
                return HttpResponse("Error: Merging failed!", content_type="text/plain")
        else:
            return HttpResponse("Invalid password!", content_type="text/plain")

    return redirect("dashboard")



def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']
        
        # Call the authentication function with correct arguments
        verify = authentication(fname, lname, password, repassword)
        
        if verify == "success":
            user = User.objects.create_user(email, password, repassword)
            user.first_name = fname
            user.last_name = lname
            user.save()
            messages.success(request, "Your Account has been Created.")
            return redirect("log_in")
        else:
            messages.error(request, verify)
            return redirect("register")
    return render(request, 'register.html')

def log_in(request):
    if request.method == "POST":
        username = request.POST['username']  # Corrected to 'username'
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Log In Successful...!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("log_in")
    return render(request, 'log_in.html')

@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def dashboard(request):
    user_images = Uploaded_Image.objects.filter(user=request.user.username)
    context = {
        'fname' : request.user.first_name,
        'user_images' : user_images
    }
    return render(request, 'dashboard.html', context)  


@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def upload_image(request):
    context = {
        'fname' : request.user.first_name
    }
    if request.method == "POST":
        image = request.FILES['image']
        password = request.POST['password']
        random_id = str(random.randint(100000000, 999999999))
        paths = t_coloring_split(image, f"media/upload/{random_id}", parts=10)
        print(type(paths))
        FERNET_KEY = Fernet.generate_key()
        cipher_suite = Fernet(FERNET_KEY)
        str_key = FERNET_KEY.decode()
        encrypted_paths = cipher_suite.encrypt(str(paths).encode())
        encrypted_password = cipher_suite.encrypt(str(password).encode())

        save_image = Uploaded_Image(user = request.user.username, random_id=random_id, key = str_key, encrypted_paths=encrypted_paths, encrypted_password=encrypted_password)
        save_image.save()
        messages.success(request, "Image Uploaded Successfully...!")
        
    return render(request, 'upload_image.html', context)  

@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def log_out(request):
    logout(request)
    messages.success(request, "Log out Successfuly...!")
    return redirect("/")


# newlly added for upload_doc and upload_pdf

import os
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from docx import Document
from .models import UploadedDocument
from .utils import split_word_document, merge_documents

# Define storage directories
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads")
SPLIT_DIR = os.path.join(settings.MEDIA_ROOT, "split_docs")
MERGED_DIR = os.path.join(settings.MEDIA_ROOT, "merged_docs")

def upload_doc(request):
    context = {
        'fname' : request.user.first_name,
    }
    """Handles DOCX file upload, splits into parts, and stores history."""
    if request.method == "POST":
        docx_file = request.FILES.get("document")
        password = request.POST.get("password")

        if not docx_file:
            messages.error(request, "No file uploaded! Please select a DOCX file.")
            return redirect("upload_doc")

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, docx_file.name)

        print(f"Saving file to: {file_path}")

        try:
            # Save the uploaded file
            with open(file_path, "wb") as f:
                for chunk in docx_file.chunks():
                    f.write(chunk)

            if not os.path.exists(file_path):
                print("❌ File was not saved properly!")
                messages.error(request, "Error saving file!")
                return redirect("upload_doc")

            print(f"✅ File saved successfully: {file_path}")

            # Ensure file is accessible before opening
            time.sleep(1)
            with open(file_path, "rb") as f:
                f.read()
            print(f"✅ File is accessible: {file_path}")

            # Check if the file is a valid DOCX before proceeding
            try:
                Document(file_path)
                print("✅ File successfully opened with python-docx.")
            except Exception as e:
                print(f"❌ Invalid DOCX file: {e}")
                messages.error(request, f"Invalid DOCX file: {e}")
                return redirect("upload_doc")

            # Save file details to the database
            doc_entry = UploadedDocument.objects.create(
                filename=docx_file.name,
                file=docx_file,
                password=password
            )

            # Split the document
            success = split_word_document(file_path)
            if not success:
                messages.error(request, "Error splitting document!")
                return redirect("upload_doc")

            messages.success(request, "File uploaded and split successfully!")
            return redirect("upload_doc")

        except Exception as e:
            print(f"❌ Error processing file: {e}")
            messages.error(request, f"File upload failed: {e}")
            return redirect("upload_doc")

    # Fetch all uploaded documents, ordered by latest first
    context['uploaded_docs'] = UploadedDocument.objects.all().order_by("-upload_date")
    return render(request, "upload_doc.html", context)

def merge_word_documents(request):
    """Merges split DOCX files into a single document."""
    os.makedirs(MERGED_DIR, exist_ok=True)
    merged_file_path = os.path.join(MERGED_DIR, "merged_document.docx")

    files = sorted([os.path.join(SPLIT_DIR, f) for f in os.listdir(SPLIT_DIR) if f.endswith(".docx")])

    if not files:
        messages.error(request, "No split files found for merging.")
        return redirect("upload_doc")

    success = merge_documents(files, merged_file_path)
    if not success:
        messages.error(request, "Error merging documents!")
        return redirect("upload_doc")

    with open(merged_file_path, "rb") as doc_file:
        response = HttpResponse(doc_file.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response["Content-Disposition"] = "attachment; filename=merged_document.docx"
        return response

def download_doc(request, doc_id):
    """Allows users to download the original uploaded file after PIN authentication."""
    if request.method == "POST":
        pin_entered = request.POST.get("pin")
        doc = get_object_or_404(UploadedDocument, id=doc_id)

        if pin_entered == doc.password:
            response = HttpResponse(doc.file.open(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response["Content-Disposition"] = f'attachment; filename="{doc.filename}"'
            return response

        messages.error(request, "Incorrect PIN!")
        return redirect("upload_doc")

    # =======================================================================
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib import messages
from django.conf import settings
from .models import UploadedPDF
from .utils import verify_pdf_pin, split_pdf_in_parts, merge_pdfs
import os

# Ensure upload directory exists
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_pdf(request):
    uploaded_pdfs = UploadedPDF.objects.all().order_by("-upload_date")
    context = {
        'fname' : request.user.first_name,
        'uploaded_pdfs': uploaded_pdfs,
    }
    """Handles PDF file upload and stores with PIN authentication."""
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf_file")
        security_pin = request.POST.get("password")  # PIN from form

        if not pdf_file or not security_pin:
            return HttpResponseBadRequest("Missing file or PIN!")

        # Save uploaded file in the uploads directory
        file_path = os.path.join(UPLOAD_DIR, pdf_file.name)

        with open(file_path, "wb") as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        # Save file details in the database
        uploaded_pdf = UploadedPDF.objects.create(
            filename=pdf_file.name,
            file=f"uploads/{pdf_file.name}",  # Correctly store file path
            security_pin=security_pin  # Save PIN
        )
        # Split PDF into parts after saving it
        split_pdf_in_parts(uploaded_pdf.file.path)

        messages.success(request, "PDF uploaded and split successfully!")
        return redirect("upload_pdf")  # Redirect to refresh page

    return render(request, "upload_pdf.html", context)


def download_pdf(request, pdf_id):
    """Handles secure PDF download after PIN verification."""
    if request.method == "POST":
        entered_pin = request.POST.get("pin")
        pdf = get_object_or_404(UploadedPDF, id=pdf_id)

        if verify_pdf_pin(pdf, entered_pin):  # Validate PIN
            file_path = pdf.file.path  # Get file path from the model

            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    response = HttpResponse(file.read(), content_type="application/pdf")
                    response["Content-Disposition"] = f'attachment; filename="{pdf.filename}"'
                    return response
            else:
                messages.error(request, "File not found.")
                return HttpResponseForbidden("File not found")
        else:
            messages.error(request, "Incorrect PIN. Please try again.")
            return HttpResponseForbidden("Incorrect PIN")

    return HttpResponseForbidden("Invalid request")


def merge_pdf_documents(request):
    """Merges split PDFs and returns a downloadable file."""
    merged_file_path = merge_pdfs()

    if not merged_file_path:
        messages.error(request, "No split files found for merging.")
        return HttpResponseBadRequest("No split files found for merging.")

    with open(merged_file_path, "rb") as merged_pdf:
        response = HttpResponse(merged_pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="merged_pdf.pdf"'
        return response

# video

import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponse
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Video
from .utils import split_video, merge_videos

# Initialize logger
logger = logging.getLogger(__name__)

def upload_video(request):
    videos = Video.objects.all()
    context = {
        'fname' : request.user.first_name,
        'videos': videos,
    }
    """Handles video upload, PIN authentication, and splitting into 10 parts."""
    if request.method == "POST":
        video_file = request.FILES.get("video_file")
        pin = request.POST.get("pin")

        if not video_file or not pin:
            messages.error(request, "Please provide both video and PIN.")
            return redirect("upload_video")

        logger.info(f"Received video: {video_file.name}, PIN: {pin}")

        # Save the uploaded video to the 'split_video' folder in media
        video_folder = os.path.join(settings.MEDIA_ROOT, "split_video")
        os.makedirs(video_folder, exist_ok=True)
        fs = FileSystemStorage(location=video_folder)
        filename = fs.save(video_file.name, video_file)
        file_path = fs.path(filename)

        # Save video info in the database
        video = Video.objects.create(
            file=f"split_video/{filename}",
            pin=pin
        )

        # Split video into 10 parts
        split_output_folder = os.path.join(settings.MEDIA_ROOT, f"split_video/{video.id}")
        split_files = split_video(file_path, split_output_folder)

        if not split_files:
            messages.error(request, "Failed to split the video.")
            return redirect("upload_video")

        # Update the video record with split file paths
        video.split_files = split_files
        video.save()

        messages.success(request, "Video uploaded and split successfully!")
        return redirect("upload_video")

    return render(request, "upload_video.html", context)


def list_videos(request):
    """Lists uploaded videos and allows authentication for merging and downloading."""
    videos = Video.objects.all()
    return render(request, "upload_video.html", {"videos": videos})


def download_video(request, video_id):
    """Merges video parts and allows download after PIN authentication."""
    if request.method == "POST":
        entered_pin = request.POST.get("pin")
        video = get_object_or_404(Video, id=video_id)

        if entered_pin != video.pin:
            messages.error(request, "Incorrect PIN!")
            return redirect("list_videos")

        # Merge video parts
        merged_video_folder = os.path.join(settings.MEDIA_ROOT, "merged_videos")
        os.makedirs(merged_video_folder, exist_ok=True)
        merged_video_path = os.path.join(merged_video_folder, f"{video_id}.mp4")

        merge_success = merge_videos(video.split_files, merged_video_path)

        if not merge_success:
            messages.error(request, "Error merging video parts.")
            return redirect("list_videos")

        # Serve the file as a response
        return FileResponse(open(merged_video_path, "rb"), as_attachment=True, filename="merged_video.mp4")

    return HttpResponse("Unauthorized", status=401)
