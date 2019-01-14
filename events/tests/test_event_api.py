from datetime import timedelta

from django.utils import timezone
from rest_framework.reverse import reverse

from events.models import Event
from events.tests.utils import delete, get, patch, post, put

LIST_URL = reverse('v1:event-list')

EXPECTED_EVENT_KEYS = {
    'id',
    'created_at',
    'modified_at',
    'name',
    'description',
    'start_time',
    'end_time',
    'location',
    'state',
    'organizer_first_name',
    'organizer_last_name',
    'organizer_email',
    'organizer_phone',
    'estimated_attendee_count',
    'targets',
    'maintenance_location',
    'additional_information',
    'has_roll_off_dumpster',
    'trash_bag_count',
    'trash_picker_count',
    'contract_zone',
}

EVENT_DATA = {
    'name': 'Testitalkoot',
    'description': "Testitalkoissa haravoidaan ahkerasti.",
    'start_time': timezone.now() + timedelta(days=8, hours=6),
    'end_time': timezone.now() + timedelta(days=8, hours=12),
    'location': {
        'type': 'Point',
        'coordinates': [
            24.95,
            60.20,
        ]
    },
    'organizer_first_name': 'Matti',
    'organizer_last_name': 'Meikäläinen',
    'organizer_email': 'matti.meikalainen@tut.fi',
    'organizer_phone': '555-123456',
    'estimated_attendee_count': 1000,
    'targets': 'Kaikki mikä ei liiku',
    'maintenance_location': 'Kumputie 7',
    'additional_information': 'Ei lisätietoja.',
    'has_roll_off_dumpster': True,
    'trash_bag_count': 10000,
    'trash_picker_count': 7,
}


def check_received_event_data(event_data, event_obj):
    """
    Check that data received from the API matches the given object
    """
    assert set(event_data) == EXPECTED_EVENT_KEYS

    simple_fields = (
        'id',
        'name',
        'description',
        'organizer_first_name',
        'organizer_last_name',
        'organizer_email',
        'organizer_phone',
        'estimated_attendee_count',
        'targets', 'maintenance_location',
        'additional_information',
        'has_roll_off_dumpster',
        'trash_bag_count',
        'trash_picker_count',
    )
    for field_name in simple_fields:
        assert event_data[field_name] == getattr(event_obj, field_name), 'Field "{}" does not match'.format(field_name)

    assert event_data['created_at']
    assert event_data['modified_at']
    assert len(event_data['location']['coordinates']) == 2
    assert not event_data['contract_zone']


def check_event_object(event_obj, event_data):
    """
    Check that a created/updated event object matches the given data
    """
    for field_name, field_value in event_data.items():
        if field_name == 'location':
            continue
        assert field_value == getattr(event_obj, field_name), 'Field "{}" does not match'.format(field_name)
    assert event_obj.location


def get_detail_url(event):
    return reverse('v1:event-detail', kwargs={'pk': event.pk})


def test_unauthenticated_user_get_list_no_results(event, api_client):
    results = get(api_client, LIST_URL)['results']
    assert len(results) == 0


def test_unauthenticated_user_get_detail_404(event, api_client):
    get(api_client, get_detail_url(event), 404)


def test_official_get_list_check_data(api_client, official, event):
    api_client.force_authenticate(user=official)

    results = get(api_client, LIST_URL)['results']

    assert len(results) == 1
    data = results[0]
    check_received_event_data(data, event)


def test_official_get_detail_check_data(api_client, official, event):
    api_client.force_authenticate(user=official)

    data = get(api_client, get_detail_url(event))
    check_received_event_data(data, event)


def test_unauthenticated_user_post_new_event(user_api_client):
    post(user_api_client, LIST_URL, EVENT_DATA)

    assert Event.objects.count() == 1
    new_event = Event.objects.latest('id')
    check_event_object(new_event, EVENT_DATA)


def test_official_put_event(official_api_client, event):
    put(official_api_client, get_detail_url(event), EVENT_DATA)

    assert Event.objects.count() == 1
    updated_event = Event.objects.latest('id')
    check_event_object(updated_event, EVENT_DATA)


def test_official_patch_event(official_api_client, event):
    old_name = event.name
    assert old_name != EVENT_DATA['name']
    assert event.state == 'waiting_for_approval'

    patch(official_api_client, get_detail_url(event), {'state': 'approved'})

    assert Event.objects.count() == 1
    updated_event = Event.objects.latest('id')
    assert updated_event.name == old_name
    assert updated_event.state == 'approved'


def test_unautenticated_user_cannot_modify_or_delete_event(user_api_client, event_with_contract_zone):
    url = get_detail_url(event_with_contract_zone)

    put(user_api_client, url, EVENT_DATA, 404)
    patch(user_api_client, url, EVENT_DATA, 404)
    delete(user_api_client, url, 404)


def test_contractor_cannot_modify_or_delete_other_than_own_event(contractor_api_client, event_with_contract_zone):
    url = get_detail_url(event_with_contract_zone)

    put(contractor_api_client, url, EVENT_DATA, 404)
    patch(contractor_api_client, url, EVENT_DATA, 404)
    delete(contractor_api_client, url, 404)


def test_contractor_can_modify_and_delete_own_event(contractor_api_client, event_with_contract_zone):
    contractor_api_client.user.contract_zones.add(event_with_contract_zone.contract_zone)
    url = get_detail_url(event_with_contract_zone)

    put(contractor_api_client, url, EVENT_DATA)
    patch(contractor_api_client, url, EVENT_DATA)
    delete(contractor_api_client, url)


def test_official_can_modify_and_delete_event(official_api_client, event_with_contract_zone):
    url = get_detail_url(event_with_contract_zone)

    put(official_api_client, url, EVENT_DATA)
    patch(official_api_client, url, EVENT_DATA)
    delete(official_api_client, url)
