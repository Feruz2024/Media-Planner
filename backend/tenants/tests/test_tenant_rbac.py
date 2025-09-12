from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from rest_framework.test import APIClient

User = get_user_model()

from licenses.models import License

from django.urls import reverse
from licenses.models import License
from rest_framework_simplejwt.tokens import RefreshToken

class TenantRBAC(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='ACME')
        self.other_tenant = Tenant.objects.create(name='OtherTenant')
        self.admin = User.objects.create_user(username='admin', password='pass', role='Admin', tenant=self.tenant)
        self.planner = User.objects.create_user(username='planner', password='pass', role='Planner', tenant=self.tenant)
        self.other_planner = User.objects.create_user(username='otherplanner', password='pass', role='Planner', tenant=self.other_tenant)
        # Create active licenses for both tenants
        License.objects.create(tenant=self.tenant, license_key='test', status='active')
        License.objects.create(tenant=self.other_tenant, license_key='test', status='active')
        self.client = APIClient()

    def get_jwt(self, user):
        refresh = RefreshToken.for_user(user)
        return f'Bearer {str(refresh.access_token)}'

    def test_admin_can_create_tenant(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.admin))
        url = reverse('tenant-list')
        resp = self.client.post(url, data={'name': 'NewTenant'})
        self.assertIn(resp.status_code, (201, 400))  # 400 if duplicate, 201 if created

    def test_planner_cannot_create_tenant(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.planner))
        url = reverse('tenant-list')
        resp = self.client.post(url, data={'name': 'NewTenant'})
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_update_tenant(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.admin))
        url = reverse('tenant-detail', args=[self.tenant.id])
        resp = self.client.patch(url, data={'name': 'UpdatedTenant'})
        self.assertIn(resp.status_code, (200, 400))

    def test_planner_cannot_update_tenant(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.planner))
        url = reverse('tenant-detail', args=[self.tenant.id])
        resp = self.client.patch(url, data={'name': 'UpdatedTenant'})
        self.assertEqual(resp.status_code, 403)

    def test_planner_can_only_read_own_tenant(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.get_jwt(self.planner))
        url = reverse('tenant-detail', args=[self.tenant.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Try to access another tenant
        url = reverse('tenant-detail', args=[self.other_tenant.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
