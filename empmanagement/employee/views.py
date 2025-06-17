from django.shortcuts import redirect, render, get_object_or_404
from .forms import *
from employee.models import (
    Employee, Attendance, Notice, workAssignments, 
    Document, UserProfile, AuditLog, JobOpening,
    designations_opt, DOCUMENT_TYPES, PerformanceReview, Goal, LeaveRequest,
    TrainingProgram, TrainingEnrollment, Payroll, Project, EmployeeInformation, IDCard, WiFiAccess, ParkingDetails, InsuranceDetails, ProfileUpdateRequest,
    TrainingTag, TrainingBlog, TrainingDocument, Asset, AssetCategory, AssetAssignment,
    BankDetail, InsurancePolicy, TaxDetail, PersonalDetail
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from functools import wraps
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Sum, Count
from datetime import datetime, timedelta, time
import uuid
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
import csv
from django.http import HttpResponse
from django import forms
from rest_framework import viewsets, serializers
from django.core.mail import send_mail
from django.conf import settings
import random
import string
import logging
from django.views.decorators.http import require_http_methods
from .utils import get_auth_url, get_access_token_from_code, test_email_sending, initiate_auth as utils_initiate_auth, auth_callback as utils_auth_callback
from .decorators import role_required
import json
from django.db import IntegrityError

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
        
        # Get employee info for the logged-in user only
        employee = Employee.objects.get(eID=request.user.username)
        
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
            'employee': employee,
            'attendance_count': attendance_count,
            'leave_balance': leave_balance,
            'task_count': task_count,
            'training_count': training_count,
            'recent_tasks': recent_tasks,
            'recent_notices': recent_notices,
            'assigned_projects_count': assigned_projects_count,
            'user_profile': user_profile
        }
        
        return render(request, 'employee/index.html', context)
        
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('login')
    except Employee.DoesNotExist:
        messages.error(request, "Employee record not found.")
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
                return redirect('employee_onboarding')
        
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

@login_required
def profile(request):
    try:
        employee = Employee.objects.get(eID=request.user.username)
        user_profile = get_object_or_404(UserProfile, user=request.user)
        bank_details = BankDetail.objects.filter(employee=employee).first()
        
        # Initialize forms
        employee_info_form = EmployeeInformationForm(instance=getattr(employee, 'employeeinformation', None))
        id_card_form = IDCardForm(instance=getattr(employee, 'idcard', None))
        wifi_access_form = WiFiAccessForm(instance=getattr(employee, 'wifiaccess', None))
        parking_form = ParkingDetailsForm(instance=getattr(employee, 'parkingdetails', None))
        insurance_form = InsuranceDetailsForm(instance=getattr(employee, 'insurancedetails', None))
        
        if request.method == 'POST':
            form_type = request.POST.get('form_type')
            
            if form_type == 'personal':
                # Update personal details
                employee.firstName = request.POST.get('firstName')
                employee.lastName = request.POST.get('lastName')
                employee.dOB = request.POST.get('dOB')
                employee.addharNo = request.POST.get('addharNo')
                employee.save()
                messages.success(request, 'Personal details updated successfully!')
                
            elif form_type == 'contact':
                # Update contact info
                employee.email = request.POST.get('email')
                employee.personal_email = request.POST.get('personal_email')
                employee.phoneNo = request.POST.get('phoneNo')
                employee.save()
                messages.success(request, 'Contact information updated successfully!')
                
            elif form_type == 'employment':
                form = EmployeeInformationForm(request.POST, instance=getattr(employee, 'employeeinformation', None))
                if form.is_valid():
                    info = form.save(commit=False)
                    info.employee = employee
                    info.save()
                    messages.success(request, 'Employment details updated successfully!')
                else:
                    messages.error(request, 'Please correct the errors below.')
                    employee_info_form = form
                
            elif form_type == 'bank':
                # Update or create bank details
                if bank_details:
                    bank_details.bank_name = request.POST.get('bank_name')
                    bank_details.account_number = request.POST.get('account_number')
                    bank_details.ifsc = request.POST.get('ifsc')
                    bank_details.branch = request.POST.get('branch')
                    bank_details.save()
                else:
                    bank_details = BankDetail.objects.create(
                        employee=employee,
                        bank_name=request.POST.get('bank_name'),
                        account_number=request.POST.get('account_number'),
                        ifsc=request.POST.get('ifsc'),
                        branch=request.POST.get('branch')
                    )
                messages.success(request, 'Bank details updated successfully!')
                
            elif form_type == 'emergency':
                # Update emergency contact
                user_profile.emergency_contact_name = request.POST.get('emergency_contact_name')
                user_profile.emergency_contact_phone = request.POST.get('emergency_contact_phone')
                user_profile.save()
                messages.success(request, 'Emergency contact updated successfully!')
                
            elif form_type == 'id_card':
                form = IDCardForm(request.POST, instance=getattr(employee, 'idcard', None))
                if form.is_valid():
                    card = form.save(commit=False)
                    card.employee = employee
                    card.save()
                    messages.success(request, 'ID Card details updated successfully!')
                else:
                    messages.error(request, 'Please correct the errors below.')
                    id_card_form = form
                
            elif form_type == 'wifi_access':
                form = WiFiAccessForm(request.POST, instance=getattr(employee, 'wifiaccess', None))
                if form.is_valid():
                    wifi = form.save(commit=False)
                    wifi.employee = employee
                    wifi.save()
                    messages.success(request, 'WiFi access details updated successfully!')
                else:
                    messages.error(request, 'Please correct the errors below.')
                    wifi_access_form = form
                
            elif form_type == 'parking':
                form = ParkingDetailsForm(request.POST, instance=getattr(employee, 'parkingdetails', None))
                if form.is_valid():
                    parking = form.save(commit=False)
                    parking.employee = employee
                    parking.save()
                    messages.success(request, 'Parking details updated successfully!')
                else:
                    messages.error(request, 'Please correct the errors below.')
                    parking_form = form
                
            elif form_type == 'insurance':
                form = InsuranceDetailsForm(request.POST, instance=getattr(employee, 'insurancedetails', None))
                if form.is_valid():
                    insurance = form.save(commit=False)
                    insurance.employee = employee
                    insurance.save()
                    messages.success(request, 'Insurance details updated successfully!')
                else:
                    messages.error(request, 'Please correct the errors below.')
                    insurance_form = form
        
        return render(request, 'employee/profile.html', {
            'employee': employee,
            'profile': user_profile,
            'bank_details': bank_details or BankDetail(),
            'employee_info_form': employee_info_form,
            'id_card_form': id_card_form,
            'wifi_access_form': wifi_access_form,
            'parking_form': parking_form,
            'insurance_form': insurance_form,
        })
        
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect('dashboard')

