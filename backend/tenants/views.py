from rest_framework import viewsets
from .models import Tenant
from rest_framework import serializers


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'


from planner.permissions import IsTenantAdmin

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsTenantAdmin]

    def get_queryset(self):
        user = self.request.user
        # Admins see all tenants
        if getattr(user, 'role', None) == 'Admin':
            return Tenant.objects.all()
        # Non-admins only see their own tenant
        if getattr(user, 'tenant', None):
            return Tenant.objects.filter(id=user.tenant.id)
        return Tenant.objects.none()

    def get_object(self):
        # Always fetch the object by pk
        obj = Tenant.objects.filter(pk=self.kwargs.get('pk')).first()
        if obj is None:
            from rest_framework.exceptions import NotFound
            raise NotFound("Tenant not found.")
        user = self.request.user
        # Admins can access any tenant
        if getattr(user, 'role', None) == 'Admin':
            return obj
        # Non-admins can only access their own tenant
        if getattr(user, 'tenant', None) and obj.id == user.tenant.id:
            return obj
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to access this tenant.")
