from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, viewsets

from areas.models import ContractZone, date_range
from common.api import UTCModelSerializer
from events.models import ERROR_MSG_NO_CONTRACT_ZONE, Event


class EventSerializer(UTCModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('contract_zone',)

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # PATCH updates only 'state', so check that start and end times are present in the data
        if (start_time and end_time) and (start_time > end_time):
            raise serializers.ValidationError(_('Event must start before ending.'))

        location = data.get('location')
        if location:
            data['contract_zone'] = ContractZone.objects.get_by_location(location)
            if not data['contract_zone']:
                raise serializers.ValidationError({'location': ERROR_MSG_NO_CONTRACT_ZONE})

            if start_time or end_time:
                start_date = localtime(start_time or self.instance.start_time).date()
                end_date = localtime(end_time or self.instance.end_time).date()
                zone_unavailable_dates = data['contract_zone'].get_unavailable_dates()
                unavailable_dates = set(date_range(start_date, end_date)) & set(zone_unavailable_dates)
                if unavailable_dates:
                    raise serializers.ValidationError(_('Unavailable dates: {}'.format(sorted(unavailable_dates))))

        return data


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        return self.queryset.filter_for_user(self.request.user)
