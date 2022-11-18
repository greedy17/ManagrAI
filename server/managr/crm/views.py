from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    permissions,
    status,
    mixins,
    viewsets,
)

from managr.crm.models import ObjectField
from managr.crm.serializers import ObjectFieldSerializer
from managr.crm.filters import ObjectFieldFilterSet

# Create your views here.


class ObjectFieldViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ObjectFieldSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ("label",)
    filter_class = ObjectFieldFilterSet

    def get_queryset(self):
        return ObjectField.objects.for_user(self.request.user)
