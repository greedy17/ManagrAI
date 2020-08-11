import requests
import logging
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.db.models import F, Q, Count

from rest_framework import (
    authentication,
    filters,
    permissions,
    generics,
    mixins,
    status,
    views,
    viewsets,
)

from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from managr.lead.models import Lead
from .models import (
   StoryReport,
)
from .serializers import (
    StoryReportSerializer,
)

logger = logging.getLogger("managr")


class StoryReportViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):

    serializer_class = StoryReportSerializer
    filter_fields = ("lead",)

    def get_queryset(self):
        return StoryReport.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        generated_by = request.user
        lead = request.data.get('lead')
        if not lead:
            raise ValidationError({'lead': 'required field'})
        try:
            lead = Lead.objects.get(pk=lead)
        except Lead.DoesNotExist:
            raise ValidationError({'lead': 'does not exist'})
        report = StoryReport.objects.create(lead=lead, generated_by=generated_by)
        # # The following should be async:
        # send_email_for_report()
        return Response(data=self.serializer_class(report).data, status=status.HTTP_200_OK)


# build generate_report_data(report) => data & datetime_generated
# explore async & triggering email
# build skeleton of /story-report/:id
# tests (e.g. structure/contents of JSON Field)
# explore graph libraries / LOE analysis on report design
