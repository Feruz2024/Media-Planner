from rest_framework import permissions


class IsTenantMember(permissions.BasePermission):
    """Allow access only to users that belong to the same tenant as the object."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not getattr(user, 'tenant', None):
            return False
        # Objects may have tenant or tenant_id
        tenant_id = getattr(obj, 'tenant_id', None) or getattr(getattr(obj, 'tenant', None), 'id', None)
        return str(tenant_id) == str(user.tenant_id)


class IsTenantAdmin(permissions.BasePermission):
    """Allow write operations only for tenant admins."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not getattr(user, 'tenant', None):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(user, 'role', '') == 'Admin'
