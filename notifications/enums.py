from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class NotificationType(Enum):
    EVENT_CREATED = 'event_created'
    EVENT_APPROVED = 'event_approved'

    class Labels:
        EVENT_CREATED = _('Event created')
        EVENT_APPROVED = _('Event approved')
