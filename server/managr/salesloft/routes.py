from managr.salesloft import constants as sl_consts
from managr.salesloft import models as sl_models
from managr.salesloft import serializers as sl_serializers

routes = {
    sl_consts.SALESLOFT_RESOURCE_PEOPLE: {
        "model": sl_models.People,
        "serializer": sl_serializers.PeopleSerializer,
    },
    sl_consts.SALESLOFT_RESOURCE_CADENCE: {
        "model": sl_models.Cadence,
        "serializer": sl_serializers.CadenceSerializer,
    },
    sl_consts.SALESLOFT_RESOURCE_SLACCOUNT: {
        "model": sl_models.SLAccount,
        "serializer": sl_serializers.SLAccountSerializer,
    },
}
