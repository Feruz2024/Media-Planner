from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .models import License
import logging

logger = logging.getLogger(__name__)


class LicenseEnforceMiddleware(MiddlewareMixin):
    """Check that the request.user.tenant has an active, non-expired license.

    Behavior is configurable via Django settings:
    - LICENSE_ENFORCE_EXEMPT_PATHS: sequence of path prefixes (strings) to skip
      enforcement for (default: ['/health', '/status', '/api/docs', '/api/openapi']).
    - LICENSE_ENFORCE_SKIP_ADMIN: bool to skip /admin/ paths (default: True).

    The middleware will also skip STATIC_URL and MEDIA_URL paths when configured.
    """

    # include the license activation endpoint so admins can activate without an existing license
    DEFAULT_EXEMPTS = [
        '/health', '/healthz', '/status', '/api/docs', '/api/openapi',
        # activation endpoint (without and with API prefix)
        '/licenses/activate', '/api/licenses/activate'
    ]

    def _is_exempt_path(self, path: str) -> bool:
        # Gather configured exempt prefixes
        configured = getattr(settings, 'LICENSE_ENFORCE_EXEMPT_PATHS', None)
        prefixes = list(configured) if configured else []
        prefixes = prefixes + self.DEFAULT_EXEMPTS

        # include admin, static and media if configured
        if getattr(settings, 'LICENSE_ENFORCE_SKIP_ADMIN', True):
            prefixes.append('/admin')
        static_url = getattr(settings, 'STATIC_URL', None)
        media_url = getattr(settings, 'MEDIA_URL', None)
        if static_url:
            prefixes.append(static_url)
        if media_url:
            prefixes.append(media_url)

        # Normalize prefixes: remove empty values and avoid root '/' which would match everything
        normalized = []
        for p in prefixes:
            if not p:
                continue
            pstr = str(p).strip()
            if not pstr or pstr == '/':
                continue
            normalized.append(pstr)

        # Check against normalized prefixes
        for p in normalized:
            if path.startswith(p):
                logger.debug('LicenseEnforceMiddleware: path %s matched exempt prefix %s', path, p)
                return True
        return False

    def process_request(self, request):
        # Skip for unauthenticated users (public endpoints remain unaffected)
        user = getattr(request, 'user', None)

        # Always skip for exempt paths early
        path = getattr(request, 'path', '') or ''
        is_exempt = self._is_exempt_path(path)
        logger.debug('LicenseEnforceMiddleware: path=%s is_exempt=%s', path, is_exempt)
        if is_exempt:
            logger.debug('LicenseEnforceMiddleware: exempt path, skipping enforcement for %s', path)
            return None

        if not user or not getattr(user, 'is_authenticated', False):
            logger.debug('LicenseEnforceMiddleware: unauthenticated user or missing user, skipping enforcement')
            return None

        tenant = getattr(user, 'tenant', None)
        if not tenant:
            logger.debug('LicenseEnforceMiddleware: authenticated user has no tenant, skipping enforcement')
            return None

        # Check for License row for tenant
        try:
            lic = License.objects.get(tenant=tenant)
        except License.DoesNotExist:
            logger.debug('LicenseEnforceMiddleware: no License row for tenant %s — blocking', getattr(tenant, 'id', None))
            return JsonResponse({'detail': 'Tenant license not found'}, status=402)

        # Only allow if license status is 'active'
        if getattr(lic, 'status', None) != 'active':
            logger.debug('LicenseEnforceMiddleware: license status for tenant %s is %s — blocking', getattr(tenant, 'id', None), getattr(lic, 'status', None))
            return JsonResponse({'detail': 'Tenant license not active'}, status=402)

        logger.debug('LicenseEnforceMiddleware: license active for tenant %s — allowing', getattr(tenant, 'id', None))
        return None
