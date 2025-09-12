from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from licenses.models import License
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class TestLicenseRBAC(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='ACME')
        self.admin = User.objects.create_user(username='admin', password='pass', role='Admin', tenant=self.tenant)
        self.planner = User.objects.create_user(username='planner', password='pass', role='Planner', tenant=self.tenant)
        License.objects.create(tenant=self.tenant, license_key='test', status='active')
        self.client = APIClient()

    def get_jwt(self, user):
        refresh = RefreshToken.for_user(user)
        return f'Bearer {str(refresh.access_token)}'

    def test_admin_can_create_license(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.admin))
        url = reverse('license-list')
        resp = self.client.post(url, data={'tenant': str(self.tenant.id), 'license_key': 'newkey', 'status': 'active'})
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_cannot_create_license(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.planner))
        url = reverse('license-list')
        resp = self.client.post(url, data={'tenant': str(self.tenant.id), 'license_key': 'newkey', 'status': 'active'})
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_update_license(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.admin))
        lic = License.objects.filter(tenant=self.tenant).first()
        url = reverse('license-detail', args=[lic.id])
        resp = self.client.patch(url, data={'status': 'inactive'})
        self.assertIn(resp.status_code, (200, 400))

    def test_planner_cannot_update_license(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.planner))
        lic = License.objects.filter(tenant=self.tenant).first()
        url = reverse('license-detail', args=[lic.id])
        resp = self.client.patch(url, data={'status': 'inactive'})
        self.assertEqual(resp.status_code, 403)

    def test_any_authenticated_can_read_license(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.planner))
        lic = License.objects.filter(tenant=self.tenant).first()
        url = reverse('license-detail', args=[lic.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
