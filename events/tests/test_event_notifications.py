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
        subject="test subject, event: {{ event.name }}!",
        body_html="<b>test body HTML!</b>",
        body_text="test body text!",

    )


def test_event_created_notification_is_sent_to_contractor(contract_zone, user, notification_template_event_created):
    contract_zone.contractor_user = user
    contract_zone.save(update_fields=('contractor_user',))

    event = EventFactory()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'test subject, event: {}!'.format(event.name)


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

    event.state = Event.APPROVED
    event.save(update_fields=('state',))
    assert len(mail.outbox) == 0

    event.delete()
    assert len(mail.outbox) == 0