@login_required
def my_documents(request):
    try:
        # Use eID instead of user field
        employee = Employee.objects.get(eID=request.user.username)
        documents = employee.documents.all().order_by('-uploaded_at')
        
        # Get document verification statuses
        info_statuses = {
            'id_verified': documents.filter(document_type='ID_PROOF', is_verified=True).exists(),
            'address_verified': documents.filter(document_type='ADDRESS_PROOF', is_verified=True).exists(),
            'education_verified': documents.filter(document_type='EDUCATION', is_verified=True).exists(),
            'experience_verified': documents.filter(document_type='EXPERIENCE', is_verified=True).exists(),
        }
        
        return render(request, 'employee/my_documents.html', {
            'documents': documents,
            'info_statuses': info_statuses,
        })
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect('dashboard')

@login_required
def upload_document(request):
    try:
        # Use eID instead of user field
        employee = Employee.objects.get(eID=request.user.username)
        
        if request.method == 'POST':
            document_type = request.POST.get('document_type')
            description = request.POST.get('description')
            file = request.FILES.get('document')
            
            if document_type and file:
                document = Document.objects.create(
                    employee=employee,
                    document_type=document_type,
                    description=description,
                    file=file
                )
                messages.success(request, 'Document uploaded successfully!')
                return redirect('my_documents')
            else:
                messages.error(request, 'Please provide all required information.')
        
        return render(request, 'employee/upload_document.html')
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect('dashboard')

