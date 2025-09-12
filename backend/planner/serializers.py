from rest_framework import serializers
from . import models


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Campaign
        fields = '__all__'


class MediaPlanSerializer(serializers.ModelSerializer):
    # ensure created_by is read-only and set by the view
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.MediaPlan
        fields = '__all__'

    def validate(self, attrs):
        # spots must be positive
        spots = attrs.get('spots')
        if spots is None:
            raise serializers.ValidationError({'spots': 'This field is required.'})
        try:
            if int(spots) <= 0:
                raise serializers.ValidationError({'spots': 'Must be greater than 0.'})
        except (TypeError, ValueError):
            raise serializers.ValidationError({'spots': 'Must be an integer.'})

        # if show provided, ensure show belongs to station if both provided
        show = attrs.get('show')
        station = attrs.get('station')
        if show and station and getattr(show, 'station_id', None) != getattr(station, 'id', None):
            raise serializers.ValidationError({'show': 'Show does not belong to the provided station.'})

        # campaign must belong to same tenant (if tenant scoping applies)
        campaign = attrs.get('campaign')
        if campaign and hasattr(self.context.get('request'), 'user'):
            req_tenant = getattr(self.context['request'].user, 'tenant_id', None)
            if req_tenant and getattr(campaign, 'tenant_id', None) != req_tenant:
                raise serializers.ValidationError({'campaign': 'Campaign tenant mismatch.'})

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class MediaBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MediaBrief
        fields = '__all__'


class MonitoringReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MonitoringReport
        fields = '__all__'


class MonitoringReportUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = models.MonitoringReport
        fields = ('id', 'campaign', 'media_plan', 'file', 'metrics')


class MonitoringImportSerializer(serializers.ModelSerializer):
    entries = serializers.SerializerMethodField()

    class Meta:
        model = models.MonitoringImport
        # use '__all__' to include model fields; declared SerializerMethodField 'entries' will be included
        fields = '__all__'

    def get_entries(self, obj):
        # include a small representation of parsed entries
        qs = obj.entries.all()[:200]
        return MonitoringEntrySerializer(qs, many=True).data


class MonitoringEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MonitoringEntry
        fields = '__all__'


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.License
        fields = '__all__'
