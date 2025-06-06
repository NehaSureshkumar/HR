from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MSUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ms_id = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {'Active' if self.is_active else 'Inactive'}"

    def deactivate(self):
        self.is_active = False
        self.save()

    def activate(self):
        self.is_active = True
        self.save() 