@login_required
def update_document(request, doc_id):
    try:
        # Use eID instead of user field
        employee = Employee.objects.get(eID=request.user.username)
        document = get_object_or_404(Document, id=doc_id, employee=employee)
        
        if document.is_verified:
            messages.error(request, "Cannot update a verified document.")
            return redirect('my_documents')
        
        if request.method == 'POST':
            description = request.POST.get('description')
            file = request.FILES.get('document')
            
            if file:
                document.file = file
            if description:
                document.description = description
            document.save()
            
            messages.success(request, 'Document updated successfully!')
            return redirect('my_documents')
        
        return render(request, 'employee/update_document.html', {'document': document})
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect('dashboard')

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
    if not request.user.is_staff:
        return redirect('dashboard')
        
    employees = Employee.objects.all()
    user_profiles = UserProfile.objects.all()
    
    # Get asset data
    assets = Asset.objects.all()
    total_assets = assets.count()
    available_assets = assets.filter(status='Available').count()
    assigned_assets = assets.filter(status='Assigned').count()
    maintenance_assets = assets.filter(status='Under Maintenance').count()
    
    # Prepare data for each tab using UserProfile
    bank_details = []
    insurance_policies = []
    tax_details = []
    personal_details = []
    
    for emp in employees:
        try:
            profile = UserProfile.objects.get(user__username=emp.eID)
            bank_details.append({
                'employee': emp,
                'account_number': profile.bank_account_number if hasattr(profile, 'bank_account_number') else '',
                'ifsc': profile.bank_ifsc if hasattr(profile, 'bank_ifsc') else ''
            })
            personal_details.append({
                'employee': emp,
                'emergency_contact_name': profile.emergency_contact_name if hasattr(profile, 'emergency_contact_name') else '',
                'emergency_contact_phone': profile.emergency_contact_phone if hasattr(profile, 'emergency_contact_phone') else ''
            })
        except UserProfile.DoesNotExist:
            bank_details.append({'employee': emp, 'account_number': '', 'ifsc': ''})
            personal_details.append({'employee': emp, 'emergency_contact_name': '', 'emergency_contact_phone': ''})
        
        # Stub data for insurance and tax
        insurance_policies.append({'employee': emp, 'policy': 'N/A'})
        tax_details.append({'employee': emp, 'tax': 'N/A'})
    
    context = {
        'employees': employees,
        'bank_details': bank_details,
        'insurance_policies': insurance_policies,
        'tax_details': tax_details,
        'personal_details': personal_details,
        # Asset data
        'assets': assets,
        'total_assets': total_assets,
        'available_assets': available_assets,
        'assigned_assets': assigned_assets,
        'maintenance_assets': maintenance_assets,
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
def employee_onboarding(request):
    if request.method == 'POST' and request.user.is_staff:
        try:
            import uuid
            from datetime import datetime
            
            # Auto-generate Employee ID
            def generate_employee_id():
                return 'EMP' + uuid.uuid4().hex[:8].upper()
            employee_id = generate_employee_id()

            # Get form data
            first_name = request.POST['firstName']
            middle_name = request.POST.get('middleName', '')
            last_name = request.POST['lastName']
            email = request.POST['email']
            join_date_str = request.POST['joinDate']
            designation = request.POST['designation']

            # Convert join_date string to datetime object
            try:
                # First try the HTML5 date format (YYYY-MM-DD)
                join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    # Then try the display format (DD-MM-YYYY)
                    join_date = datetime.strptime(join_date_str, '%d-%m-%Y').date()
                except ValueError:
                    messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
                    return redirect('employee_onboarding')

            # Generate a temporary Aadhar number that's unique
            temp_aadhar = f'TEMP_{employee_id}'

            # Create new employee with minimal required fields
            employee = Employee.objects.create(
                eID=employee_id,
                firstName=first_name,
                middleName=middle_name,
                lastName=last_name,
                email=email,
                joinDate=join_date,
                designation=designation,
                phoneNo=None,
                dOB=timezone.now().date(),
                salary='0',
                addharNo=temp_aadhar  # Using the unique temporary Aadhar number
            )

            # Create User account for the employee
            try:
                # Generate a random password
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                user = User.objects.create_user(
                    username=employee_id,
                    email=email,
                    password=temp_password,
                    first_name=first_name,
                    last_name=last_name
                )
                UserProfile.objects.create(
                    user=user,
                    role='EMPLOYEE',
                    profile_completion=0
                )

                # Send notification email using Microsoft Graph API
                try:
                    from .utils import send_new_employee_notification
                    send_new_employee_notification(employee, temp_password)
                    messages.success(request, f'Employee created successfully with ID: {employee_id}. Welcome email with login credentials sent.')
                except Exception as email_error:
                    print(f"Email sending failed: {str(email_error)}")
                    messages.warning(request, f'''Employee created successfully with ID: {employee_id}.
                    However, welcome email could not be sent. Please provide these credentials manually:
                    Username: {employee_id}
                    Temporary Password: {temp_password}''')

            except Exception as user_error:
                employee.delete()  # Rollback employee creation if user creation fails
                raise Exception(f"Failed to create user account: {str(user_error)}")

            return redirect('employee_onboarding')
        except Exception as e:
            print(f"Employee creation failed with error: {str(e)}")
            messages.error(request, f'Error creating employee: {str(e)}')
    employees = Employee.objects.all().order_by('-joinDate')
    return render(request, 'employee/onboarding.html', {
        'employees': employees,
        'designations_opt': designations_opt
    })

@login_required
def complete_onboarding(request, employee_id):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard')
    
    try:
        employee = Employee.objects.get(eID=employee_id)
        employee.onboarding_completed = True
        employee.onboarding_date = timezone.now()
        employee.save()
        
        # Send completion email
        send_mail(
            'Onboarding Completed',
            f'''Dear {employee.firstName},

Your onboarding process has been completed successfully.

You can now access all company resources using your company email: {employee.email}

Best regards,
HR Team''',
            settings.DEFAULT_FROM_EMAIL,
            [employee.personal_email],
            fail_silently=False,
        )
        
        messages.success(request, 'Onboarding completed successfully.')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee not found.')
    except Exception as e:
        messages.error(request, f'Error completing onboarding: {str(e)}')
    
    return redirect('employee_onboarding')

@login_required
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
        
    return redirect('employee_onboarding')

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
        today = timezone.now().date()
        
        # Get today's attendance
        today_attendance = Attendance.objects.filter(
            eId=request.user.username,
            date=today
        ).first()

        # Get attendance history (last 30 days)
        attendance_records = Attendance.objects.filter(
            eId=request.user.username
        ).order_by('-date', '-time_in')[:30]

        context = {
            'today_attendance': today_attendance,
            'attendance_records': attendance_records,
        }
        
        return render(request, 'employee/attendance_list.html', context)
    except Exception as e:
        logger.error(f"Attendance list error: {str(e)}")
        messages.error(request, 'An error occurred while fetching attendance records.')
        return redirect('dashboard')

@login_required
@require_http_methods(["POST"])
def clock_in(request):
    try:
        today = timezone.now().date()
        current_time = timezone.now()

        # Check if there's an existing clock-in record for today
        existing_attendance = Attendance.objects.filter(
            eId=request.user.username,
            date=today
        ).first()

        if existing_attendance:
            return JsonResponse({
                'success': False,
                'message': 'You have already clocked in for today.'
            }, status=400)

        # Create new attendance record
        attendance = Attendance.objects.create(
            eId=request.user.username,
            time_in=current_time,
            date=today,
            status='PRESENT'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Clocked in successfully!',
            'clock_in_time': attendance.time_in.strftime('%H:%M')
        }, status=201)

    except IntegrityError as e:
        logger.error(f"Clock-in IntegrityError for user {request.user.username}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Failed to clock in due to a duplicate record. Please contact support.'
        }, status=400)
    except Exception as e:
        logger.error(f"Clock-in error for user {request.user.username}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'An unexpected error occurred while clocking in. Please try again later.'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def clock_out(request):
    try:
        today = timezone.now().date()
        current_time = timezone.now()

        attendance = Attendance.objects.filter(
            eId=request.user.username,
            date=today,
            time_out__isnull=True
        ).first()

        if not attendance:
            return JsonResponse({
                'success': False,
                'message': 'No active clock-in record found for today.'
            }, status=400)

        attendance.time_out = current_time
        attendance.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Clocked out successfully!',
            'clock_out_time': attendance.time_out.strftime('%H:%M')
        }, status=200)

    except Exception as e:
        logger.error(f"Clock-out error for user {request.user.username}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'An unexpected error occurred while clocking out. Please try again later.'
        }, status=500)

