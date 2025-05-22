# API Guide

## Overview

This project provides a REST API for integration with other systems, mobile apps, or external services. The API is documented and browsable via Swagger/OpenAPI.

## API Documentation

- Visit `/ems/api/docs/` (login required) for interactive API docs (Swagger UI).

## Endpoints

- `/ems/api/employees/` — List all employees (GET)
- `/ems/api/employees/{eID}/` — Retrieve a single employee (GET)
- `/ems/api/projects/` — List all projects (GET)
- `/ems/api/projects/{id}/` — Retrieve a single project (GET)

## Authentication
- All API endpoints require authentication (login via the web UI first).
- You can use session authentication for browser-based API exploration.

## Example Usage

- To get all employees:
  ```bash
  curl -b cookies.txt http://localhost:8000/ems/api/employees/
  ```
- To get all projects:
  ```bash
  curl -b cookies.txt http://localhost:8000/ems/api/projects/
  ```

## Extending the API
- Add more endpoints or permissions as needed using Django REST Framework.
- See [DRF docs](https://www.django-rest-framework.org/) for more. 