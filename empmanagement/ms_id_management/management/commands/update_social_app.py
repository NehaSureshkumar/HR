from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings

class Command(BaseCommand):
    help = 'Updates the Microsoft social application configuration'

    def handle(self, *args, **options):
        # First, delete any existing sites
        Site.objects.all().delete()
        
        # Create new site
        site = Site.objects.create(
            id=settings.SITE_ID,
            domain='localhost:8000',
            name='Local Development'
        )
        self.stdout.write(self.style.SUCCESS('Created new site configuration'))

        # Delete existing Microsoft apps
        SocialApp.objects.filter(provider='microsoft').delete()
        self.stdout.write(self.style.SUCCESS('Deleted existing Microsoft apps'))

        # Create new app
        social_app = SocialApp.objects.create(
            provider='microsoft',
            name='Employee Management App',
            client_id=settings.MS_GRAPH_CLIENT_ID,
            secret=settings.MS_GRAPH_CLIENT_SECRET
        )
        social_app.sites.add(site)
        self.stdout.write(self.style.SUCCESS('Created new Microsoft app with localhost configuration'))

        # Print configuration for verification
        self.stdout.write('\nCurrent Configuration:')
        self.stdout.write(f'Site Domain: {site.domain}')
        self.stdout.write(f'Client ID: {social_app.client_id}')
        self.stdout.write(f'Callback URL: {settings.SOCIALACCOUNT_PROVIDERS["microsoft"]["CALLBACK_URL"]}') 