from django.conf import settings
import logging
import json
from requests.exceptions import HTTPError
from managr.utils.client import Client
from .exceptions import CustomAPIException
from urllib.parse import urlencode
from managr.utils.misc import object_to_snake_case
from .. import constants as hubspot_consts
from managr.core.models import User
from managr.organization import constants as org_consts

logger = logging.getLogger("managr")


DATA_TYPE_OBJ = {
    "calculation_score": "Int",
    "text": "String",
    "checkbox": "Boolean",
    "radio": "Picklist",
    "booleancheckbox": "Boolean",
    "calculation_read_time": "DateTime",
    "phonenumber": "Phone",
    "select": "Picklist",
    "date": "Date",
    "number": "Int",
    "calculation_rollup": "Int",
    "textarea": "TextArea",
    "calculation_equation": "Int",
    "text": "String",
}

REFERENCE_INFO_OBJ = {
    "OWNER": ["firstname", "lastname"],
    "COMPANY": ["name"],
    "DEAL": ["dealname"],
    "CONTACT": ["email"],
}


class HubspotAuthAccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.hubspot_id = kwargs.get("hubspot_id", None)
        self.user = kwargs.get("user", None)
        self.hubspot_fields = kwargs.get("hubspot_fields", None)
        self.object_fields = kwargs.get("object_fields", {})

    @property
    def internal_user(self):
        return User.objects.get(id=self.user)

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code == 200 or response.status_code == 201:
            if response.status_code == 204:
                return {}
            try:
                data = response.json()
            except Exception as e:
                CustomAPIException(e, fn_name)
        else:
            status_code = response.status_code
            error_data = response.json()
            if status_code == 400:
                error_param = error_data.get("error", error_data.get("errorCode", None))
                error_message = error_data.get("error_description", error_data.get("message", None))
            else:
                error_param = error_data.get("category", None)
                error_message = error_data.get("message", None)
            kwargs = {
                "status_code": status_code,
                "error_param": error_param,
                "error_message": error_message,
            }

            CustomAPIException(HTTPError(kwargs), fn_name)
        return data

    @classmethod
    def create_account(cls, code, user_id):
        user = User.objects.get(id=user_id)
        res = cls.authenticate(code)
        if settings.IN_DEV:
            # user_res = cls.get_user_info(res["access_token"], "support@mymanagr.com")["results"]
            user_res = cls.get_user_info(res["access_token"], user.email)["results"]
        else:
            user_res = cls.get_user_info(res["access_token"], user.email)["results"]
        data = {
            "user": user.id,
            "access_token": res.get("access_token"),
            "refresh_token": res.get("refresh_token"),
            "hubspot_id": user_res[0].get("id") if len(user_res) else None,
        }
        return cls(**data)

    def _format_resource_response(self, response_data, class_name, *args, **kwargs):

        res = response_data.get("results", [])
        formatted_data = []
        from .routes import routes

        resource_class = routes.get(class_name, None)
        for result in res:
            if resource_class:
                formatted_data.append(
                    resource_class.from_api(result["properties"], self.user, *args)
                )
            else:
                formatted_data.append(result)

        return formatted_data

    def format_field_options(
        self, hubspot_account_id, user_id, resource, res_data=[],
    ):
        fields = res_data["results"]
        custom_additions = dict(user=user_id, crm_object=resource, imported_by=user_id,)
        data = [HObjectFieldAdapter.create_from_api({**f, **custom_additions}) for f in fields]

        return data

    def list_deal_stages(self, resource):
        url = hubspot_consts.HUBSPOT_PIPELINE_URI(resource)
        headers = hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token)
        with Client as client:
            res = client.get(url, headers=headers,)
            return self._handle_response(res)

    def associate_objects(
        self, associate_type, associate_id, to_object, to_object_id, association_id
    ):
        url = hubspot_consts.HUBSPOT_ASSOCIATIONS_CREATE_URI(
            associate_type, associate_id, to_object, to_object_id
        )
        headers = hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token)
        payload = (
            '[{"associationCategory":"HUBSPOT_DEFINED","associationTypeId":'
            + f"{association_id}"
            + "}]"
        )
        with Client as client:
            res = client.put(url, headers=headers, data=payload,)
            return self._handle_response(res)

    def get_associated_resource(self, resource, associated_resource, resource_id):
        url = hubspot_consts.HUBSPOT_ASSOCIATIONS_READ_URI(resource, associated_resource)
        headers = hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token)
        data = {"inputs": [{"id": resource_id}]}
        with Client as client:
            res = client.post(url, data=json.dumps(data), headers=headers,)
            return self._handle_response(res)

    def create_meeting_in_hubspot(self, meeting_data):
        url = hubspot_consts.HUBSPOT_RESOURCE_URI("meetings")
        headers = hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token)
        send_data = {"properties": meeting_data}
        with Client as client:
            res = client.post(url, data=json.dumps(send_data), headers=headers,)
            return self._handle_response(res)

    def create_note_in_hubspot(self, note_data):
        url = hubspot_consts.HUBSPOT_RESOURCE_URI("notes")
        headers = hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token)
        send_data = {"properties": note_data}
        with Client as client:
            res = client.post(url, data=json.dumps(send_data), headers=headers,)
            return self._handle_response(res)

    @staticmethod
    def get_authorization():
        query = urlencode(hubspot_consts.AUTHORIZATION_QUERY_PARAMS)
        return f"{hubspot_consts.AUTHORIZATION_URI}?{query}"

    @staticmethod
    def authenticate(code):
        data = hubspot_consts.AUTHENTICATION_BODY(code)
        with Client as client:
            res = client.post(
                f"{hubspot_consts.AUTHENTICATION_URI}",
                data=data,
                headers=hubspot_consts.AUTHENTICATION_HEADERS,
            )
            return HubspotAuthAccountAdapter._handle_response(res)

    @staticmethod
    def get_user_info(access_token, email):
        with Client as client:
            res = client.get(
                hubspot_consts.HUBSPOT_OWNERS_URI(email),
                headers=hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token),
            )
        return HubspotAuthAccountAdapter._handle_response(res)

    def refresh(self):
        with Client as client:
            data = hubspot_consts.REAUTHENTICATION_BODY(self.refresh_token)
            res = client.post(
                f"{hubspot_consts.BASE_URL}{hubspot_consts.REFRESH_TOKEN_URI}",
                data=data,
                headers=hubspot_consts.AUTHENTICATION_HEADERS,
            )
            return HubspotAuthAccountAdapter._handle_response(res)

    def list_fields(self, resource):
        url = f"{hubspot_consts.BASE_URL}{hubspot_consts.HUBSPOT_PROPERTIES_URI}{resource}"
        with Client as client:
            res = client.get(
                url, headers=hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)
            return self.format_field_options(str(self.id), str(self.user), resource, res_data=res)

    def list_resource_data(self, resource, *args, **kwargs):
        # add extra fields to query string
        from ..routes import routes

        resource_fields = self.internal_user.object_fields.filter(crm_object=resource).values_list(
            "api_name", flat=True
        )
        add_filters = kwargs.get(
            "filters",
            [{"propertyName": "hubspot_owner_id", "operator": "EQ", "value": self.hubspot_id}],
        )
        resource_class = routes.get(resource)
        limit = kwargs.pop("limit", hubspot_consts.HUBSPOT_QUERY_LIMIT)
        url = hubspot_consts.HUBSPOT_SEARCH_URI(resource)
        data = hubspot_consts.HUBSPOT_SEARCH_SYNC_BODY(resource_fields, add_filters, limit)
        logger.info(f"{url} was sent with data: {data}")
        with Client as client:
            res = client.post(
                url,
                headers=hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token),
                data=json.dumps(data),
            )
            res = self._handle_response(res)
            saved_response = res
            logger.info(
                f"Request returned {len(res.get('results'))} number of results for {resource} with limit {limit}"
            )
            while True:
                has_next_page = res.get("paging", None)
                if has_next_page:
                    logger.info(f"Request returned a next page")
                    next_page_url = has_next_page.get("next").get("link")
                    with Client as client:
                        res = client.get(
                            next_page_url,
                            headers=hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token),
                        )
                        res = self._handle_response(res)
                        saved_response["results"] = [*saved_response["results"], *res["results"]]

                else:
                    break
            res = self._format_resource_response(saved_response, resource)
            return res

    def list_relationship_data(self, relationship, fields, value, resource, *args, **kwargs):
        # build the filter query from the name fields and value

        # always retreive id
        if len(value) > 0 and relationship != "OWNER":
            url = hubspot_consts.HUBSPOT_SEARCH_URI(resource)
        else:
            url = (
                hubspot_consts.HUBSPOT_OWNERS_URI(value)
                if relationship == "OWNER"
                else hubspot_consts.HUBSPOT_OBJECTS_URI(resource, fields)
            )
        with Client as client:
            if len(value) > 0 and relationship != "OWNER":
                data = hubspot_consts.HUBSPOT_SEARCH_BODY(fields, value)
                res = client.post(
                    url,
                    data=json.dumps(data),
                    headers=hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token),
                )
            else:
                res = client.get(
                    url, headers=hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token),
                )
            res = self._handle_response(res)
            # no need to format to any adapter
            res = self._format_resource_response(res, None)
            res = (
                [{"Name": item["email"], "Id": item["id"]} for item in res]
                if relationship == "OWNER"
                else [{"Name": item["properties"]["name"], "Id": item["id"]} for item in res]
            )
            return res

    def get_individual_picklist_values(self, resource, field_name):
        url = f"{hubspot_consts.BASE_URL}{hubspot_consts.HUBSPOT_PROPERTIES_URI}{resource}/{field_name}"
        with Client as client:
            res = client.get(
                url, headers=hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)
            res_obj = {}
            for item in res["options"]:
                res_obj[item["label"]] = {"value": item["value"], "label": item["label"]}
            return res_obj

    def execute_alert_query(self, url, resource):
        """Handles alert requests to salesforce"""
        data = json.dumps(url[1])
        with Client as client:
            res = client.post(
                url[0], headers=hubspot_consts.HUBSPOT_REQUEST_HEADERS(self.access_token), data=data
            )
            res = self._handle_response(res)

            res = self._format_resource_response(res, resource)
            return res

    def revoke(self):
        # if a token is already expired a 400 error occurs we can ignore that
        with Client as client:
            client.post(hubspot_consts.REVOKE_URI, data={"token": self.access_token})
            client.post(hubspot_consts.REVOKE_URI, data={"token": self.refresh_token})

    @property
    def as_dict(self):
        return vars(self)


