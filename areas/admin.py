from django.contrib.admin import register
from django.contrib.gis.admin import OSMGeoAdmin

from .models import ContractZone


@register(ContractZone)
class ContractAdmin(OSMGeoAdmin):
    default_lon = 2776460  # Central Railway Station in EPSG:3857
    default_lat = 8438120
    default_zoom = 10
