from django.core.management.base import BaseCommand
from django.core.management.commands.runserver import Command as RunserverCommand

class Command(BaseCommand):
    help = 'Runs the development server with localhost binding'

    def handle(self, *args, **options):
        # Override the default host and port
        options['addrport'] = 'localhost:8000'
        options['use_reloader'] = True
        options['use_threading'] = True
        options['use_ipv6'] = False
        options['insecure'] = True
        
        # Run the server with the modified options
        RunserverCommand().handle(*args, **options) 