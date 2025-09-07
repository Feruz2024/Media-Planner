from rest_framework import serializers
from .models import License


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'


class LicenseActivateSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
