from tkinter import Widget
from django import forms
from .models import workAssignments, Requests, Document, Employee, UserProfile, EmployeeInformation, IDCard, WiFiAccess, ParkingDetails, InsuranceDetails, TrainingBlog, TrainingDocument, TrainingProgram

class workform(forms.ModelForm):
    class Meta:
        model=workAssignments
        widgets={
            "assignDate" : forms.DateInput(attrs={'type':'datetime-local'}),
            "dueDate" : forms.DateInput(attrs={'type':'datetime-local'}),
            }
        labels={"assignerId" : "Select Your Id"}
        
        fields=[
            "assignerId",
            "work",
            "assignDate",
            "dueDate",
            "taskerId",
        ]
        
class makeRequestForm(forms.ModelForm):
    class Meta:
        model=Requests
        widgets={
            "requestDate" : forms.DateInput(attrs={'type':'datetime-local'}),
            }
        labels={"requesterId" : "Select Your Id"}
        
        fields=[
            "requesterId",
            "requestMessage",
            "requestDate",
            "destinationEmployeeId",
        ]

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['phoneNo', 'email']
        widgets = {
            'phoneNo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['emergency_contact_name', 'emergency_contact_phone', 'bank_account_number', 'bank_ifsc']
        widgets = {
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_ifsc': forms.TextInput(attrs={'class': 'form-control'})
        }

class EmployeeInformationForm(forms.ModelForm):
    class Meta:
        model = EmployeeInformation
        fields = ['title', 'status', 'employment_type', 'joining_date', 
                 'employment_type_at_hiring', 'full_time_conversion_date', 'exit_date']
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'full_time_conversion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'exit_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'employment_type_at_hiring': forms.Select(attrs={'class': 'form-control'}),
        }

class IDCardForm(forms.ModelForm):
    class Meta:
        model = IDCard
        fields = ['title', 'mobile_number', 'blood_group', 'emergency_contact_name', 
                 'emergency_contact_number', 'address']
        widgets = {
            'title': forms.Select(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{10}'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_number': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{10}'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class WiFiAccessForm(forms.ModelForm):
    class Meta:
        model = WiFiAccess
        fields = ['mobile_number', 'access_card_number']
        widgets = {
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{10}'}),
            'access_card_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ParkingDetailsForm(forms.ModelForm):
    class Meta:
        model = ParkingDetails
        fields = ['parking_status', 'vehicle_number_plate', 'vehicle_make', 
                 'vehicle_year', 'vehicle_color']
        widgets = {
            'parking_status': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_number_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_make': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2100}),
            'vehicle_color': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InsuranceDetailsForm(forms.ModelForm):
    class Meta:
        model = InsuranceDetails
        fields = ['mobile_number', 'insured_name', 'relationship', 'gender', 
                 'date_of_birth', 'date_of_joining', 'date_of_leaving', 
                 'reason_for_leaving', 'sum_insured', 'endorsement_type', 
                 'critical_illness_maternity', 'remarks']
        widgets = {
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{10}'}),
            'insured_name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_leaving': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason_for_leaving': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sum_insured': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'endorsement_type': forms.Select(attrs={'class': 'form-control'}),
            'critical_illness_maternity': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TrainingBlogForm(forms.ModelForm):
    tags = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter tags separated by commas'
    }))

    class Meta:
        model = TrainingBlog
        fields = ['title', 'content', 'tags', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        return tag_list

class TrainingDocumentForm(forms.ModelForm):
    class Meta:
        model = TrainingDocument
        fields = ['title', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model = TrainingProgram
        fields = ['title', 'description', 'start_date', 'end_date', 'capacity', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }