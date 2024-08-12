from rest_framework import routers

from slack_integration.api import SlackViewSet

router = routers.DefaultRouter()
router.register(r"slack", SlackViewSet, basename="slack")

urlpatterns = router.urls
