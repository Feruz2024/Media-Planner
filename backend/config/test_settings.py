from .settings import *

# Use in-memory SQLite for fast test runs in environments without Postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use a test license secret so HS256 tokens can be verified in tests
LICENSE_TOKEN_ALGORITHM = 'HS256'
LICENSE_PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzYd7q3+WZ1j6mZqX5eQ+
...REDACTED FOR SECURITY IN THIS EXAMPLE...
-----END PUBLIC KEY-----'''

# Reduce logging noise during tests (if LOGGING exists)
if 'LOGGING' in globals():
    LOGGING['loggers']['django']['level'] = 'WARNING'

# Allow session-based test login via APIClient.login() during tests
REST_FRAMEWORK = globals().get('REST_FRAMEWORK', {})
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
)
