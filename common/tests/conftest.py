import factory.random
import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient


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
def force_settings(settings):
    settings.LANGUAGE_CODE = 'en'
    settings.EVENT_MINIMUM_DAYS_BEFORE_START = 7


@pytest.fixture(autouse=True)
def autouse_django_db(db):
    pass


@pytest.fixture
def api_client():
    return APIClient()
