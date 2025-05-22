# Docker Guide

## Overview

This project supports Docker for easy local development and deployment. Docker ensures consistency across environments and simplifies onboarding for new developers.

## Prerequisites
- [Docker](https://www.docker.com/get-started) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

## Quick Start

### 1. Build and run with Docker Compose

```bash
docker-compose up --build
```

- The Django app will be available at [http://localhost:8000](http://localhost:8000)
- The Postgres database will be available at port 5432

### 2. Stopping the containers

```bash
docker-compose down
```

### 3. Running management commands

You can run Django management commands inside the running container:

```bash
docker-compose run web python manage.py migrate
```

### 4. Environment Variables

- Copy `.env.example` to `.env` and set your secrets and database settings.
- For Docker Compose, use:
  ```env
  SECRET_KEY=your-secret-key
  DEBUG=False
  ALLOWED_HOSTS=localhost,127.0.0.1
  DB_ENGINE=django.db.backends.postgresql
  DB_NAME=empdb
  DB_USER=empuser
  DB_PASSWORD=emppass
  DB_HOST=db
  DB_PORT=5432
  ```

## Notes
- Static files are collected automatically during the build.
- For production, use a production-ready database and web server setup.

---

For more, see the [official Django Docker docs](https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/#deploying-with-docker) 