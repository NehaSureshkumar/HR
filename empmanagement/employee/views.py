from django.shortcuts import redirect, render, get_object_or_404
from .forms import *
from employee.models import (
    Employee, Attendance, Notice, workAssignments, 
    Document, UserProfile, AuditLog, JobOpening,
    designations_opt, DOCUMENT_TYPES, PerformanceReview, Goal, LeaveRequest,
    TrainingProgram, TrainingEnrollment, Payroll, Project, EmployeeInformation, IDCard, WiFiAccess, ParkingDetails, InsuranceDetails, ProfileUpdateRequest
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from functools import wraps
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Sum, Count
from datetime import datetime, timedelta
import uuid
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
import csv
from django.http import HttpResponse
from django import forms
from rest_framework import viewsets, serializers

def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                profile = UserProfile.objects.get(user=request.user)
                if profile.role in roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "You don't have permission to access this page.")
                    return redirect('dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, "User profile not found.")
                return redirect('dashboard')
        return _wrapped_view
    return decorator

def staff_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_staff, login_url='/')(view_func)
    return decorated_view_func

# Create your views here.
@login_required(login_url='/ems/accounts/login/')
def dashboard(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Redirect admins/HR to their dashboard
        if user_profile.role in ['ADMIN', 'HR']:
            return redirect('admin_dashboard')
        
        # For regular employees, check profile completion
        employee, created = Employee.objects.get_or_create(
            eID=request.user.username,
            defaults={
                'firstName': request.user.first_name or 'New',
                'middleName': '',
                'lastName': request.user.last_name or 'Employee',
                'phoneNo': f'temp_{request.user.username}',
                'email': request.user.email or f'{request.user.username}@temp.com',
                'addharNo': f'temp_{request.user.username}',
                'dOB': timezone.now().date(),
                'designation': 'Intern',
                'salary': '0',
                'joinDate': timezone.now().date()
            }
        )
        
        # Only check onboarding for regular employees
        documents = Document.objects.filter(employee=employee)
        if user_profile.profile_completion < 100 or documents.count() < 3:
            return redirect('onboarding')
        
        # Get employee info
        info = Employee.objects.filter(eID=request.user.username)
        
        # Get attendance count for current month
        current_month = timezone.now().month
        attendance_count = Attendance.objects.filter(
            eId=employee.eID,
            date__month=current_month,
            status='PRESENT'
        ).count()
        
        # Get leave balance (assuming 20 days annual leave)
        leave_requests = LeaveRequest.objects.filter(
            eId=employee.eID,
            status='APPROVED',
            start_date__year=timezone.now().year
        )
        leave_taken = sum((lr.end_date - lr.start_date).days + 1 for lr in leave_requests)
        leave_balance = 20 - leave_taken
        
        # Get pending tasks count
        task_count = workAssignments.objects.filter(
            taskerId=employee,
            dueDate__gte=timezone.now()
        ).count()
        
        # Get enrolled training programs count
        training_count = TrainingEnrollment.objects.filter(
            employee=employee,
            status='ENROLLED'
        ).count()
        
        # Get recent tasks
        recent_tasks = workAssignments.objects.filter(
            taskerId=employee
        ).order_by('-assignDate')[:5]
        
        # Get recent notices
        recent_notices = Notice.objects.all().order_by('-publishDate')[:5]
        
        # Get assigned projects count
        assigned_projects_count = employee.projects.count()
        
        context = {
            'info': info,
            'attendance_count': attendance_count,
            'leave_balance': leave_balance,
            'task_count': task_count,
            'training_count': training_count,
            'recent_tasks': recent_tasks,
            'recent_notices': recent_notices,
            'assigned_projects_count': assigned_projects_count
        }
        
        return render(request, "employee/index.html", context)
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('login')
    
@login_required(login_url='/')
def notice(request):
    notices  = Notice.objects.all()
    return render(request,"employee/notice.html",{"notices":notices})

@login_required(login_url='/')
def noticedetail(request,id):
    noticedetail = Notice.objects.get(Id=id)
    return render(request,"employee/noticedetail.html",{"noticedetail":noticedetail})

@login_required(login_url='/')
def assignWork(request):
    context={}
    initialData = {
        "assignerId" : request.user.username,
    }
    flag = ""
    form = workform(request.POST or None, initial=initialData)
    if form.is_valid():
        currentTaskerId = request.POST["taskerId"]
        currentUserId = request.user.username
        if currentTaskerId == currentUserId:
            flag="Invalid ID Selected..."
        else:
            # Generate a unique ID for the work assignment
            work_instance = form.save(commit=False)
            work_instance.Id = f"WRK-{uuid.uuid4().hex[:8].upper()}"
            work_instance.save()
            flag = "Work Assigned Successfully!!"

    context['form']=form
    context['flag'] = flag
    return render(request,"employee/workassign.html",context)

@login_required(login_url='/')
def mywork(request):
    try:
        # Get work assignments for the current user
        work_assignments = workAssignments.objects.filter(taskerId__eID=request.user.username)
        # Get employee object
        employee = get_object_or_404(Employee, eID=request.user.username)
        # Get assigned projects
        assigned_projects = employee.projects.all()
        # Add current date for template comparison
        context = {
            'work': work_assignments,
            'now': timezone.now().date(),
            'employee': employee,
            'assigned_projects': assigned_projects
        }
        return render(request, "employee/mywork.html", context)
    except Exception as e:
        messages.error(request, f"Error loading work assignments: {str(e)}")
        return redirect('dashboard')

@login_required(login_url='/')
def workdetails(request,wid):
    workdetails = workAssignments.objects.get(Id=wid)
    return render(request,"employee/workdetails.html",{"workdetails":workdetails})

@login_required(login_url='/')
def assignedworklist(request):
    try:
        # Check if user is admin/HR
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Get work assignments
        works = workAssignments.objects.filter(assignerId=request.user.username).all()
        
        # Only check profile completion for regular employees
        if user_profile.role not in ['ADMIN', 'HR']:
            employee = Employee.objects.get(eID=request.user.username)
            documents = Document.objects.filter(employee=employee)
            if user_profile.profile_completion < 100 or documents.count() < 3:
                return redirect('onboarding')
        
        return render(request, "employee/assignedworklist.html", {
            "works": works,
            "now": timezone.now().date()
        })
    except Exception as e:
        messages.error(request, f"Error loading work assignments: {str(e)}")
        return redirect('dashboard')

@login_required(login_url='/')
def deletework(request, wid):
    obj = get_object_or_404(workAssignments, Id=wid)
    obj.delete()
    return redirect('assignedworklist')

@login_required(login_url='/')
def updatework(request,wid):
    work = workAssignments.objects.get(Id=wid)
    form = workform(request.POST or None, instance=work)
    flag = ""
    if form.is_valid():
        currentTaskerId = request.POST["taskerId"]
        currentUserId = request.user.username
        if currentTaskerId == currentUserId:
            flag="Invalid ID Selected..."
        else:
            flag = "Work Updated Successfully!!"
            form.save()
    return render(request,"employee/updatework.html", {'currentWork': work, "filledForm": form, "flag":flag})

@login_required(login_url='/')
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Try to get Employee by eID
    try:
        employee = Employee.objects.get(eID=request.user.username)
        created = False
    except Employee.DoesNotExist:
        # Try to get Employee by email (avoid duplicate email)
        employee = Employee.objects.filter(email=request.user.email).first()
        if not employee:
            # Create new Employee with unique email
            unique_email = request.user.email or f'{request.user.username}@temp.com'
            # If email exists, append a suffix
            if Employee.objects.filter(email=unique_email).exists():
                unique_email = f'{request.user.username}+{uuid.uuid4().hex[:4]}@temp.com'
            employee = Employee.objects.create(
                eID=request.user.username,
                firstName=request.user.first_name or 'Admin',
                middleName='',
                lastName=request.user.last_name or 'User',
                phoneNo=f'temp_{request.user.username}',
                email=unique_email,
                addharNo=f'temp_{request.user.username}',
                dOB=timezone.now().date(),
                designation='HR/Admin' if request.user.is_staff else 'Employee',
                salary='0',
                joinDate=timezone.now().date()
            )
        created = True
    documents = Document.objects.filter(employee=employee)
    
    # Initialize forms for the new sections
    employee_info_form = EmployeeInformationForm(instance=getattr(employee, 'employeeinformation', None))
    id_card_form = IDCardForm(instance=getattr(employee, 'idcard', None))
    wifi_access_form = WiFiAccessForm(instance=getattr(employee, 'wifiaccess', None))
    parking_form = ParkingDetailsForm(instance=getattr(employee, 'parkingdetails', None))
    insurance_form = InsuranceDetailsForm(instance=getattr(employee, 'insurancedetails', None))
    
    if request.method == "POST":
        # Update profile information
        employee.phoneNo = request.POST.get('phone')
        employee.email = request.POST.get('email')
        employee.save()
        user_profile.emergency_contact_name = request.POST.get('emergency_contact_name')
        user_profile.emergency_contact_phone = request.POST.get('emergency_contact_phone')
        user_profile.bank_account_number = request.POST.get('bank_account')
        user_profile.bank_ifsc = request.POST.get('ifsc')
        user_profile.save()
        # Calculate profile completion
        fields = [
            employee.phoneNo,
            employee.email,
            user_profile.emergency_contact_name,
            user_profile.emergency_contact_phone,
            user_profile.bank_account_number,
            user_profile.bank_ifsc
        ]
        completed = sum(1 for field in fields if field)
        user_profile.profile_completion = (completed / len(fields)) * 100
        user_profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
        
    context = {
        'profile': user_profile,
        'employee': employee,
        'documents': documents,
        'employee_info_form': employee_info_form,
        'id_card_form': id_card_form,
        'wifi_access_form': wifi_access_form,
        'parking_form': parking_form,
        'insurance_form': insurance_form,
    }
    return render(request, "employee/profile.html", context)

@login_required
@role_required(['EMPLOYEE'])
def my_documents(request):
    employee = get_object_or_404(Employee, eID=request.user.username)
    documents = employee.document_set.all().order_by('-uploaded_at')

    # Helper to get status for each info section
    def get_info_status(attr, form_type):
        req = ProfileUpdateRequest.objects.filter(
            employee=employee,
            proposed_changes__has_key=form_type  # If using PostgreSQL JSONField
        ).order_by('-reviewed_at').first()
        if req:
            return req.status
        if hasattr(employee, attr):
            return 'Submitted'
        return 'Not Submitted'

    info_statuses = {
        'Employee Information': get_info_status('employeeinformation', 'employee_info'),
        'ID Card': get_info_status('idcard', 'id_card'),
        'WiFi Access': get_info_status('wifiaccess', 'wifi_access'),
        'Parking Details': get_info_status('parkingdetails', 'parking'),
        'Insurance Details': get_info_status('insurancedetails', 'insurance'),
    }

    return render(request, 'employee/my_documents.html', {
        'documents': documents,
        'info_statuses': info_statuses,
    })

@login_required(login_url='/')
def upload_document(request):
    if request.method == "POST":
        employee = get_object_or_404(Employee, eID=request.user.username)
        doc_type = request.POST.get('document_type')
        file = request.FILES.get('document')
        
        if not file:
            messages.error(request, "Please select a file to upload.")
            return redirect('upload_document')
            
        document = Document.objects.create(
            employee=employee,
            document_type=doc_type,
            file=file
        )
        
        AuditLog.objects.create(
            user=request.user,
            action=f"Document Upload - {doc_type}",
            details=f"Document uploaded for {employee.eID}"
        )
        
        messages.success(request, "Document uploaded successfully!")
        return redirect('my_documents')
        
    return render(request, "employee/upload_document.html", {
        'document_types': DOCUMENT_TYPES
    })

@login_required(login_url='/')
@role_required(['ADMIN', 'HR'])
def document_verification(request):
    status_filter = request.GET.get('status', 'all')
    
    # Get all employees
    employees = Employee.objects.all().order_by('-joinDate')
    
    # Add validation status to each employee
    for employee in employees:
        # Document status
        documents = Document.objects.filter(employee=employee)
        doc_count = documents.count()
        
        # Form status
        pending_updates = ProfileUpdateRequest.objects.filter(
            employee=employee,
            status='PENDING'
        ).exists()
        
        has_employee_info = hasattr(employee, 'employeeinformation')
        has_id_card = hasattr(employee, 'idcard')
        has_wifi_access = hasattr(employee, 'wifiaccess')
        has_parking = hasattr(employee, 'parkingdetails')
        has_insurance = hasattr(employee, 'insurancedetails')
        
        # Determine form validation status
        if pending_updates:
            employee.validation_status = 'PENDING'
        elif all([has_employee_info, has_id_card, has_wifi_access, has_parking, has_insurance]):
            employee.validation_status = 'APPROVED'
        else:
            employee.validation_status = 'INCOMPLETE'
        
        # Determine overall status
        if doc_count == 0 or employee.validation_status == 'INCOMPLETE':
            employee.overall_status = 'INCOMPLETE'
        elif pending_updates or documents.filter(status='PENDING').exists():
            employee.overall_status = 'PENDING'
        elif doc_count >= 3 and employee.validation_status == 'APPROVED' and not documents.filter(status='REJECTED').exists():
            employee.overall_status = 'APPROVED'
        else:
            employee.overall_status = 'PENDING'
    
    # Filter employees based on status
    if status_filter != 'all':
        employees = [emp for emp in employees if emp.overall_status == status_filter]
    
    # Pagination
    paginator = Paginator(employees, 10)
    page = request.GET.get('page')
    employees = paginator.get_page(page)
    
    context = {
        'employees': employees,
        'status_filter': status_filter,
        'is_hr_admin': True,
    }
    return render(request, "employee/document_verification.html", context)

@login_required(login_url='/')
@role_required(['ADMIN', 'HR'])
def verify_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    if request.method == "POST":
        status = request.POST.get('status')
        comments = request.POST.get('comments', '')
        document.status = status
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.comments = comments
        document.save()
        AuditLog.objects.create(
            user=request.user,
            action=f"Document Verification - {status}",
            details=f"Document {doc_id} verified for {document.employee.eID}"
        )
        messages.success(request, "Document verification updated successfully!")
        return redirect('document_verification')
    return render(request, "employee/verify_document.html", {
        'document': document
    })

@login_required
@role_required(['ADMIN', 'HR'])
def admin_dashboard(request):
    # Fetch all employees
    employees = Employee.objects.all()
    user_profile = UserProfile.objects.get(user=request.user)
    # Fetch ongoing and upcoming projects
    ongoing_projects = Project.objects.filter(status='ONGOING').order_by('-start_date')
    upcoming_projects = Project.objects.filter(status='UPCOMING').order_by('-start_date')
    # Prepare data for each tab
    bank_details = []
    insurance_policies = []
    tax_details = []
    personal_details = []
    for emp in employees:
        # Bank details from UserProfile
        try:
            profile = UserProfile.objects.get(user__username=emp.eID)
            bank_details.append({
                'employee': emp,
                'account_number': profile.bank_account_number,
                'ifsc': profile.bank_ifsc,
            })
            personal_details.append({
                'employee': emp,
                'emergency_contact_name': profile.emergency_contact_name,
                'emergency_contact_phone': profile.emergency_contact_phone,
            })
        except UserProfile.DoesNotExist:
            bank_details.append({'employee': emp, 'account_number': '', 'ifsc': ''})
            personal_details.append({'employee': emp, 'emergency_contact_name': '', 'emergency_contact_phone': ''})
        # Insurance and tax (stub, expand if models exist)
        insurance_policies.append({'employee': emp, 'policy': 'N/A'})
        tax_details.append({'employee': emp, 'tax': 'N/A'})
    context = {
        'employees': employees,
        'user_profile': user_profile,
        'bank_details': bank_details,
        'insurance_policies': insurance_policies,
        'tax_details': tax_details,
        'personal_details': personal_details,
        'active_hirings': 0,  # Add real logic if needed
        'total_employees': employees.count(),
        'ongoing_projects': ongoing_projects,
        'upcoming_projects': upcoming_projects,
    }
    return render(request, 'employee/admin_dashboard.html', context)

@login_required
@role_required(['HR', 'Admin'])
def export_employees(request):
    """Export employee data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Department', 'Position', 'Join Date', 'Status'])
    
    employees = Employee.objects.all()
    for employee in employees:
        writer.writerow([
            employee.id,
            employee.user.get_full_name(),
            employee.user.email,
            employee.department,
            employee.position,
            employee.join_date,
            'Active' if employee.user.is_active else 'Inactive'
        ])
    
    return response

@login_required
@role_required(['HR', 'Admin'])
def generate_payroll(request):
    """Generate payroll for all employees"""
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        
        # Generate payroll for each employee
        employees = Employee.objects.all()
        for employee in employees:
            # Calculate basic salary
            basic_salary = employee.salary
            
            # Calculate allowances
            allowances = 0
            if hasattr(employee, 'allowances'):
                allowances = sum(allowance.amount for allowance in employee.allowances.all())
            
            # Calculate deductions
            deductions = 0
            if hasattr(employee, 'deductions'):
                deductions = sum(deduction.amount for deduction in employee.deductions.all())
            
            # Calculate net salary
            net_salary = basic_salary + allowances - deductions
            
            # Create payroll record
            Payroll.objects.create(
                employee=employee,
                month=month,
                year=year,
                basic_salary=basic_salary,
                allowances=allowances,
                deductions=deductions,
                net_salary=net_salary,
                status='Pending'
            )
        
        messages.success(request, 'Payroll generated successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'employee/generate_payroll.html', {
        'page_title': 'Generate Payroll',
        'active_page': 'payroll'
    })

@login_required
@role_required(['ADMIN', 'HR'])
def manage_job_openings(request):
    """View for managing job openings."""
    job_openings = JobOpening.objects.all().order_by('-created_at')
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'add':
            title = request.POST.get('title')
            department = request.POST.get('department')
            description = request.POST.get('description')
            requirements = request.POST.get('requirements')
            positions = request.POST.get('positions', 1)
            
            JobOpening.objects.create(
                title=title,
                department=department,
                description=description,
                requirements=requirements,
                positions=positions,
                created_by=request.user
            )
            messages.success(request, "Job opening created successfully!")
            
        elif action == 'update':
            job_id = request.POST.get('job_id')
            job = get_object_or_404(JobOpening, id=job_id)
            job.status = request.POST.get('status')
            job.save()
            messages.success(request, "Job opening updated successfully!")
            
        elif action == 'delete':
            job_id = request.POST.get('job_id')
            job = get_object_or_404(JobOpening, id=job_id)
            job.delete()
            messages.success(request, "Job opening deleted successfully!")
            
    context = {
        'page_title': 'Manage Job Openings',
        'active_page': 'jobs',
        'job_openings': job_openings,
        'departments': designations_opt
    }
    return render(request, 'employee/manage_jobs.html', context)

@login_required(login_url='/ems/accounts/login/')
def onboarding(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        employee = Employee.objects.get(eID=request.user.username)
        
        from django import forms
        class SimpleOnboardingForm(forms.ModelForm):
            class Meta:
                model = employee.__class__
                fields = ['firstName', 'lastName', 'phoneNo', 'email']
                widgets = {
                    'firstName': forms.TextInput(attrs={'class': 'form-control'}),
                    'lastName': forms.TextInput(attrs={'class': 'form-control'}),
                    'phoneNo': forms.TextInput(attrs={'class': 'form-control'}),
                    'email': forms.EmailInput(attrs={'class': 'form-control'}),
                }
        if request.method == 'POST':
            form = SimpleOnboardingForm(request.POST, instance=employee)
            if form.is_valid():
                form.save()
                user_profile.profile_completion = 100
                user_profile.save()
                messages.success(request, "Onboarding complete! Welcome.")
                return redirect('dashboard')
        else:
            form = SimpleOnboardingForm(instance=employee)
        context = {
            'form': form,
            'profile_completion': user_profile.profile_completion
        }
        return render(request, "employee/onboarding.html", context)
    except (UserProfile.DoesNotExist, Employee.DoesNotExist):
        messages.error(request, "User profile or employee record not found.")
        return redirect('login')

@login_required(login_url='/')
def update_profile(request):
    if request.method == "POST":
        user_profile = get_object_or_404(UserProfile, user=request.user)
        employee = get_object_or_404(Employee, eID=request.user.username)
        
        # Update employee info
        if 'phone' in request.POST:
            employee.phoneNo = request.POST.get('phone')
        if 'email' in request.POST:
            employee.email = request.POST.get('email')
            
        # Update profile info
        if 'emergency_contact_name' in request.POST:
            user_profile.emergency_contact_name = request.POST.get('emergency_contact_name')
        if 'emergency_contact_phone' in request.POST:
            user_profile.emergency_contact_phone = request.POST.get('emergency_contact_phone')
        if 'bank_account' in request.POST:
            user_profile.bank_account_number = request.POST.get('bank_account')
        if 'ifsc' in request.POST:
            user_profile.bank_ifsc = request.POST.get('ifsc')
        
        employee.save()
        
        # Calculate profile completion
        fields = [
            employee.phoneNo, employee.email,
            user_profile.emergency_contact_name,
            user_profile.emergency_contact_phone,
            user_profile.bank_account_number,
            user_profile.bank_ifsc
        ]
        completed = sum(1 for field in fields if field)
        user_profile.profile_completion = (completed / len(fields)) * 100
        user_profile.save()
        
        messages.success(request, "Profile updated successfully!")
        
    return redirect('onboarding')

@login_required
def performance_review_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role in ['ADMIN', 'HR']:
            reviews = PerformanceReview.objects.all()
        else:
            employee = Employee.objects.get(eID=request.user.username)
            reviews = PerformanceReview.objects.filter(employee=employee)
        return render(request, 'employee/performance_review_list.html', {'reviews': reviews})
    except (UserProfile.DoesNotExist, Employee.DoesNotExist):
        reviews = []
        return render(request, 'employee/performance_review_list.html', {'reviews': reviews})

@login_required
def create_performance_review(request):
    if not request.user.is_staff:
        messages.error(request, "Only staff members can create performance reviews.")
        return redirect('performance_review_list')
        
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        goals_achieved = request.POST.get('goals_achieved')
        areas_of_improvement = request.POST.get('areas_of_improvement')
        next_review_date = request.POST.get('next_review_date')

        try:
            employee = Employee.objects.get(eID=employee_id)
            review = PerformanceReview.objects.create(
                employee=employee,
                reviewer=request.user,
                review_date=timezone.now().date(),
                rating=rating,
                comments=comments,
                goals_achieved=goals_achieved,
                areas_of_improvement=areas_of_improvement,
                next_review_date=next_review_date
            )
            messages.success(request, 'Performance review created successfully.')
            return redirect('performance_review_list')
        except Employee.DoesNotExist:
            messages.error(request, 'Selected employee does not exist.')
            
    employees = Employee.objects.all()
    return render(request, 'employee/create_performance_review.html', {'employees': employees})

@login_required
def goal_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role in ['ADMIN', 'HR']:
            goals = Goal.objects.all()
        else:
            employee = Employee.objects.get(eID=request.user.username)
            goals = Goal.objects.filter(employee=employee)
        return render(request, 'employee/goal_list.html', {'goals': goals})
    except (UserProfile.DoesNotExist, Employee.DoesNotExist):
        goals = []
        return render(request, 'employee/goal_list.html', {'goals': goals})

@login_required
def create_goal(request):
    try:
        employee = Employee.objects.get(eID=request.user.username)
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            target_date = request.POST.get('target_date')

            goal = Goal.objects.create(
                employee=employee,
                title=title,
                description=description,
                start_date=start_date,
                target_date=target_date,
                status='NOT_STARTED'
            )
            messages.success(request, 'Goal created successfully.')
            return redirect('goal_list')
        return render(request, 'employee/create_goal.html')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('dashboard')

def get_employee_name(eid):
    try:
        emp = Employee.objects.get(eID=eid)
        return f"{emp.firstName} {emp.lastName}"
    except Employee.DoesNotExist:
        return eid

@login_required
def leave_request_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if request.user.is_staff:
            requests = LeaveRequest.objects.all()
        else:
            requests = LeaveRequest.objects.filter(eId=request.user.username)
        # Attach employee name for template
        for req in requests:
            req.employee_name = get_employee_name(req.eId)
        return render(request, 'employee/leave_request_list.html', {'requests': requests})
    except UserProfile.DoesNotExist:
        requests = []
        return render(request, 'employee/leave_request_list.html', {'requests': requests})

@login_required
def create_leave_request(request):
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        # Validation: start_date <= end_date
        if start_date > end_date:
            messages.error(request, 'End date cannot be before start date.')
            return redirect('create_leave_request')
        # Validation: no overlapping leave
        overlap = LeaveRequest.objects.filter(
            eId=request.user.username,
            status__in=['PENDING', 'APPROVED'],
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()
        if overlap:
            messages.error(request, 'You already have a leave request for these dates.')
            return redirect('create_leave_request')
        request_obj = LeaveRequest.objects.create(
            eId=request.user.username,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='PENDING'
        )
        AuditLog.objects.create(user=request.user, action='Leave Request', details=f'Requested {leave_type} leave from {start_date} to {end_date}')
        messages.success(request, 'Leave request submitted successfully.')
        return redirect('leave_request_list')
    return render(request, 'employee/create_leave_request.html')

@login_required
def approve_leave_request(request, request_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not request.user.is_staff:
            messages.error(request, 'Only staff members can approve/reject leave requests.')
            return redirect('leave_request_list')
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        action = request.GET.get('action', 'approve')
        if action == 'reject':
            leave_request.status = 'REJECTED'
            messages.success(request, 'Leave request rejected.')
            AuditLog.objects.create(user=request.user, action='Leave Rejected', details=f'Rejected leave for {leave_request.eId} ({leave_request.start_date} to {leave_request.end_date})')
        else:
            leave_request.status = 'APPROVED'
            messages.success(request, 'Leave request approved.')
            AuditLog.objects.create(user=request.user, action='Leave Approved', details=f'Approved leave for {leave_request.eId} ({leave_request.start_date} to {leave_request.end_date})')
        leave_request.approved_by = request.user
        leave_request.save()
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
    return redirect('leave_request_list')

@login_required
def attendance_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role in ['ADMIN', 'HR']:
            attendance_records = Attendance.objects.all()
        else:
            attendance_records = Attendance.objects.filter(eId=request.user.username)
        return render(request, 'employee/attendance_list.html', {'attendance_records': attendance_records})
    except UserProfile.DoesNotExist:
        attendance_records = []
        return render(request, 'employee/attendance_list.html', {'attendance_records': attendance_records})

@login_required
def mark_attendance(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        time_in = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        overtime_hours = request.POST.get('overtime_hours', 0)

        attendance = Attendance.objects.create(
            eId=request.user.username,
            date=timezone.now().date(),
            time_in=time_in,
            time_out=time_out,
            status=status,
            overtime_hours=overtime_hours
        )
        messages.success(request, 'Attendance marked successfully.')
        return redirect('attendance_list')
    return render(request, 'employee/mark_attendance.html')

@login_required
def training_program_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role in ['ADMIN', 'HR']:
            programs = TrainingProgram.objects.all()
        else:
            programs = TrainingProgram.objects.filter(status='UPCOMING')
        return render(request, 'employee/training_program_list.html', {'programs': programs})
    except UserProfile.DoesNotExist:
        programs = []
        return render(request, 'employee/training_program_list.html', {'programs': programs})

@login_required
def enroll_training(request, program_id):
    try:
        employee = Employee.objects.get(eID=request.user.username)
        program = get_object_or_404(TrainingProgram, id=program_id)
        
        if program.enrolled_count < program.capacity:
            enrollment = TrainingEnrollment.objects.create(
                employee=employee,
                program=program,
                status='ENROLLED'
            )
            program.enrolled_count += 1
            program.save()
            messages.success(request, 'Successfully enrolled in training program.')
        else:
            messages.error(request, 'Training program is full.')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
    return redirect('training_program_list')

@login_required
def payroll_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.role in ['ADMIN', 'HR']:
            payroll_records = Payroll.objects.all()
        else:
            employee = Employee.objects.get(eID=request.user.username)
            payroll_records = Payroll.objects.filter(employee=employee)
        return render(request, 'employee/payroll_list.html', {'payroll_records': payroll_records})
    except (UserProfile.DoesNotExist, Employee.DoesNotExist):
        payroll_records = []
        return render(request, 'employee/payroll_list.html', {'payroll_records': payroll_records})

@login_required
@staff_required
def create_employee(request):
    if request.method == 'POST':
        eid = request.POST.get('eid')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        addhar = request.POST.get('addhar')
        dob = request.POST.get('dob')
        designation = request.POST.get('designation')
        salary = request.POST.get('salary')
        join_date = request.POST.get('join_date')
        password = request.POST.get('password')
        # Create User
        if User.objects.filter(username=eid).exists():
            messages.error(request, 'A user with this Employee ID already exists.')
            return redirect('create_employee')
        user = User.objects.create_user(username=eid, email=email, password=password, first_name=first_name, last_name=last_name)
        # Create Employee
        Employee.objects.create(
            eID=eid,
            firstName=first_name,
            middleName=middle_name,
            lastName=last_name,
            phoneNo=phone,
            email=email,
            addharNo=addhar,
            dOB=dob,
            designation=designation,
            salary=salary,
            joinDate=join_date
        )
        # Create UserProfile
        UserProfile.objects.create(user=user, role='EMPLOYEE', profile_completion=0)
        messages.success(request, 'Employee and account created successfully!')
        return redirect('admin_dashboard')
    return render(request, 'employee/create_employee.html', {'designations': designations_opt})

# Attendance Regulation (admin only)
@login_required
@staff_required
def regulate_attendance(request, record_id):
    record = get_object_or_404(Attendance, id=record_id)
    if request.method == 'POST':
        record.status = request.POST.get('status', record.status)
        record.time_in = request.POST.get('time_in', record.time_in)
        record.time_out = request.POST.get('time_out', record.time_out)
        record.overtime_hours = request.POST.get('overtime_hours', record.overtime_hours)
        record.save()
        messages.success(request, 'Attendance record updated.')
        return redirect('attendance_list')
    return render(request, 'employee/regulate_attendance.html', {'record': record})

# Payroll Processing (admin only)
@login_required
@staff_required
def process_payroll(request, record_id):
    record = get_object_or_404(Payroll, id=record_id)
    if request.method == 'POST':
        record.status = 'PROCESSED'
        record.payment_date = timezone.now().date()
        record.save()
        messages.success(request, 'Payroll marked as processed.')
        return redirect('payroll_list')
    return JsonResponse({'success': True})

# Audit Log UI (admin only)
@login_required
@staff_required
def audit_log(request):
    logs = AuditLog.objects.all().order_by('-timestamp')[:100]
    return render(request, 'employee/audit_log.html', {'logs': logs})

# Notification stub (to be implemented)
@login_required
@staff_required
def send_notification(request):
    # Placeholder for notification logic
    return JsonResponse({'success': True})

# Analytics stub (to be implemented)
@login_required
@staff_required
def analytics_dashboard(request):
    # Placeholder for analytics logic
    return render(request, 'employee/analytics_dashboard.html')

# --- Generic Workflow of Actions (Stub) ---
@login_required
@role_required(['ADMIN', 'HR'])
def workflow_actions(request):
    """Stub for a generic workflow engine (e.g., onboarding, approvals, document flows)."""
    # TODO: Implement workflow engine for multi-step actions
    return render(request, 'employee/workflow_actions.html')

# --- Enhanced Search Functionality (Stub) ---
@login_required
@role_required(['ADMIN', 'HR'])
def search(request):
    """Search employees, documents, jobs, etc."""
    # TODO: Implement search logic and UI
    query = request.GET.get('q', '')
    results = []
    return render(request, 'employee/search.html', {'query': query, 'results': results})

# --- Reporting System (Stub) ---
@login_required
@role_required(['ADMIN', 'HR'])
def reporting_dashboard(request):
    """Reporting dashboard for leave, attendance, payroll, documents, etc."""
    # TODO: Implement reporting logic and charts
    return render(request, 'employee/reporting_dashboard.html')

# --- Admin CRUD Views (Stubs) ---
@login_required
@role_required(['ADMIN', 'HR'])
def employee_crud(request):
    """Admin CRUD for Employee model."""
    # TODO: Implement CRUD logic (list, create, update, delete)
    return render(request, 'employee/employee_crud.html')

@login_required
@role_required(['ADMIN', 'HR'])
def document_crud(request):
    """Admin CRUD for Document model."""
    # TODO: Implement CRUD logic (list, create, update, delete)
    return render(request, 'employee/document_crud.html')

@login_required
@role_required(['ADMIN', 'HR'])
def job_crud(request):
    """Admin CRUD for JobOpening model."""
    # TODO: Implement CRUD logic (list, create, update, delete)
    return render(request, 'employee/job_crud.html')

@login_required
@role_required(['ADMIN', 'HR'])
def userprofile_crud(request):
    """Admin CRUD for UserProfile model."""
    # TODO: Implement CRUD logic (list, create, update, delete)
    return render(request, 'employee/userprofile_crud.html')

# --- Dynamic View Generation System (Stub) ---
@login_required
@role_required(['ADMIN', 'HR', 'EMPLOYEE'])
def dynamic_view(request, view_name):
    """Dynamically render views based on role and view_name."""
    # TODO: Implement dynamic view logic
    return render(request, f'employee/dynamic/{view_name}.html')

# Add this new view for the admin panel
@login_required
@role_required(['ADMIN', 'HR'])
def admin_panel(request):
    """Protected Django admin panel access."""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access the admin panel.")
        return redirect('dashboard')
    return admin.site.index(request)

@login_required
def create_notice(request):
    from employee.models import NOTICE_TAGS
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        tag = request.POST.get('tag', 'GENERAL')
        notice = Notice.objects.create(
            Id=f'NTC-{uuid.uuid4().hex[:8].upper()}',
            title=title,
            description=description,
            publishDate=timezone.now(),
            tag=tag,
            created_by=request.user
        )
        messages.success(request, 'Notice posted successfully!')
        return redirect('notice')
    return render(request, 'employee/create_notice.html', {'tags': NOTICE_TAGS})

@login_required
def delete_notice(request, id):
    notice = get_object_or_404(Notice, Id=id)
    user_profile = UserProfile.objects.get(user=request.user)
    # Only creator or HR/Admin can delete
    if notice.created_by == request.user or user_profile.role in ['ADMIN', 'HR']:
        notice.delete()
        messages.success(request, 'Notice deleted successfully!')
    else:
        messages.error(request, 'You do not have permission to delete this notice.')
    return redirect('notice')

@login_required
@role_required(['HR', 'Admin'])
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    return render(request, 'employee/employee_detail.html', {'employee': employee})

@login_required
@role_required(['HR', 'Admin'])
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.firstName = request.POST.get('firstName', employee.firstName)
        employee.lastName = request.POST.get('lastName', employee.lastName)
        employee.email = request.POST.get('email', employee.email)
        employee.phoneNo = request.POST.get('phoneNo', employee.phoneNo)
        employee.department = request.POST.get('department', employee.department)
        employee.designation = request.POST.get('designation', employee.designation)
        employee.salary = request.POST.get('salary', employee.salary)
        employee.save()
        messages.success(request, 'Employee updated successfully!')
        return redirect('admin_dashboard')
    return render(request, 'employee/edit_employee.html', {'employee': employee})

@login_required
@role_required(['HR', 'Admin'])
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'employee/delete_employee.html', {'employee': employee})

@login_required
@role_required(['ADMIN', 'HR'])
def employee_list(request):
    # Get all employees
    employees = list(Employee.objects.all().order_by('-joinDate'))
    for emp in employees:
        emp.is_hr_admin = False
        emp.is_dummy = False
    # Get all HR/Admin users from UserProfile
    from django.contrib.auth.models import User
    hr_admin_profiles = UserProfile.objects.filter(role__in=['HR', 'ADMIN'])
    for profile in hr_admin_profiles:
        try:
            emp = Employee.objects.get(eID=profile.user.username)
            emp.is_hr_admin = True
            emp.is_dummy = False
        except Employee.DoesNotExist:
            user = profile.user
            dummy = type('DummyEmp', (), {})()
            dummy.id = user.id
            dummy.firstName = user.first_name or user.username
            dummy.lastName = user.last_name or ''
            dummy.email = user.email
            dummy.department = getattr(profile, 'department', '-')
            dummy.designation = profile.role
            dummy.joinDate = user.date_joined
            dummy.user = user
            dummy.is_hr_admin = True
            dummy.is_dummy = True
            employees.append(dummy)
    all_employees = employees
    return render(request, 'employee/employee_list.html', {'employees': all_employees})

@login_required
@role_required(['ADMIN', 'HR'])
def report_download(request):
    return render(request, 'employee/report_download.html')

@login_required
@role_required(['ADMIN', 'HR'])
def company_profile(request):
    return render(request, 'employee/company_profile.html')

@login_required
@role_required(['ADMIN', 'HR'])
def policies(request):
    return render(request, 'employee/policies.html')

@login_required
@role_required(['ADMIN', 'HR'])
def notifications(request):
    # Get all notifications for the user
    notifications = Notice.objects.all().order_by('-publishDate')
    return render(request, 'employee/notifications.html', {
        'notifications': notifications
    })

@login_required
@role_required(['ADMIN', 'HR'])
def organizational_chart(request):
    # Get all employees grouped by department
    departments = Employee.objects.values('department').distinct()
    org_data = {}
    for dept in departments:
        if dept['department']:
            org_data[dept['department']] = Employee.objects.filter(
                department=dept['department']
            ).order_by('designation')
    
    return render(request, 'employee/organizational_chart.html', {
        'org_data': org_data
    })

@login_required
@role_required(['ADMIN', 'HR'])
def project_list(request, status):
    status_map = {
        'ongoing': ('ONGOING', 'Ongoing Projects'),
        'at-risk': ('AT_RISK', 'At Risk Projects'),
        'upcoming': ('UPCOMING', 'Upcoming Projects'),
        'on-schedule': ('ON_SCHEDULE', 'On Schedule Projects'),
    }
    if status not in status_map:
        messages.error(request, 'Invalid project status.')
        return redirect('admin_dashboard')
    status_code, title = status_map[status]
    # Fix: Get employees by matching eID to UserProfile's user.username where role is EMPLOYEE
    employee_eids = UserProfile.objects.filter(role='EMPLOYEE').values_list('user__username', flat=True)
    employees = Employee.objects.filter(eID__in=employee_eids)
    if request.method == 'POST':
        name = request.POST.get('name')
        project_status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        employee_ids = request.POST.getlist('employees')
        project = Project.objects.create(
            name=name,
            status=project_status,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        if employee_ids:
            project.employees.set(employee_ids)
        project.save()
        messages.success(request, 'Project created successfully!')
        return redirect('project_list', project_status.lower().replace('_', '-'))
    projects = Project.objects.filter(status=status_code).order_by('-start_date')
    return render(request, 'employee/project_list.html', {'projects': projects, 'title': title, 'employees': employees})

# --- Project Management Forms ---
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'status', 'start_date', 'end_date', 'description', 'employees']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'employees': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow employees (not admins/HR) to be assigned
        employee_eids = UserProfile.objects.filter(role='EMPLOYEE').values_list('user__username', flat=True)
        self.fields['employees'].queryset = Employee.objects.filter(eID__in=employee_eids)

# --- Project Management Views ---
@login_required
@role_required(['ADMIN', 'HR'])
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list', project.status.lower().replace('_', '-'))
    else:
        form = ProjectForm()
    return render(request, 'employee/project_form.html', {'form': form, 'action': 'Create'})

@login_required
@role_required(['ADMIN', 'HR'])
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list', project.status.lower().replace('_', '-'))
    else:
        form = ProjectForm(instance=project)
    return render(request, 'employee/project_form.html', {'form': form, 'action': 'Edit', 'project': project})

@login_required
@role_required(['ADMIN', 'HR'])
def assign_employees_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        employee_ids = request.POST.getlist('employees')
        if employee_ids:
            valid_employees = Employee.objects.filter(eID__in=employee_ids)
            project.employees.set(valid_employees)
        else:
            project.employees.clear()
        project.save()
        messages.success(request, 'Employees assigned successfully!')
        return redirect('project_list', project.status.lower().replace('_', '-'))
    # Get only employees (not admins/HR)
    employee_eids = UserProfile.objects.filter(role='EMPLOYEE').values_list('user__username', flat=True)
    employees = Employee.objects.filter(eID__in=employee_eids)
    return render(request, 'employee/assign_employees.html', {'project': project, 'employees': employees})

@login_required
def mark_project_complete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Only allow if user is assigned to this project
    if user_profile.role == 'EMPLOYEE' and project.employees.filter(eID=request.user.username).exists():
        project.status = 'COMPLETED'
        project.save()
        messages.success(request, 'Project marked as complete!')
    else:
        messages.error(request, 'You are not assigned to this project or not allowed to complete it.')
    return redirect('project_list', 'ongoing')

@login_required
@role_required(['EMPLOYEE'])
def my_projects(request):
    employee = get_object_or_404(Employee, eID=request.user.username)
    ongoing_projects = employee.projects.filter(status='ONGOING').order_by('-start_date')
    upcoming_projects = employee.projects.filter(status='UPCOMING').order_by('-start_date')
    return render(request, 'employee/my_projects.html', {
        'employee': employee,
        'ongoing_projects': ongoing_projects,
        'upcoming_projects': upcoming_projects
    })

@login_required
@role_required(['ADMIN', 'HR', 'EMPLOYEE'])
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    employees = project.employees.all()
    return render(request, 'employee/project_detail.html', {'project': project, 'employees': employees})

@login_required
@role_required(['ADMIN', 'HR'])
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list', 'ongoing')
    return render(request, 'employee/project_confirm_delete.html', {'project': project})

# API Serializers
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['eID', 'firstName', 'lastName', 'email', 'designation']

class ProjectSerializer(serializers.ModelSerializer):
    employees = EmployeeSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'name', 'status', 'start_date', 'end_date', 'description', 'employees']

# API ViewSets
class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

@login_required
def employee_profile_forms(request):
    """View to handle all employee profile forms"""
    employee = get_object_or_404(Employee, eID=request.user.username)
    
    # Initialize forms
    employee_info_form = EmployeeInformationForm(instance=getattr(employee, 'employeeinformation', None))
    id_card_form = IDCardForm(instance=getattr(employee, 'idcard', None))
    wifi_access_form = WiFiAccessForm(instance=getattr(employee, 'wifiaccess', None))
    parking_form = ParkingDetailsForm(instance=getattr(employee, 'parkingdetails', None))
    insurance_form = InsuranceDetailsForm(instance=getattr(employee, 'insurancedetails', None))
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'employee_info':
            form = EmployeeInformationForm(request.POST, instance=getattr(employee, 'employeeinformation', None))
            if form.is_valid():
                info = form.save(commit=False)
                info.employee = employee
                info.save()
                messages.success(request, 'Employee information updated successfully!')
                return redirect('employee_profile_forms')
                
        elif form_type == 'id_card':
            form = IDCardForm(request.POST, instance=getattr(employee, 'idcard', None))
            if form.is_valid():
                id_card = form.save(commit=False)
                id_card.employee = employee
                id_card.save()
                messages.success(request, 'ID Card information updated successfully!')
                return redirect('employee_profile_forms')
                
        elif form_type == 'wifi_access':
            form = WiFiAccessForm(request.POST, instance=getattr(employee, 'wifiaccess', None))
            if form.is_valid():
                wifi = form.save(commit=False)
                wifi.employee = employee
                wifi.save()
                messages.success(request, 'WiFi access information updated successfully!')
                return redirect('employee_profile_forms')
                
        elif form_type == 'parking':
            form = ParkingDetailsForm(request.POST, instance=getattr(employee, 'parkingdetails', None))
            if form.is_valid():
                parking = form.save(commit=False)
                parking.employee = employee
                parking.save()
                messages.success(request, 'Parking details updated successfully!')
                return redirect('employee_profile_forms')
                
        elif form_type == 'insurance':
            form = InsuranceDetailsForm(request.POST, instance=getattr(employee, 'insurancedetails', None))
            if form.is_valid():
                insurance = form.save(commit=False)
                insurance.employee = employee
                insurance.save()
                messages.success(request, 'Insurance details updated successfully!')
                return redirect('employee_profile_forms')
    
    context = {
        'employee': employee,
        'employee_info_form': employee_info_form,
        'id_card_form': id_card_form,
        'wifi_access_form': wifi_access_form,
        'parking_form': parking_form,
        'insurance_form': insurance_form,
    }
    return render(request, 'employee/profile_forms.html', context)

@login_required
@role_required(['HR', 'ADMIN'])
def review_employee_forms(request, employee_id):
    """View for HR/Admin to review employee forms"""
    employee = get_object_or_404(Employee, eID=employee_id)
    
    # Get all forms data
    employee_info = getattr(employee, 'employeeinformation', None)
    id_card = getattr(employee, 'idcard', None)
    wifi_access = getattr(employee, 'wifiaccess', None)
    parking = getattr(employee, 'parkingdetails', None)
    insurance = getattr(employee, 'insurancedetails', None)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        action = request.POST.get('action')
        
        if action == 'approve':
            # Create or update ProfileUpdateRequest
            ProfileUpdateRequest.objects.create(
                employee=employee,
                requested_by=request.user,
                proposed_changes={form_type: 'approved'},
                status='APPROVED',
                reviewed_by=request.user,
                reviewed_at=timezone.now()
            )
            messages.success(request, f'{form_type.replace("_", " ").title()} approved successfully!')
        elif action == 'reject':
            ProfileUpdateRequest.objects.create(
                employee=employee,
                requested_by=request.user,
                proposed_changes={form_type: 'rejected'},
                status='REJECTED',
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
                review_comments=request.POST.get('comments', '')
            )
            messages.warning(request, f'{form_type.replace("_", " ").title()} rejected.')
        
        return redirect('review_employee_forms', employee_id=employee_id)
    
    context = {
        'employee': employee,
        'employee_info': employee_info,
        'id_card': id_card,
        'wifi_access': wifi_access,
        'parking': parking,
        'insurance': insurance,
    }
    return render(request, 'employee/review_forms.html', context)

@login_required
@role_required(['HR', 'ADMIN'])
def employee_validation_list(request):
    """View for HR/Admin to list and validate employee information"""
    # Get all employees with their validation status
    employees = Employee.objects.all().order_by('-joinDate')
    
    # Add validation status to each employee
    for employee in employees:
        # Check if employee has any pending updates
        pending_updates = ProfileUpdateRequest.objects.filter(
            employee=employee,
            status='PENDING'
        ).exists()
        
        # Check if all required information is provided
        has_employee_info = hasattr(employee, 'employeeinformation')
        has_id_card = hasattr(employee, 'idcard')
        has_wifi_access = hasattr(employee, 'wifiaccess')
        has_parking = hasattr(employee, 'parkingdetails')
        has_insurance = hasattr(employee, 'insurancedetails')
        
        # Determine overall validation status
        if pending_updates:
            employee.validation_status = 'PENDING'
        elif all([has_employee_info, has_id_card, has_wifi_access, has_parking, has_insurance]):
            employee.validation_status = 'APPROVED'
        else:
            employee.validation_status = 'INCOMPLETE'
            
        # Get last update time
        last_update = ProfileUpdateRequest.objects.filter(
            employee=employee
        ).order_by('-reviewed_at').first()
        
        employee.last_updated = last_update.reviewed_at if last_update else employee.joinDate
    
    context = {
        'employees': employees,
        'page_title': 'Employee Information Validation',
        'active_page': 'validation'
    }
    return render(request, 'employee/employee_validation.html', context)

@login_required(login_url='/')
@role_required(['ADMIN', 'HR'])
def employee_documents(request, employee_id):
    """View for displaying and verifying employee documents"""
    employee = get_object_or_404(Employee, eID=employee_id)
    documents = Document.objects.filter(employee=employee).order_by('-uploaded_at')
    
    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        status = request.POST.get('status')
        comments = request.POST.get('comments', '')
        
        document = get_object_or_404(Document, id=doc_id)
        document.status = status
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.comments = comments
        document.save()
        
        AuditLog.objects.create(
            user=request.user,
            action=f"Document Verification - {status}",
            details=f"Document {doc_id} verified for {employee.eID}"
        )
        
        messages.success(request, "Document verification updated successfully!")
        return redirect('employee_documents', employee_id=employee_id)
    
    context = {
        'employee': employee,
        'documents': documents,
        'page_title': f'Documents - {employee.firstName} {employee.lastName}',
        'active_page': 'documents'
    }
    return render(request, 'employee/employee_documents.html', context)