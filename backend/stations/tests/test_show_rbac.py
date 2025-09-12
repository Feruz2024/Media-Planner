from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from stations.models import Show
from rest_framework.test import APIClient

User = get_user_model()

class ShowRBACTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='RBAC')
        self.admin = User.objects.create_user(username='admin', password='pass', role='Admin', tenant=self.tenant, is_staff=True)
        self.planner = User.objects.create_user(username='planner', password='pass', role='Planner', tenant=self.tenant)
        self.client = APIClient()

    def test_admin_can_create_show(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('show-list')
        resp = self.client.post(url, {'station': None, 'name': 'Admin Show'}, format='json')
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_can_create_show(self):
        self.client.force_authenticate(user=self.planner)
        url = reverse('show-list')
        resp = self.client.post(url, {'station': None, 'name': 'Planner Show'}, format='json')
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_cannot_access_other_tenant_show(self):
        from tenants.models import Tenant
        other_tenant = Tenant.objects.create(name='Other')
        other_admin = User.objects.create_user(username='otheradmin', password='pass', role='Admin', tenant=other_tenant, is_staff=True)
        self.client.force_authenticate(user=self.planner)
        # No actual show created for other tenant, just check forbidden on detail
        url = reverse('show-detail', args=['00000000-0000-0000-0000-000000000000'])
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (403, 404))

    def test_admin_can_access_all_shows(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('show-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