@login_required
@role_required(['ADMIN', 'HR'])
def admin_attendance(request):
    employees = User.objects.filter(is_staff=False, is_superuser=False)
    attendance_records = Attendance.objects.all().order_by('-date', '-clock_in')

    # Filters
    selected_employee_id = request.GET.get('employee')
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    selected_status = request.GET.get('status')

    if selected_employee_id:
        attendance_records = attendance_records.filter(employee__id=selected_employee_id)
    if date_from_str:
        attendance_records = attendance_records.filter(date__gte=date_from_str)
    if date_to_str:
        attendance_records = attendance_records.filter(date__lte=date_to_str)
    if selected_status:
        attendance_records = attendance_records.filter(status=selected_status)

    # Pagination
    paginator = Paginator(attendance_records, 10) # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'employees': employees,
        'attendance_records': page_obj,
        'selected_employee': int(selected_employee_id) if selected_employee_id else '',
        'date_from': date_from_str if date_from_str else '',
        'date_to': date_to_str if date_to_str else '',
        'selected_status': selected_status if selected_status else '',
    }
    return render(request, 'employee/admin_attendance.html', context)

@login_required
@require_http_methods(["GET"])
def record_details(request, record_id):
    record = get_object_or_404(Attendance, id=record_id)
    data = {
        'employee_name': record.employee.get_full_name(),
        'date': record.date.strftime('%Y-%m-%d'),
        'clock_in': record.clock_in.strftime('%H:%M'),
        'clock_out': record.clock_out.strftime('%H:%M') if record.clock_out else None,
        'total_hours': str(record.total_hours) if record.total_hours else None,
        'status': record.status,
        'reason': record.reason,
        'is_manual': record.is_manual,
    }
    return JsonResponse(data)

