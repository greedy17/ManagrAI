from django_filters.rest_framework import FilterSet

from .models import Contact


class ContactFilterSet(FilterSet):

    class Meta:
        model = Contact
        fields = ('account',)
