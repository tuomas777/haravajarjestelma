import pytest
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.core.exceptions import ValidationError

from areas.factories import ContractZoneFactory
from events.factories import EventFactory


def test_contract_zone_autopopulating():
    zone_1, zone_2, zone_3 = (
        ContractZoneFactory(
            boundary=MultiPolygon(
                Polygon(
                    (
                        (24 + n, 60),
                        (25 + n, 60),
                        (25 + n, 61),
                        (24 + n, 61),
                        (24 + n, 60),
                    )
                )
            )
        )
        for n in range(3)
    )

    point_outside_all_zones = Point(10, 10)
    point_inside_zone_2 = Point(25.5, 60.5)

    new_event = EventFactory.build(location=point_outside_all_zones)
    with pytest.raises(ValidationError):
        new_event.clean()

    new_event = EventFactory.build(location=point_inside_zone_2)
    new_event.clean()
    new_event.save()
    assert new_event.contract_zone == zone_2


@pytest.mark.parametrize(
    "email, secondary_email, expected",
    (
        ("foo@example.com", "", ["foo@example.com"]),
        ("", "bar@example.com", ["bar@example.com"]),
        ("foo@example.com", "bar@example.com", ["foo@example.com", "bar@example.com"]),
        ("", "", []),
    ),
)
def test_get_contact_emails(email, secondary_email, expected):
    contract_zone = ContractZoneFactory(email=email, secondary_email=secondary_email)
    assert contract_zone.get_contact_emails() == expected
