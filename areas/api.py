from collections import defaultdict

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from munigeo.models import Address, AdministrativeDivision, Street
from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import mixins, serializers, viewsets
from rest_framework.response import Response


class TranslatedModelSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField()

    def to_representation(self, obj):
        ret = super(TranslatedModelSerializer, self).to_representation(obj)
        if obj is None:
            return ret
        return self.translated_fields_to_representation(obj, ret)

    def translated_fields_to_representation(self, obj, ret):
        translated_fields = {}

        for lang_key, trans_dict in ret.pop('translations', {}).items():

            for field_name, translation in trans_dict.items():
                if field_name not in translated_fields:
                    translated_fields[field_name] = {lang_key: translation}
                else:
                    translated_fields[field_name].update({lang_key: translation})

        ret.update(translated_fields)

        return ret


class AdministrativeDivisionSerializer(TranslatedModelSerializer):
    bbox = serializers.ReadOnlyField(source='geometry.boundary.extent')

    class Meta:
        model = AdministrativeDivision
        fields = ('translations', 'ocd_id', 'origin_id', 'bbox')


class NeigborhoodSerializer(AdministrativeDivisionSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_districts'] = serializers.SerializerMethodField()

        sub_district_qs = self._get_base_sub_district_qs().filter(
            type__type='sub_district'
        ).exclude(
            origin_id='Aluemeri'  # wtf
        ).select_related(
            'geometry'
        ).prefetch_related(
            'translations'
        ).order_by(
            'origin_id'
        )

        # cache sub districts grouped by their parent origin_id for faster access
        sub_district_map = defaultdict(list)
        for sub_district in sub_district_qs:
            origin_id = sub_district.origin_id
            if origin_id.endswith('0'):
                # When a sub district id ends with '0', it means the neighborhood consists of only one sub district,
                # which for us means basically "the neighborhood has no sub districts", so we skip the sub district.
                # For example neighborhood Konala 32 has only one sub district, Konala 320.
                continue
            parent_origin_id = origin_id[:2]
            sub_district_map[parent_origin_id].append(sub_district)

        self._sub_district_map = sub_district_map

    def get_sub_districts(self, obj):
        sub_districts = self._sub_district_map.get(obj.origin_id, [])
        serializer = AdministrativeDivisionSerializer(sub_districts, many=True, context=self.context)
        return serializer.data

    def _get_base_sub_district_qs(self):
        if not isinstance(self.instance, AdministrativeDivision):
            return AdministrativeDivision.objects.all()

        # when we are dealing with a single neighborhood, we can skip some unnecessary work by fetching only
        # its sub districts instead of all districts
        try:
            int_origin_id = int(self.instance.origin_id)
        except ValueError:
            return AdministrativeDivision.objects.none()

        if int_origin_id >= 10:  # only neighborhoods with origin id >= 10 can have sub districts
            origin_id_min = self.instance.origin_id + '0'
            origin_id_max = self.instance.origin_id + '9'

            # filter sub districts based on the neighborhood's id,
            # for example for neighborhood 32 filter sub districts by id 320 - 329
            return AdministrativeDivision.objects.filter(
                type__type='sub_district', origin_id__gte=origin_id_min, origin_id__lte=origin_id_max
            )
        else:
            return AdministrativeDivision.objects.none()


class NeighborhoodViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AdministrativeDivision.objects.filter(
        type__type='neighborhood'
    ).select_related(
        'geometry'
    ).prefetch_related(
        'translations'
    ).order_by(
        'origin_id'
    )
    serializer_class = NeigborhoodSerializer


class GeoQueryParamSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=True)
    lon = serializers.FloatField(required=True)


class StreetSerializer(TranslatedModelSerializer):
    class Meta:
        model = Street
        fields = ('name', 'translations')


class AddressSerializer(serializers.ModelSerializer):
    street = StreetSerializer()
    distance = serializers.FloatField(source='distance.m')

    class Meta:
        model = Address
        exclude = ('id', 'modified_at')


class GeoQueryViewSet(viewsets.ViewSet):
    def list(self, request, format=None):
        param_serializer = GeoQueryParamSerializer(data=request.query_params)
        if not param_serializer.is_valid():
            return Response(param_serializer.errors)

        point = Point(param_serializer.validated_data['lon'], param_serializer.validated_data['lat'])
        areas = AdministrativeDivision.objects.filter(
            type__type='neighborhood',
            geometry__boundary__contains=point,
        )
        neighborhood = areas[0] if areas else None
        address = self.get_closest_address(point)

        data = {
            'neighborhood': NeigborhoodSerializer(neighborhood).data if neighborhood else None,
            'closest_address': AddressSerializer(address).data if address else None,
        }

        return Response(data)

    @classmethod
    def get_closest_address(cls, point):
        try:
            return Address.objects.annotate(distance=Distance('location', point)).order_by('distance')[0]
        except KeyError:
            return None
