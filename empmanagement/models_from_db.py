# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EmployeeAuditlog(models.Model):
    id = models.BigAutoField(primary_key=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    details = models.TextField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'employee_auditlog'


class EmployeeDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    document_type = models.CharField(max_length=20)
    file = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    uploaded_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    comments = models.TextField()
    employee = models.ForeignKey('EmployeeEmployee', models.DO_NOTHING)
    verified_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_document'


class EmployeeEmployee(models.Model):
    eid = models.CharField(db_column='eID', primary_key=True, max_length=20)  # Field name made lowercase.
    firstname = models.CharField(db_column='firstName', max_length=50)  # Field name made lowercase.
    middlename = models.CharField(db_column='middleName', max_length=50)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=50)  # Field name made lowercase.
    phoneno = models.CharField(db_column='phoneNo', unique=True, max_length=12)  # Field name made lowercase.
    email = models.CharField(unique=True, max_length=70)
    addharno = models.CharField(db_column='addharNo', unique=True, max_length=20)  # Field name made lowercase.
    dob = models.DateField(db_column='dOB')  # Field name made lowercase.
    designation = models.CharField(max_length=50)
    salary = models.CharField(max_length=20)
    joindate = models.DateField(db_column='joinDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'employee_employee'


class EmployeeJobopening(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    description = models.TextField()
    requirements = models.TextField()
    status = models.CharField(max_length=20)
    positions = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_jobopening'


class EmployeeNotice(models.Model):
    id = models.CharField(db_column='Id', primary_key=True, max_length=20)  # Field name made lowercase.
    title = models.CharField(max_length=250)
    description = models.TextField()
    publishdate = models.DateTimeField(db_column='publishDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'employee_notice'


class EmployeeOnboarding(models.Model):
    id = models.BigAutoField(primary_key=True)
    start_date = models.DateField()
    status = models.CharField(max_length=20)
    documents_submitted = models.BooleanField()
    documents_verified = models.BooleanField()
    personal_info_completed = models.BooleanField()
    emergency_contact_provided = models.BooleanField()
    bank_details_provided = models.BooleanField()
    pf_details_provided = models.BooleanField()
    insurance_enrolled = models.BooleanField()
    email_setup = models.BooleanField()
    system_access_granted = models.BooleanField()
    orientation_completed = models.BooleanField()
    training_materials_provided = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    notes = models.TextField()
    employee = models.OneToOneField(EmployeeEmployee, models.DO_NOTHING)
    hr_assigned = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    job_opening = models.ForeignKey(EmployeeJobopening, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_onboarding'


class EmployeeRequests(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_0 = models.CharField(db_column='Id', max_length=20)  # Field name made lowercase. Field renamed because of name conflict.
    requestmessage = models.TextField(db_column='requestMessage')  # Field name made lowercase.
    requestdate = models.DateTimeField(db_column='requestDate')  # Field name made lowercase.
    destinationemployeeid = models.ForeignKey(EmployeeEmployee, models.DO_NOTHING, db_column='destinationEmployeeId_id')  # Field name made lowercase.
    requesterid = models.ForeignKey(EmployeeEmployee, models.DO_NOTHING, db_column='requesterId_id', related_name='employeerequests_requesterid_set')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'employee_requests'


class EmployeeUserprofile(models.Model):
    id = models.BigAutoField(primary_key=True)
    role = models.CharField(max_length=20)
    profile_completion = models.IntegerField()
    is_active = models.BooleanField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    pf_number = models.CharField(max_length=20)
    bank_account_number = models.CharField(max_length=30)
    bank_ifsc = models.CharField(max_length=20)
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'employee_userprofile'


class EmployeeWorkassignments(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_0 = models.CharField(db_column='Id', max_length=20)  # Field name made lowercase. Field renamed because of name conflict.
    work = models.TextField()
    assigndate = models.DateTimeField(db_column='assignDate')  # Field name made lowercase.
    duedate = models.DateTimeField(db_column='dueDate')  # Field name made lowercase.
    assignerid = models.ForeignKey(EmployeeEmployee, models.DO_NOTHING, db_column='assignerId_id')  # Field name made lowercase.
    taskerid = models.ForeignKey(EmployeeEmployee, models.DO_NOTHING, db_column='taskerId_id', related_name='employeeworkassignments_taskerid_set')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'employee_workassignments'
