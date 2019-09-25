import logging

from django.utils.translation import ugettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications
from django_ilmoitin.utils import send_notification
from enumfields import Enum

from events.factories import EventFactory

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    EVENT_CREATED = "event_created"
    EVENT_APPROVED = "event_approved"

    class Labels:
        EVENT_CREATED = _("Event created")
        EVENT_APPROVED = _("Event approved")


notifications.register(
    NotificationType.EVENT_CREATED.value, NotificationType.EVENT_CREATED.label
)
notifications.register(
    NotificationType.EVENT_APPROVED.value, NotificationType.EVENT_APPROVED.label
)


# dummy_context.context.update({"event": EventFactory.build()})


def send_event_created_notification(event):
    email = event.contract_zone.get_contact_email()
    if not email:
        logger.warning(
            'Contract zone {} has no contact email so cannot send "event created" notification.'.format(
                event.contract_zone
            )
        )
        return

    send_notification(email, NotificationType.EVENT_CREATED, {"event": event})


def send_event_approved_notification(event):
    send_notification(
        event.organizer_email, NotificationType.EVENT_APPROVED, {"event": event}
    )
