from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .. import models, serializers
from tenants.models import Tenant
from stations.models import Station, Show, Daypart
import io


User = get_user_model()


class MediaPlanSerializerTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='TestTenant')
        self.user = User.objects.create_user(username='u1', password='pass', tenant=self.tenant)
        self.campaign = models.Campaign.objects.create(tenant=self.tenant, name='C1')
        self.station = Station.objects.create(tenant=self.tenant, name='Station 1', type='TV')
        self.show = Show.objects.create(station=self.station, name='Show A')

    def test_spots_must_be_positive(self):
        data = {
            'campaign': self.campaign.id,
            'name': 'Plan 1',
            'station': self.station.id,
            'show': self.show.id,
            'date': '2025-09-01',
            'spots': 0,
        }
        serializer = serializers.MediaPlanSerializer(data=data, context={'request': type('r', (), {'user': self.user})()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('spots', serializer.errors)

    def test_show_belongs_to_station(self):
        other_station = Station.objects.create(tenant=self.tenant, name='Station 2', type='TV')
        data = {
            'campaign': self.campaign.id,
            'name': 'Plan 2',
            'station': other_station.id,
            'show': self.show.id,  # show belongs to station 1, not other_station
            'date': '2025-09-01',
            'spots': 5,
        }
        serializer = serializers.MediaPlanSerializer(data=data, context={'request': type('r', (), {'user': self.user})()})
        self.assertFalse(serializer.is_valid())
        self.assertIn('show', serializer.errors)


class MonitoringImportViewTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='MonTenant')
        self.user = User.objects.create_user(username='mon', password='pass', tenant=self.tenant)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_upload_csv_creates_import_and_entries(self):
        csv_content = 'airtime,spots_aired,campaign_name\n2025-09-01T10:00:00,2,TestCampaign\n2025-09-01T11:00:00,3,TestCampaign\n'
        f = io.BytesIO(csv_content.encode('utf-8'))
        f.name = 'sample.csv'
        resp = self.client.post('/api/monitoring-imports/upload/', {'file': f}, format='multipart')
        # Accept 201 Created or 200 OK; allow redirects (301/302) in some router configs
        self.assertIn(resp.status_code, (200, 201, 301, 302))
        # check there is at least one MonitoringImport
        self.assertTrue(models.MonitoringImport.objects.exists())
        mi = models.MonitoringImport.objects.first()
        # parsed summary should mention entries
        self.assertIn('Parsed', mi.summary)