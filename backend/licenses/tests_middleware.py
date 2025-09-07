from django.test import TestCase, override_settings, RequestFactory
from django.contrib.auth import get_user_model

from tenants.models import Tenant
from .models import License
from .middleware import LicenseEnforceMiddleware


User = get_user_model()


class LicenseMiddlewareTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='MidTenant')
        self.user = User.objects.create_user(username='tm', password='pass', tenant=self.tenant)
        # Use RequestFactory to create realistic HttpRequest objects for middleware
        self.rf = RequestFactory()
        # MiddlewareMixin requires a get_response callable on construction
        # Provide a simple callable that returns a minimal HttpResponse when needed.
        self.middleware = LicenseEnforceMiddleware(get_response=lambda req: None)

    def _req(self, path='/', user=None):
        req = self.rf.get(path)
        # Ensure request.path and path_info are set for middleware checks
        req.path = path
        req.path_info = path
        # Ensure user is attached (RequestFactory doesn't run auth middleware), so attach directly
        req.user = user
        return req

    def test_unauthenticated_skips(self):
        req = self._req('/', user=None)
        res = self.middleware.process_request(req)
        self.assertIsNone(res)

    def test_block_when_no_active_license(self):
        # ensure no license exists for this tenant
        License.objects.filter(tenant=self.tenant).delete()
        req = self._req('/protected', user=self.user)
        import logging
        logger = logging.getLogger('licenses.middleware')
        with self.assertLogs('licenses.middleware', level='DEBUG') as cm:
            logger.debug('test debug: user=%r is_authenticated=%r tenant_id=%r license_exists=%s',
                         self.user, getattr(self.user, 'is_authenticated', None), getattr(self.user, 'tenant_id', None),
                         License.objects.filter(tenant=self.tenant).exists())
            res = self.middleware.process_request(req)
        self.assertIsNotNone(res)
        self.assertEqual(res.status_code, 402)
        # ensure middleware logged the blocking reason
        logs = '\n'.join(cm.output)
        self.assertIn('no License row', logs)

    def test_allow_when_active_license(self):
        License.objects.create(tenant=self.tenant, status='active', license_key='abc')
        req = self._req('/', user=self.user)
        res = self.middleware.process_request(req)
        self.assertIsNone(res)

    @override_settings(LICENSE_ENFORCE_EXEMPT_PATHS=['/custom-exempt'])
    def test_exempt_path_settings(self):
        req = self._req('/custom-exempt/endpoint', user=self.user)
        res = self.middleware.process_request(req)
        # exempt path should skip enforcement even without license
        self.assertIsNone(res)

    def test_admin_skip(self):
        # admin path should be exempt by default
        req = self._req('/admin/login', user=self.user)
        res = self.middleware.process_request(req)
        self.assertIsNone(res)

    @override_settings(STATIC_URL='/static/', MEDIA_URL='/media/')
    def test_static_media_skip(self):
        req = self._req('/static/app.js', user=self.user)
        res = self.middleware.process_request(req)
        self.assertIsNone(res)
        req2 = self._req('/media/upload.png', user=self.user)
        res2 = self.middleware.process_request(req2)
        self.assertIsNone(res2)
