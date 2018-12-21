from collections import defaultdict

from munigeo.models import AdministrativeDivision
from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import mixins, serializers, viewsets


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

        sub_district_qs = AdministrativeDivision.objects.filter(
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
