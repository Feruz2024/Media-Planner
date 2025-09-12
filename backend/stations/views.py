from rest_framework import viewsets, permissions
from planner.permissions import IsTenantMember
from .models import Station, Show, Daypart, RateCard
from .serializers import StationSerializer, ShowSerializer, DaypartSerializer, RateCardSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]


class ShowViewSet(viewsets.ModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]


class DaypartViewSet(viewsets.ModelViewSet):
    queryset = Daypart.objects.all()
    serializer_class = DaypartSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]


class RateCardViewSet(viewsets.ModelViewSet):
    queryset = RateCard.objects.all()
    serializer_class = RateCardSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMember]
