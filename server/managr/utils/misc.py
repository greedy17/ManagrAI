from django.conf import settings
from django.utils import timezone

from rest_framework.response import Response
from rest_framework import filters


def datetime_appended_filepath(instance, filename):
    """
    Appending datetime to filepath makes each filepath unique.
    This prevents users from overwriting each others' files.
    """
    extension = filename.split('.')[-1]
    original_name = filename.split('.')[:-1][0]
    time = str(timezone.now().isoformat())
    time = time.split('.')[0]  # Remove trailing tz info
    name = f'{original_name}_{time}.{extension}'
    return name


def apply_filter_and_search(viewset, request):
    """
    Apply filter parameters and search query to a detailed endpoint.
    """
    # Get appropriate results from queryset method
    results = viewset.get_queryset()

    # Instantiate filter class to apply all query params as filters
    filter_set = viewset.filter_class(
        request=request,
        data=request.query_params
    )
    if filter_set.is_valid():
        results = filter_set.filter_queryset(results)

    # Apply 'search' filter to results as well, and return
    filter = filters.SearchFilter()
    return filter.filter_queryset(request, results, viewset)


def paginate_results(viewset, results, serializer, request=None):
    """
    Paginate results of a detail endpoint, which doesn't automatically
    respect default pagination settings.
    """
    page = viewset.paginate_queryset(results)

    if page is not None:
        serializer = serializer(page, many=True, context={'request': request})
        return viewset.get_paginated_response(serializer.data)

    serializer = serializer(results, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


def get_site_url():
    """Get the full base URL for this site based on settings."""
    protocol = 'http' if settings.IN_DEV else 'https'
    domain = settings.CURRENT_DOMAIN
    return '{0}://{1}{2}'.format(
        protocol,
        domain,
        f':{settings.CURRENT_PORT}' if settings.CURRENT_PORT else ''
    )
