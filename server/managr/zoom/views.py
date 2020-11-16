from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.conf import settings

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
from rest_framework.decorators import (
    api_view,
    permission_classes,
)


from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from managr.zoom.zoom_helper import constants as zoom_model_consts
from managr.zoom.zoom_helper.models import ZoomAcct


# Create your views here.


@api_view(["get"])
@permission_classes([permissions.IsAuthenticated])
def get_zoom_auth_link(request):
    link = ZoomAcct.get_authorization()
    return Response({"link": link})


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def get_zoom_authentication(request):
    code = request.data.get("code", None)
    if not code:
        raise ValidationError()
    return Response()


def redirect_from_zoom(request):
    ## decide on whether i should do this directly or not since it is an open endpoint
    code = request.GET.get("code", None)
    q = urlencode({"code": code})
    if not code:
        err = {"error": "there was an error"}
        err = urlencode(err)
        return redirect(f"{zoom_model_consts.ZOOM_FRONTEND_REDIRECT}")
    return redirect(f"{zoom_model_consts.ZOOM_FRONTEND_REDIRECT}?{q}")

