from django.contrib import admin
from employee.models import Employee, Attendance, Notice, workAssignments, Document, UserProfile, AuditLog, JobOpening, ProfileUpdateRequest

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('eID', 'firstName', 'lastName', 'designation', 'email', 'joinDate')
    search_fields = ('eID', 'firstName', 'lastName', 'email')
    list_filter = ('designation', 'joinDate')

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document_type', 'status', 'uploaded_at', 'verified_by')
    list_filter = ('document_type', 'status', 'uploaded_at')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName')
    raw_id_fields = ('employee', 'verified_by')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'profile_completion', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__email')

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('user', 'action', 'timestamp', 'details')

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Attendance)
admin.site.register(Notice)
admin.site.register(workAssignments)
admin.site.register(Document, DocumentAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(JobOpening)
admin.site.register(ProfileUpdateRequest)