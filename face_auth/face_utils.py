# Create this file at: face_auth_project/face_auth/face_utils.py

import cv2
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def detect_face_from_image(image_data):
    """
    Detect face from image data and return face encoding
    
    Args:
        image_data: Base64 encoded image or file-like object
        
    Returns:
        face_encoding or None if no face detected
    """
    try:
        # Convert base64 to image if needed
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Extract the base64 part
            image_data = image_data.split(',')[1]
            image = Image.open(BytesIO(base64.b64decode(image_data)))
            image = np.array(image)
        else:
            # Assume it's a file-like object or numpy array
            image = np.array(Image.open(image_data))
            
        # Convert to RGB (face_recognition uses RGB)
        if len(image.shape) == 3 and image.shape[2] == 4:  # If RGBA
            image = image[:, :, :3]
            
        # Find face locations
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return None
            
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if not face_encodings:
            return None
            
        # Return the first face encoding
        return face_encodings[0]
        
    except Exception as e:
        print(f"Error detecting face: {e}")
        return None

def capture_face_from_webcam():
    """
    Capture face from webcam
    
    Returns:
        face_encoding or None if no face detected
    """
    try:
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Could not open webcam")
            return None
            
        print("Capturing face... Look at the camera")
        
        # Capture frame
        ret, frame = cap.read()
        
        # Release webcam
        cap.release()
        
        if not ret:
            print("Failed to capture image")
            return None
            
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            print("No face detected")
            return None
            
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        if not face_encodings:
            print("Could not encode face")
            return None
            
        # Return the first face encoding
        return face_encodings[0]
        
    except Exception as e:
        print(f"Error capturing face: {e}")
        return None

def verify_face(known_encoding, image_data, tolerance=0.6):
    """
    Verify if the face in the image matches the known encoding
    
    Args:
        known_encoding: Known face encoding
        image_data: Base64 encoded image or file-like object
        tolerance: Tolerance for face comparison (lower is stricter)
        
    Returns:
        True if face matches, False otherwise
    """
    try:
        # Get face encoding from image
        face_encoding = detect_face_from_image(image_data)
        
        if face_encoding is None:
            return False
            
        # Compare faces
        matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=tolerance)
        
        return matches[0]
        
    except Exception as e:
        print(f"Error verifying face: {e}")
        return False