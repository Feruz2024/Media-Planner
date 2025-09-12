from django.db import migrations, models
import django.utils.timezone


def set_uploaded_at(apps, schema_editor):
    MonitoringReport = apps.get_model('planner', 'MonitoringReport')
    now = django.utils.timezone.now()
    # set uploaded_at for all existing rows
    MonitoringReport.objects.filter(uploaded_at__isnull=True).update(uploaded_at=now)


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0003_remove_mediaplan_slots_campaign_advertiser_name_and_more'),
    ]

    operations = [
        # ensure field exists as nullable first (models already declare auto_now_add=True)
        migrations.AddField(
            model_name='monitoringreport',
            name='uploaded_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.RunPython(set_uploaded_at, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='monitoringreport',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
