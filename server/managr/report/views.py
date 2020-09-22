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

from managr.core.models import User
from managr.lead.models import Lead
from managr.core.background import emit_report_event
from .models import (
   StoryReport,
   PerformanceReport,
)
from .serializers import (
    StoryReportSerializer,
    PerformanceReportSerializer,
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
        emit_report_event(str(report.id), str(generated_by.id))
        return Response(data=self.serializer_class(report).data, status=status.HTTP_200_OK)


class PerformanceReportViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = PerformanceReportSerializer

    def get_queryset(self):
        return PerformanceReport.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        generated_by = request.user
        representative = request.data.get('representative')
        date_range = request.data.get('date_range')

        if representative:
            try:
                representative = User.objects.get(pk=representative)
            except User.DoesNotExist:
                raise ValidationError({'representative': 'does not exist'})

        report = PerformanceReport.objects.create(
            representative=representative,
            date_range=date_range,
            generated_by=generated_by,
        )

        # TODO: async report data generation.
        # below is for story report, therefore give it a more specific name or use for
        # both report types
        # emit_report_event(str(report.id), str(generated_by.id))
        return Response(data=self.serializer_class(report).data, status=status.HTTP_200_OK)
