from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed the database with minimal development data'

    def handle(self, *args, **options):
        from tenants.models import Tenant
        from users.models import User
        from stations.models import Station, Show, Daypart
        from planner.models import Campaign, MediaPlan
        tenant, created = Tenant.objects.get_or_create(name='Demo Tenant')
        self.stdout.write(self.style.SUCCESS(f'Tenant: {tenant.id}'))

        admin, created = User.objects.get_or_create(
            username='admin', defaults={'email': 'admin@example.com', 'tenant': tenant}
        )
        if created:
            admin.set_password('admin')
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
        self.stdout.write(self.style.SUCCESS(f'Admin user: {admin.id}'))

        station, created = Station.objects.get_or_create(tenant=tenant, name='Demo FM')
        self.stdout.write(self.style.SUCCESS(f'Station: {station.id}'))

        show, created = Show.objects.get_or_create(station=station, name='Morning Show')
        self.stdout.write(self.style.SUCCESS(f'Show: {show.id}'))

        import datetime
        daypart, created = Daypart.objects.get_or_create(
            name='Breakfast', start_time=datetime.time(6, 0), end_time=datetime.time(9, 0)
        )
        self.stdout.write(self.style.SUCCESS(f'Daypart: {daypart.id}'))

        campaign = Campaign.objects.create(
            tenant=tenant,
            name='Demo Campaign',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(days=30)).date(),
        )
        self.stdout.write(self.style.SUCCESS(f'Campaign: {campaign.id}'))

        mp = MediaPlan.objects.create(campaign=campaign, name='Initial Plan', created_by=admin)
        self.stdout.write(self.style.SUCCESS(f'MediaPlan: {mp.id}'))

        self.stdout.write(self.style.SUCCESS('Seeding complete'))