@login_required
@role_required(['ADMIN', 'HR'])
@require_http_methods(["POST"])
def approve_record(request, record_id):
    record = get_object_or_404(Attendance, id=record_id)
    if record.status == 'PENDING':
        record.status = 'APPROVED' # Or 'PRESENT' if it was a manual clock-in
        record.save()
        return JsonResponse({'success': True, 'message': 'Attendance record approved.'})
    return JsonResponse({'success': False, 'message': 'Record is not pending approval.'})

@login_required
@role_required(['ADMIN', 'HR'])
@require_http_methods(["POST"])
def reject_record(request, record_id):
    record = get_object_or_404(Attendance, id=record_id)
    if record.status == 'PENDING':
        data = json.loads(request.body)
        reason = data.get('reason', 'No reason provided.')
        record.status = 'REJECTED'
        record.reason = reason # Store rejection reason
        record.save()
        return JsonResponse({'success': True, 'message': 'Attendance record rejected.'})
    return JsonResponse({'success': False, 'message': 'Record is not pending approval.'})

@login_required
def regulate_attendance(request, record_id):
    record = get_object_or_404(Attendance, id=record_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        time_in_str = request.POST.get('time_in')
        time_out_str = request.POST.get('time_out')
        overtime_hours = request.POST.get('overtime_hours', 0)
        reason = request.POST.get('reason', '')

        try:
            record.clock_in = datetime.strptime(time_in_str, '%H:%M').time() if time_in_str else None
            record.clock_out = datetime.strptime(time_out_str, '%H:%M').time() if time_out_str else None
        except ValueError:
            messages.error(request, "Invalid time format.")
            return redirect('regulate_attendance', record_id=record.id)

        record.status = status
        record.overtime_hours = overtime_hours
        record.reason = reason # Store reason for changes
        record.is_manual = True # Mark as manual if edited
        record.save()
        messages.success(request, 'Attendance record updated successfully.')
        return redirect('attendance_list')
    
    context = {
        'record': record,
    }
    return render(request, 'employee/regulate_attendance.html', context)

@login_required
@role_required(['ADMIN', 'HR'])
def export_attendance(request):
    attendance_records = Attendance.objects.all().order_by('date', 'employee__username')

    # Apply filters from GET parameters
    selected_employee_id = request.GET.get('employee')
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    selected_status = request.GET.get('status')

    if selected_employee_id:
        attendance_records = attendance_records.filter(employee__id=selected_employee_id)
    if date_from_str:
        attendance_records = attendance_records.filter(date__gte=date_from_str)
    if date_to_str:
        attendance_records = attendance_records.filter(date__lte=date_to_str)
    if selected_status:
        attendance_records = attendance_records.filter(status=selected_status)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Employee', 'Date', 'Clock In', 'Clock Out', 'Total Hours', 'Status', 'Is Manual', 'Reason'])

    for record in attendance_records:
        writer.writerow([
            record.employee.get_full_name(),
            record.date.strftime('%Y-%m-%d'),
            record.clock_in.strftime('%H:%M') if record.clock_in else '',
            record.clock_out.strftime('%H:%M') if record.clock_out else '',
            str(record.total_hours) if record.total_hours else '',
            record.status,
            'Yes' if record.is_manual else 'No',
            record.reason if record.reason else '',
        ])

    return response

@login_required
def training_program_list(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        # Show all programs regardless of role
        programs = TrainingProgram.objects.all()
        return render(request, 'employee/training_program_list.html', {'programs': programs})
    except UserProfile.DoesNotExist:
        programs = []
        return render(request, 'employee/training_program_list.html', {'programs': programs})

@login_required
@role_required(['ADMIN', 'HR'])
def create_training_program(request):
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, 'Training program created successfully!')
            return redirect('training_program_list')
    else:
        form = TrainingProgramForm()
    
    return render(request, 'employee/create_training_program.html', {
        'form': form,
        'page_title': 'Create Training Program'
    })

@login_required
@role_required(['ADMIN', 'HR'])
def edit_training_program(request, program_id):
    program = get_object_or_404(TrainingProgram, id=program_id)
    
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, 'Training program updated successfully!')
            return redirect('training_program_list')
    else:
        form = TrainingProgramForm(instance=program)
    
    return render(request, 'employee/create_training_program.html', {
        'form': form,
        'program': program,
        'page_title': 'Edit Training Program'
    })

