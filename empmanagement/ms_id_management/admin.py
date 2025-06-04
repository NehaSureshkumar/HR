from django.contrib import admin
from .models import MSUserProfile, VerificationRequest

@admin.register(MSUserProfile)
class MSUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'ms_id', 'status', 'created_at', 'verified_at', 'deactivated_at')
    list_filter = ('status', 'created_at', 'verified_at', 'deactivated_at')
    search_fields = ('user__email', 'ms_id')
    readonly_fields = ('created_at', 'verified_at', 'deactivated_at')
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'requested_at', 'verified_at', 'verified_by')
    list_filter = ('requested_at', 'verified_at')
    search_fields = ('user_profile__user__email',)
    readonly_fields = ('requested_at', 'verified_at') 