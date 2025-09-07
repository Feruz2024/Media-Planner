import json
from django.core.management.base import BaseCommand
from licenses.lib import get_machine_hash


class Command(BaseCommand):
    help = 'Print a JSON activation request containing tenant_id and machine_hash'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id')

    def handle(self, *args, **options):
        tenant_id = options['tenant_id']
        payload = {
            'tenant_id': str(tenant_id),
            'machine_hash': get_machine_hash(),
        }
        self.stdout.write(json.dumps(payload))
