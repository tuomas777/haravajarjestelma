from datetime import timedelta

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, viewsets

from events.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

    def validate(self, data):
        start_time = data.get('start_time', None)
        end_time = data.get('end_time', None)

        # PATCH updates only 'state', so check that start and end times are present in the data
        if (start_time and end_time) and (start_time > end_time):
            raise serializers.ValidationError(_('Event must start before ending.'))

        # TODO should the 7 day minimum waiting time be configurable from e.g. admin?
        # discussion can be had in https://github.com/City-of-Helsinki/haravajarjestelma/issues/8
        if start_time and (start_time < timezone.now() + timedelta(days=7)):
            raise serializers.ValidationError(_('Event cannot start earlier than a week from now.'))
        return data


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        return self.queryset.filter_for_user(self.request.user)
