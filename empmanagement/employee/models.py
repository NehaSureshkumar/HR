from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from pickle import TRUE
from turtle import title
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField  # For JSON storage (if using Postgres)
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import send_new_employee_notification
import logging
from threading import local
from django.conf import settings

logger = logging.getLogger(__name__)

# Role choices
ROLE_CHOICES = (
    ('ADMIN', 'Admin'),
    ('HR', 'HR'),
    ('EMPLOYEE', 'Employee'),
)

# Document types
DOCUMENT_TYPES = (
    ('PAN', 'PAN Card'),
    ('AADHAR', 'Aadhar Card'),
    ('RESUME', 'Resume'),
    ('PASSPORT', 'Passport'),
    ('BANK', 'Bank Documents'),
    ('PF', 'PF Documents'),
    ('PASSBOOK', 'Passbook'),
    ('OTHER', 'Other'),
)

# Document status
DOCUMENT_STATUS = (
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
)

NOTICE_TAGS = (
    ('PROJECT', 'Project'),
    ('GENERAL', 'General'),
    ('HR', 'HR'),
    ('OTHER', 'Other'),
)

designations_opt = (
    ('Team Leader','Team Leader'),
    ('Project Manager','Project Manager'),
    ('Senior Developer','Senior Developer'),
    ('Junior Developer','Junior Developer'),
    ('Intern','Intern'),
    ('QA Tester','QA Tester')
)

months = (
    ('January','January'),
    ('February','February'),
    ('March','March'),
    ('April','April'),
    ('May','May'),
    ('June','June'),
    ('July','July'),
    ('August','August'),
    ('September','September'),
    ('October','October'),
    ('November','November'),
    ('December','December')
)

days = (('0','0'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),
('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),
('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31'))

# Employment type choices
EMPLOYMENT_TYPE_CHOICES = (
    ('INTERN', 'Intern'),
    ('FULL_TIME', 'Full-Time'),
    ('CONSULTANT', 'Consultant'),
)

# Status choices
STATUS_CHOICES = (
    ('ACTIVE', 'Active'),
    ('TERMINATED', 'Terminated'),
)

# Blood group choices
BLOOD_GROUP_CHOICES = (
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
)

# Vehicle make choices
VEHICLE_MAKE_CHOICES = (
    ('TOYOTA', 'Toyota'),
    ('HONDA', 'Honda'),
    ('FORD', 'Ford'),
    ('BMW', 'BMW'),
    ('MERCEDES', 'Mercedes'),
    ('AUDI', 'Audi'),
    ('HYUNDAI', 'Hyundai'),
    ('OTHER', 'Other'),
)

# Relationship choices
RELATIONSHIP_CHOICES = (
    ('SELF', 'Self'),
    ('SPOUSE', 'Spouse'),
    ('CHILD', 'Child'),
)

# Gender choices
GENDER_CHOICES = (
    ('MALE', 'Male'),
    ('FEMALE', 'Female'),
)

# Endorsement type choices
ENDORSEMENT_TYPE_CHOICES = (
    ('A', 'A'),
    ('D', 'D'),
)

# Create your models here.

class Employee(models.Model):
    eID = models.CharField(primary_key=True,max_length=20)
    firstName = models.CharField(max_length=50)
    middleName = models.CharField(max_length=50, blank=True)
    lastName = models.CharField(max_length=50)
    phoneNo = models.CharField(max_length=12, unique=True, null=True, blank=True)  # Made optional
    email = models.EmailField(max_length=70, unique=True)  # This will be the company email
    personal_email = models.EmailField(max_length=70, unique=True, null=True, blank=True)  # Personal email field
    addharNo = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Made optional
    dOB = models.DateField(null=True, blank=True)  # Made optional
    designation = models.CharField(max_length=50,choices=designations_opt)
    salary = models.CharField(max_length=20, default='0')
    joinDate = models.DateField()
    onboarding_completed = models.BooleanField(default=False)
    onboarding_date = models.DateField(null=True, blank=True)

    def __str__(self):  
        return "%s %s" % (self.eID, self.firstName)

class Attendance(models.Model):
    eId = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now)
    time_in = models.DateTimeField(default=timezone.now)
    time_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day')
    ], default='PRESENT')
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_attendance'
        ordering = ['-date', '-time_in']

    def __str__(self):
        return f"{self.eId} - {self.date}"

