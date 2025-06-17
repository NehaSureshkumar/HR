from django.core.management.base import BaseCommand
from django.core.management.commands.runserver import Command as RunserverCommand

class Command(BaseCommand):
    help = 'Runs the development server on localhost (for SSO) or 0.0.0.0 (for LAN access)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lan',
            action='store_true',
            help='Bind to 0.0.0.0:8000 to allow LAN access',
        )

    def handle(self, *args, **options):
        # Decide binding address based on --lan flag
        if options['lan']:
            self.stdout.write(self.style.SUCCESS("Starting server on 0.0.0.0:8000 (LAN mode)"))
            options['addrport'] = '0.0.0.0:8000'
        else:
            self.stdout.write(self.style.SUCCESS("Starting server on localhost:8000 (Azure SSO mode)"))
            options['addrport'] = 'localhost:8000'

        # Standard Django options
        options['use_reloader'] = True
        options['use_threading'] = True
        options['use_ipv6'] = False
        options['insecure'] = True

        # Start the server
        RunserverCommand().handle(*args, **options)
