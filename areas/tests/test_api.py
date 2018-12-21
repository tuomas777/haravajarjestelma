import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_smoke(client):
    response = client.get(reverse('v1:neighborhood-list'))
    assert response.status_code == 200
