# Deployment Guide

## Environment Variables

This project uses [python-decouple](https://github.com/henriquebastos/python-decouple) to manage sensitive settings via environment variables. This is more secure and production-ready than hardcoding secrets in your code.

### 1. Create a `.env` file in your project root:

```
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,127.0.0.1,localhost

# Database settings (for production, e.g. PostgreSQL)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

- **Never commit your `.env` file to version control!**
- Use `.env.example` as a template for new environments.

### 2. Install dependencies

```
pip install python-decouple
```

### 3. Configure your server
- Set environment variables as needed for your deployment (e.g., using Docker, Heroku, or your own server).
- Make sure `DEBUG=False` and `ALLOWED_HOSTS` is set to your domain(s).

### 4. Collect static files

```
python manage.py collectstatic
```

### 5. Run migrations

```
python manage.py migrate
```

### 6. Start your server (e.g., gunicorn, uwsgi, or Django's runserver for testing)

```
gunicorn empmanagement.wsgi:application
```

---

For more details, see the Django deployment checklist: https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/ 