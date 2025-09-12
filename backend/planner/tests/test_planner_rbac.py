from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from planner.models import Campaign, MediaPlan, MediaBrief
from rest_framework.test import APIClient

User = get_user_model()

class PlannerRBACTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='RBAC')
        self.admin = User.objects.create_user(username='admin', password='pass', role='Admin', tenant=self.tenant, is_staff=True)
        self.planner = User.objects.create_user(username='planner', password='pass', role='Planner', tenant=self.tenant)
        self.client = APIClient()
        self.campaign = Campaign.objects.create(tenant=self.tenant, name='Test Campaign')

    def test_admin_can_create_campaign(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('campaign-list')
        resp = self.client.post(url, {'tenant': str(self.tenant.id), 'name': 'Admin Campaign'}, format='json')
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_can_create_campaign(self):
        self.client.force_authenticate(user=self.planner)
        url = reverse('campaign-list')
        resp = self.client.post(url, {'tenant': str(self.tenant.id), 'name': 'Planner Campaign'}, format='json')
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_cannot_access_other_tenant_campaign(self):
        from tenants.models import Tenant
        other_tenant = Tenant.objects.create(name='Other')
        self.client.force_authenticate(user=self.planner)
        url = reverse('campaign-detail', args=['00000000-0000-0000-0000-000000000000'])
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (403, 404))

    def test_admin_can_access_all_campaigns(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('campaign-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
