from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from areas.api import GeoQueryViewSet, NeighborhoodViewSet
from events.api import EventViewSet
from users.api import UserViewSet

router = DefaultRouter()
router.register('event', EventViewSet)
router.register('neighborhood', NeighborhoodViewSet, basename='neighborhood')
router.register('geo_query', GeoQueryViewSet, basename='geo_query')
router.register('user', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/', include((router.urls, 'haravajarjestelma'), namespace='v1')),
]
