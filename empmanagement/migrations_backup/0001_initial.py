# Generated by Django 5.2.1 on 2025-05-15 06:07

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_start_time', models.TimeField(default='09:00')),
                ('work_end_time', models.TimeField(default='17:00')),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('location', models.CharField(default='Main Office', max_length=100)),
                ('allow_remote', models.BooleanField(default=False)),
                ('grace_period_minutes', models.IntegerField(default=15)),
                ('weekend_days', models.CharField(default='6,7', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('eID', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('firstName', models.CharField(max_length=50)),
                ('middleName', models.CharField(max_length=50)),
                ('lastName', models.CharField(max_length=50)),
                ('phoneNo', models.CharField(max_length=12, unique=True)),
                ('email', models.EmailField(max_length=70, unique=True)),
                ('addharNo', models.CharField(max_length=20, unique=True)),
                ('dOB', models.DateField()),
                ('designation', models.CharField(choices=[('Team Leader', 'Team Leader'), ('Project Manager', 'Project Manager'), ('Senior Developer', 'Senior Developer'), ('Junior Developer', 'Junior Developer'), ('Intern', 'Intern'), ('QA Tester', 'QA Tester')], max_length=50)),
                ('salary', models.CharField(max_length=20)),
                ('joinDate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('Id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('publishDate', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('PAN', 'PAN Card'), ('AADHAR', 'Aadhar Card'), ('PASSPORT', 'Passport'), ('BANK', 'Bank Documents'), ('PF', 'PF Documents'), ('OTHER', 'Other')], max_length=20)),
                ('file', models.FileField(upload_to='employee_documents/')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('comments', models.TextField(blank=True)),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
            ],
        ),
        migrations.CreateModel(
            name='JobOpening',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('department', models.CharField(choices=[('Team Leader', 'Team Leader'), ('Project Manager', 'Project Manager'), ('Senior Developer', 'Senior Developer'), ('Junior Developer', 'Junior Developer'), ('Intern', 'Intern'), ('QA Tester', 'QA Tester')], max_length=50)),
                ('description', models.TextField()),
                ('requirements', models.TextField()),
                ('status', models.CharField(choices=[('OPEN', 'Open'), ('CLOSED', 'Closed'), ('ON_HOLD', 'On Hold')], default='OPEN', max_length=20)),
                ('positions', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Onboarding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('DELAYED', 'Delayed')], default='PENDING', max_length=20)),
                ('documents_submitted', models.BooleanField(default=False)),
                ('documents_verified', models.BooleanField(default=False)),
                ('personal_info_completed', models.BooleanField(default=False)),
                ('emergency_contact_provided', models.BooleanField(default=False)),
                ('bank_details_provided', models.BooleanField(default=False)),
                ('pf_details_provided', models.BooleanField(default=False)),
                ('insurance_enrolled', models.BooleanField(default=False)),
                ('email_setup', models.BooleanField(default=False)),
                ('system_access_granted', models.BooleanField(default=False)),
                ('orientation_completed', models.BooleanField(default=False)),
                ('training_materials_provided', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('employee', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
                ('hr_assigned', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hr_onboardings', to=settings.AUTH_USER_MODEL)),
                ('job_opening', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='employee.jobopening')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Id', models.CharField(max_length=20)),
                ('requestMessage', models.TextField()),
                ('requestDate', models.DateTimeField()),
                ('destinationEmployeeId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='toEmployeeId', to='employee.employee')),
                ('requesterId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requesterId', to='employee.employee')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('HR', 'HR'), ('EMPLOYEE', 'Employee')], default='EMPLOYEE', max_length=20)),
                ('profile_completion', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('emergency_contact_name', models.CharField(blank=True, max_length=100)),
                ('emergency_contact_phone', models.CharField(blank=True, max_length=15)),
                ('pf_number', models.CharField(blank=True, max_length=20)),
                ('bank_account_number', models.CharField(blank=True, max_length=30)),
                ('bank_ifsc', models.CharField(blank=True, max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='workAssignments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Id', models.CharField(max_length=20)),
                ('work', models.TextField()),
                ('assignDate', models.DateTimeField()),
                ('dueDate', models.DateTimeField()),
                ('assignerId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignerId', to='employee.employee')),
                ('taskerId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taskerId', to='employee.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('clock_in', models.DateTimeField(blank=True, null=True)),
                ('clock_out', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PRESENT', 'Present'), ('ABSENT', 'Absent'), ('LATE', 'Late'), ('HALF_DAY', 'Half Day'), ('ON_LEAVE', 'On Leave')], default='ABSENT', max_length=20)),
                ('work_hours', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('location', models.CharField(default='Office', max_length=100)),
                ('is_remote', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
            ],
            options={
                'ordering': ['-date', 'employee'],
                'unique_together': {('employee', 'date')},
            },
        ),
    ]
