import django
import os
import logging


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.test_settings')
django.setup()

from django.test import RequestFactory
from tenants.models import Tenant
from django.contrib.auth import get_user_model
from licenses.middleware import LicenseEnforceMiddleware
from licenses.models import License


def run_debug():
    logger = logging.getLogger('licenses.middleware')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    rf = RequestFactory()
    # create tenant and user
    tenant = Tenant.objects.create(name='DBG')
    User = get_user_model()
    user = User.objects.create_user(username='dbg', password='pass', tenant=tenant)

    # ensure no license exists
    License.objects.filter(tenant=tenant).delete()

    req = rf.get('/protected')
    req.user = user

    mw = LicenseEnforceMiddleware(get_response=lambda r: None)
    print('Calling middleware.process_request')
    res = mw.process_request(req)
    print('Result type:', type(res), 'value:', res)
    if res is not None:
        try:
            print('status_code:', res.status_code, 'content:', res.content)
        except Exception:
            pass


if __name__ == '__main__':
    run_debug()
