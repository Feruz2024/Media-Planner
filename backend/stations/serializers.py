from rest_framework import serializers
from .models import Station, Show, Daypart, RateCard


class DaypartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daypart
        fields = '__all__'


class ShowSerializer(serializers.ModelSerializer):
    default_dayparts = DaypartSerializer(many=True, read_only=True)

    class Meta:
        model = Show
        fields = '__all__'


class StationSerializer(serializers.ModelSerializer):
    shows = ShowSerializer(many=True, read_only=True)

    class Meta:
        model = Station
        fields = '__all__'


class RateCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateCard
        fields = '__all__'
