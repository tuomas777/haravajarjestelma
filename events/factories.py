from datetime import timedelta

import factory.fuzzy
from django.contrib.gis.geos import Point
from django.utils import timezone
from factory.random import randgen

from areas.models import ContractZone

from .models import Event


class EventFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('bs')
    description = factory.Faker('text')
    start_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=8, hours=randgen.randint(1, 6)))
    end_time = factory.LazyAttribute(lambda e: e.start_time + timedelta(hours=randgen.randint(1, 6)))
    location = factory.LazyFunction(
        lambda: Point(24.915 + randgen.uniform(0, 0.040), 60.154 + randgen.uniform(0, 0.022))
    )
    organizer_first_name = factory.Faker('first_name')
    organizer_last_name = factory.Faker('last_name')
    organizer_email = factory.Faker('email')
    organizer_phone = factory.Faker('phone_number')
    estimated_attendee_count = factory.fuzzy.FuzzyInteger(1, 100)
    targets = factory.Faker('text')
    maintenance_location = factory.Faker('address')
    additional_information = factory.Faker('text')
    trash_bag_count = factory.fuzzy.FuzzyInteger(1, 500)
    trash_picker_count = factory.fuzzy.FuzzyInteger(1, 50)
    equipment_information = factory.Faker('text')
    contract_zone = factory.LazyAttribute(lambda e: ContractZone.objects.get_by_location(e.location))

    class Meta:
        model = Event
