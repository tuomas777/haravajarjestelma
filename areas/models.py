from collections import defaultdict
from datetime import timedelta

import holidays
from django.conf import settings
from django.contrib.gis.db import models
from django.utils.timezone import localtime, now
from django.utils.translation import ugettext_lazy as _
from munigeo.utils import get_default_srid

PROJECTION_SRID = get_default_srid()

ONE_DAY = timedelta(days=1)
SATURDAY = 6
SUNDAY = 7
HOLIDAYS_FINLAND = holidays.Finland()


class ContractZoneQuerySet(models.QuerySet):
    def get_by_location(self, location):
        return self.filter(boundary__covers=location).first()


class ContractZone(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=255)
    boundary = models.MultiPolygonField(verbose_name=_('boundary'), srid=PROJECTION_SRID)
    contact_person = models.CharField(verbose_name=_('contact person'), max_length=255, blank=True)
    email = models.EmailField(verbose_name=_('email'), blank=True)
    phone = models.CharField(verbose_name=_('phone'), max_length=255, blank=True)

    objects = ContractZoneQuerySet.as_manager()

    class Meta:
        verbose_name = _('contract zone')
        verbose_name_plural = _('contract zones')
        ordering = ('id',)

    def __str__(self):
        return self.name

    def get_unavailable_dates(self):
        """
        Return a list of dates for which it is not possible to create an Event ATM.
        """
        today = localtime(now()).date()
        last_too_early_day = today + timedelta(days=settings.EVENT_MINIMUM_DAYS_BEFORE_START)
        too_early_dates = {date for date in date_range(today, last_too_early_day)}

        events = self.events.filter(start_time__date__gt=last_too_early_day)
        day_event_map = defaultdict(set)

        for event in events:
            for date in date_range(localtime(event.start_time).date(), localtime(event.end_time).date()):
                for affected_date in get_affected_dates(date):
                    day_event_map[affected_date].add(event)

        too_many_events_dates = {
            date
            for date, events in day_event_map.items()
            if len(events) >= settings.EVENT_MAXIMUM_COUNT_PER_CONTRACT_ZONE
        }

        return list(sorted(too_early_dates | too_many_events_dates))


def get_affected_dates(date):
    """
    Return a list of all the dates in the "vacation day group" the given date belongs to

    The root need is that we have to calculate how many events there are on a specific
    day. Because contractors don't work on weekends or other vacation days, events on
    those days need to be added to closest preceding non-vacation day's event count.
    So this function returns all dates that are affected and therefore considered to be
    in the same "group" as the given date.

    Hopefully these couple of examples explain this a bit better (the examples have
    weekday names instead of actual dates to make it more simple):

    For a normal business day, this this will return just that day, Mon -> [Mon]
    For Fri, Sat or Sun, this this will return [Fri, Sat, Sun].
    For Mon or Tue when Tue is a national holiday, this this will return [Mon, Tue]
    For Thu, Fri, Sat, Sun or next week Mon when Thu, Fri and next week Mon are
    national holidays, this this will return [Thu, Fri, Sat, Sun, next week Mon]
    """
    start_date = end_date = date

    while is_vacation_day(start_date):
        start_date -= ONE_DAY
    while is_vacation_day(end_date + ONE_DAY):
        end_date += ONE_DAY

    return [d for d in date_range(start_date, end_date)]


def date_range(start, end):
    current = start
    while current <= end:
        yield current
        current += ONE_DAY


def is_vacation_day(date):
    return date.isoweekday() in (SATURDAY, SUNDAY) or date in HOLIDAYS_FINLAND
