from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'networks', views.NetworkViewSet)
router.register(r'show-categories', views.ShowCategoryViewSet)
router.register(r'audience-categories', views.AudienceCategoryViewSet)
router.register(r'sponsorship-prices', views.SponsorshipPriceViewSet)
router.register(r'campaigns', views.CampaignViewSet)
router.register(r'media-plans', views.MediaPlanViewSet)
router.register(r'media-briefs', views.MediaBriefViewSet)
router.register(r'monitoring-reports', views.MonitoringReportViewSet)
router.register(r'monitoring-imports', views.MonitoringImportViewSet)

urlpatterns = router.urls