@login_required
@role_required(['ADMIN', 'HR'])
def delete_training_program(request, program_id):
    program = get_object_or_404(TrainingProgram, id=program_id)
    
    if request.method == 'POST':
        program.delete()
        messages.success(request, 'Training program deleted successfully!')
        return redirect('training_program_list')
    
    return render(request, 'employee/delete_training_program.html', {
        'program': program
    })

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
def training_blog_list(request, program_id):
    program = get_object_or_404(TrainingProgram, id=program_id)
    tag = request.GET.get('tag')
    
    if tag:
        blogs = program.blogs.filter(tags__name=tag, is_published=True)
    else:
        blogs = program.blogs.filter(is_published=True)
    
    tags = TrainingTag.objects.filter(blogs__program=program).distinct()
    
    context = {
        'program': program,
        'blogs': blogs,
        'tags': tags,
        'current_tag': tag
    }
    return render(request, 'employee/training_blog_list.html', context)

@login_required
def create_training_blog(request, program_id):
    program = get_object_or_404(TrainingProgram, id=program_id)
    
    if request.method == 'POST':
        form = TrainingBlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.program = program
            blog.author = request.user
            blog.save()
            
            # Handle tags
            tag_list = form.cleaned_data['tags']
            for tag_name in tag_list:
                tag, _ = TrainingTag.objects.get_or_create(name=tag_name)
                blog.tags.add(tag)
            
            # Handle documents
            files = request.FILES.getlist('documents')
            for file in files:
                TrainingDocument.objects.create(
                    blog=blog,
                    file=file,
                    title=file.name
                )
            
            messages.success(request, 'Blog post created successfully.')
            return redirect('training_blog_list', program_id=program.id)
    else:
        form = TrainingBlogForm()
    
    context = {
        'form': form,
        'program': program,
        'blog': None
    }
    return render(request, 'employee/create_training_blog.html', context)

@login_required
def training_blog_detail(request, blog_id):
    blog = get_object_or_404(TrainingBlog, id=blog_id)
    context = {
        'blog': blog,
        'documents': blog.documents.all()
    }
    return render(request, 'employee/training_blog_detail.html', context)

@login_required
def edit_training_blog(request, blog_id):
    blog = get_object_or_404(TrainingBlog, id=blog_id)
    
    if request.user != blog.author:
        messages.error(request, 'You do not have permission to edit this blog post.')
        return redirect('training_blog_detail', blog_id=blog.id)
    
    if request.method == 'POST':
        form = TrainingBlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            blog = form.save()
            
            # Handle tags
            blog.tags.clear()
            tag_list = form.cleaned_data['tags']
            for tag_name in tag_list:
                tag, _ = TrainingTag.objects.get_or_create(name=tag_name)
                blog.tags.add(tag)
            
            # Handle new documents
            files = request.FILES.getlist('documents')
            for file in files:
                TrainingDocument.objects.create(
                    blog=blog,
                    file=file,
                    title=file.name
                )
            
            messages.success(request, 'Blog post updated successfully.')
            return redirect('training_blog_detail', blog_id=blog.id)
    else:
        initial_data = {
            'tags': ', '.join(tag.name for tag in blog.tags.all())
        }
        form = TrainingBlogForm(instance=blog, initial=initial_data)
    
    context = {
        'form': form,
        'blog': blog,
        'program': blog.program
    }
    return render(request, 'employee/create_training_blog.html', context)

@login_required
def delete_training_blog(request, blog_id):
    blog = get_object_or_404(TrainingBlog, id=blog_id)
    
    if request.user != blog.author:
        messages.error(request, 'You do not have permission to delete this blog post.')
        return redirect('training_blog_detail', blog_id=blog.id)
    
    program_id = blog.program.id
    blog.delete()
    messages.success(request, 'Blog post deleted successfully.')
    return redirect('training_blog_list', program_id=program_id)

