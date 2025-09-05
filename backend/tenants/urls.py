from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tenants', views.TenantViewSet)

urlpatterns = router.urls
