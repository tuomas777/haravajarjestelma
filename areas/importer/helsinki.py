import logging
import urllib

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.db import transaction

from areas.models import ContractZone

from .utils import ModelSyncher

logger = logging.getLogger(__name__)


class HelsinkiImporter:
    def import_contract_zones(self):
        logger.info('Importing Helsinki contract zones')

        data_source = self._fetch_contract_zones()
        self._process_contract_zones(data_source)

        logger.info('Helsinki contract zone import done!')

    def _fetch_contract_zones(self):
        query_params = {
            'SERVICE': 'WFS',
            'VERSION': '2.0.0',
            'REQUEST': 'GetFeature',
            'TYPENAME': 'avoindata:Vastuualue_rya_urakkarajat',
            'SRSNAME': 'EPSG:{}'.format(settings.DEFAULT_SRID),
            'cql_filter': "tehtavakokonaisuus='PUISTO' and status='voimassa'",
        }
        wfs_url = '{}?{}'.format(settings.HELSINKI_WFS_BASE_URL, urllib.parse.urlencode(query_params))

        logger.debug('Fetching contract zone data from url {}'.format(wfs_url))
        data_source = DataSource(wfs_url)
        logger.debug('Fetched {} active contract zones'.format(len(data_source[0])))

        return data_source

    @transaction.atomic
    def _process_contract_zones(self, data_source):
        layer = data_source[0]
        syncher = ModelSyncher(ContractZone.objects.all(), lambda x: x.origin_id, self._deactivate_contract_zone)

        for feat in layer:
            data = {
                'name': str(feat['nimi']),
                'boundary': feat.geom.geos,
                'contractor': str(feat['urakoitsija']),
                'origin_id': str(feat['id']),
                'active': True,
            }

            contract_zone = syncher.get(data['origin_id'])
            if contract_zone:
                logger.info('Updating contract zone {} (id {})'.format(data['name'], data['origin_id']))
                for field, new_value in data.items():
                    setattr(contract_zone, field, new_value)
            else:
                logger.info('Creating new contract zone {} (id {})'.format(data['name'], data['origin_id']))
                contract_zone = ContractZone(**data)

            contract_zone.save()
            syncher.mark(contract_zone)

        syncher.finish()

    @staticmethod
    def _deactivate_contract_zone(contract_zone):
        if contract_zone.active:
            contract_zone.active = False
            contract_zone.save(update_fields=('active',))
