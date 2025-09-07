from django.test import TestCase, override_settings

from .middleware import LicenseEnforceMiddleware


class PrefixNormalizationTests(TestCase):
    def setUp(self):
        # Middleware requires a callable get_response
        self.middleware = LicenseEnforceMiddleware(get_response=lambda req: None)

    @override_settings(LICENSE_ENFORCE_EXEMPT_PATHS=['/', '/health', '/api/docs'])
    def test_root_prefix_is_ignored(self):
        # When '/' is present in configured prefixes, normalization should ignore it
        # so only '/health' and '/api/docs' are treated as exempt.
        is_exempt_health = self.middleware._is_exempt_path('/health')
        is_exempt_docs = self.middleware._is_exempt_path('/api/docs/openapi')
        is_exempt_rooted = self.middleware._is_exempt_path('/protected')

        self.assertTrue(is_exempt_health)
        self.assertTrue(is_exempt_docs)
        # '/protected' should NOT be exempt just because '/' was in the config
        self.assertFalse(is_exempt_rooted)
