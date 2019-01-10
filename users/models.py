from django.db import models
from django.utils.translation import ugettext_lazy as _
from helusers.models import AbstractUser

from areas.models import ContractZone


class User(AbstractUser):
    is_official = models.BooleanField(verbose_name=_('official'), default=False)
    is_contractor = models.BooleanField(verbose_name=_('contractor'), default=False)

