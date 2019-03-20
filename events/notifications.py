import logging

from notifications.enums import NotificationType
from notifications.utils import send_notification

logger = logging.getLogger(__name__)


def send_event_created_notification(event):
    email = event.contract_zone.get_contact_email()
    if not email:
        logger.warning(
            'Contract zone {} has no contact email so cannot send "event created" notification.'.format(
                event.contract_zone
            )
        )
        return

    send_notification(email, NotificationType.EVENT_CREATED, {'event': event})


def send_event_approved_notification(event):
    send_notification(event.organizer_email, NotificationType.EVENT_APPROVED, {'event': event})
