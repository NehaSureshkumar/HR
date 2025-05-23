from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.decorators import login_required

router = DefaultRouter()
router.register(r'api/employees', views.EmployeeViewSet, basename='api-employees')
router.register(r'api/projects', views.ProjectViewSet, basename='api-projects')

schema_view = get_schema_view(
    openapi.Info(
        title="Employee Management API",
        default_version='v1',
        description="API documentation for Employee Management System",
    ),
    public=True,
)

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name="dashboard"),
    
    # Employee Profile
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('onboarding/', views.onboarding, name='onboarding'),
    
    # Notices
    path('notices/', views.notice, name="notice"),
    path('notices/create/', views.create_notice, name="create_notice"),
    path('notices/<str:id>/', views.noticedetail, name="noticedetail"),
    path('notices/<str:id>/delete/', views.delete_notice, name="delete_notice"),
    
    # Work Management
    path('work/', views.mywork, name="mywork"),
    path('work/assign/', views.assignWork, name="assignwork"),
    path('work/<str:wid>/', views.workdetails, name="workdetails"),
    path('work/<str:wid>/update/', views.updatework, name="updatework"),
    path('work/<str:wid>/delete/', views.deletework, name="deletework"),
    
    # Attendance
    path('attendance/', views.attendance_list, name="attendance_list"),
    path('attendance/mark/', views.mark_attendance, name="mark_attendance"),
    path('attendance/report/', views.report_download, name='report_download'),
    
    # Leave Management
    path('leave/', views.leave_request_list, name="leave_request_list"),
    path('leave/create/', views.create_leave_request, name="create_leave_request"),
    
    # HR Dashboard (protected by role_required decorator)
    path('hr/', views.admin_dashboard, name='admin_dashboard'),
    path('hr/employees/', views.admin_panel, name='admin_panel'),
    path('hr/leave/<int:request_id>/approve/', views.approve_leave_request, name='approve_leave_request'),
    
    # Document Verification URLs
    path('documents/verification/', views.document_verification, name='document_verification'),
    path('documents/verify/<int:doc_id>/', views.verify_document, name='verify_document'),
    path('documents/employee/<str:employee_id>/', views.employee_documents, name='employee_documents'),
    
    # Job Openings Management
    path('hr/jobs/', views.manage_job_openings, name='manage_job_openings'),
    
    # Employee Management
    path('hr/employees/create/', views.create_employee, name='create_employee'),
    path('hr/employees/export/', views.export_employees, name='export_employees'),
    path('hr/employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('hr/employees/<int:employee_id>/edit/', views.edit_employee, name='edit_employee'),
    path('hr/employees/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),
    path('hr/employees/list/', views.employee_list, name='employee_list'),
    
    # Payroll Management
    path('hr/payroll/generate/', views.generate_payroll, name='generate_payroll'),
    
    # Company Profile and Policies
    path('hr/company-profile/', views.company_profile, name='company_profile'),
    path('hr/policies/', views.policies, name='policies'),
    
    # Notifications
    path('hr/notifications/', views.notifications, name='notifications'),
    
    # Organizational Chart
    path('hr/org-chart/', views.organizational_chart, name='organizational_chart'),
    
    # Project Status Views (Unified)
    path('hr/projects/<str:status>/', views.project_list, name='project_list'),
    
    # Project Management Actions
    path('hr/projects/create/', views.create_project, name='create_project'),
    path('hr/projects/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('hr/projects/<int:project_id>/assign/', views.assign_employees_to_project, name='assign_employees_to_project'),
    path('hr/projects/<int:project_id>/complete/', views.mark_project_complete, name='mark_project_complete'),
    path('hr/projects/<int:project_id>/detail/', views.project_detail, name='project_detail'),
    path('hr/projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    
    # New URL pattern for my_documents
    path('my-documents/', views.my_documents, name='my_documents'),
    # New URL pattern for my_projects
    path('my-projects/', views.my_projects, name='my_projects'),
    
    # Training Program List
    path('training/', views.training_program_list, name='training_program_list'),
    path('', include(router.urls)),
    path('api/docs/', login_required(schema_view.with_ui('swagger', cache_timeout=0)), name='api-docs'),
    path('profile/forms/', views.employee_profile_forms, name='employee_profile_forms'),
    path('profile/review/<str:employee_id>/', views.review_employee_forms, name='review_employee_forms'),
    path('hr/validation/', views.employee_validation_list, name='employee_validation_list'),
]