from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from .models import (
    Employee, Attendance, Notice, workAssignments, Document, 
    UserProfile, AuditLog, JobOpening, ProfileUpdateRequest, 
    EmployeeInformation, IDCard, WiFiAccess, ParkingDetails, 
    InsuranceDetails, TrainingProgram, TrainingBlog, 
    TrainingDocument, TrainingTag, EmailSettings, Shift, 
    EmployeeShift, Leave, LeaveType
)

# Admin Classes
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('eID', 'firstName', 'lastName', 'designation', 'email', 'joinDate')
    search_fields = ('eID', 'firstName', 'lastName', 'email')
    list_filter = ('designation', 'joinDate')

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document_type', 'is_verified', 'uploaded_at')
    list_filter = ('document_type', 'is_verified')
    search_fields = ('employee__firstName', 'employee__lastName', 'document_type')
    raw_id_fields = ('employee',)
    readonly_fields = ('uploaded_at',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'profile_completion', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__email')

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('user', 'action', 'timestamp', 'details')

class EmployeeInformationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'status', 'employment_type', 'joining_date')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName')
    list_filter = ('status', 'employment_type')

class IDCardAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'mobile_number', 'blood_group')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName', 'mobile_number')
    list_filter = ('blood_group',)

class WiFiAccessAdmin(admin.ModelAdmin):
    list_display = ('employee', 'mobile_number', 'access_card_number')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName', 'access_card_number')

class ParkingDetailsAdmin(admin.ModelAdmin):
    list_display = ('employee', 'parking_status', 'vehicle_number_plate', 'vehicle_make')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName', 'vehicle_number_plate')
    list_filter = ('parking_status', 'vehicle_make')

class InsuranceDetailsAdmin(admin.ModelAdmin):
    list_display = ('employee', 'insured_name', 'relationship', 'sum_insured')
    search_fields = ('employee__eID', 'employee__lastName', 'insured_name')
    list_filter = ('relationship', 'endorsement_type', 'critical_illness_maternity')

class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'capacity', 'enrolled_count', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'

class TrainingBlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'author', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at', 'program')
    search_fields = ('title', 'content', 'program__title')
    filter_horizontal = ('tags',)

class TrainingDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog', 'uploaded_at')
    search_fields = ('title', 'blog__title')
    list_filter = ('uploaded_at',)

class TrainingTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ('EMAIL_HOST_USER', 'EMAIL_HOST', 'EMAIL_PORT', 'DEFAULT_FROM_EMAIL')

class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'grace_period', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

class EmployeeShiftAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'shift')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName')
    date_hierarchy = 'start_date'

class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'duration')
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName', 'reason')
    date_hierarchy = 'start_date'

class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_days', 'requires_approval', 'is_active')
    list_filter = ('requires_approval', 'is_active')
    search_fields = ('name', 'description')

class LateFilter(SimpleListFilter):
    title = 'Late Status'
    parameter_name = 'late_status'

    def lookups(self, request, model_admin):
        return (
            ('late', 'Late'),
            ('not_late', 'Not Late'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'late':
            return queryset.filter(is_late=True)
        if self.value() == 'not_late':
            return queryset.filter(is_late=False)
        return queryset

class AdjustedFilter(SimpleListFilter):
    title = 'Adjustment Status'
    parameter_name = 'adjusted'

    def lookups(self, request, model_admin):
        return (
            ('adjusted', 'Adjusted'),
            ('not_adjusted', 'Not Adjusted'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'adjusted':
            return queryset.filter(is_adjusted=True)
        if self.value() == 'not_adjusted':
            return queryset.filter(is_adjusted=False)
        return queryset

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('eId', 'date', 'time_in_display', 'time_out_display', 
                   'status', 'is_late', 'overtime_hours', 'location', 
                   'is_remote', 'is_adjusted', 'adjusted_by_display')
    list_filter = ('status', LateFilter, AdjustedFilter, 'location', 'is_remote', 'shift')
    search_fields = ('eId', 'notes', 'adjustment_reason')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at', 'is_adjusted', 'adjusted_by', 
                      'adjustment_date', 'adjustment_reason')
    fieldsets = (
        ('Basic Information', {
            'fields': ('eId', 'date', 'shift')
        }),
        ('Time Records', {
            'fields': ('time_in', 'time_out', 'status', 'is_late', 'overtime_hours')
        }),
        ('Location & Notes', {
            'fields': ('location', 'is_remote', 'notes')
        }),
        ('Adjustment Information', {
            'fields': ('is_adjusted', 'adjusted_by', 'adjustment_date', 'adjustment_reason'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def time_in_display(self, obj):
        if obj.time_in:
            return timezone.localtime(obj.time_in).strftime('%H:%M')
        return '-'
    time_in_display.short_description = 'Clock In'

    def time_out_display(self, obj):
        if obj.time_out:
            return timezone.localtime(obj.time_out).strftime('%H:%M')
        return '-'
    time_out_display.short_description = 'Clock Out'

    def adjusted_by_display(self, obj):
        if obj.adjusted_by:
            return obj.adjusted_by.username
        return '-'
    adjusted_by_display.short_description = 'Adjusted By'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='HR').exists():
            return qs
        return qs.filter(eId=request.user.username)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser or request.user.groups.filter(name='HR').exists():
            return True
        return obj.eId == request.user.username

    def save_model(self, request, obj, form, change):
        if change and any(field in form.changed_data for field in ['time_in', 'time_out', 'status', 'notes']):
            obj.adjust_attendance(
                user=request.user,
                time_in=form.cleaned_data.get('time_in'),
                time_out=form.cleaned_data.get('time_out'),
                status=form.cleaned_data.get('status'),
                notes=form.cleaned_data.get('notes')
            )
        else:
            super().save_model(request, obj, form, change)

# Register all models with their admin classes
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Notice)
admin.site.register(workAssignments)
admin.site.register(Document, DocumentAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(JobOpening)
admin.site.register(ProfileUpdateRequest)
admin.site.register(EmployeeInformation, EmployeeInformationAdmin)
admin.site.register(IDCard, IDCardAdmin)
admin.site.register(WiFiAccess, WiFiAccessAdmin)
admin.site.register(ParkingDetails, ParkingDetailsAdmin)
admin.site.register(InsuranceDetails, InsuranceDetailsAdmin)
admin.site.register(TrainingProgram, TrainingProgramAdmin)
admin.site.register(TrainingBlog, TrainingBlogAdmin)
admin.site.register(TrainingDocument, TrainingDocumentAdmin)
admin.site.register(TrainingTag, TrainingTagAdmin)
admin.site.register(EmailSettings, EmailSettingsAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(EmployeeShift, EmployeeShiftAdmin)
admin.site.register(Leave, LeaveAdmin)
admin.site.register(LeaveType, LeaveTypeAdmin)