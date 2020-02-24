from django.contrib.admin import register
from django.contrib.gis.admin import OSMGeoAdmin

from .models import ContractZone


@register(ContractZone)
class ContractZoneAdmin(OSMGeoAdmin):
    default_lon = 2776460  # Central Railway Station in EPSG:3857
    default_lat = 8438120
    default_zoom = 10
    modifiable = False
    list_display = ("name", "active")
    ordering = ("name",)
    fields = (
        "name",
        "boundary",
        "active",
        "origin_id",
        "contractor",
        "contact_person",
        "phone",
        "email",
        "secondary_contact_person",
        "secondary_phone",
        "secondary_email",
        "contractor_users",
    )
    readonly_fields = (
        "active",
        "name",
        "origin_id",
        "contractor",
        "contact_person",
        "phone",
        "email",
        "secondary_contact_person",
        "secondary_phone",
        "secondary_email",
    )

    def has_add_permission(self, request, obj=None):
        return False