class HObjectFieldAdapter:
    def __init__(self, data):
        self.user = data.get("user", None)
        self.crm_object = data.get("crm_object", None)
        self.api_name = data.get("name", None)
        self.label = data.get("label", None)
        self.data_type = data.get("field_type", None)
        self.display_value = data.get("label", None)
        self.options = data.get("options", None)
        self.createable = data.get("createable", True)
        self.reference = data.get("reference", False)
        self.reference_to_infos = data.get("reference_to_infos", [])
        self.relationship_name = data.get("referenced_object_type", None)
        self.updateable = data.get("updateable", True)
        self.filterable = data.get("filterable", True)
        self.integration_source = data.get("integration_source", "")
        self.integration_id = data.get("integration_id", "")
        self.imported_by = data.get("imported_by", None)

    @staticmethod
    def from_api(data):
        data["integration_source"] = "HUBSPOT"
        type = data["fieldType"]
        data["fieldType"] = DATA_TYPE_OBJ[type]
        if "referencedObjectType" in data.keys() and data["referencedObjectType"]:
            data["reference"] = True
            data["fieldType"] = "Reference"
            reference_info = REFERENCE_INFO_OBJ.get(data["referencedObjectType"], None)
            if reference_info is not None:
                data["referenceToInfos"] = [
                    {"api_name": data["referencedObjectType"], "name_fields": reference_info}
                ]
        update_check = data["modificationMetadata"]["readOnlyValue"]
        if update_check:
            data["updateable"] = False
            data["createable"] = False
        d = object_to_snake_case(data)
        return d

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)


