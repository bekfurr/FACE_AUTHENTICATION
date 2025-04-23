from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
import json
import base64

from .models import FaceProfile
from .face_utils import detect_face_from_image, verify_face

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        face_image = request.POST.get('face_image')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')
        
        # Process face image
        if face_image:
            face_encoding = detect_face_from_image(face_image)
            if face_encoding is None:
                messages.error(request, 'No face detected in the image')
                return render(request, 'register.html')
        else:
            messages.error(request, 'Face image is required')
            return render(request, 'register.html')
        
        # Create user
        user = User.objects.create_user(username=username, password=password)
        
        # Create face profile
        face_profile = FaceProfile(user=user)
        face_profile.set_encoding(face_encoding)
        face_profile.save()
        
        messages.success(request, 'Registration successful! You can now login.')
        return redirect('login')
    
    return render(request, 'register.html')

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_method = request.POST.get('login_method', 'password')
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'login.html')
        
        if login_method == 'password':
            # Password authentication
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        
        elif login_method == 'face':
            # Face authentication
            face_image = request.POST.get('face_image')
            
            if not face_image:
                messages.error(request, 'Face image is required')
                return render(request, 'login.html')
            
            try:
                # Get user's face profile
                face_profile = FaceProfile.objects.get(user=user)
                known_encoding = face_profile.get_encoding()
                
                # Verify face
                if verify_face(known_encoding, face_image):
                    # Login user
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Face verification failed')
            except FaceProfile.DoesNotExist:
                messages.error(request, 'Face profile not found')
    
    return render(request, 'login.html')

def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    """Dashboard view (protected)"""
    return render(request, 'dashboard.html', {'user': request.user})

def capture_face_ajax(request):
    """AJAX endpoint for face capture"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image_data')
            
            if not image_data:
                return JsonResponse({'success': False, 'error': 'No image data provided'})
            
            # Check if face is detected
            face_encoding = detect_face_from_image(image_data)
            
            if face_encoding is None:
                return JsonResponse({'success': False, 'error': 'No face detected'})
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})