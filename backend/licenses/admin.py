from django.contrib import admin
from .models import License


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'status', 'valid_from', 'valid_until')
    list_filter = ('status',)
    search_fields = ('tenant__name', 'id')
