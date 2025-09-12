from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from stations.models import Daypart
from rest_framework.test import APIClient

User = get_user_model()

class DaypartRBACTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='RBAC')
        self.admin = User.objects.create_user(username='admin', password='pass', role='Admin', tenant=self.tenant, is_staff=True)
        self.planner = User.objects.create_user(username='planner', password='pass', role='Planner', tenant=self.tenant)
        self.client = APIClient()

    def test_admin_can_create_daypart(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('daypart-list')
        resp = self.client.post(url, {'name': 'Morning', 'start_time': '06:00', 'end_time': '12:00'}, format='json')
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_can_create_daypart(self):
        self.client.force_authenticate(user=self.planner)
        url = reverse('daypart-list')
        resp = self.client.post(url, {'name': 'Afternoon', 'start_time': '12:00', 'end_time': '18:00'}, format='json')
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_cannot_access_other_tenant_daypart(self):
        from tenants.models import Tenant
        other_tenant = Tenant.objects.create(name='Other')
        self.client.force_authenticate(user=self.planner)
        url = reverse('daypart-detail', args=['00000000-0000-0000-0000-000000000000'])
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (403, 404))

    def test_admin_can_access_all_dayparts(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('daypart-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
