from django.core.management.base import BaseCommand

from areas.importer.helsinki import HelsinkiImporter


class Command(BaseCommand):
    help = "Import Helsinki contract zones"

    def handle(self, *args, **options):
        HelsinkiImporter().import_contract_zones()
