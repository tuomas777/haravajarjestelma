import factory
import pytest
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from freezegun import freeze_time
from rest_framework.test import APIClient

from areas.factories import ContractZoneFactory
from users.factories import UserFactory

from ..factories import EventFactory


@pytest.fixture(autouse=True)
def set_random_seed():
    factory.random.reseed_random(777)


@pytest.fixture(autouse=True)
def set_frozen_time():
    freezer = freeze_time('2018-01-14T08:00:00Z')
    freezer.start()
    yield
    freezer.stop()


@pytest.fixture(autouse=True)
def autouse_django_db(db):
    pass


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def contractor():
    return UserFactory(is_contractor=True)


@pytest.fixture
def official():
    return UserFactory(is_official=True)


@pytest.fixture
def event():
    return EventFactory()


@pytest.fixture
def event_with_contract_zone():
    contract_zone = ContractZoneFactory(boundary=MultiPolygon(
        Polygon((
            (24, 60),
            (25, 60),
            (25, 61),
            (24, 61),
            (24, 60),
        ))
    ))
    event = EventFactory(location=Point(24.5, 60.5))
    assert event.contract_zone == contract_zone
    return event


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_api_client(api_client, user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    api_client.user = user
    return api_client


@pytest.fixture
def contractor_api_client(api_client, contractor):
    api_client = APIClient()
    api_client.force_authenticate(user=contractor)
    api_client.user = contractor
    return api_client


@pytest.fixture
def official_api_client(api_client, official):
    api_client = APIClient()
    api_client.force_authenticate(user=official)
    api_client.user = official
    return api_client
