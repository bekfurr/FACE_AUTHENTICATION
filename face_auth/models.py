from django.db import models
from django.contrib.auth.models import User
import numpy as np
import pickle
import base64

class FaceProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_encoding = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_encoding(self, encoding):
        """Convert numpy array to binary for storage"""
        if encoding is not None:
            self.face_encoding = pickle.dumps(encoding)
    
    def get_encoding(self):
        """Convert stored binary back to numpy array"""
        if self.face_encoding:
            return pickle.loads(self.face_encoding)
        return None
    
    def __str__(self):
        return f"Face profile for {self.user.username}"