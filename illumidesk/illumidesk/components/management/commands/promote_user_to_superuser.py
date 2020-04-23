from django.core.management.base import BaseCommand, CommandError
from illumidesk.users.models import IllumiDeskUser


class Command(BaseCommand):
    help = 'Promotes the given user to a superuser and provides admin access.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, username, **options):
        try:
            user = IllumiDeskUser.objects.get(username=username)
        except IllumiDeskUser.DoesNotExist:
            raise CommandError('No user with username/email {} found!'.format(username))
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print('{} successfully promoted to superuser and can now access the admin site'.format(username))
