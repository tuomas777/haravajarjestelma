from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from events.api import EventViewSet

router = DefaultRouter()
router.register('event', EventViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/', include((router.urls, 'haravajarjestelma'), namespace='v1')),
]