@login_required
def delete_training_document(request, document_id):
    document = get_object_or_404(TrainingDocument, id=document_id)
    blog_id = document.blog.id
    
    if request.user != document.blog.author:
        messages.error(request, 'You do not have permission to delete this document.')
        return redirect('training_blog_detail', blog_id=blog_id)
    
    document.delete()
    messages.success(request, 'Document deleted successfully.')
    return redirect('training_blog_detail', blog_id=blog_id)

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
    
    # Determine if each section is editable based on allow_edit
    def get_is_editable(form_type):
        req = ProfileUpdateRequest.objects.filter(
            employee=employee,
            proposed_changes__has_key=form_type
        ).order_by('-submitted_at').first()
        return getattr(req, 'allow_edit', False) if req else False

    form_statuses = {
        'employee_info': {'is_editable': get_is_editable('employee_info')},
        'id_card': {'is_editable': get_is_editable('id_card')},
        'wifi_access': {'is_editable': get_is_editable('wifi_access')},
        'parking': {'is_editable': get_is_editable('parking')},
        'insurance': {'is_editable': get_is_editable('insurance')},
    }

    context = {
        'employee': employee,
        'employee_info_form': employee_info_form,
        'id_card_form': id_card_form,
        'wifi_access_form': wifi_access_form,
        'parking_form': parking_form,
        'insurance_form': insurance_form,
        'form_statuses': form_statuses,
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
                reviewed_at=timezone.now(),
                allow_edit=False
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
                review_comments=request.POST.get('comments', ''),
                allow_edit=False
            )
            messages.warning(request, f'{form_type.replace("_", " ").title()} rejected.')
        elif action == 'allow_edit':
            # Set allow_edit=True for the latest ProfileUpdateRequest for this form_type
            latest_req = ProfileUpdateRequest.objects.filter(
                employee=employee,
                proposed_changes__has_key=form_type
            ).order_by('-submitted_at').first()
            if latest_req:
                latest_req.allow_edit = True
                latest_req.save()
                messages.success(request, f'Re-upload enabled for {form_type.replace("_", " ").title()}!')
            else:
                messages.error(request, f'No submission found to enable re-upload for {form_type.replace("_", " ").title()}.')
            return redirect('review_employee_forms', employee_id=employee_id)
        return redirect('review_employee_forms', employee_id=employee_id)

    # Prepare form_statuses for button state
    def get_allow_edit(form_type):
        req = ProfileUpdateRequest.objects.filter(
            employee=employee,
            proposed_changes__has_key=form_type
        ).order_by('-submitted_at').first()
        return {'allow_edit': getattr(req, 'allow_edit', False) if req else False}

    form_statuses = {
        'employee_info': get_allow_edit('employee_info'),
        'id_card': get_allow_edit('id_card'),
        'wifi_access': get_allow_edit('wifi_access'),
        'parking': get_allow_edit('parking'),
        'insurance': get_allow_edit('insurance'),
    }

    context = {
        'employee': employee,
        'employee_info': employee_info,
        'id_card': id_card,
        'wifi_access': wifi_access,
        'parking': parking,
        'insurance': insurance,
        'form_statuses': form_statuses,
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
        allow_reupload = request.POST.get('allow_reupload')
        
        document = get_object_or_404(Document, id=doc_id)
        if allow_reupload == 'true':
            document.allow_reupload = True
            document.save()
            messages.success(request, "Re-upload enabled for this document!")
            return redirect('employee_documents', employee_id=employee_id)
        else:
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
@role_required(['ADMIN', 'HR'])
def admin_panel(request):
    """Protected Django admin panel access."""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access the admin panel.")
        return redirect('dashboard')
    from django.contrib import admin
    return admin.site.index(request)

@login_required
@role_required(['ADMIN', 'HR'])
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

def generate_company_email(first_name, last_name):
    # Generate a random string to ensure uniqueness
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{first_name.lower()}.{last_name.lower()}.{random_str}@company.com"

@require_http_methods(["GET"])
def initiate_auth(request):
    """Initiate the OAuth flow"""
    return utils_initiate_auth(request)

@require_http_methods(["GET"])
def auth_callback(request):
    """Handle the OAuth callback"""
    return utils_auth_callback(request)

@require_http_methods(["GET"])
def test_email(request):
    """Test email sending functionality"""
    test_email_sending(request)
    return redirect('dashboard')

@login_required
@role_required(['ADMIN', 'HR'])
def asset_dashboard(request):
    total_assets = Asset.objects.count()
    available_assets = Asset.objects.filter(status='AVAILABLE').count()
    assigned_assets = Asset.objects.filter(status='ASSIGNED').count()
    maintenance_assets = Asset.objects.filter(status='MAINTENANCE').count()
    
    recent_assignments = AssetAssignment.objects.filter(is_returned=False).order_by('-assigned_date')[:5]
    categories = AssetCategory.objects.annotate(asset_count=Count('asset'))
    
    context = {
        'total_assets': total_assets,
        'available_assets': available_assets,
        'assigned_assets': assigned_assets,
        'maintenance_assets': maintenance_assets,
        'recent_assignments': recent_assignments,
        'categories': categories,
    }
    return render(request, 'employee/asset_dashboard.html', context)

@login_required
@role_required(['ADMIN', 'HR'])
def asset_list(request):
    assets = Asset.objects.all().order_by('-created_at')
    return render(request, 'employee/asset_list.html', {'assets': assets})

@login_required
@role_required(['ADMIN', 'HR'])
def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, asset_id=asset_id)
    assignments = AssetAssignment.objects.filter(asset=asset).order_by('-assigned_date')
    return render(request, 'employee/asset_detail.html', {
        'asset': asset,
        'assignments': assignments
    })

