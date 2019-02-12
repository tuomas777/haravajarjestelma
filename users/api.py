from django.contrib.auth import get_user_model
from rest_framework import mixins, serializers, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uuid', 'first_name', 'last_name', 'is_official', 'is_contractor')


class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'uuid'

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            raise NotFound

        if kwargs['uuid'] == 'me':
            instance = self.request.user
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        if kwargs['uuid'] != str(user.uuid):
            raise NotFound

        return super().retrieve(request, *args, **kwargs)
