from tkinter import Widget
from django import forms
from .models import workAssignments, Requests, Document, Employee, UserProfile

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