class Notice(models.Model):
    Id = models.CharField(primary_key=True,max_length=20)
    title = models.CharField(max_length=250)
    description = models.TextField()
    publishDate = models.DateTimeField()
    tag = models.CharField(max_length=20, choices=NOTICE_TAGS, default='GENERAL')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_pinned = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='notice_attachments/', null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class NoticeComment(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.notice.title}"

class workAssignments(models.Model):
    Id = models.CharField(primary_key=True, max_length=20)
    assignerId = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="assignerId")
    work = models.TextField()
    assignDate = models.DateTimeField()
    dueDate = models.DateTimeField()
    taskerId = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="taskerId") 

class Requests(models.Model):
    Id = models.CharField(primary_key=True, max_length=20)
    requesterId = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="requesterId")
    requestMessage = models.TextField()
    requestDate = models.DateTimeField()
    destinationEmployeeId = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="toEmployeeId") 

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    profile_completion = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    pf_number = models.CharField(max_length=20, blank=True)
    bank_account_number = models.CharField(max_length=30, blank=True)
    bank_ifsc = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Document(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=[
        ('ID_PROOF', 'ID Proof'),
        ('ADDRESS_PROOF', 'Address Proof'),
        ('EDUCATION', 'Education Certificate'),
        ('EXPERIENCE', 'Experience Certificate'),
        ('OFFER_LETTER', 'Offer Letter'),
        ('OTHER', 'Other')
    ])
    file = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.employee.firstName}'s {self.get_document_type_display()}"

    class Meta:
        ordering = ['-uploaded_at']

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}" 

class JobOpening(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('ON_HOLD', 'On Hold'),
    )

    title = models.CharField(max_length=100)
    department = models.CharField(max_length=50, choices=designations_opt)
    description = models.TextField()
    requirements = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    positions = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.title} ({self.department}) - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at'] 

class PerformanceReview(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    review_date = models.DateField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField()
    goals_achieved = models.TextField()
    areas_of_improvement = models.TextField()
    next_review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_performance_review'

class Goal(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ])
    progress = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_goal'

class LeaveRequest(models.Model):
    eId = models.CharField(max_length=20)
    leave_type = models.CharField(max_length=20, choices=[
        ('ANNUAL', 'Annual Leave'),
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual Leave'),
        ('MATERNITY', 'Maternity Leave'),
        ('PATERNITY', 'Paternity Leave'),
        ('UNPAID', 'Unpaid Leave')
    ], default='ANNUAL')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    reason = models.TextField(default='')
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ], default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_leave_request'

    def __str__(self):
        return f"{self.eId} - {self.leave_type} ({self.start_date} to {self.end_date})"

class TrainingProgram(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.IntegerField()
    enrolled_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('UPCOMING', 'Upcoming'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_training_program'

class TrainingTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'employee_training_tag'

class TrainingBlog(models.Model):
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='blogs')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.ManyToManyField(TrainingTag, related_name='blogs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.program.title}"

    class Meta:
        db_table = 'employee_training_blog'
        ordering = ['-created_at']

class TrainingDocument(models.Model):
    blog = models.ForeignKey(TrainingBlog, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='training_documents/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'employee_training_document'

class TrainingEnrollment(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('ENROLLED', 'Enrolled'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped')
    ])
    completion_date = models.DateField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_training_enrollment'

class Payroll(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    month = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid')
    ])
    payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_payroll' 

class ProfileUpdateRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_update_requests')
    proposed_changes = models.JSONField()  # Use JSONField for SQLite 3.9+ and Django 3.1+
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profile_update_reviews')
    review_comments = models.TextField(blank=True)
    allow_edit = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.eID} - {self.status}" 

PROJECT_STATUS_CHOICES = [
    ('ONGOING', 'Ongoing'),
    ('AT_RISK', 'At Risk'),
    ('UPCOMING', 'Upcoming'),
    ('ON_SCHEDULE', 'On Schedule'),
    ('COMPLETED', 'Completed'),
]

class Project(models.Model):
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='ONGOING')
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    employees = models.ManyToManyField('Employee', related_name='projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})" 

class EmployeeInformation(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    title = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    joining_date = models.DateField()
    employment_type_at_hiring = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    full_time_conversion_date = models.DateField(null=True, blank=True)
    exit_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.eID} - {self.employee.firstName}"

class IDCard(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    title = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=10)
    address = models.TextField()

    def __str__(self):
        return f"{self.employee.eID} - {self.employee.firstName}"

class WiFiAccess(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    mobile_number = models.CharField(max_length=10)
    access_card_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.employee.eID} - {self.employee.firstName}"

class ParkingDetails(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    parking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    vehicle_number_plate = models.CharField(max_length=20)
    vehicle_make = models.CharField(max_length=20, choices=VEHICLE_MAKE_CHOICES)
    vehicle_year = models.IntegerField()
    vehicle_color = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.employee.eID} - {self.employee.firstName}"

class InsuranceDetails(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    mobile_number = models.CharField(max_length=10)
    insured_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    reason_for_leaving = models.TextField(null=True, blank=True)
    sum_insured = models.DecimalField(max_digits=12, decimal_places=2)
    endorsement_type = models.CharField(max_length=1, choices=ENDORSEMENT_TYPE_CHOICES)
    critical_illness_maternity = models.BooleanField(default=False)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.eID} - {self.employee.firstName}" 

PROVIDER_CHOICES = [
    ('gmail', 'Gmail/Google Workspace'),
    ('office365', 'Outlook/Office365'),
    ('zoho', 'Zoho Mail'),
    ('sendgrid', 'SendGrid'),
    ('ses', 'Amazon SES'),
    ('other', 'Other'),
]

class EmailSettings(models.Model):
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES, default='other')
    EMAIL_BACKEND = models.CharField(max_length=255, default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = models.CharField(max_length=255, default='smtp.office365.com')
    EMAIL_PORT = models.PositiveIntegerField(default=587)
    EMAIL_USE_TLS = models.BooleanField(default=True)
    EMAIL_HOST_USER = models.EmailField()
    EMAIL_HOST_PASSWORD = models.CharField(max_length=255)
    DEFAULT_FROM_EMAIL = models.EmailField()

    def __str__(self):
        return f"SMTP: {self.EMAIL_HOST_USER} ({self.get_provider_display()})" 

class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Asset Categories"

class Asset(models.Model):
    CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('DAMAGED', 'Damaged'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ASSIGNED', 'Assigned'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('RETIRED', 'Retired'),
    ]

    asset_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='NEW')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset_id} - {self.name}"

class AssetAssignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    assigned_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.PROTECT)
    assignment_notes = models.TextField(blank=True)
    return_notes = models.TextField(blank=True)
    is_returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset} assigned to {self.employee}"

    def save(self, *args, **kwargs):
        if not self.is_returned:
            self.asset.status = 'ASSIGNED'
        else:
            self.asset.status = 'AVAILABLE'
        self.asset.save()
        super().save(*args, **kwargs) 

class BankDetail(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=50)
    ifsc = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName}'s Bank Details"

class InsurancePolicy(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    policy_number = models.CharField(max_length=50)
    provider = models.CharField(max_length=100)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    expiry_date = models.DateField()
    
    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName}'s Insurance"

class TaxDetail(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    pan_number = models.CharField(max_length=10)
    tax_regime = models.CharField(max_length=20, choices=[('OLD', 'Old Regime'), ('NEW', 'New Regime')])
    tax_declarations = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName}'s Tax Details"

class PersonalDetail(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName}'s Personal Details" 