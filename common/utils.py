from datetime import timedelta

import holidays
from django.utils.timezone import localtime, now

ONE_DAY = timedelta(days=1)
SATURDAY = 6
SUNDAY = 7
HOLIDAYS_FINLAND = holidays.Finland()


def get_today():
    return localtime(now()).date()


def date_range(start, end):
    current = start
    while current <= end:
        yield current
        current += ONE_DAY


def is_vacation_day(date):
    return date.isoweekday() in (SATURDAY, SUNDAY) or date in HOLIDAYS_FINLAND
