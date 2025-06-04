from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MSUserProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('deactivated', 'Deactivated'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ms_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    verification_requested_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"

    def mark_as_verified(self):
        self.status = 'verified'
        self.verified_at = timezone.now()
        self.save()

    def mark_as_deactivated(self):
        self.status = 'deactivated'
        self.deactivated_at = timezone.now()
        self.save()

class VerificationRequest(models.Model):
    user_profile = models.ForeignKey(MSUserProfile, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verifications')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Verification for {self.user_profile.user.email} - {self.requested_at}" 