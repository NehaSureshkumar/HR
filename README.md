# Employee Management System

A comprehensive web-based Employee Management System built with Django that helps organizations manage their workforce efficiently.

## Features

- **User Authentication**
  - Secure login/logout functionality
  - User registration
  - Password reset capabilities

- **Employee Management**
  - Add, edit, and delete employee records
  - View employee details
  - Track employee information
  - Manage employee documents
  - Assign employees to projects (with project count on dashboard and work page)

- **Dashboard**
  - Overview of key metrics
  - Quick access to important functions
  - Employee statistics
  - Assigned Projects stat card (NEW)

- **Work & Projects**
  - Employees see assigned projects on both dashboard and "My Work" page
  - HR/Admin can assign employees to projects

## Technology Stack

- **Backend**: Django 4.0+
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Database**: SQLite (default)
- **Authentication**: Django Allauth
- **Additional Packages**:
  - django-crispy-forms
  - Pillow (for image handling)

## Installation

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd empmanagement
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
empmanagement/
├── empmanagement/          # Project settings
├── employee/              # Employee management app (all business logic)
├── accounts/              # User authentication app
├── static/                # Static files (css, js, images)
│   ├── css/               # CSS files (style.css, hr_dashboard.css, ...)
│   ├── js/                # JavaScript files
│   └── ...
├── media/                 # User-uploaded files
├── templates/             # HTML templates
│   ├── employee/          # All employee and HR/admin templates
│   └── admin/             # Django admin customizations
├── docs/                  # Documentation, deployment, and integration guides
└── README.md
```

## Deployment & Integration

- **Static Files**: Place static files in the `static/` directory. Use subfolders for organization (e.g., `css/`, `js/`).
- **Templates**: All templates are in `templates/employee/` for both employee and HR/admin features. You can further split if needed.
- **Docs**: See the `docs/` folder for deployment, integration, and onboarding guides.
- **Settings**: Update `ALLOWED_HOSTS`, database, and email settings in `empmanagement/settings.py` for production.
- **Collect Static**: Run `python manage.py collectstatic` before deploying to production.

## Recent Updates

- Unified project assignment and display for employees and HR/admins
- Assigned Projects stat card on dashboard and "My Work" page
- Modernized UI with Tailwind CSS
- Improved folder structure for easier deployment and integration

## Important URLs

- **Admin Interface**: http://127.0.0.1:8000/admin/
- **Login Page**: http://127.0.0.1:8000/ems/accounts/login/
- **Dashboard**: http://127.0.0.1:8000/ems/dashboard/
  // **Employee List**: http://127.0.0.1:8000/ems/employees/

## Configuration

The project uses the following key settings:

```python
# Authentication Settings
LOGIN_URL = '/ems/accounts/login/'
LOGIN_REDIRECT_URL = '/ems/dashboard/'
LOGOUT_REDIRECT_URL = '/ems/accounts/login/'

# Email Settings (Development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ACCOUNT_EMAIL_VERIFICATION = 'none'
```

## Development

1. **Static Files**
   - Place static files in the `static/` directory
   - Run `python manage.py collectstatic` to collect static files

2. **Media Files**
   - User-uploaded files are stored in the `media/` directory
   - Configured to serve media files in development

3. **Database**
   - Uses SQLite by default
   - Can be configured to use other databases in `settings.py`

## Docker

This project supports Docker for easy local development and deployment. See [docs/DOCKER.md](docs/DOCKER.md) for full instructions.

- To build and run with Docker Compose:
  ```bash
  docker-compose up --build
  ```
- To stop:
  ```bash
  docker-compose down
  ```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Support

For support, please [contact details or issue tracker information]

## Testing

Automated tests are provided for core features (login, dashboard, project assignment, role-based access). All tests run automatically on every push and pull request via GitHub Actions CI.

- To run tests locally:
  ```bash
  python manage.py test
  ```
- See [docs/TESTING.md](docs/TESTING.md) for details and how to add more tests.

## API

A REST API is available for integration and automation. See [docs/API.md](docs/API.md) for details.

- Interactive API docs: `/ems/api/docs/` (login required)
- Endpoints for employees and projects (read-only by default)

## Documentation

- [User Manual](docs/USER_MANUAL.md): How to use the system (for employees and HR/admins)
- [API Guide](docs/API.md): REST API endpoints and usage
- [Testing Guide](docs/TESTING.md): How to run and add tests
- [Docker Guide](docs/DOCKER.md): Running the project with Docker
- [Production Checklist](docs/PRODUCTION.md): Secure deployment steps
- [Changelog](CHANGELOG.md): Track all major changes and releases

## Monitoring & Backups
- For production, integrate [Sentry](https://sentry.io/) or another error monitoring tool (see docs/PRODUCTION.md)
- Set up regular database and media backups 
