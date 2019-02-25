import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumField
from parler.models import TranslatableModel, TranslatedFields

from notifications.enums import NotificationType

logger = logging.getLogger(__name__)


class NotificationTemplateException(Exception):
    pass


class NotificationTemplate(TranslatableModel):
    type = EnumField(NotificationType, max_length=50, verbose_name=_('type'), unique=True)

    translations = TranslatedFields(
        subject=models.CharField(verbose_name=_('subject'), max_length=255),
        body_html=models.TextField(verbose_name=_('body, HTML version'), blank=True),
        body_text=models.TextField(
            verbose_name=_('body, plain text version'),
            blank=True,
            help_text=_('If left blank, the HTML version without HTML tags will be used.'),
        )
    )

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')

    def __str__(self):
        return str(self.type)