@login_required
@role_required(['ADMIN', 'HR'])
def asset_create(request):
    if request.method == 'POST':
        # Generate unique asset ID
        last_asset = Asset.objects.order_by('-asset_id').first()
        if last_asset:
            last_num = int(last_asset.asset_id[3:])
            new_num = str(last_num + 1).zfill(6)
            new_asset_id = f"AST{new_num}"
        else:
            new_asset_id = "AST000001"
            
        asset = Asset.objects.create(
            asset_id=new_asset_id,
            name=request.POST['name'],
            category_id=request.POST['category'],
            description=request.POST.get('description', ''),
            serial_number=request.POST.get('serial_number', ''),
            purchase_date=request.POST.get('purchase_date'),
            purchase_cost=request.POST.get('purchase_cost'),
            condition=request.POST['condition'],
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Asset created successfully!')
        return redirect('asset_detail', asset_id=asset.asset_id)
    
    categories = AssetCategory.objects.all()
    return render(request, 'employee/asset_form.html', {'categories': categories})

@login_required
@role_required(['ADMIN', 'HR'])
def asset_edit(request, asset_id):
    asset = get_object_or_404(Asset, asset_id=asset_id)
    if request.method == 'POST':
        asset.name = request.POST['name']
        asset.category_id = request.POST['category']
        asset.description = request.POST.get('description', '')
        asset.serial_number = request.POST.get('serial_number', '')
        asset.purchase_date = request.POST.get('purchase_date')
        asset.purchase_cost = request.POST.get('purchase_cost')
        asset.condition = request.POST['condition']
        asset.status = request.POST['status']
        asset.notes = request.POST.get('notes', '')
        asset.save()
        messages.success(request, 'Asset updated successfully!')
        return redirect('asset_detail', asset_id=asset.asset_id)
    
    categories = AssetCategory.objects.all()
    return render(request, 'employee/asset_form.html', {
        'asset': asset,
        'categories': categories
    })

@login_required
@role_required(['ADMIN', 'HR'])
def asset_assign(request, asset_id):
    asset = get_object_or_404(Asset, asset_id=asset_id)
    if request.method == 'POST':
        if asset.status != 'AVAILABLE':
            messages.error(request, 'This asset is not available for assignment.')
            return redirect('asset_detail', asset_id=asset.asset_id)
            
        assignment = AssetAssignment.objects.create(
            asset=asset,
            employee_id=request.POST['employee'],
            assigned_date=request.POST['assigned_date'],
            return_date=request.POST.get('return_date'),
            assigned_by=request.user,
            assignment_notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Asset assigned successfully!')
        return redirect('asset_detail', asset_id=asset.asset_id)
    
    employees = Employee.objects.all()
    return render(request, 'employee/asset_assign.html', {
        'asset': asset,
        'employees': employees
    })

@login_required
@role_required(['ADMIN', 'HR'])
def asset_return(request, assignment_id):
    assignment = get_object_or_404(AssetAssignment, id=assignment_id)
    if request.method == 'POST':
        assignment.is_returned = True
        assignment.return_notes = request.POST.get('return_notes', '')
        assignment.save()
        messages.success(request, 'Asset returned successfully!')
        return redirect('asset_detail', asset_id=assignment.asset.asset_id)
    
    return render(request, 'employee/asset_return.html', {'assignment': assignment})

@login_required
@role_required(['ADMIN', 'HR'])
def asset_delete(request, asset_id):
    asset = get_object_or_404(Asset, asset_id=asset_id)
    
    if request.method == 'POST':
        # Check if asset can be deleted (not assigned)
        if asset.status == 'ASSIGNED':
            messages.error(request, 'Cannot delete an assigned asset. Please return the asset first.')
            return redirect('asset_detail', asset_id=asset.asset_id)
        
        asset.delete()
        messages.success(request, 'Asset deleted successfully!')
        return redirect('asset_list')
    
    return render(request, 'employee/asset_delete.html', {'asset': asset})

