import json
import pytz
import requests
from datetime import datetime
import os.path
import logging

from urllib.parse import urlencode, quote_plus, urlparse
from requests.exceptions import HTTPError
from django.contrib.postgres.fields import JSONField

from managr.utils.client import HttpClient
from managr.utils.misc import object_to_snake_case
from managr.organization import constants as org_consts
from managr.api.decorators import log_all_exceptions
from managr.slack.helpers import block_builders

from .exceptions import CustomAPIException
from .. import constants as sf_consts

logger = logging.getLogger("managr")

client = HttpClient(timeout=20).client


class SObjectFieldAdapter:
    def __init__(self, data):
        self.api_name = data.get("apiName", None)
        self.custom = data.get("custom", None)
        self.createable = data.get("createable", None)
        self.data_type = data.get("data_type", None)
        self.label = data.get("label", None)
        self.length = data.get("length", None)
        self.reference = data.get("reference", None)
        self.reference_to_infos = data.get("reference_to_infos", [])
        self.updateable = data.get("updateable", None)
        self.required = data.get("required", None)
        self.unique = data.get("unique", None)
        self.updateable = data.get("updateable", None)
        self.value = data.get("value", None)
        self.display_value = data.get("display_value", None)
        self.options = data.get("options", [])

    @staticmethod
    def from_api(data):
        return object_to_snake_case(data)

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)


class SObjectValidationAdapter:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id", None)
        self.validation_id = kwargs.get("validation_id", None)
        self.description = kwargs.get("description", None)
        self.message = kwargs.get("message", None)

    @staticmethod
    def from_api(data):
        return dict(
            validation_id=data.get("Id", None),
            description=data.get("Description", None),
            message=data.get("ErrorMessage", None),
        )

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)


class SObjectPicklistAdapter:
    def __init__(self, *args, **kwargs):

        self.field = kwargs.get("field", None)

    @staticmethod
    def from_api(data):
        return object_to_snake_case(data)

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)


class SalesforceAuthAccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.signature = kwargs.get("signature", None)
        self.scope = kwargs.get("scope", None)
        self.id_token = kwargs.get("id_token", None)
        self.instance_url = kwargs.get("instance_url", None)
        self.salesforce_id = kwargs.get("salesforce_id", None)
        self.salesforce_account = kwargs.get("salesforce_account", None)
        self.login_link = kwargs.get("login_link", None)
        self.user = kwargs.get("user", None)
        self.object_fields = kwargs.get("object_fields", {})
        self.default_record_id = kwargs.get("default_record_id", {})

    @staticmethod
    def _handle_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code >= 200 and response.status_code < 300:
            if response.status_code == 204:
                return {}
            try:
                data = response.json()
            except Exception as e:
                CustomAPIException(e, fn_name)
        else:
            try:
                error_code = response.status_code
                error_data = (
                    response.json()[0] if isinstance(response.json(), list) else response.json()
                )
                if error_code == 400:
                    error_param = error_data.get("error", error_data.get("errorCode", None))
                    error_message = error_data.get(
                        "error_description", error_data.get("message", None)
                    )
                else:
                    error_param = error_data.get("errorCode", None)
                    error_message = error_data.get("message", None)
                kwargs = {
                    "error_code": error_code,
                    "error_param": error_param,
                    "error_message": error_message,
                }
                raise HTTPError(kwargs)
            except HTTPError as e:
                CustomAPIException(e, fn_name)
        return data

    @classmethod
    def create_account(cls, code, user_id):
        res = cls.authenticate(code)
        # get fields for resources
        data = cls.from_api(res, user_id)

        return data

    def _format_resource_response(self, response_data, class_name, *args, **kwargs):

        res = response_data.get("records", [])
        formatted_data = []
        from .routes import routes

        resource_class = routes.get(class_name, None)
        for result in res:
            result.pop("attributes")  # unnecessary metadata field

            if resource_class:
                formatted_data.append(resource_class.from_api(result, self.user, *args))
            else:
                formatted_data.append(result)

        return formatted_data

    @staticmethod
    def custom_field(
        label,
        key,
        type="String",
        required=True,
        updateable=True,
        creatable=True,
        options=[],
        length=0,
        value=None,
    ):
        """ Helper method to convert custom fields we want to add to forms that we do not get from SF"""
        return dict(
            label=label,
            key=key,
            type=type,
            required=required,  # is required to pass val on create
            updateable=updateable,  # cannot be patched
            createable=creatable,
            options=options,
            length=length,
            value=value,
        )

    def format_field_options(self, res_data=[]):
        fields = res_data["fields"]
        data = [SObjectFieldAdapter.create_from_api(f) for f in fields]

        return data

    def format_validation_rules(self, res_data=[]):
        records = res_data["records"]
        return list(map(lambda rule: SObjectValidationAdapter.create_from_api(rule), records,))

    def format_picklist_values(self, res_data=[]):
        fields = res_data["picklistFieldValues"]

        return [map(lambda field: SObjectPicklistAdapter.create_from_api(field), fields)]

    @staticmethod
    def from_api(data, user_id=None):
        salesforce_link = data.pop("id", None)
        data["login_link"] = salesforce_link
        if data["login_link"]:
            new_link, value = os.path.split(data["login_link"])
            data["salesforce_id"] = value
            new_link, value = os.path.split(new_link)
            data["salesforce_account"] = value
        else:
            data["salesforce_id"] = None
            data["salesforce_account"] = None

        data["user"] = user_id
        return SalesforceAuthAccountAdapter(**data)

    @staticmethod
    def generate_auth_link():
        return f"{sf_consts.AUTHORIZATION_URI}?{sf_consts.AUTHORIZATION_QUERY}"

    @staticmethod
    def authenticate(code):
        data = sf_consts.AUTHENTICATION_BODY(code)
        res = client.post(
            f"{sf_consts.AUTHENTICATION_URI}", data, headers=sf_consts.AUTHENTICATION_HEADERS,
        )

        return SalesforceAuthAccountAdapter._handle_response(res)

    def refresh(self):
        data = sf_consts.REAUTHENTICATION_BODY(self.refresh_token)
        res = client.post(
            f"{sf_consts.REFRESH_URI}", data, headers=sf_consts.AUTHENTICATION_HEADERS,
        )

        return SalesforceAuthAccountAdapter._handle_response(res)

    def list_fields(self, resource):
        """ Uses the UI API to list fields for a resource using this endpoint only returns fields a user has access to """
        url = f"{self.instance_url}{sf_consts.SALESFORCE_FIELDS_URI(resource)}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)
        res = self._handle_response(res)
        return {
            "fields": self.format_field_options(res),
            "record_type_id": res["defaultRecordTypeId"],  # required for the picklist options
        }

    def list_picklist_values(self, resource):
        """ Uses the UI API to list all picklist values resource using this endpoint only returns fields a user has access to """
        extra_fields_object = self.object_fields.get(resource, None)
        if extra_fields_object:
            record_type_id = extra_fields_object.get("record_type_id")
            url = f"{self.instance_url}{sf_consts.SALESFORCE_PICKLIST_URI(sf_consts.SALESFORCE_FIELDS_URI(resource), record_type_id)}"
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)
            return self.format_picklist_values(res)

    def list_validations(self, resource):
        """ Lists all (active) Validations that apply to a resource from the ValidationRules object """

        url = f"{self.instance_url}{sf_consts.SALESFORCE_VALIDATION_QUERY(resource)}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)
        res = self._handle_response(res)
        return self.format_validation_rules(res)

    def list_resource_data(self, resource, offset, *args, **kwargs):
        # add extra fields to query string
        extra_items = self.object_fields.get(resource)
        extra_fields = []
        if extra_items:
            extra_fields = extra_items.get("fields", [])
        from .routes import routes

        resource_class = routes.get(resource)
        relationships = resource_class.get_child_rels()
        url = f"{self.instance_url}{sf_consts.SALSFORCE_RESOURCE_QUERY_URI(self.salesforce_id, resource, extra_fields, relationships,)}"
        if offset:
            url = f"{url} offset {offset}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)
        res = self._handle_response(res)
        res = self._format_resource_response(res, resource)
        return res

    def list_relationship_data(self, relationship, fields, value, *args, **kwargs):

        # build the filter query from the name fields and value
        filter_query = ""
        for index, f in enumerate(fields):
            string_val = f"{f} LIKE '%{value}%'"
            if index != 0:
                string_val = f" OR {string_val}"
            filter_query = filter_query + string_val

        filter_query_string = f"AND ({filter_query})"
        # always retreive id
        fields.append("Id")
        url = f"{self.instance_url}{sf_consts.SALSFORCE_RESOURCE_QUERY_URI(self.salesforce_id, relationship, fields, additional_filters=[filter_query_string], limit=20 )}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)
        res = self._handle_response(res)
        # no need to format to any adapter
        res = self._format_resource_response(res, None)
        return res

    def get_resource_count(self, resource):
        res = client.get(
            f"{self.instance_url}{sf_consts.SF_COUNT_URI(resource, self.salesforce_id)}",
            headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
        )

        return self._handle_response(res)

    def revoke(self):
        # if a token is already expired a 400 error occurs we can ignore that
        client.post(sf_consts.REVOKE_URI, {"token": self.access_token})
        client.post(sf_consts.REVOKE_URI, {"token": self.refresh_token})

    @property
    def as_dict(self):
        return vars(self)


class AccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.integration_id = kwargs.get("integration_id", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.name = kwargs.get("name", None)
        self.organization = kwargs.get("organization", None)
        self.parent = kwargs.get("parent", None)
        self.parent_integration_id = kwargs.get("parent_integration_id", None)
        self.owner = kwargs.get("owner", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.imported_by = kwargs.get("imported_by", None)
        self.secondary_data = kwargs.get("secondary_data", None)

    integration_mapping = dict(
        # mapping of 'standard' data when sending to the SF API
        integration_id="Id",
        name="Name",
        owner="OwnerId",  # overwritten (ignored in reverse)
        external_owner="OwnerId",
        parent_integration_id="ParentId",
    )

    @staticmethod
    def reverse_integration_mapping():
        """ mapping of 'standard' data when sending from the SF API """
        reverse = {}
        for k, v in AccountAdapter.integration_mapping.items():
            reverse[v] = k
        return reverse

    @staticmethod
    def get_child_rels():
        return {}

    @staticmethod
    def to_api(data, mapping, object_fields):
        """ data : data to be passed, mapping: map managr fields to sf fields, object_fields: if a field is not in this list it cannot be pushed"""
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

    @staticmethod
    def from_api(data, user_id, *args, **kwargs):
        formatted_data = dict()

        mapping = AccountAdapter.reverse_integration_mapping()
        formatted_data = dict(secondary_data={})
        for k, v in data.items():
            if k in mapping:
                formatted_data[mapping.get(k)] = v

            formatted_data["secondary_data"][k] = v

        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["imported_by"] = str(user_id)

        return AccountAdapter(**formatted_data)

    @property
    def as_dict(self):
        return vars(self)

    @staticmethod
    def update_account(data, access_token, custom_base, salesforce_id, object_fields):
        json_data = json.dumps(
            AccountAdapter.to_api(data, AccountAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.RESOURCE_SYNC_ACCOUNT, salesforce_id
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.patch(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )
        return SalesforceAuthAccountAdapter._handle_response(r)

    @staticmethod
    def create_account(data, access_token, custom_base, object_fields, user_id):
        json_data = json.dumps(
            AccountAdapter.to_api(data, AccountAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.RESOURCE_SYNC_ACCOUNT, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.post(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )
        # get the opp as well uses the same url as the write but with get
        r = SalesforceAuthAccountAdapter._handle_response(r)
        url = f"{url}{r['id']}"
        r = client.get(url, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header})

        r = SalesforceAuthAccountAdapter._handle_response(r)
        r = AccountAdapter.from_api(r, user_id)
        return r


class ContactAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.integration_id = kwargs.get("integration_id", None)
        self.email = kwargs.get("email", None)
        self.owner = kwargs.get("owner", None)
        self.account = kwargs.get("account", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.external_account = kwargs.get("external_account", None)
        self.imported_by = kwargs.get("imported_by", None)
        self.secondary_data = kwargs.get("secondary_data", None)

    integration_mapping = dict(
        # mapping of 'standard' data when sending to the SF API
        integration_id="Id",
        email="Email",
        owner="OwnerId",  # overwritten (ignored in reverse)
        account="AccountId",
        external_account="AccountId",
        external_owner="OwnerId",
    )

    @staticmethod
    def get_child_rels():
        return {}

    @staticmethod
    def reverse_integration_mapping():
        """ mapping of 'standard' data when sending from the SF API """
        reverse = {}
        for k, v in ContactAdapter.integration_mapping.items():
            reverse[v] = k
        return reverse

    @staticmethod
    def from_api(data, user_id, *args, **kwargs):
        formatted_data = dict()
        mapping = ContactAdapter.reverse_integration_mapping()
        formatted_data = dict(secondary_data={})
        for k, v in data.items():
            if k in mapping:
                formatted_data[mapping.get(k)] = v

            formatted_data["secondary_data"][k] = v
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["imported_by"] = str(user_id)

        return ContactAdapter(**formatted_data)

    @staticmethod
    def to_api(data, mapping, object_fields):
        formatted_data = dict()
        for k, v in data.items():
            if k == "Id":
                print(k)
            key = mapping.get(k, None)
            if key and key != "Id":
                if v is not None:
                    formatted_data[key] = v
            else:

                # TODO: add extra check here to only push creatable on creatable and updateable on updateable
                if k in object_fields and k != "Id":
                    if v is not None:
                        formatted_data[k] = v

        return formatted_data

    @staticmethod
    def create_new_contact(data, access_token, custom_base, object_fields):
        json_data = json.dumps(
            ContactAdapter.to_api(data, ContactAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.RESOURCE_SYNC_CONTACT, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.post(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )
        return SalesforceAuthAccountAdapter._handle_response(r)

    @staticmethod
    def update_contact(data, access_token, custom_base, integration_id, object_fields):
        json_data = json.dumps(
            ContactAdapter.to_api(data, ContactAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.RESOURCE_SYNC_CONTACT, integration_id
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.patch(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )
        return SalesforceAuthAccountAdapter._handle_response(r)

    @property
    def as_dict(self):
        return vars(self)


class OpportunityAdapter:
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
        self.last_stage_update = kwargs.get("last_stage_update", None)
        self.last_activity_date = kwargs.get("last_activity_date", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.external_account = kwargs.get("external_account", None)
        self.imported_by = kwargs.get("imported_by", None)
        self.contacts = kwargs.get("contacts", None)
        self.is_stale = kwargs.get("is_stale", None)
        self.secondary_data = kwargs.get("secondary_data", None)

    integration_mapping = dict(
        # mapping of 'standard' data when sending to the SF API
        integration_id="Id",
        account="AccountId",  # overwritten (ignored in reverse)
        name="Name",
        stage="StageName",
        amount="Amount",
        close_date="CloseDate",
        forecast_category="ForecastCategoryName",
        owner="OwnerId",  # overwritten (ignored in reverse)
        external_account="AccountId",
        external_owner="OwnerId",
        last_activity_date="LastActivityDate",
    )

    @staticmethod
    def get_child_rels():
        return {
            sf_consts.OPPORTUNITY_CONTACT_ROLES: {
                "fields": sf_consts.OPPORTUNITY_CONTACT_ROLE_FIELDS,
                "attrs": [],
            },
            sf_consts.OPPORTUNITY_HISTORIES: {
                "fields": sf_consts.OPPORTUNITY_HISTORY_FIELDS,
                "attrs": sf_consts.OPPORTUNITY_HISTORY_ATTRS,
            },
        }

    @staticmethod
    def reverse_integration_mapping():
        """ mapping of 'standard' data when sending from the SF API """
        reverse = {}
        for k, v in OpportunityAdapter.integration_mapping.items():
            reverse[v] = k
        return reverse

    @staticmethod
    def _format_date_time_from_api(d):
        if d and len(d) > 10:
            return datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%f%z")
        elif d and len(d) <= 10:
            return datetime.strptime(d, "%Y-%m-%d")
        return None

    @staticmethod
    def _format_stage_update(obj):
        if obj and obj.get("totalSize", 0) > 0:
            return OpportunityAdapter._format_date_time_from_api(obj["records"][0]["CreatedDate"])
        return None

    @staticmethod
    def _format_contacts_list(contacts):
        return list(map(lambda contact: contact["ContactId"], contacts))

    @staticmethod
    def from_api(data, user_id, *args, **kwargs):
        mapping = OpportunityAdapter.reverse_integration_mapping()
        formatted_data = dict(secondary_data={})
        for k, v in data.items():
            if k in mapping:
                formatted_data[mapping.get(k)] = v
            formatted_data["secondary_data"][k] = v
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["last_stage_update"] = OpportunityAdapter._format_stage_update(
            data.get("OpportunityHistories", None)
        )
        formatted_data["contacts"] = (
            OpportunityAdapter._format_contacts_list(
                data.get("OpportunityContactRoles").get("records")
            )
            if data.get("OpportunityContactRoles", None)
            else []
        )
        formatted_data["imported_by"] = str(user_id)
        formatted_data["is_stale"] = False

        return OpportunityAdapter(**formatted_data)

    @staticmethod
    def to_api(data, mapping, object_fields):
        """ data : data to be passed, mapping: map managr fields to sf fields, object_fields: if a field is not in this list it cannot be pushed"""
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

    @staticmethod
    def update_opportunity(data, access_token, custom_base, salesforce_id, object_fields):
        json_data = json.dumps(
            OpportunityAdapter.to_api(data, OpportunityAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.RESOURCE_SYNC_OPPORTUNITY, salesforce_id
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.patch(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )
        return SalesforceAuthAccountAdapter._handle_response(r)

    @staticmethod
    def create_opportunity(data, access_token, custom_base, object_fields, user_id):
        logger.info(f"UNFORMATED DATA: {data}")
        json_data = json.dumps(
            OpportunityAdapter.to_api(data, OpportunityAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.RESOURCE_SYNC_OPPORTUNITY, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        logger.info(f"REQUEST DATA: {json_data}")
        r = client.post(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )

        # get the opp as well uses the same url as the write but with get
        logger.info(f"REQUEST RES: {r.json()}")
        r = SalesforceAuthAccountAdapter._handle_response(r)
        url = f"{url}{r['id']}"
        r = client.get(url, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header})
        logger.info(f"NEW DATA: {r.json()}")
        r = SalesforceAuthAccountAdapter._handle_response(r)
        r = OpportunityAdapter.from_api(r, user_id)
        return r

    @staticmethod
    def add_contact_role(access_token, custom_base, contact_id, opp_id):
        data = {"ContactId": contact_id, "OpportunityId": opp_id}
        json_data = json.dumps(data)
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.SALESFORCE_RESOURCE_OPPORTUNITY_CONTACT_ROLE, ""
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.post(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )
        return SalesforceAuthAccountAdapter._handle_response(r)

    @property
    def as_dict(self):
        return vars(self)


class ActivityAdapter:
    """ Two types of activities Task (includes calls, emails) and Events"""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.type = kwargs.get("type", None)
        self.category = kwargs.get("category", None)
        self.subject = kwargs.get("subject", None)
        self.description = kwargs.get("description", None)
        self.created_date = kwargs.get("created_date", None)

    @staticmethod
    def save_zoom_meeting_to_salesforce(data, access_token, custom_base):
        json_data = json.dumps(data)
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.SALESFORCE_RESOURCE_TASK, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.post(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )
        return SalesforceAuthAccountAdapter._handle_response(r)
