import os
import jwt
from django.test import SimpleTestCase, override_settings

from .lib import verify_activation_token, get_machine_hash


class RS256ActivationTest(SimpleTestCase):
    def test_rs256_activation_with_dev_key(self):
        # locate dev private/public keys committed for developer testing
        base = os.path.dirname(__file__)
        priv_path = os.path.join(base, 'keys', 'dev_private.pem')
        pub_path = os.path.join(base, 'keys', 'dev_public.pem')
        if not os.path.exists(priv_path) or not os.path.exists(pub_path):
            self.skipTest('dev RSA keypair not present')

        priv_pem = open(priv_path, 'rb').read()
        pub_pem = open(pub_path, 'rb').read()

        payload = {
            'tenant_id': '00000000-0000-0000-0000-000000000002',
            'machine_hash': get_machine_hash(),
            'features': {'pro': False}
        }
        try:
            token = jwt.encode(payload, priv_pem, algorithm='RS256')
        except Exception as e:
            # Likely cryptography not installed or key parse error
            self.skipTest(f'Cannot encode RS256 token in this environment: {e}')

        # run verification with settings patched to use RS256 and the dev public key
        with override_settings(LICENSE_TOKEN_ALGORITHM='RS256', LICENSE_PUBLIC_KEY=pub_pem.decode('utf-8')):
            decoded = verify_activation_token(token, expected_machine_hash=payload['machine_hash'])

        self.assertEqual(decoded['tenant_id'], payload['tenant_id'])
        self.assertEqual(decoded['machine_hash'], payload['machine_hash'])