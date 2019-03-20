import pytest
from django.core import mail

from events.factories import EventFactory
from events.models import Event
from notifications.enums import NotificationType
from notifications.models import NotificationTemplate


@pytest.fixture
def notification_template_event_created():
    return NotificationTemplate.objects.language('fi').create(
        type=NotificationType.EVENT_CREATED,
        subject="test event created subject, event: {{ event.name }}!",
        body_html="<b>test event created body HTML!</b>",
        body_text="test event created body text!",

    )


@pytest.fixture
def notification_template_event_approved():
    return NotificationTemplate.objects.language('fi').create(
        type=NotificationType.EVENT_APPROVED,
        subject="test event approved subject, event: {{ event.name }}!",
        body_html="<b>test event approved body HTML!</b>",
        body_text="test event approved body text!",

    )


def test_event_created_notification_is_sent_to_contractor(contract_zone, user, notification_template_event_created):
    contract_zone.contractor_user = user
    contract_zone.save(update_fields=('contractor_user',))

    event = EventFactory()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'test event created subject, event: {}!'.format(event.name)


def test_event_created_notification_is_not_sent_to_other_contractor(contract_zone, user,
                                                                    notification_template_event_created):
    assert contract_zone.contractor_user != user

    EventFactory()

    assert len(mail.outbox) == 0


def test_notification_is_not_sent_when_event_modified_or_deleted(contract_zone, user,
                                                                 notification_template_event_created):
    contract_zone.contractor_user = user
    contract_zone.save(update_fields=('contractor_user',))
    event = EventFactory()
    mail.outbox = []

    event.name = 'foobar'
    event.save(update_fields=('name',))
    assert len(mail.outbox) == 0

    event.delete()
    assert len(mail.outbox) == 0


def test_event_approved_notification_is_sent_to_organizer(contract_zone, user, notification_template_event_approved):
    event = EventFactory(state=Event.WAITING_FOR_APPROVAL, organizer_email='organizer@example.com')
    mail.outbox = []
    event.state = Event.APPROVED
    event.save()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['organizer@example.com']
    assert mail.outbox[0].subject == 'test event approved subject, event: {}!'.format(event.name)
