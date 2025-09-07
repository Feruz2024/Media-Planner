from django.contrib import admin
from . import models


@admin.register(models.Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'start_date', 'end_date', 'status')
    search_fields = ('name',)


@admin.register(models.MediaPlan)
class MediaPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'status', 'created_by')


@admin.register(models.MediaBrief)
class MediaBriefAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'requested_by', 'due_date')


@admin.register(models.MonitoringReport)
class MonitoringReportAdmin(admin.ModelAdmin):
    list_display = ('media_plan', 'generated_at')


@admin.register(models.License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('license_key', 'tenant', 'activated_at', 'expires_at')
