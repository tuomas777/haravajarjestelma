from django.contrib.admin import register
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils.translation import ugettext_lazy as _

from .models import ContractZone


@register(ContractZone)
class ContractZoneAdmin(OSMGeoAdmin):
    default_lon = 2776460  # Central Railway Station in EPSG:3857
    default_lat = 8438120
    default_zoom = 10
    modifiable = False

    fieldsets = (
        ("", {"fields": ("contact_person", "phone", "email", "contractor_user")}),
        (
            _("Imported fields"),
            {"fields": ("name", "active", "origin_id", "contractor", "boundary")},
        ),
    )

    def has_add_permission(self, request, obj=None):
        return False

    readonly_fields = ("active", "name", "origin_id", "contractor")
