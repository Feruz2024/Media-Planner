from celery import shared_task
from . import models
from django.utils import timezone

@shared_task(bind=True)
def process_monitoring_import(self, import_id):
    """Background task to parse MonitoringImport file and create MonitoringEntry rows.
    This mirrors the parsing logic in views.upload but runs asynchronously.
    """
    try:
        imp = models.MonitoringImport.objects.get(id=import_id)
        imp.status = 'processing'
        imp.save()

        f = imp.file
        # re-open via storage
        file_obj = f.open('rb')
        parsed = 0
        matched = 0
        entries = []

        # simple CSV fallback
        if imp.original_filename.lower().endswith('.csv'):
            import csv
            text = file_obj.read().decode('utf-8', errors='replace').splitlines()
            reader = csv.DictReader(text)
            for raw in reader:
                parsed += 1
                entry = models.MonitoringEntry.objects.create(
                    monitoring_import=imp,
                    tenant=imp.tenant,
                    raw_row=raw,
                    spots_aired=int(raw.get('spots_aired') or raw.get('spots') or 0),
                )
                entries.append(entry)
        else:
            # For now, unsupported types will mark as failed
            imp.status = 'failed'
            imp.summary = 'unsupported file type for background processing'
            imp.processed_at = timezone.now()
            imp.save()
            return {'status': 'failed'}

        imp.status = 'processed'
        imp.processed_at = timezone.now()
        imp.summary = f'Parsed {parsed} entries in background'
        imp.save()
        return {'status': 'ok', 'parsed': parsed}
    except models.MonitoringImport.DoesNotExist:
        return {'status': 'not_found'}
    except Exception as exc:
        try:
            imp.status = 'failed'
            imp.summary = str(exc)
            imp.save()
        except Exception:
            pass
        raise
