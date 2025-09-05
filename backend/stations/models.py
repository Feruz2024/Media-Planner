import uuid
from django.db import models


class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=(('TV','TV'),('Radio','Radio')))
    region = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type})"


class Daypart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name


class Show(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    station = models.ForeignKey(Station, related_name='shows', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, blank=True, null=True)
    default_dayparts = models.ManyToManyField(Daypart, blank=True)

    def __str__(self):
        return f"{self.name} @ {self.station.name}"


class RateCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE, null=True, blank=True)
    daypart = models.ForeignKey(Daypart, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    class Meta:
        unique_together = ('station','show','daypart')

    def __str__(self):
        return f"{self.station.name} {self.show or ''} {self.daypart.name} {self.price} {self.currency}"
