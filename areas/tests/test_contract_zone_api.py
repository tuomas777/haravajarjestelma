from datetime import datetime

import pytest
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.utils.timezone import make_aware
from rest_framework.reverse import reverse

from common.tests.utils import get
from events.factories import EventFactory

from ..factories import ContractZoneFactory

LIST_URL = reverse('v1:contractzone-list')


@pytest.fixture
def contract_zone():
    return ContractZoneFactory(boundary=MultiPolygon(Polygon((
        (24, 60),
        (25, 60),
        (25, 61),
        (24, 61),
        (24, 60),
    ))))


@pytest.fixture
def two_events_2018():
    return EventFactory.create_batch(2)


@pytest.fixture
def two_events_2019():
    return EventFactory.create_batch(2, start_time=make_aware(datetime(2019, 3, 3)))


def get_expected_base_data(contract_zone):
    return {
        'id': contract_zone.id,
        'name': contract_zone.name,
    }


def test_get_list_non_official_no_stats(contract_zone, two_events_2018, user_api_client):
    response_data = get(user_api_client, LIST_URL + '?stats_year=2018')

    assert response_data['results'] == [get_expected_base_data(contract_zone)]


def test_get_list_official_no_filter_no_stats(contract_zone, two_events_2018, official_api_client):
    response_data = get(official_api_client, LIST_URL)

    assert response_data['results'] == [get_expected_base_data(contract_zone)]


def test_get_list_official_check_stats(contract_zone, two_events_2018, two_events_2019, official_api_client):
    response_data = get(official_api_client, LIST_URL + '?stats_year=2018')

    event_1, event_2 = two_events_2018
    expected_data = dict(
        get_expected_base_data(contract_zone),
        event_count=2,
        estimated_attendee_count=event_1.estimated_attendee_count + event_2.estimated_attendee_count,
    )
    assert response_data['results'] == [expected_data]
