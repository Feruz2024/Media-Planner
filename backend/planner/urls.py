from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'campaigns', views.CampaignViewSet)
router.register(r'media-plans', views.MediaPlanViewSet)
router.register(r'briefs', views.MediaBriefViewSet)
router.register(r'reports', views.MonitoringReportViewSet)
router.register(r'monitoring-imports', views.MonitoringImportViewSet)
router.register(r'licenses', views.LicenseViewSet)

urlpatterns = router.urls
