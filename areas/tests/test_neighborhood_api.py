from parler.utils.context import switch_language
from rest_framework.reverse import reverse

from areas.factories import NeighborhoodFactory, SubDistrictFactory
from common.tests.utils import check_translated_field_data_matches_object, get

LIST_URL = reverse("v1:neighborhood-list")

NEIGHBORHOOD_KEYS = {"name", "ocd_id", "origin_id", "bbox", "sub_districts"}

SUB_DISTRICT_KEYS = {"name", "ocd_id", "origin_id", "bbox"}


def check_division_data_matches_object(division_data, division_obj):
    if division_data is None:
        assert division_obj is None
        return
    if division_obj.type.type == "neighborhood":
        keys = NEIGHBORHOOD_KEYS
    elif division_obj.type.type == "sub_district":
        keys = SUB_DISTRICT_KEYS
    else:
        raise AssertionError(
            "Unknown division object type {}.".format(type(division_obj))
        )
    assert set(division_data.keys()) == keys

    check_translated_field_data_matches_object(division_data, division_obj, "name")
    assert division_data["ocd_id"] == division_obj.ocd_id
    assert division_data["origin_id"] == division_obj.origin_id
    assert division_data["bbox"] == division_obj.geometry.boundary.extent


def test_get_list_check_data(api_client):
    neighborhood_1 = NeighborhoodFactory(origin_id="10")
    neighborhood_2 = NeighborhoodFactory()
    sub_district_1 = SubDistrictFactory(origin_id="101")
    SubDistrictFactory(origin_id="201")  # should not be visible
    sub_district_2 = SubDistrictFactory(origin_id="102")

    with switch_language(neighborhood_1, "fi"):
        neighborhood_1.name = "kaupunginosan nimi"
        neighborhood_1.save()
    with switch_language(sub_district_1, "fi"):
        sub_district_1.name = "osa-alueen nimi"
        sub_district_1.save()

    response_data = get(api_client, LIST_URL)["results"]

    assert len(response_data) == 2
    check_division_data_matches_object(response_data[0], neighborhood_1)
    check_division_data_matches_object(response_data[1], neighborhood_2)

    sub_districts_data = response_data[0]["sub_districts"]
    assert len(sub_districts_data) == 2
    check_division_data_matches_object(sub_districts_data[0], sub_district_1)
    check_division_data_matches_object(sub_districts_data[1], sub_district_2)
