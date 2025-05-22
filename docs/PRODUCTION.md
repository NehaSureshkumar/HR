# Production Deployment Checklist

## Security
- [ ] Set `DEBUG=False` in your `.env` file
- [ ] Set a strong, unique `SECRET_KEY` in `.env`
- [ ] Set `ALLOWED_HOSTS` to your real domain(s) in `.env`
- [ ] Use HTTPS (SSL/TLS) for all traffic
- [ ] Configure secure session and CSRF cookies
- [ ] Restrict admin access to trusted IPs

## Database
- [ ] Use PostgreSQL or another production-grade database
- [ ] Set strong DB credentials in `.env`
- [ ] Automate regular database backups

## Static & Media Files
- [ ] Use WhiteNoise, S3, or Nginx for static/media file serving
- [ ] Run `python manage.py collectstatic` before deployment

## Monitoring & Logging
- [ ] Integrate Sentry or another error monitoring tool ([Sentry setup guide](https://docs.sentry.io/platforms/python/guides/django/))
- [ ] Set up logging for warnings, errors, and critical events

## Performance
- [ ] Enable Django caching (Redis/Memcached)
- [ ] Optimize database queries (use `select_related`, `prefetch_related`)

## Documentation
- [ ] Update `README.md` with deployment steps
- [ ] Maintain a `CHANGELOG.md` for releases (review regularly)
- [ ] Provide a user manual in `docs/` (review and update for new features)

## Other
- [ ] Test accessibility (screen readers, keyboard navigation)
- [ ] Add translation support if needed

---

For more, see the [Django deployment checklist](https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/) 