import json
import pytz
import requests
from datetime import datetime
import os.path
from urllib.parse import urlencode, quote_plus, urlparse
from requests.exceptions import HTTPError

from managr.utils.client import HttpClient
from managr.organization import constants as org_consts
from managr.api.decorators import log_all_exceptions

from .exceptions import CustomAPIException
from .. import constants as sf_consts

client = HttpClient().client


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

    @staticmethod
    # @log_all_exceptions
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
                    error_param = error_data.get("error", None)
                    error_message = error_data.get("error_description", None)
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
        data = cls.from_api(res, user_id)

        return data

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

    def list_accounts(self, offset):
        url = f"{self.instance_url}{sf_consts.SALSFORCE_ACCOUNT_QUERY_URI}"
        if offset:
            url = f"{url} offset {offset}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)

        return self._handle_response(res)

    def list_stages(self, offset):
        url = f"{self.instance_url}{sf_consts.SALSFORCE_STAGE_QUERY_URI}"
        if offset:
            url = f"{url} offset {offset}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)

        return self._handle_response(res)

    def list_opportunities(self, offset):
        url = f"{self.instance_url}{sf_consts.SALSFORCE_OPP_QUERY_URI}"
        if offset:
            url = f"{url} offset {offset}"
        res = client.get(url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),)
        return self._handle_response(res)

    def get_stage_count(self):
        res = client.get(
            f"{self.instance_url}{sf_consts.SALSFORCE_STAGE_QUERY_URI_COUNT}",
            headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
        )

        return self._handle_response(res)

    def get_opportunity_count(self):
        res = client.get(
            f"{self.instance_url}{sf_consts.SALSFORCE_OPP_QUERY_URI_COUNT}",
            headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
        )

        return self._handle_response(res)

    def get_account_count(self):
        res = client.get(
            f"{self.instance_url}{sf_consts.SALSFORCE_ACCOUNT_QUERY_URI_COUNT}",
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
        self.url = kwargs.get("url", None)
        self.type = kwargs.get("type", None)
        self.organization = kwargs.get("organization", None)
        self.logo = kwargs.get("logo", None)
        self.parent = kwargs.get("parent", None)
        self.parent_integration_id = kwargs.get("parent_integration_id", None)
        self.imported_by = kwargs.get("imported_by", None)

    @staticmethod
    def from_api(data, organization_id, user_id, mapping):
        formatted_data = dict()
        formatted_data["integration_id"] = data.get("Id", "") if data.get("Id", "") else ""
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["name"] = data.get("Name", "") if data.get("Name", "") else ""
        formatted_data["url"] = data.get("Website", "") if data.get("Website", "") else ""
        formatted_data["type"] = data.get("Type", "") if data.get("Type", "") else ""
        formatted_data["logo"] = data.get("PhotoUrl", "") if data.get("PhotoUrl", "") else ""
        formatted_data["parent_integration_id"] = (
            data.get("ParentId", "") if data.get("ParentId", "") else ""
        )
        formatted_data["organization"] = str(organization_id)
        formatted_data["imported_by"] = str(user_id)

        return AccountAdapter(**formatted_data)

    @property
    def as_dict(self):
        return vars(self)


class StageAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.label = kwargs.get("label", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.integration_id = kwargs.get("integration_id", None)
        self.label = kwargs.get("label", None)
        self.value = kwargs.get("value", None)
        self.is_closed = kwargs.get("is_closed", None)
        self.is_won = kwargs.get("is_won", None)
        self.description = kwargs.get("description", None)
        self.organization = kwargs.get("organization", None)
        self.order = kwargs.get("order", None)
        self.is_active = kwargs.get("is_active", None)
        self.forecast_category = kwargs.get("forecast_category", None)
        self.imported_by = kwargs.get("imported_by", None)

    @staticmethod
    def from_api(data, organization_id, user_id, mapping):
        formatted_data = dict()
        formatted_data["integration_id"] = data.get("Id", "") if data.get("Id", "") else ""
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["label"] = data.get("MasterLabel", "") if data.get("MasterLabel", "") else ""
        formatted_data["value"] = data.get("ApiName", "") if data.get("ApiName", "") else ""
        formatted_data["is_closed"] = (
            data.get("IsClosed", "") if data.get("IsClosed", "") else False
        )
        formatted_data["is_won"] = data.get("IsWon", "") if data.get("IsWon", "") else False
        formatted_data["is_active"] = (
            data.get("IsActive", "") if data.get("IsActive", "") else False
        )
        formatted_data["description"] = data.get("Description") if data.get("Description") else ""
        formatted_data["order"] = data.get("SortOrder") if data.get("SortOrder", None) else None
        formatted_data["forecast_category"] = (
            data.get("ForecastCategory") if data.get("ForecastCategory", None) else None
        )
        formatted_data["organization"] = str(organization_id)
        formatted_data["imported_by"] = str(user_id)
        return StageAdapter(**formatted_data)

    @property
    def as_dict(self):
        return vars(self)


class ContactAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.integration_id = kwargs.get("integration_id", None)
        self.title = kwargs.get("title", None)
        self.email = kwargs.get("email", None)
        self.first_name = kwargs.get("first_name", None)
        self.last_name = kwargs.get("last_name", None)
        self.phone_number = kwargs.get("phone_number", None)
        self.mobile_phone = kwargs.get("mobile_phone", None)
        self.user = kwargs.get("user", None)
        self.account = kwargs.get("account", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.external_account = kwargs.get("external_account", None)
        self.imported_by = kwargs.get("imported_by", None)

    from_mapping = dict(
        id="Id",
        first_name="FirstName",
        last_name="Lastname",
        title="Title",
        email="Email",
        mobile_phone="MobilePhone",
        phone_number="PhoneNumber",
        account="AccountId",
        owner="OwnerId",
    )

    @staticmethod
    def from_api(data, user_id, mapping):
        formatted_data = dict()
        contact_data = data.get("Contact")
        formatted_data["integration_id"] = (
            contact_data.get("Id", "") if contact_data.get("Id", "") else ""
        )
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["first_name"] = (
            contact_data.get("FirstName", "") if contact_data.get("FirstName", "") else ""
        )
        formatted_data["last_name"] = (
            contact_data.get("LastName", "") if contact_data.get("LastName", "") else ""
        )
        formatted_data["title"] = (
            contact_data.get("Title", "") if contact_data.get("Title", "") else ""
        )
        formatted_data["email"] = (
            contact_data.get("Email", "") if contact_data.get("Email", "") else ""
        )
        formatted_data["mobile_phone"] = (
            contact_data.get("MobilePhone", "") if contact_data.get("MobilePhone", "") else ""
        )
        formatted_data["phone_number"] = (
            contact_data.get("Phone", "") if contact_data.get("Phone", "") else ""
        )
        formatted_data["user"] = user_id
        formatted_data["external_account"] = (
            contact_data.get("AccountId", "") if contact_data.get("AccountId", "") else ""
        )
        formatted_data["external_owner"] = (
            contact_data.get("OwnerId", "") if contact_data.get("OwnerId", "") else ""
        )
        formatted_data["account"] = (
            None
            if not len(formatted_data["external_account"])
            else formatted_data["external_account"]
        )
        formatted_data["imported_by"] = str(user_id)

        return ContactAdapter(**formatted_data)

    @staticmethod
    def to_api(data, mapping):
        formatted_data = dict()
        for k, v in data.items():
            key = mapping.get(k, None)
            if key:
                formatted_data[key] = v

        return formatted_data

    @staticmethod
    def create_new_contact(data, access_token, custom_base, salesforce_id):
        json_data = json.dumps(ContactAdapter.to_api(data, ContactAdapter.from_mapping))
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.SALESFORCE_RESOURCE_CONTACT, salesforce_id
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
        self.title = kwargs.get("title", None)
        self.description = kwargs.get("description", None)
        self.stage = kwargs.get("stage", None)
        self.amount = kwargs.get("amount", None)
        self.close_date = kwargs.get("close_date", None)
        self.type = kwargs.get("type", None)
        self.next_step = kwargs.get("next_step", None)
        self.lead_source = kwargs.get("lead_source", None)
        self.forecast_category = kwargs.get("forecast_category", None)
        self.owner = kwargs.get("owner", None)
        self.last_stage_update = kwargs.get("last_stage_update", None)
        self.last_activity_date = kwargs.get("last_activity_date", None)
        self.external_stage = kwargs.get("external_stage", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.external_account = kwargs.get("external_account", None)
        self.imported_by = kwargs.get("imported_by", None)
        self.contacts = kwargs.get("contacts", None)
        self.is_stale = kwargs.get("is_stale", None)

    from_mapping = dict(
        id="Id",
        account="AccountId",
        title="Name",
        description="Description",
        stage="StageName",
        amount="Amount",
        close_date="CloseDate",
        type="Type",
        next_step="NextStep",
        lead_source="LeadSource",
        forecast_category="ForecastCategoryName",
        owner="OwnerId",
    )

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
    def _format_contacts_list(contacts, user_id, mapping):
        formatted_contacts = list()
        for contact in contacts:
            formatted_contacts.append(ContactAdapter.from_api(contact, user_id, mapping).as_dict)
        return formatted_contacts

    @staticmethod
    def from_api(data, user_id, mapping):
        formatted_data = dict()
        formatted_data["integration_id"] = data.get("Id", "") if data.get("Id", "") else ""
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["external_account"] = (
            data.get("AccountId", "") if data.get("AccountId", "") else ""
        )
        formatted_data["title"] = data.get("Name", "") if data.get("Name", "") else ""
        formatted_data["description"] = (
            data.get("Description", "") if data.get("Description", "") else ""
        )
        formatted_data["external_stage"] = (
            data.get("StageName", "") if data.get("StageName", "") else ""
        )
        formatted_data["amount"] = (
            float(data.get("Amount", "")) if data.get("Amount", "") else "0.00"
        )
        formatted_data["close_date"] = (
            data.get("CloseDate", "") if data.get("CloseDate", "") else ""
        )
        formatted_data["type"] = data.get("Type", "") if data.get("Type", "") else ""
        formatted_data["next_step"] = data.get("NextStep", "") if data.get("NextStep", "") else ""
        formatted_data["lead_source"] = (
            data.get("LeadSource", "") if data.get("LeadSource", "") else ""
        )
        formatted_data["forecast_category"] = (
            data.get("ForecastCategory", "") if data.get("ForecastCategory", "") else ""
        )
        formatted_data["external_owner"] = (
            data.get("OwnerId", "") if data.get("OwnerId", "") else ""
        )
        formatted_data["last_activity_date"] = (
            OpportunityAdapter._format_date_time_from_api(data.get("LastActivityDate", None))
            if data.get("LastActivityDate", "")
            else None
        )
        formatted_data["last_stage_update"] = OpportunityAdapter._format_stage_update(
            data.get("OpportunityHistories", None)
        )
        formatted_data["contacts"] = (
            OpportunityAdapter._format_contacts_list(
                data.get("OpportunityContactRoles").get("records"), user_id, []
            )
            if data.get("OpportunityContactRoles", None)
            else []
        )
        formatted_data["imported_by"] = str(user_id)

        formatted_data["account"] = formatted_data["external_account"]
        formatted_data["stage"] = formatted_data["external_stage"]
        formatted_data["owner"] = formatted_data["external_owner"]
        # opps are stale if a meeting occured and lead is updated
        # after each refresh the opp is not stale anymore
        formatted_data["is_stale"] = False

        return OpportunityAdapter(**formatted_data)

    @staticmethod
    def to_api(data, mapping):
        formatted_data = dict()
        for k, v in data.items():
            key = mapping.get(k, None)
            if key:
                formatted_data[key] = v

        return formatted_data

    @staticmethod
    def update_opportunity(data, access_token, custom_base, salesforce_id):
        json_data = json.dumps(OpportunityAdapter.to_api(data, OpportunityAdapter.from_mapping))
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.SALESFORCE_RESOURCE_OPPORTUNITY, salesforce_id
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.patch(
            url, json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
        )
        return SalesforceAuthAccountAdapter._handle_response(r)

    @staticmethod
    def add_contact_role(data, access_token, custom_base, contact_id, opp_id):
        data = {"ContactId": contact_id, "OpportunityId": opp_id}
        json_data = json.dumps(data)
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.SALESFORCE_RESOURCE_OPPORTUNITY_CONTACT_ROLE, ""
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        r = client.patch(
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
