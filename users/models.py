from django.db import models
from django.utils.translation import ugettext_lazy as _
from helusers.models import AbstractUser

from areas.models import ContractZone


class User(AbstractUser):
    is_official = models.BooleanField(verbose_name=_('official'), default=False)
    is_contractor = models.BooleanField(verbose_name=_('contractor'), default=False)
    contract_zones = models.ManyToManyField(
        ContractZone, verbose_name=_('contract zones'), related_name='contractors', blank=True
    )
