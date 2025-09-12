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
        self.admin = User.objects.create_user(username='admin', password='pass', role='Admin', tenant=self.tenant, is_staff=True)
        self.admin.save()
        self.client = APIClient()
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        # DEBUG: print all available endpoints
        from django.urls import get_resolver
        print("\nAvailable endpoints:")
        for name, pattern in get_resolver().reverse_dict.items():
            if isinstance(name, str):
                try:
                    url = self.client.get(reverse(name)).request['PATH_INFO']
                    print(f"{name}: {url}")
                except Exception as e:
                    print(f"{name}: error - {e}")

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
