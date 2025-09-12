import json
from django.core.management.base import BaseCommand
from pathlib import Path
import jwt


class Command(BaseCommand):
    help = 'Sign an activation payload for a given tenant_id using the dev RSA private key (local only)'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id')

    def handle(self, *args, **options):
        tenant_id = options['tenant_id']
        payload = {
            'tenant_id': str(tenant_id),
        }
        key_path = Path(__file__).resolve().parents[3] / 'keys' / 'dev_private.pem'
        priv = key_path.read_text()
        token = jwt.encode(payload, priv, algorithm='RS256')
        self.stdout.write(token)
