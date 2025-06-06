from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Deletes a user by email address'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address of the user to delete')

    def handle(self, *args, **options):
        email = options['email']
        try:
            user = User.objects.get(email=email)
            user.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted user with email {email}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No user found with email {email}')) 