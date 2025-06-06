from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Clean up duplicate social applications and ensure correct configuration'

    def handle(self, *args, **options):
        # Get or create the default site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'Local Development'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created default site'))

        # Delete all existing Microsoft social apps
        SocialApp.objects.filter(provider='microsoft').delete()
        self.stdout.write(self.style.SUCCESS('Deleted existing Microsoft social apps'))

        # Create new Microsoft social app
        social_app = SocialApp.objects.create(
            provider='microsoft',
            name='Employee Management App',
            client_id='4b4a2fc8-31b1-4df1-a06d-49dab8795c3b',
            secret='PTf8Q~hN2DiZU3KzPqn4Zs9UOqijrqNqGAujkcEO'
        )
        social_app.sites.add(site)
        self.stdout.write(self.style.SUCCESS('Created new Microsoft social app')) 