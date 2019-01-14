from django.contrib.gis.geos import MultiPolygon, Point, Polygon

from areas.factories import ContractZoneFactory
from events.factories import EventFactory


def test_contract_zone_autopopulating():
    zone_1, zone_2, zone_3 = (ContractZoneFactory(boundary=MultiPolygon(Polygon((
        (24 + n, 60),
        (25 + n, 60),
        (25 + n, 61),
        (24 + n, 61),
        (24 + n, 60),
    )))) for n in range(3))

    point_outside_all_zones = Point(10, 10)
    point_inside_zone_2 = Point(25.5, 60.5)

    new_event = EventFactory(location=point_outside_all_zones)
    updated_event = EventFactory()
    updated_event.location = point_outside_all_zones
    updated_event.save()
    assert new_event.contract_zone is None
    assert updated_event.contract_zone is None

    new_event = EventFactory(location=point_inside_zone_2)
    updated_event = EventFactory()
    updated_event.location = point_inside_zone_2
    updated_event.save()
    assert new_event.contract_zone == zone_2
    assert updated_event.contract_zone == zone_2
