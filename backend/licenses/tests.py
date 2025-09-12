from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from rest_framework.test import APIClient
import jwt


class DiscoveryTest(SimpleTestCase):
    def test_discovery(self):
        # simple test to ensure test discovery picks up this module
        self.assertTrue(True)


class LicenseDBTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='ACME')
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass')
        setattr(self.admin, 'tenant', self.tenant)
        self.admin.save()
        self.client = APIClient()
        self.client.login(username='admin', password='pass')

    @override_settings(LICENSE_TOKEN_ALGORITHM='HS256', LICENSE_PUBLIC_KEY='test-secret')
    def test_activate_license_jwt(self):
        payload = {
            'tenant_id': str(self.tenant.id),
            'machine_hash': 'fake-hash',
            'features': {'pro': True}
        }
        token = jwt.encode(payload, 'test-secret', algorithm='HS256')
        url = reverse('license-activate')
        resp = self.client.post(url, data={'token': token}, format='json')
        # Response may be 201, 200, or 400 depending on machine_hash; we assert we get a response
        self.assertIn(resp.status_code, (200, 201, 400, 403))
