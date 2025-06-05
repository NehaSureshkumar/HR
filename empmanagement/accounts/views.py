from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from employee.models import UserProfile, Employee
from django.contrib.auth.decorators import login_required
from django.utils import timezone

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Create UserProfile if it doesn't exist
            try:
                user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # Check if user is superuser
                if user.is_superuser:
                    user_profile = UserProfile.objects.create(
                        user=user,
                        role='ADMIN',
                        profile_completion=100
                    )
                else:
                    # Check if user is an employee
                    try:
                        employee = Employee.objects.get(eID=user.username)
                        user_profile = UserProfile.objects.create(
                            user=user,
                            role='EMPLOYEE',
                            profile_completion=0
                        )
                    except Employee.DoesNotExist:
                        messages.error(request, "Employee profile not found.")
                        logout(request)
                        return redirect('login_user')
            
            # Get the next URL from the request
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Redirect based on user role
            if user_profile.role in ['ADMIN', 'HR']:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('login_user')
    
    return render(request, 'accounts/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')
        
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(
            user=user,
            role='EMPLOYEE',
            profile_completion=0
        )
        
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login_user')
    
    return render(request, 'accounts/signup.html')

@login_required
def profile_completion(request):
    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        employee = Employee.objects.get(eID=request.user.username)
        
        # Update employee info
        employee.phoneNo = request.POST.get('phone')
        employee.email = request.POST.get('email')
        employee.save()
        
        # Update profile info
        user_profile.emergency_contact_name = request.POST.get('emergency_contact_name')
        user_profile.emergency_contact_phone = request.POST.get('emergency_contact_phone')
        user_profile.bank_account_number = request.POST.get('bank_account')
        user_profile.bank_ifsc = request.POST.get('ifsc')
        
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
        return redirect('dashboard')
        
    return render(request, 'accounts/profile_completion.html')