import factory
from django.contrib.gis.geos import MultiPolygon, Polygon

from .models import ContractZone


class ContractZoneFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('bs')
    boundary = factory.Sequence(
        lambda n: MultiPolygon(
            Polygon((
                (24 + n, 60),
                (25 + n, 60),
                (25 + n, 61),
                (24 + n, 61),
                (24 + n, 60),
            ))
        )
    )

    class Meta:
        model = ContractZone
