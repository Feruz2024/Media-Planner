from rest_framework.routers import DefaultRouter
from .views import StationViewSet, ShowViewSet, DaypartViewSet, RateCardViewSet

router = DefaultRouter()
router.register('stations', StationViewSet)
router.register('shows', ShowViewSet)
router.register('dayparts', DaypartViewSet)
router.register('ratecards', RateCardViewSet)

urlpatterns = router.urls
