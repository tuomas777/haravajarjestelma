import pytest
from rest_framework.test import APIClient

from common.tests.conftest import *  # noqa
from users.factories import UserFactory


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
