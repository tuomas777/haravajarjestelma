import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from events.models import Event
from notifications.enums import NotificationType
from notifications.utils import send_notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Event)
def handle_event_save(sender, instance, created, **kwargs):
    if not created:
        return

    email = instance.contract_zone.get_contact_email()
    if not email:
        logger.warning(
            'Contract zone {} has no contact email so cannot send "event created" notification.'.format(
                instance.contract_zone
            )
        )
        return

    send_notification(email, NotificationType.EVENT_CREATED, {'event': instance})
