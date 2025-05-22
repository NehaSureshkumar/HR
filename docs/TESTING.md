# Testing Guide

## Overview

This project uses Django's built-in test framework to ensure reliability and prevent regressions. Automated tests are run on every push and pull request via GitHub Actions (see `.github/workflows/django.yml`).

## Running Tests Locally

To run all tests:

```bash
python manage.py test
```

## What's Covered
- User login/logout
- Dashboard access for employees
- Project assignment by HR
- Role-based access control (employees cannot access HR-only views)

## Adding More Tests
- Add new test cases to `employee/tests.py` or create new `tests.py` files in other apps.
- Use Django's `TestCase` class and the test client for simulating requests.
- Cover new features, bug fixes, and edge cases as your project grows.

## Continuous Integration
- All tests are run automatically on GitHub via the workflow in `.github/workflows/django.yml`.
- The build will fail if any test fails, helping you catch issues early.

## Resources
- [Django Testing Docs](https://docs.djangoproject.com/en/4.0/topics/testing/)
- [Writing and running tests](https://docs.djangoproject.com/en/4.0/topics/testing/overview/) 