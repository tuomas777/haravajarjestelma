from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from areas.api import GeoQueryViewSet, NeighborhoodViewSet
from events.api import EventViewSet

router = DefaultRouter()
router.register('event', EventViewSet)
router.register('neighborhood', NeighborhoodViewSet, base_name='neighborhood')
router.register('geo_query', GeoQueryViewSet, base_name='geo_query')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/', include((router.urls, 'haravajarjestelma'), namespace='v1')),
]
