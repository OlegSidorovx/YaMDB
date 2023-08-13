from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter

from .permissions import AdminRO


class ListCreateDeleteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = (SearchFilter,)
    permission_classes = (AdminRO, )
    search_fields = ('name', )
    lookup_field = 'slug'
    pass
