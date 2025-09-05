import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', null=True, blank=True, on_delete=models.CASCADE)

    class Role(models.TextChoices):
        ADMIN = 'Admin'
        PLANNER = 'Planner'
        CLIENT = 'Client'
        STATIONREP = 'StationRep'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PLANNER)
