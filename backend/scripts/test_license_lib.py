"""Standalone script to test licenses.lib.verify_activation_token locally.

Run with DJANGO_SETTINGS_MODULE=config.test_settings to use the in-memory test settings.
"""
import os
import sys
import jwt

# Ensure the backend package root is on sys.path so local imports work when running this
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from licenses.lib import verify_activation_token, get_machine_hash


def test_hs256():
    secret = 'test-secret'
    payload = {
        'tenant_id': '00000000-0000-0000-0000-000000000001',
        'machine_hash': get_machine_hash(),
        'features': {'pro': True}
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    print('HS256 token generated')
    decoded = verify_activation_token(token, expected_machine_hash=payload['machine_hash'])
    print('HS256 decoded:', decoded)


def test_rs256():
    # generate a temporary RSA keypair using the cryptography package if available,
    # otherwise skip RS256 test
    # try to use a dev private key if present under licenses/keys/dev_private.pem
    key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'licenses', 'keys', 'dev_private.pem')
    if not os.path.exists(key_path):
        print('dev_private.pem not found, skipping RS256 test')
        return

    priv_pem = open(key_path, 'rb').read()
    payload = {
        'tenant_id': '00000000-0000-0000-0000-000000000002',
        'machine_hash': get_machine_hash(),
        'features': {'pro': False}
    }
    token = jwt.encode(payload, priv_pem, algorithm='RS256')
    # Ensure test settings include the dev public key; verify_activation_token will read it
    decoded = verify_activation_token(token, expected_machine_hash=payload['machine_hash'])
    print('RS256 decoded:', decoded)


if __name__ == '__main__':
    print('Testing license lib')
    test_hs256()
    test_rs256()
