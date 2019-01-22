import pytest
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from rest_framework.reverse import reverse

from common.tests.utils import check_translated_field_data_matches_object, get

from ..factories import AddressFactory, NeighborhoodFactory, SubDistrictFactory
from .test_neighborhood_api import check_division_data_matches_object

URL = reverse('v1:geo_query-list')

ADDRESS_KEYS = {'street', 'distance', 'number', 'number_end', 'letter', 'location'}


def get_url(lat, lon):
    return URL + '?lat={}&lon={}'.format(lat, lon)


def check_address_data_matches_object(address_data, address_obj):
    assert set(address_data.keys()) == ADDRESS_KEYS

    for field_name in ('number', 'number_end', 'letter'):
        assert address_data[field_name] == getattr(address_obj, field_name)
    assert len(address_data['location']['coordinates']) == 2

    street_data = address_data['street']
    assert set(street_data.keys()) == {'name'}
    check_translated_field_data_matches_object(street_data, address_obj.street, 'name')


@pytest.fixture
def neighborhoods():
    # three side by side neighborhoods with origin ids 10, 11 and 12
    return [
        NeighborhoodFactory(
            origin_id=str(10+n),
            geometry__boundary=MultiPolygon(Polygon((
                (24+n, 60),
                (25+n, 60),
                (25+n, 61),
                (24+n, 61),
                (24+n, 60),
            )))
        ) for n in range(3)
    ]


@pytest.fixture
def sub_district():
    # this should be the sub district of the second neighborhood of the "neighborhoods" fixture
    return SubDistrictFactory(origin_id='111')


@pytest.fixture
def addresses():
    return [AddressFactory(location=Point((lon, 60))) for lon in (24, 27, 30)]


def test_required_parameters(api_client):
    response_data = get(api_client, URL)
    assert all(param in response_data for param in ('lat', 'lon'))


def test_no_neighborhood_or_address_objects_in_database(api_client):
    response_data = get(api_client, get_url(60.0, 24.0))
    assert response_data['neighborhood'] is None
    assert response_data['closest_address'] is None


def test_no_matching_neighborhood(api_client, neighborhoods):
    response_data = get(api_client, get_url(67.0, 24.5))
    assert response_data['neighborhood'] is None


def test_neighborhood_matches_check_data(api_client, neighborhoods, sub_district):
    SubDistrictFactory(origin_id='151')  # some irrelevant sub district
    response_data = get(api_client, get_url(60.5, 25.5))

    neighborhood_data = response_data['neighborhood']
    check_division_data_matches_object(neighborhood_data, neighborhoods[1])

    sub_districts_data = neighborhood_data['sub_districts']
    assert len(sub_districts_data) == 1
    check_division_data_matches_object(sub_districts_data[0], sub_district)


def test_closest_address_check_data(api_client, addresses):
    response_data = get(api_client, get_url(60.0, 26.0))
    check_address_data_matches_object(response_data['closest_address'], addresses[1])


def test_neighborhood_borders_count_also(api_client, neighborhoods):
    response_data = get(api_client, get_url(60, 24))
    check_division_data_matches_object(response_data['neighborhood'], neighborhoods[0])
