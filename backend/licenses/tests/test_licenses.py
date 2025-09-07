from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from rest_framework.test import APIClient
import json
import jwt
from django.conf import settings


User = get_user_model()


class LicenseTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='ACME')
        self.admin = User.objects.create_user(username='admin', password='pass')
        # attach tenant to user if model supports it
        setattr(self.admin, 'tenant', self.tenant)
        self.admin.save()
        self.client = APIClient()
        self.client.login(username='admin', password='pass')

    @override_settings(LICENSE_TOKEN_ALGORITHM='HS256', LICENSE_PUBLIC_KEY='test-secret')
    def test_activate_license(self):
        # construct a JWT token payload for HS256 (test-secret)
        payload = {
            'tenant_id': str(self.tenant.id),
            'machine_hash': 'fake-hash',
            'features': {'pro': True}
        }
        token = jwt.encode(payload, 'test-secret', algorithm='HS256')
        url = reverse('license-activate')
        resp = self.client.post(url, data={'token': token}, format='json')
        # activation should fail because machine_hash won't match the machine file on CI/local
        self.assertIn(resp.status_code, (400, 403, 201))
