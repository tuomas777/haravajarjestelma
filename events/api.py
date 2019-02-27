from datetime import datetime, time, timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, viewsets

from areas.models import ContractZone
from events.models import ERROR_MSG_NO_CONTRACT_ZONE, Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('contract_zone',)

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        now = timezone.now()

        # PATCH updates only 'state', so check that start and end times are present in the data
        if (start_time and end_time) and (start_time > end_time):
            raise serializers.ValidationError(_('Event must start before ending.'))

        min_days = settings.EVENT_MINIMUM_DAYS_BEFORE_START
        beginning_of_today = datetime.combine(now.date(), time(), tzinfo=now.tzinfo)
        if start_time and (start_time < beginning_of_today + timedelta(days=min_days+1)):
            error_msg = _('Event cannot start earlier than {} full days from now.').format(min_days)
            raise serializers.ValidationError(error_msg)

        location = data.get('location')
        if location:
            data['contract_zone'] = ContractZone.objects.get_by_location(location)
            if not data['contract_zone']:
                raise serializers.ValidationError({'location': ERROR_MSG_NO_CONTRACT_ZONE})

        return data


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        return self.queryset.filter_for_user(self.request.user)
