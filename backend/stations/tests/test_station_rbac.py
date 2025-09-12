from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from stations.models import Station
from rest_framework.test import APIClient

class StationRBACTests(TestCase):
    def setUp(self):
        from tenants.models import Tenant
        self.tenant = Tenant.objects.create(name='RBAC')
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass', role='Admin', tenant=self.tenant, is_staff=True)
        self.planner = User.objects.create_user(username='planner', password='pass', role='Planner', tenant=self.tenant)
        self.station = Station.objects.create(name='Test Station', tenant=self.tenant, type='TV')

    def test_admin_can_create_station(self):
        client = APIClient()
        client.force_authenticate(user=self.admin)
        url = reverse('station-list')
        resp = client.post(url, {'name': 'Admin Station', 'tenant': str(self.tenant.id), 'type': 'TV'}, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_planner_can_create_station(self):
        client = APIClient()
        client.force_authenticate(user=self.planner)
        url = reverse('station-list')
        resp = client.post(url, {'name': 'Planner Station', 'tenant': str(self.tenant.id), 'type': 'TV'}, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_planner_cannot_access_other_tenant_station(self):
        from tenants.models import Tenant
        other_tenant = Tenant.objects.create(name='Other')
        other_station = Station.objects.create(name='Other Station', tenant=other_tenant, type='TV')
        client = APIClient()
        client.force_authenticate(user=self.planner)
        url = reverse('station-detail', args=[str(other_station.id)])
        resp = client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_access_all_stations(self):
        client = APIClient()
        client.force_authenticate(user=self.admin)
        url = reverse('station-detail', args=[str(self.station.id)])
        resp = client.get(url)
        self.assertEqual(resp.status_code, 200)
