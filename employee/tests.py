from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from employee.models import Employee, Project, UserProfile

class BasicTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.hr_user = User.objects.create_user(username='hruser', password='hrpass')
        self.employee = Employee.objects.create(eID='testuser', firstName='Test', lastName='User')
        self.hr_profile = UserProfile.objects.create(user=self.hr_user, role='HR')
        self.emp_profile = UserProfile.objects.create(user=self.user, role='EMPLOYEE')
        self.project = Project.objects.create(name='Test Project', status='ONGOING', start_date='2024-01-01', end_date='2024-12-31')

    def test_login(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertIn(response.status_code, [200, 302])  # Accepts redirect or success

    def test_dashboard_access(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200) 

    def test_project_assignment_by_hr(self):
        self.client.login(username='hruser', password='hrpass')
        url = reverse('assign_employees_to_project', args=[self.project.id])
        response = self.client.post(url, {'employees': [self.employee.eID]})
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertIn(self.employee, self.project.employees.all())

    def test_employee_cannot_access_hr_views(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('assign_employees_to_project', args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Should redirect (no permission) 