from rest_framework import viewsets
from .models import Station, Show, Daypart, RateCard
from .serializers import StationSerializer, ShowSerializer, DaypartSerializer, RateCardSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class ShowViewSet(viewsets.ModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer


class DaypartViewSet(viewsets.ModelViewSet):
    queryset = Daypart.objects.all()
    serializer_class = DaypartSerializer


class RateCardViewSet(viewsets.ModelViewSet):
    queryset = RateCard.objects.all()
    serializer_class = RateCardSerializer
