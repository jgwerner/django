from django.db import transaction
from django.test import TestCase
from servers.management.commands.create_server_size import Command
from servers.models import ServerSize
from servers.tests.factories import ServerSizeFactory

class CreateServerSizeCommandTest(TestCase):

    def test_command_handle(self):
        existing_server_size = ServerSizeFactory(name="Nano",
                                                 cpu=1,
                                                 memory=512)
        cmd = Command()

        # We're also implicitly testing that the defaults work correctly
        cmd.handle()

        with transaction.atomic():
            server_size_queryset = ServerSize.objects.all()
            server_size = ServerSize.objects.get(name="Nano")

        self.assertEqual(server_size_queryset.count(), 4)

        self.assertEqual(server_size.name, "Nano")
        self.assertEqual(server_size.name, existing_server_size.name)
        self.assertEqual(server_size.cpu, existing_server_size.cpu)
        self.assertEqual(server_size.memory, existing_server_size.memory)
        self.assertTrue(server_size.active)
