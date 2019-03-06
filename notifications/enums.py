from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class NotificationType(Enum):
    EVENT_CREATED = 'event_created'

    class Labels:
        EVENT_CREATED = _('Event created')
