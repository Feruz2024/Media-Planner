import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Campaign(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=128, blank=True, null=True)
    advertiser_name = models.CharField(max_length=255, blank=True, null=True)
    target_audience = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=['tenant', 'start_date', 'end_date'])]

    def __str__(self):
        return f"{self.name} ({self.tenant_id})"


class MediaPlan(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, related_name='plans', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    campaign = models.ForeignKey(Campaign, related_name='plans', on_delete=models.CASCADE)
    station = models.ForeignKey('stations.Station', null=True, blank=True, on_delete=models.SET_NULL)
    show = models.ForeignKey('stations.Show', null=True, blank=True, on_delete=models.SET_NULL)
    daypart = models.ForeignKey('stations.Daypart', null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(null=True, blank=True)
    spots = models.IntegerField(null=True, blank=True)
    price_per_spot = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('locked', 'Locked'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='draft')

    class Meta:
        indexes = [models.Index(fields=['campaign', 'status'])]

    def __str__(self):
        return self.name


class MediaBrief(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, related_name='briefs', on_delete=models.CASCADE)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    objective = models.TextField(blank=True)
    target = models.JSONField(default=dict, blank=True)
    assets = models.JSONField(default=list, blank=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Brief for {self.campaign.name}"


class MonitoringReport(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media_plan = models.ForeignKey(MediaPlan, related_name='reports', on_delete=models.CASCADE, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, related_name='monitoring_reports', on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='monitoring_reports/', null=True, blank=True)
    generated_at = models.DateTimeField(default=timezone.now)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    metrics = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=['media_plan', 'generated_at'])]

    def __str__(self):
        return f"Report {self.id} for {self.media_plan_id}"


class License(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE)
    license_key = models.CharField(max_length=255, unique=True)
    machine_hash = models.CharField(max_length=255, blank=True, null=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    def is_active(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return self.activated_at is not None

    def __str__(self):
        return f"License {self.license_key} for {self.tenant_id}"


class MonitoringImport(TimestampedModel):
    """Represents an uploaded monitoring file and its processing state."""
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("processed", "Processed"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    file = models.FileField(upload_to='monitoring_imports/')
    original_filename = models.CharField(max_length=512, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=['tenant', 'status', 'created_at'])]

    def __str__(self):
        return f"Import {self.id} ({self.original_filename})"


class MonitoringEntry(TimestampedModel):
    """A single parsed row/entry from a monitoring import (one aired spot row)."""
    MATCH_STATUS = (
        ('unmatched', 'Unmatched'),
        ('matched', 'Matched'),
        ('ambiguous', 'Ambiguous'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    monitoring_import = models.ForeignKey(MonitoringImport, related_name='entries', on_delete=models.CASCADE)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL)
    media_plan = models.ForeignKey('MediaPlan', null=True, blank=True, on_delete=models.SET_NULL)
    station = models.ForeignKey('stations.Station', null=True, blank=True, on_delete=models.SET_NULL)
    show = models.ForeignKey('stations.Show', null=True, blank=True, on_delete=models.SET_NULL)
    daypart = models.ForeignKey('stations.Daypart', null=True, blank=True, on_delete=models.SET_NULL)
    airtime = models.DateTimeField(null=True, blank=True)
    spots_aired = models.IntegerField(default=0)
    duration_seconds = models.IntegerField(null=True, blank=True)
    raw_row = models.JSONField(default=dict, blank=True)
    match_status = models.CharField(max_length=32, choices=MATCH_STATUS, default='unmatched')
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['tenant', 'campaign', 'media_plan', 'processed'])]

    def __str__(self):
        return f"Entry {self.id} import={self.monitoring_import_id} spots={self.spots_aired}"