class CompanyAdapter:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.organization = kwargs.get("organization", None)
        self.owner = kwargs.get("owner", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.integration_source = kwargs.get("integration_source", "")
        self.integration_id = kwargs.get("integration_id", "")
        self.imported_by = kwargs.get("imported_by", None)
        self.secondary_data = kwargs.get("secondary_data", None)

    integration_mapping = dict(
        integration_id="hs_object_id",
        name="name",
        owner="hubspot_owner_id",
        external_owner="hubspot_owner_id",
    )

    @property
    def internal_user(self):
        try:
            user = User.objects.get(id=self.owner)
        except User.DoesNotExist:
            user = None
        return user

    @staticmethod
    def reverse_integration_mapping():
        """mapping of 'standard' data when sending from the SF API"""
        reverse = {}
        for k, v in CompanyAdapter.integration_mapping.items():
            reverse[v] = k
        return reverse

    @staticmethod
    def from_api(data, user_id, *args, **kwargs):
        mapping = CompanyAdapter.reverse_integration_mapping()
        formatted_data = dict(secondary_data={})
        for k, v in data.items():
            if k in mapping:
                formatted_data[mapping.get(k)] = v
            formatted_data["secondary_data"][k] = v
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_HUBSPOT
        formatted_data["imported_by"] = str(user_id)
        return CompanyAdapter(**formatted_data)

    @staticmethod
    def to_api(data, mapping, object_fields):
        """data : data to be passed, mapping: map managr fields to sf fields, object_fields: if a field is not in this list it cannot be pushed"""
        formatted_data = dict()
        for k, v in data.items():
            key = mapping.get(k, None)
            if key:
                formatted_data[key] = v
            else:
                # TODO: add extra check here to only push creatable on creatable and updateable on updateable
                if k in object_fields:
                    formatted_data[k] = v

        return formatted_data

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)

    @staticmethod
    def update(data, access_token, deal_id, object_fields, custom_base=None):
        json_data = json.dumps(
            {
                "properties": CompanyAdapter.to_api(
                    data, CompanyAdapter.integration_mapping, object_fields
                )
            }
        )
        url = hubspot_consts.HUBSPOT_RESOURCE_URI("companies") + deal_id
        with Client as client:
            r = client.patch(
                url,
                data=json_data,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)},
            )
            return HubspotAuthAccountAdapter._handle_response(r)

    @staticmethod
    def create(data, access_token, object_fields, user_id):
        json_data = json.dumps(
            {
                "properties": CompanyAdapter.to_api(
                    data, CompanyAdapter.integration_mapping, object_fields
                )
            }
        )
        url = hubspot_consts.HUBSPOT_RESOURCE_URI("companies")
        with Client as client:
            r = client.post(
                url,
                data=json_data,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)},
            )
            res = HubspotAuthAccountAdapter._handle_response(r)
            url = hubspot_consts.HUBSPOT_OBJECTS_URI("companies", object_fields, res["id"])
            r = client.get(url, headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)})
            r = HubspotAuthAccountAdapter._handle_response(r)
            r = CompanyAdapter.from_api(r["properties"], user_id)
            return r

    def get_current_values(self):
        user = self.internal_user
        resource_fields = user.object_fields.filter(crm_object="Company").values_list(
            "api_name", flat=True
        )

        url = hubspot_consts.HUBSPOT_OBJECTS_URI("companies", resource_fields, self.integration_id)
        with Client as client:
            r = client.get(
                url,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(user.crm_account.access_token)},
            )
            r = HubspotAuthAccountAdapter._handle_response(r)
            r = DealAdapter.from_api(r["properties"], self.owner)
            return r


class DealAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.integration_id = kwargs.get("integration_id", None)
        self.account = kwargs.get("account", None)
        self.name = kwargs.get("name", None)
        self.stage = kwargs.get("stage", None)
        self.amount = kwargs.get("amount", None)
        self.close_date = kwargs.get("close_date", None)
        self.forecast_category = kwargs.get("forecast_category", None)
        self.owner = kwargs.get("owner", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.external_account = kwargs.get("external_account", None)
        self.imported_by = kwargs.get("imported_by", None)
        self.contacts = kwargs.get("contacts", [])
        self.secondary_data = kwargs.get("secondary_data", None)

    integration_mapping = dict(
        integration_id="hs_object_id",
        name="dealname",
        owner="hubspot_owner_id",
        external_owner="hubspot_owner_id",
        stage="dealstage",
        close_date="closedate",
        forecast_category="hs_manual_forecast_category",
        amount="amount",
        external_account="company",
        account="company",
    )

    @staticmethod
    def reverse_integration_mapping():
        """mapping of 'standard' data when sending from the SF API"""
        reverse = {}
        for k, v in DealAdapter.integration_mapping.items():
            reverse[v] = k
        return reverse

    @staticmethod
    def from_api(data, user_id, *args, **kwargs):
        mapping = DealAdapter.reverse_integration_mapping()
        formatted_data = dict(secondary_data={})
        for k, v in data.items():
            if k in mapping:
                formatted_data[mapping.get(k)] = v
            formatted_data["secondary_data"][k] = v
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_HUBSPOT
        formatted_data["imported_by"] = str(user_id)
        return DealAdapter(**formatted_data)

    @staticmethod
    def to_api(data, mapping, object_fields):
        """data : data to be passed, mapping: map managr fields to sf fields, object_fields: if a field is not in this list it cannot be pushed"""
        formatted_data = dict()
        for k, v in data.items():
            key = mapping.get(k, None)
            if key:
                formatted_data[key] = v
            else:
                # TODO: add extra check here to only push creatable on creatable and updateable on updateable
                if k in object_fields:
                    formatted_data[k] = v

        return formatted_data

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)

    @property
    def internal_user(self):
        try:
            user = User.objects.get(id=self.owner)
        except User.DoesNotExist:
            user = None
        return user

    def get_deal_stage_options(self, access_token):
        url = hubspot_consts.HUBSPOT_PIPELINES_URI(self.secondary_data["pipeline"])
        headers = hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)
        with Client as client:
            res = client.get(url, headers=headers,)
            return HubspotAuthAccountAdapter._handle_response(res)

    @staticmethod
    def update(data, access_token, deal_id, object_fields, custom_base=None):
        json_data = json.dumps(
            {"properties": DealAdapter.to_api(data, DealAdapter.integration_mapping, object_fields)}
        )
        url = hubspot_consts.HUBSPOT_RESOURCE_URI("deals") + deal_id
        with Client as client:
            r = client.patch(
                url,
                data=json_data,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)},
            )
            return HubspotAuthAccountAdapter._handle_response(r)

    @staticmethod
    def create(data, access_token, object_fields, user_id):
        json_data = json.dumps(
            {"properties": DealAdapter.to_api(data, DealAdapter.integration_mapping, object_fields)}
        )
        url = hubspot_consts.HUBSPOT_RESOURCE_URI("deals")
        with Client as client:
            r = client.post(
                url,
                data=json_data,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)},
            )
            res = HubspotAuthAccountAdapter._handle_response(r)
            url = hubspot_consts.HUBSPOT_OBJECTS_URI("deals", object_fields, res["id"])
            r = client.get(url, headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)})
            r = HubspotAuthAccountAdapter._handle_response(r)
            r = DealAdapter.from_api(r["properties"], user_id)
            return r

    def get_current_values(self):
        user = self.internal_user
        resource_fields = user.crm_account.adapter_class.object_fields.get("Deal")
        url = hubspot_consts.HUBSPOT_OBJECTS_URI("deals", resource_fields, self.integration_id)
        with Client as client:
            r = client.get(
                url,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(user.crm_account.access_token)},
            )
            r = HubspotAuthAccountAdapter._handle_response(r)
            r = DealAdapter.from_api(r["properties"], self.owner)
            return r


class HubspotContactAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.integration_id = kwargs.get("integration_id", None)
        self.account = kwargs.get("account", None)
        self.email = kwargs.get("email", None)
        self.owner = kwargs.get("owner", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.external_account = kwargs.get("external_account", None)
        self.imported_by = kwargs.get("imported_by", None)
        self.secondary_data = kwargs.get("secondary_data", None)

    integration_mapping = dict(
        integration_id="hs_object_id",
        email="email",
        owner="hubspot_owner_id",
        external_owner="hubspot_owner_id",
        external_account="company",
    )

    @property
    def internal_user(self):
        try:
            user = User.objects.get(id=self.owner)
        except User.DoesNotExist:
            user = None
        return user

    @staticmethod
    def reverse_integration_mapping():
        """mapping of 'standard' data when sending from the SF API"""
        reverse = {}
        for k, v in HubspotContactAdapter.integration_mapping.items():
            reverse[v] = k
        return reverse

    @staticmethod
    def from_api(data, user_id, *args, **kwargs):
        mapping = HubspotContactAdapter.reverse_integration_mapping()
        formatted_data = dict(secondary_data={})
        for k, v in data.items():
            if k in mapping:
                formatted_data[mapping.get(k)] = v
            formatted_data["secondary_data"][k] = v
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_HUBSPOT
        formatted_data["imported_by"] = str(user_id)
        return HubspotContactAdapter(**formatted_data)

    @staticmethod
    def to_api(data, mapping, object_fields):
        """data : data to be passed, mapping: map managr fields to sf fields, object_fields: if a field is not in this list it cannot be pushed"""
        formatted_data = dict()
        for k, v in data.items():
            key = mapping.get(k, None)
            if key:
                formatted_data[key] = v
            else:
                # TODO: add extra check here to only push creatable on creatable and updateable on updateable
                if k in object_fields:
                    formatted_data[k] = v

        return formatted_data

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)

    @staticmethod
    def update(data, access_token, deal_id, object_fields, custom_base=None):
        json_data = json.dumps(
            {
                "properties": HubspotContactAdapter.to_api(
                    data, HubspotContactAdapter.integration_mapping, object_fields
                )
            }
        )
        url = hubspot_consts.HUBSPOT_RESOURCE_URI("contacts") + deal_id
        with Client as client:
            r = client.patch(
                url,
                data=json_data,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)},
            )
            return HubspotAuthAccountAdapter._handle_response(r)

    @staticmethod
    def create(data, access_token, object_fields, user_id):
        json_data = json.dumps(
            {
                "properties": HubspotContactAdapter.to_api(
                    data, HubspotContactAdapter.integration_mapping, object_fields
                )
            }
        )
        url = hubspot_consts.HUBSPOT_RESOURCE_URI("contacts")
        with Client as client:
            r = client.post(
                url,
                data=json_data,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)},
            )
            res = HubspotAuthAccountAdapter._handle_response(r)
            url = hubspot_consts.HUBSPOT_OBJECTS_URI("contacts", list(object_fields), res["id"])
            r = client.get(url, headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(access_token)})
            r = HubspotAuthAccountAdapter._handle_response(r)
            r = HubspotContactAdapter.from_api(r["properties"], user_id)
            return r

    def get_current_values(self):
        user = self.internal_user
        resource_fields = user.object_fields.filter(crm_object="Contact").values_list(
            "api_name", flat=True
        )
        url = hubspot_consts.HUBSPOT_OBJECTS_URI("contacts", resource_fields, self.integration_id)
        with Client as client:
            r = client.get(
                url,
                headers={**hubspot_consts.HUBSPOT_REQUEST_HEADERS(user.crm_account.access_token)},
            )
            r = HubspotAuthAccountAdapter._handle_response(r)
            r = DealAdapter.from_api(r["properties"], self.owner)
            return r
