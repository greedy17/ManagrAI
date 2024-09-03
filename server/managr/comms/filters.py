import django_filters
from .models import JournalistContact
from django.db.models import Q


class JournalistContactFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_by_all_fields")

    class Meta:
        model = JournalistContact
        fields = []

    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            Q(journalist__first_name__icontains=value)
            | Q(journalist__last_name__icontains=value)
            | Q(journalist__email__icontains=value) | Q(journalist__outlet__icontains=value)
        )
