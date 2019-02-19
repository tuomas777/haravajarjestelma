from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from munigeo.utils import get_default_srid

PROJECTION_SRID = get_default_srid()


class ContractZone(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=255)
    boundary = models.MultiPolygonField(verbose_name=_('boundary'), srid=PROJECTION_SRID)
    contact_person = models.CharField(verbose_name=_('contact person'), max_length=255, blank=True)
    email = models.EmailField(verbose_name=_('email'), blank=True)
    phone = models.CharField(verbose_name=_('phone'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('contract zone')
        verbose_name_plural = _('contract zones')
        ordering = ('id',)

    def __str__(self):
        return self.name
