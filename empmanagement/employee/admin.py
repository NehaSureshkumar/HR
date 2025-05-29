from django.contrib import admin
from employee.models import Employee, Attendance, Notice, workAssignments, Document, UserProfile, AuditLog, JobOpening, ProfileUpdateRequest, EmployeeInformation, IDCard, WiFiAccess, ParkingDetails, InsuranceDetails, TrainingProgram, TrainingBlog, TrainingDocument, TrainingTag

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

@admin.register(EmployeeInformation)
class EmployeeInformationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'status', 'employment_type', 'joining_date')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName')
    list_filter = ('status', 'employment_type')

@admin.register(IDCard)
class IDCardAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'mobile_number', 'blood_group')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName', 'mobile_number')
    list_filter = ('blood_group',)

@admin.register(WiFiAccess)
class WiFiAccessAdmin(admin.ModelAdmin):
    list_display = ('employee', 'mobile_number', 'access_card_number')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName', 'access_card_number')

@admin.register(ParkingDetails)
class ParkingDetailsAdmin(admin.ModelAdmin):
    list_display = ('employee', 'parking_status', 'vehicle_number_plate', 'vehicle_make')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName', 'vehicle_number_plate')
    list_filter = ('parking_status', 'vehicle_make')

@admin.register(InsuranceDetails)
class InsuranceDetailsAdmin(admin.ModelAdmin):
    list_display = ('employee', 'insured_name', 'relationship', 'sum_insured')
    search_fields = ('employee__eID', 'employee__firstName', 'employee__lastName', 'insured_name')
    list_filter = ('relationship', 'endorsement_type', 'critical_illness_maternity')

@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'capacity', 'enrolled_count', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'

@admin.register(TrainingBlog)
class TrainingBlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'author', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at', 'program')
    search_fields = ('title', 'content', 'program__title')
    filter_horizontal = ('tags',)

@admin.register(TrainingDocument)
class TrainingDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog', 'uploaded_at')
    search_fields = ('title', 'blog__title')
    list_filter = ('uploaded_at',)

@admin.register(TrainingTag)
class TrainingTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Attendance)
admin.site.register(Notice)
admin.site.register(workAssignments)
admin.site.register(Document, DocumentAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(JobOpening)
admin.site.register(ProfileUpdateRequest)