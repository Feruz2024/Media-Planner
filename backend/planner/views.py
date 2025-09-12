from . import models, serializers
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .permissions import IsTenantMember, IsTenantAdmin


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = models.Network.objects.all()
    serializer_class = serializers.NetworkSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

class ShowCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.ShowCategory.objects.all()
    serializer_class = serializers.ShowCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

class AudienceCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.AudienceCategory.objects.all()
    serializer_class = serializers.AudienceCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]

class SponsorshipPriceViewSet(viewsets.ModelViewSet):
    queryset = models.SponsorshipPrice.objects.all()
    serializer_class = serializers.SponsorshipPriceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]





class TenantScopedMixin:
    """Mixin to scope queryset by tenant from request.user.tenant or X-Tenant header."""

    def get_tenant_id(self):
        user = getattr(self.request, 'user', None)
        if user and getattr(user, 'tenant_id', None):
            return user.tenant_id
        # allow service calls to set X-Tenant header
        header = self.request.headers.get('X-Tenant')
        if header:
            return header
        return None

    def get_queryset(self):
        qs = super().get_queryset()
        tid = self.get_tenant_id()
        if tid:
            return qs.filter(tenant_id=tid)
        return qs


class CampaignViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = models.Campaign.objects.all()
    serializer_class = serializers.CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['tenant', 'status', 'start_date', 'end_date']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    search_fields = ['name', 'advertiser_name', 'target_audience']


class MediaPlanViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = models.MediaPlan.objects.all()
    serializer_class = serializers.MediaPlanSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['campaign', 'station', 'show', 'daypart', 'date', 'status']
    ordering_fields = ['date', 'created_at', 'spots']
    search_fields = ['notes']

    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_create(self, request):
        """Bulk create media plans (spots) for a campaign."""
        items = request.data.get('items', [])
        created = []
        errors = []
        for item in items:
            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                obj = serializer.save()
                created.append(obj.id)
            else:
                errors.append(serializer.errors)
        if errors:
            return Response({'detail': 'Some items failed', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'created': created}, status=status.HTTP_201_CREATED)


class MediaBriefViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = models.MediaBrief.objects.all()
    serializer_class = serializers.MediaBriefSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['campaign']
    ordering_fields = ['due_date', 'created_at']
    search_fields = ['objective', 'target']


class MonitoringReportViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = models.MonitoringReport.objects.all()
    serializer_class = serializers.MonitoringReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['media_plan']
    ordering_fields = ['generated_at', 'created_at']
    search_fields = ['summary', 'metrics']

    def get_serializer_class(self):
        if self.action == 'upload':
            return serializers.MonitoringReportUploadSerializer
        return serializers.MonitoringReportSerializer

    @action(detail=False, methods=['post'], url_path='upload', parser_classes=[
        # default parsers include MultiPartParser; DRF will handle file uploads
    ])
    def upload(self, request):
        """Accept multipart file upload of monitoring report (CSV) and parse basic metrics."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()

        # Basic CSV parsing if provided
        f = request.FILES.get('file')
        if f and f.name.endswith('.csv'):
            import csv
            decoded = f.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded)
            total_spots = 0
            for row in reader:
                try:
                    total_spots += int(row.get('spots_aired', 0))
                except Exception:
                    continue
            report.metrics = {'spots_aired': total_spots}
            report.summary = f'Parsed {total_spots} spots from CSV'
            report.save()

        return Response(serializers.MonitoringReportSerializer(report).data, status=status.HTTP_201_CREATED)


class MonitoringImportViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """Handle raw monitoring file uploads and parse them into MonitoringEntry rows."""
    queryset = models.MonitoringImport.objects.all()
    serializer_class = serializers.MonitoringImportSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['tenant', 'status']
    ordering_fields = ['created_at', 'processed_at']

    def get_serializer_class(self):
        return self.serializer_class

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """Accept CSV or XLSX, create a MonitoringImport and parse rows into MonitoringEntry."""
        f = request.FILES.get('file')
        if not f:
            return Response({'detail': 'file is required'}, status=status.HTTP_400_BAD_REQUEST)

        import_obj = models.MonitoringImport.objects.create(
            tenant_id=self.get_tenant_id(),
            uploaded_by=(request.user if getattr(request, 'user', None) and request.user.is_authenticated else None),
            file=f,
            original_filename=getattr(f, 'name', '')
        )
    # Improved parsing: for small CSVs parse inline, otherwise enqueue a Celery task
    # to process the import asynchronously.
        entries_to_create = []
        matched = 0
        parsed = 0
        try:
            tenant_id = self.get_tenant_id()
            # helper to normalize keys
            def normalize_row(d):
                return { (k or '').strip().lower(): (v if v is not None else '') for k,v in d.items() }

            def parse_csv(file_obj):
                import csv
                text = file_obj.read().decode('utf-8', errors='replace').splitlines()
                reader = csv.DictReader(text)
                for raw in reader:
                    yield normalize_row(raw)

            def parse_xlsx(file_obj):
                try:
                    import openpyxl
                except Exception:
                    raise RuntimeError('openpyxl not installed')
                wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
                ws = wb.active
                rows = ws.iter_rows(values_only=True)
                try:
                    headers = [str(h).strip().lower() if h is not None else '' for h in next(rows)]
                except StopIteration:
                    return
                for row in rows:
                    data = {headers[i] if i < len(headers) else f'col_{i}': row[i] for i in range(len(row))}
                    yield normalize_row(data)

            # choose parser
            if f.name.lower().endswith('.csv'):
                row_iter = parse_csv(f)
            elif f.name.lower().endswith(('.xlsx', '.xls')):
                row_iter = parse_xlsx(f)
            else:
                import_obj.status = 'failed'
                import_obj.summary = 'unsupported file type'
                import_obj.save()
                return Response({'detail': 'unsupported file type'}, status=status.HTTP_400_BAD_REQUEST)

            from django.db import transaction
            from dateutil import parser as dateparser

            # If file is small, parse inline; otherwise enqueue background task
            f_size = None
            try:
                f_size = f.size
            except Exception:
                pass

            # threshold in bytes for inline parsing
            INLINE_THRESHOLD = 100 * 1024  # 100KB

            if f_size is not None and f_size > INLINE_THRESHOLD:
                # enqueue background processing
                try:
                    from .tasks import process_monitoring_import
                except Exception:
                    raise RuntimeError('Celery tasks not available')
                process_monitoring_import.delay(str(import_obj.id))
                import_obj.status = 'processing'
                import_obj.save()
                return Response({'import_id': import_obj.id, 'status': 'processing'}, status=status.HTTP_202_ACCEPTED)

            # inline parse for small files
            with transaction.atomic():
                for raw in row_iter:
                    parsed += 1
                    # normalize common column names
                    spots_candidates = [raw.get('spots_aired'), raw.get('spots'), raw.get('sold'), raw.get('count')]
                    spots = 0
                    for s in spots_candidates:
                        try:
                            if s is None or s == '':
                                continue
                            spots = int(float(str(s).strip()))
                            break
                        except Exception:
                            continue

                    airtime = None
                    airtime_value = raw.get('airtime') or raw.get('time') or raw.get('datetime') or raw.get('date_time')
                    if airtime_value:
                        try:
                            airtime = dateparser.parse(str(airtime_value))
                        except Exception:
                            airtime = None

                    duration = None
                    try:
                        dur = raw.get('duration') or raw.get('duration_seconds') or raw.get('length')
                        if dur not in (None, ''):
                            duration = int(float(str(dur).strip()))
                    except Exception:
                        duration = None

                    # best-effort matching: campaign by external_id or name
                    campaign_obj = None
                    campaign_id_val = raw.get('campaign_id') or raw.get('campaign_external_id') or raw.get('campaign_id_external')
                    campaign_name_val = raw.get('campaign') or raw.get('campaign_name') or raw.get('advertiser')
                    if campaign_id_val:
                        try:
                            campaign_obj = models.Campaign.objects.filter(tenant_id=tenant_id, external_id=str(campaign_id_val)).first()
                        except Exception:
                            campaign_obj = None
                    if not campaign_obj and campaign_name_val:
                        campaign_obj = models.Campaign.objects.filter(tenant_id=tenant_id, name__iexact=str(campaign_name_val).strip()).first()

                    # try to find a MediaPlan: by campaign + date (from airtime) + show/station if available
                    media_plan_obj = None
                    if campaign_obj and airtime:
                        try:
                            date_val = airtime.date()
                            qs = models.MediaPlan.objects.filter(campaign=campaign_obj, date=date_val)
                            # narrow by show/station if provided
                            show_val = raw.get('show') or raw.get('show_name')
                            station_val = raw.get('station') or raw.get('station_name')
                            if show_val:
                                qs = qs.filter(show__name__iexact=str(show_val).strip())
                            if station_val:
                                qs = qs.filter(station__name__iexact=str(station_val).strip())
                            media_plan_obj = qs.first()
                        except Exception:
                            media_plan_obj = None

                    match_status = 'unmatched'
                    if media_plan_obj:
                        match_status = 'matched'
                        matched += 1
                    elif campaign_obj:
                        match_status = 'ambiguous'

                    entry = models.MonitoringEntry(
                        monitoring_import=import_obj,
                        tenant_id=tenant_id,
                        campaign=campaign_obj,
                        media_plan=media_plan_obj,
                        spots_aired=spots,
                        airtime=airtime,
                        duration_seconds=duration,
                        raw_row=raw,
                        match_status=match_status,
                    )
                    entries_to_create.append(entry)

                # bulk create for performance
                if entries_to_create:
                    models.MonitoringEntry.objects.bulk_create(entries_to_create, batch_size=500)

                import_obj.status = 'processed'
                import_obj.processed_at = models.timezone.now()
                import_obj.summary = f'Parsed {parsed} entries, matched {matched}'
                import_obj.save()

        except RuntimeError as rexc:
            import_obj.status = 'failed'
            import_obj.summary = str(rexc)
            import_obj.save()
            return Response({'detail': 'parsing failed', 'error': str(rexc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            import_obj.status = 'failed'
            import_obj.summary = str(exc)
            import_obj.save()
            return Response({'detail': 'parsing failed', 'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'import_id': import_obj.id, 'parsed': parsed, 'matched': matched}, status=status.HTTP_201_CREATED)


class LicenseViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = models.License.objects.all()
    serializer_class = serializers.LicenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantAdmin]
