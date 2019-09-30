import logging

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django_ilmoitin.registry import notifications
from django_ilmoitin.utils import send_notification
from enumfields import Enum

User = get_user_model()

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    EVENT_CREATED = "event_created"
    EVENT_APPROVED_TO_ORGANIZER = "event_approved_to_organizer"
    EVENT_APPROVED_TO_CONTRACTOR = "event_approved_to_contractor"
    EVENT_APPROVED_TO_OFFICIAL = "event_approved_to_official"

    class Labels:
        EVENT_CREATED = _("Event created")
        EVENT_APPROVED_TO_ORGANIZER = _("Event approved notification to organizer")
        EVENT_APPROVED_TO_CONTRACTOR = _("Event approved notification to contractor")
        EVENT_APPROVED_TO_OFFICIAL = _("Event approved notification to official")


notifications.register(
    NotificationType.EVENT_CREATED.value, NotificationType.EVENT_CREATED.label
)
notifications.register(
    NotificationType.EVENT_APPROVED_TO_ORGANIZER.value,
    NotificationType.EVENT_APPROVED_TO_ORGANIZER.label,
)
notifications.register(
    NotificationType.EVENT_APPROVED_TO_CONTRACTOR.value,
    NotificationType.EVENT_APPROVED_TO_CONTRACTOR.label,
)
notifications.register(
    NotificationType.EVENT_APPROVED_TO_OFFICIAL.value,
    NotificationType.EVENT_APPROVED_TO_OFFICIAL.label,
)


def send_event_created_notification(event):
    _send_notifications_to_contractor_and_officials(
        event, NotificationType.EVENT_CREATED
    )


def send_event_approved_notification(event):
    send_notification(
        event.organizer_email,
        NotificationType.EVENT_APPROVED_TO_ORGANIZER,
        {"event": event},
    )
    _send_notifications_to_contractor_and_officials(
        event,
        NotificationType.EVENT_APPROVED_TO_CONTRACTOR,
        NotificationType.EVENT_APPROVED_TO_OFFICIAL,
    )


def _send_notifications_to_contractor_and_officials(
    event, notification_type_contractor, notification_type_official=None
):
    if not notification_type_official:
        notification_type_official = notification_type_contractor

    contact_email = event.contract_zone.get_contact_email()
    if contact_email:
        send_notification(
            contact_email,
            notification_type_contractor,
            {"event": event, "user": event.contract_zone.contractor_user},
        )
    else:
        logger.warning(
            'Contract zone {} has no contact email so cannot send "{}" notification there.'.format(
                event.contract_zone, notification_type_contractor.label
            )
        )

    for official in User.objects.filter(is_official=True):
        send_notification(
            official.email,
            notification_type_official,
            {"event": event, "user": official},
        )
