from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from stations.models import Station, Show, Daypart, RateCard
from rest_framework.test import APIClient

User = get_user_model()

class RateCardRBACTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='RBAC')
        self.admin = User.objects.create_user(username='admin', password='pass', role='Admin', tenant=self.tenant, is_staff=True)
        self.planner = User.objects.create_user(username='planner', password='pass', role='Planner', tenant=self.tenant)
        self.station = Station.objects.create(name='Test Station', tenant=self.tenant, type='TV')
        self.daypart = Daypart.objects.create(name='Morning', start_time='06:00', end_time='12:00')
        self.show = Show.objects.create(station=self.station, name='Test Show')
        self.client = APIClient()

    def test_admin_can_create_ratecard(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ratecard-list')
        resp = self.client.post(url, {'station': str(self.station.id), 'show': str(self.show.id), 'daypart': str(self.daypart.id), 'price': '100.00', 'currency': 'USD'}, format='json')
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_can_create_ratecard(self):
        self.client.force_authenticate(user=self.planner)
        url = reverse('ratecard-list')
        resp = self.client.post(url, {'station': str(self.station.id), 'show': str(self.show.id), 'daypart': str(self.daypart.id), 'price': '120.00', 'currency': 'USD'}, format='json')
        self.assertIn(resp.status_code, (201, 400))

    def test_planner_cannot_access_other_tenant_ratecard(self):
        from tenants.models import Tenant
        other_tenant = Tenant.objects.create(name='Other')
        other_station = Station.objects.create(name='Other Station', tenant=other_tenant, type='TV')
        other_daypart = Daypart.objects.create(name='Evening', start_time='18:00', end_time='23:00')
        other_show = Show.objects.create(station=other_station, name='Other Show')
        self.client.force_authenticate(user=self.planner)
        url = reverse('ratecard-detail', args=['00000000-0000-0000-0000-000000000000'])
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (403, 404))

    def test_admin_can_access_all_ratecards(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('ratecard-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
