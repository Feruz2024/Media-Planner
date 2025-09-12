import hashlib
import json
import os
from django.conf import settings
import jwt
from jwt import InvalidTokenError


def get_machine_hash():
    """Return a stable machine hash stored in a file under the project data dir.
    This is a simple placeholder: in production you may derive from host identifiers.
    """
    data_dir = getattr(settings, 'DATA_DIR', None) or os.path.join(settings.BASE_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, 'machine_id')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    # generate and persist
    random = os.urandom(32)
    with open(path, 'wb') as f:
        f.write(random)
    return hashlib.sha256(random).hexdigest()


def verify_activation_token(token: str, expected_machine_hash: str | None = None) -> dict:
    """Verify a JWT activation token.

    Supports HS256 (using LICENSE_PUBLIC_KEY as secret for tests) and RS256 (using public key).
    Returns the decoded payload or raises ValueError.
    """
    algo = getattr(settings, 'LICENSE_TOKEN_ALGORITHM', 'HS256')
    key_setting = getattr(settings, 'LICENSE_PUBLIC_KEY', None)

    # If settings contains a path to a key file, prefer reading the file.
    key = None
    if key_setting:
        # treat as file path if it looks like one
        if isinstance(key_setting, str) and os.path.exists(key_setting):
            with open(key_setting, 'r', encoding='utf-8') as f:
                key = f.read()
        else:
            key = key_setting

    try:
        if algo.upper().startswith('HS'):
            # symmetric: public key setting is used as shared secret in tests/environments
            secret = key or ''
            payload = jwt.decode(token, secret, algorithms=[algo])
        else:
            # asymmetric: require public key (PEM)
            if not key:
                raise ValueError('Public key not configured for asymmetric verification')
            payload = jwt.decode(token, key, algorithms=[algo])
    except InvalidTokenError as e:
        raise ValueError('Invalid token') from e

    # check machine hash if provided
    mh = payload.get('machine_hash')
    if expected_machine_hash and mh and mh != expected_machine_hash:
        raise ValueError('Machine hash mismatch')

    if 'tenant_id' not in payload:
        raise ValueError('Missing tenant_id')

    return payload
