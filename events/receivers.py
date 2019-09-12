from django.db.models.signals import post_save
from django.dispatch import receiver

from events.models import Event
from events.notifications import (
    send_event_approved_notification,
    send_event_created_notification,
)
from events.signals import event_approved


@receiver(post_save, sender=Event, dispatch_uid="send_notification_on_creation")
def send_notification_on_creation(sender, instance, created, **kwargs):
    if created:
        send_event_created_notification(instance)


@receiver(event_approved, sender=Event, dispatch_uid="send_notification_on_approval")
def send_notification_on_approval(sender, instance, **kwargs):
    send_event_approved_notification(instance)
