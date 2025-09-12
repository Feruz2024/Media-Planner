from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import License
from .serializers import LicenseSerializer, LicenseActivateSerializer
from .lib import verify_activation_token, get_machine_hash


class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # tenant-scoped: only licenses for the user's tenant
        user = self.request.user
        tenant = getattr(user, 'tenant', None)
        if tenant is None:
            return License.objects.none()
        return License.objects.filter(tenant=tenant)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser], url_path='activate')
    def activate(self, request):
        # Accept either JSON body with token or multipart file upload
        token = None
        if 'token' in request.data:
            token = request.data['token']
        elif 'file' in request.FILES:
            token = request.FILES['file'].read().decode('utf-8')

        if not token:
            return Response({'detail': 'No activation token provided'}, status=status.HTTP_400_BAD_REQUEST)

        machine_hash = get_machine_hash()
        try:
            payload = verify_activation_token(token, expected_machine_hash=machine_hash)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        tenant_id = payload['tenant_id']
        # Ensure this admin belongs to the tenant referenced
        user_tenant = getattr(request.user, 'tenant', None)
        if not user_tenant or str(user_tenant.id) != str(tenant_id):
            return Response({'detail': 'Activation token tenant mismatch'}, status=status.HTTP_403_FORBIDDEN)

        # create or update license record for this tenant
        lic, created = License.objects.update_or_create(
            tenant=user_tenant,
            defaults={
                'license_key': token,
                'features': payload.get('features', {}),
                'machine_hash': payload.get('machine_hash'),
                'status': 'active',
                'valid_from': payload.get('valid_from'),
                'valid_until': payload.get('valid_until'),
                'meta': payload.get('meta', {}),
            }
        )
        return Response(LicenseSerializer(lic).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
