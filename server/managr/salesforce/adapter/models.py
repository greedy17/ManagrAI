import json
import pytz
import requests
from datetime import datetime
import os.path
import logging

from urllib.parse import urlencode, quote_plus, urlparse
from requests.exceptions import HTTPError
from django.contrib.postgres.fields import JSONField

from managr.utils.client import HttpClient, Client
from managr.utils.misc import object_to_snake_case
from managr.organization import constants as org_consts
from managr.api.decorators import log_all_exceptions
from managr.slack.helpers import block_builders

from .exceptions import CustomAPIException, UnableToUnlockRow
from .. import constants as sf_consts

logger = logging.getLogger("managr")

# client = HttpClient(timeout=20).client


class SObjectFieldAdapter:
    def __init__(self, data):
        self.api_name = data.get("api_name", None)
        self.custom = data.get("custom", None)
        self.createable = data.get("createable", None)
        self.data_type = data.get("data_type", None)
        self.label = data.get("label", "")
        self.length = data.get("length", 0)
        self.reference = data.get("reference", None)
        self.reference_to_infos = data.get("reference_to_infos", [])
        self.relationship_name = data.get("relationship_name", None)
        self.updateable = data.get("updateable", None)
        self.required = data.get("required", None)
        self.unique = data.get("unique", None)
        self.value = data.get("value", None)
        self.filterable = data.get("filterable", None)
        self.display_value = data.get("display_value", "")
        self.options = data.get("options", [])
        self.integration_source = data.get("integration_source", "")
        self.integration_id = data.get("integration_id", "")
        self.salesforce_account = data.get("salesforce_account", None)
        self.salesforce_object = data.get("salesforce_object", None)
        self.imported_by = data.get("imported_by", None)
        self.allow_multiple = data.get("allow_multiple", None)
        self.default_filters = data.get("default_filters", [])

    @staticmethod
    def from_api(data):
        data["integration_source"] = "SALESFORCE"
        d = object_to_snake_case(data)

        return d

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)


class SObjectValidationAdapter:
    def __init__(self, data):
        self.id = data.get("id", None)
        self.integration_id = data.get("integration_id", None)
        self.description = data.get("description", "")
        self.message = data.get("message", "")
        self.salesforce_account = data.get("salesforce_account", None)
        self.integration_source = data.get("integration_source", None)
        self.salesforce_object = data.get("salesforce_object", None)
        self.imported_by = data.get("imported_by", None)

    @staticmethod
    def from_api(data):
        d = dict(
            integration_id=data.get("Id", None),
            description=data.get("Description", None),
            message=data.get("ErrorMessage", None),
            salesforce_object=data.get("EntityDefinition", {}).get("DeveloperName", None),
            integration_source="SALESFORCE",
            salesforce_account=data.get("salesforce_account", None),
            imported_by=data.get("imported_by", None),
        )

        return d

    @classmethod
    def create_from_api(cls, data):
        return cls(cls.from_api(data))

    @property
    def as_dict(self):
        return vars(self)


class SObjectPicklistAdapter:
    def __init__(self, data):
        self.values = data.get("values", [])
        self.field = data.get("field", None)
        self.picklist_for = data.get("picklist_for", "")
        self.salesforce_account = data.get("salesforce_account", None)
        self.integration_source = data.get("integration_source", "")
        self.imported_by = data.get("imported_by", None)
        self.salesforce_object = data.get("salesforce_object", None)

    @staticmethod
    def from_api(data):

        d = object_to_snake_case(data)

        return d

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
        self.sobjects = kwargs.get(
            "sobjects", None
        )  # NB: Currently Made obsolete will use this in future pb 04/19/21
        self.object_fields = kwargs.get("object_fields", {})
        self.default_record_id = kwargs.get(
            "default_record_id", {}
        )  # TODO: Obsolete ready for delete pb 04/19/21 - default_record_id
        self.default_record_ids = kwargs.get("default_record_ids", {})
        self.exclude_fields = kwargs.get("exclude_fields", {})

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

            status_code = response.status_code
            error_data = (
                response.json()[0] if isinstance(response.json(), list) else response.json()
            )
            # sf does not use this field
            error_code = None
            if status_code == 400:
                error_param = error_data.get("error", error_data.get("errorCode", None))
                error_message = error_data.get("error_description", error_data.get("message", None))
            else:
                error_param = error_data.get("errorCode", None)
                error_message = error_data.get("message", None)
            kwargs = {
                "status_code": status_code,
                "error_code": error_code,
                "error_param": error_param,
                "error_message": error_message,
            }

            CustomAPIException(HTTPError(kwargs), fn_name)
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

    def format_field_options(
        self, sf_account_id, user_id, resource, res_data=[],
    ):
        fields = res_data["fields"]
        ### REMOVE CLONESOURCE, OPPORTUNITYSCOREID ID THIS FIELD DOES NOT WORK IN QUERY
        if "CloneSourceId" in fields.keys():
            del fields["CloneSourceId"]
        if "OpportunityScoreId" in fields.keys():
            del fields["OpportunityScoreId"]

        for exclude in self.exclude_fields.get(resource, []):
            # remove any exclude fields we have already caught in previous requests
            # in addition to the static ones above
            if exclude in fields.keys():
                del fields[exclude]
        custom_additions = dict(
            salesforce_account=sf_account_id,
            salesforce_object=res_data["apiName"],
            imported_by=user_id,
        )

        data = [
            SObjectFieldAdapter.create_from_api({**f, **custom_additions}) for f in fields.values()
        ]

        return data

    def format_validation_rules(
        self, sf_account_id, user_id, res_data=[],
    ):
        records = res_data["records"]
        return list(
            map(
                lambda rule: SObjectValidationAdapter.create_from_api(
                    {**rule, "salesforce_account": sf_account_id, "imported_by": user_id}
                ),
                records,
            )
        )

    def format_picklist_values(
        self, sf_account_id, user_id, resource, res_data=[],
    ):
        fields = res_data["picklistFieldValues"]
        return list(
            map(
                lambda field: SObjectPicklistAdapter.create_from_api(
                    {
                        "values": field[1]["values"],
                        "salesforce_account": sf_account_id,
                        "picklist_for": field[0],
                        "imported_by": user_id,
                        "salesforce_object": resource,
                        "integration_source": "SALESFORCE",
                    }
                ),
                fields.items(),
            )
        )

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
        data["sobjects"] = {
            sf_consts.RESOURCE_SYNC_ACCOUNT: True,
            sf_consts.RESOURCE_SYNC_CONTACT: True,
            sf_consts.RESOURCE_SYNC_LEAD: True,
            sf_consts.RESOURCE_SYNC_OPPORTUNITY: True,
            sf_consts.RESOURCE_SYNC_PRODUCT2: True,
            sf_consts.RESOURCE_SYNC_PRICEBOOK2: True,
            sf_consts.RESOURCE_SYNC_PRICEBOOKENTRY: True,
            sf_consts.RESOURCE_SYNC_OPPORTUNITYLINEITEM: True,
        }
        return SalesforceAuthAccountAdapter(**data)

    @staticmethod
    def generate_auth_link():
        return f"{sf_consts.AUTHORIZATION_URI}?{sf_consts.AUTHORIZATION_QUERY}"

    @staticmethod
    def authenticate(code):
        data = sf_consts.AUTHENTICATION_BODY(code)
        with Client as client:
            res = client.post(
                f"{sf_consts.AUTHENTICATION_URI}",
                data=data,
                headers=sf_consts.AUTHENTICATION_HEADERS,
            )

            return SalesforceAuthAccountAdapter._handle_response(res)

    def refresh(self):
        data = sf_consts.REAUTHENTICATION_BODY(self.refresh_token)
        with Client as client:
            res = client.post(
                f"{sf_consts.REFRESH_URI}", data=data, headers=sf_consts.AUTHENTICATION_HEADERS,
            )

            return SalesforceAuthAccountAdapter._handle_response(res)

    def list_fields(self, resource):
        """Uses the UI API to list fields for a resource using this endpoint only returns fields a user has access to"""
        url = f"{self.instance_url}{sf_consts.SALESFORCE_FIELDS_URI(resource)}"
        print(url)
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)

            return {
                "fields": self.format_field_options(
                    str(self.id), str(self.user), resource, res_data=res
                ),
                "record_type_id": res["defaultRecordTypeId"],  # required for the picklist options
            }

    def list_picklist_values(self, resource):
        """Uses the UI API to list all picklist values resource using this endpoint only returns fields a user has access to"""

        record_type_id = self.default_record_ids[resource]
        url = f"{self.instance_url}{sf_consts.SALESFORCE_PICKLIST_URI(sf_consts.SALESFORCE_FIELDS_URI(resource), record_type_id)}"
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)

            return self.format_picklist_values(str(self.id), str(self.user), resource, res)

    def get_stage_picklist_values(self, resource):
        """Sync method to help users whose stages are not populated"""
        record_type_id = self.default_record_ids[resource]
        url = f"{self.instance_url}{sf_consts.SALESFORCE_PICKLIST_URI(sf_consts.SALESFORCE_FIELDS_URI(resource), record_type_id)}"
        url = f"{url}/StageName"
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)

            return SObjectPicklistAdapter.create_from_api(
                {
                    "values": res["values"],
                    "salesforce_account": str(self.id),
                    "picklist_for": "StageName",
                    "imported_by": str(self.user),
                    "salesforce_object": resource,
                    "integration_source": "SALESFORCE",
                }
            )

    def get_individual_picklist_values(self, resource, field_name=None):
        """Sync method to get picklist values for resources not saved in our db"""

        record_type_id = self.default_record_ids.get(resource, None)
        if not record_type_id:
            # a record type id is required so we may get picklist values these are saved on the sf auth object
            # some orgs will have custom record id's if this is the case we can retrieve using this method lines 353-356
            # if the user profile does not have access and all records have the same default id then we can use that
            # TODO: Take this one level up and save the record id so we only have to do this once

            url = f"{self.instance_url}{sf_consts.SF_DEFAULT_RECORD_ID(resource)}"
            with Client as client:
                res = client.get(
                    url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
                )

                res = self._handle_response(res)

                if res.get("totalSize", 0) > 0:
                    record_type_id = res.get("Id")
                else:
                    record_type_id = self.default_record_ids.get(resource, None)
                    if (
                        not record_type_id
                        and self.default_record_ids
                        and len(self.default_record_ids.items())
                    ):
                        items = list(self.default_record_ids.items())
                        record_type_id = items[0][1] if len(items) else None
                        if not record_type_id:
                            return logger.exception(
                                f"Unable to retreive record id for {url} from field {field_name} for resource {resource}"
                            )

        url = f"{self.instance_url}{sf_consts.SALESFORCE_PICKLIST_URI(sf_consts.SALESFORCE_FIELDS_URI(resource), record_type_id)}"

        url = f"{url}/{field_name}" if field_name else url
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)

            return SObjectPicklistAdapter.create_from_api(
                {
                    "values": res["values"],
                    "salesforce_account": str(self.id),
                    "picklist_for": field_name,
                    "imported_by": str(self.user),
                    "salesforce_object": resource,
                    "integration_source": "SALESFORCE",
                }
            )

    def list_validations(self, resource):
        """Lists all (active) Validations that apply to a resource from the ValidationRules object"""

        url = f"{self.instance_url}{sf_consts.SALESFORCE_VALIDATION_QUERY(resource)}"
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)

            return self.format_validation_rules(str(self.id), str(self.user), res)

    def list_resource_data(self, resource, offset, *args, **kwargs):
        # add extra fields to query string
        extra_items = self.object_fields.get(resource)

        from .routes import routes

        resource_class = routes.get(resource)
        relationships = resource_class.get_child_rels()
        additional_filters = resource_class.additional_filters()
        limit = kwargs.pop("limit", sf_consts.SALESFORCE_QUERY_LIMIT)
        url = f"{self.instance_url}{sf_consts.SALESFORCE_RESOURCE_QUERY_URI(self.salesforce_id, resource, extra_items, relationships, limit=limit, additional_filters=additional_filters)}"
        if offset:
            url = f"{url} offset {offset}"
        logger.info(f"{url} was sent")
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)
            saved_response = res
            logger.info(
                f"Request returned {res.get('totalSize')} number of results for {resource} at offset {offset} with limit {limit}"
            )
            # regardless of the offset if the data is too large Salesforce will paginate
            while True:
                has_next_page = res.get("nextRecordsUrl", None)
                if has_next_page:
                    logger.info(f"Request returned a next page {has_next_page}")
                    next_page_url = self.instance_url + has_next_page
                    with Client as client:
                        res = client.get(
                            next_page_url,
                            headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
                        )
                        res = self._handle_response(res)
                        saved_response["records"] = [*saved_response["records"], *res["records"]]
                else:
                    break

            res = self._format_resource_response(saved_response, resource)
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
        fields.insert(0, "Id")
        url = f"{self.instance_url}{sf_consts.SALESFORCE_RESOURCE_QUERY_URI(self.salesforce_id, relationship, fields, additional_filters=[filter_query_string], limit=20 )}"
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)
            # no need to format to any adapter
            res = self._format_resource_response(res, None)
            return res

    def list_tasks(self):
        additional_filters = TaskAdapter.additional_filters()
        url = f"{self.instance_url}{sf_consts.SALSFORCE_TASK_QUERY_URI(self.salesforce_id, sf_consts.SALESFORCE_RESOURCE_TASK,sf_consts.TASK_QUERY_FIELDS, additional_filters=additional_filters,limit=10)}"
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)
            # no need to format to any adapter
            res = self._format_resource_response(res, "Task")
            return res

    def get_resource_count(self, resource):
        with Client as client:
            res = client.get(
                f"{self.instance_url}{sf_consts.SF_COUNT_URI(resource, self.salesforce_id)}",
                headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )

            return self._handle_response(res)

    def execute_alert_query(self, url, resource):
        """Handles alert requests to salesforce"""
        with Client as client:
            res = client.get(
                url, headers=sf_consts.SALESFORCE_USER_REQUEST_HEADERS(self.access_token),
            )
            res = self._handle_response(res)

            res = self._format_resource_response(res, resource)
            return res

    def revoke(self):
        # if a token is already expired a 400 error occurs we can ignore that
        with Client as client:
            client.post(sf_consts.REVOKE_URI, data={"token": self.access_token})
            client.post(sf_consts.REVOKE_URI, data={"token": self.refresh_token})

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
        """mapping of 'standard' data when sending from the SF API"""
        reverse = {}
        for k, v in AccountAdapter.integration_mapping.items():
            reverse[v] = k
        return reverse

    @staticmethod
    def get_child_rels():
        return {}

    @staticmethod
    def additional_filters():
        """pass custom additional filters to the url"""
        return ["AND IsDeleted = false"]

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
        with Client as client:
            r = client.patch(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )
            return SalesforceAuthAccountAdapter._handle_response(r)

    @staticmethod
    def create(data, access_token, custom_base, object_fields, user_id):
        json_data = json.dumps(
            AccountAdapter.to_api(data, AccountAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.RESOURCE_SYNC_ACCOUNT, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        with Client as client:
            r = client.post(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
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

    @property
    def name(self):
        return f"{self.secondary_data.get('FirstName')} {self.secondary_data.get('LastName')}"

    @staticmethod
    def get_child_rels():
        return {}

    @staticmethod
    def additional_filters():
        """pass custom additional filters to the url"""
        return ["AND IsDeleted = false"]

    @staticmethod
    def reverse_integration_mapping():
        """mapping of 'standard' data when sending from the SF API"""
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
    def create(data, access_token, custom_base, object_fields, user_id=None):
        json_data = json.dumps(
            ContactAdapter.to_api(data, ContactAdapter.integration_mapping, object_fields)
        )
        logger.info(f"JSON_DATA Create Contact {json_data}")
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.RESOURCE_SYNC_CONTACT, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        with Client as client:
            res = client.post(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )
            res = SalesforceAuthAccountAdapter._handle_response(res)

            url = f"{url}{res['id']}"
            r = client.get(url, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header})
            r = SalesforceAuthAccountAdapter._handle_response(r)
            r = OpportunityAdapter.from_api(r, user_id)
            return r

    @staticmethod
    def update_contact(data, access_token, custom_base, integration_id, object_fields):
        json_data = json.dumps(
            ContactAdapter.to_api(data, ContactAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.RESOURCE_SYNC_CONTACT, integration_id
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        with Client as client:
            r = client.patch(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )
            return SalesforceAuthAccountAdapter._handle_response(r)

    @property
    def as_dict(self):
        return vars(self)


class LeadAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.integration_source = kwargs.get("integration_source", None)
        self.integration_id = kwargs.get("integration_id", None)
        self.email = kwargs.get("email", None)
        self.owner = kwargs.get("owner", None)
        self.external_owner = kwargs.get("external_owner", None)
        self.name = kwargs.get("name", None)
        self.imported_by = kwargs.get("imported_by", None)
        self.secondary_data = kwargs.get("secondary_data", None)

    integration_mapping = dict(
        # mapping of 'standard' data when sending to the SF API
        integration_id="Id",
        email="Email",
        name="Name",
        owner="OwnerId",  # overwritten (ignored in reverse)
        account="AccountId",
        external_account="AccountId",
        external_owner="OwnerId",
    )

    @staticmethod
    def get_child_rels():
        return {}

    @staticmethod
    def additional_filters():
        """pass custom additional filters to the url"""
        return ["AND IsDeleted = false", "AND IsConverted = false"]

    @staticmethod
    def reverse_integration_mapping():
        """mapping of 'standard' data when sending from the SF API"""
        reverse = {}
        for k, v in LeadAdapter.integration_mapping.items():
            reverse[v] = k
        return reverse

    @staticmethod
    def from_api(data, user_id, *args, **kwargs):
        formatted_data = dict()
        mapping = LeadAdapter.reverse_integration_mapping()
        formatted_data = dict(secondary_data={})
        for k, v in data.items():
            if k in mapping:
                formatted_data[mapping.get(k)] = v

            formatted_data["secondary_data"][k] = v
        formatted_data["integration_source"] = org_consts.INTEGRATION_SOURCE_SALESFORCE
        formatted_data["imported_by"] = str(user_id)

        return LeadAdapter(**formatted_data)

    @staticmethod
    def to_api(data, mapping, object_fields):
        formatted_data = dict()
        for k, v in data.items():
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
    def create(data, access_token, custom_base, object_fields, user_id):
        logger.info(f"UNFORMATED DATA: {data}")
        json_data = json.dumps(
            LeadAdapter.to_api(data, LeadAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.RESOURCE_SYNC_LEAD, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        logger.info(f"REQUEST DATA: {json_data}")
        with Client as client:
            r = client.post(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )

            # get the opp as well uses the same url as the write but with get
            logger.info(f"REQUEST RES: {r.json()}")
            r = SalesforceAuthAccountAdapter._handle_response(r)
            url = f"{url}{r['id']}"
            r = client.get(url, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header})
            logger.info(f"NEW DATA: {r.json()}")
            r = SalesforceAuthAccountAdapter._handle_response(r)
            r = LeadAdapter.from_api(r, user_id)
            return r

    @staticmethod
    def update_lead(data, access_token, custom_base, salesforce_id, object_fields):
        json_data = json.dumps(
            LeadAdapter.to_api(data, LeadAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.RESOURCE_SYNC_LEAD, salesforce_id
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        with Client as client:
            r = client.patch(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
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
        """Builds sub query for resource"""
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
    def additional_filters():
        """pass custom additional filters to the url"""
        return ["AND IsDeleted = false", "AND IsClosed = false"]

    @staticmethod
    def reverse_integration_mapping():
        """mapping of 'standard' data when sending from the SF API"""
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

    @staticmethod
    def update_opportunity(data, access_token, custom_base, salesforce_id, object_fields):
        json_data = json.dumps(
            OpportunityAdapter.to_api(data, OpportunityAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(
            custom_base, sf_consts.RESOURCE_SYNC_OPPORTUNITY, salesforce_id
        )
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        with Client as client:
            r = client.patch(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )
            return SalesforceAuthAccountAdapter._handle_response(r)

    @staticmethod
    def create(data, access_token, custom_base, object_fields, user_id):

        json_data = json.dumps(
            OpportunityAdapter.to_api(data, OpportunityAdapter.integration_mapping, object_fields)
        )
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.RESOURCE_SYNC_OPPORTUNITY, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)

        with Client as client:
            r = client.post(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )
            # get the opp as well uses the same url as the write but with get
            r = SalesforceAuthAccountAdapter._handle_response(r)
            url = f"{url}{r['id']}"
            r = client.get(url, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header})

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
        with Client as client:
            r = client.post(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )
            return SalesforceAuthAccountAdapter._handle_response(r)

    @property
    def as_dict(self):
        return vars(self)


class ActivityAdapter:
    """Two types of activities Task (includes calls, emails) and Events"""

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
        with Client as client:
            r = client.post(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )
            return SalesforceAuthAccountAdapter._handle_response(r)


class TaskAdapter:
    """Two types of activities Task (includes calls, emails) and Events"""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.type = kwargs.get("type", None)
        self.category = kwargs.get("category", None)
        self.subject = kwargs.get("subject", None)
        self.description = kwargs.get("description", None)
        self.created_date = kwargs.get("created_date", None)
        self.activity_date = kwargs.get("activity_date", None)
        self.what_id = kwargs.get("what_id", None)
        self.who_id = kwargs.get("who_id", None)
        self.status = kwargs.get("status", None)

    @staticmethod
    def get_child_rels():
        return {}

    @staticmethod
    def additional_filters(**kwargs):
        """pass custom additional filters to the url"""
        time_zone = datetime.now().date().strftime("%Y-%m-%d")
        return [f"AND ActivityDate >= {time_zone}", "AND (NOT Status LIKE '%Completed%') "]

    # formatted_data.append(resource_class.from_api(result, self.user, *args))
    @staticmethod
    def from_api(result, user):
        """pass custom additional filters to the url"""
        return TaskAdapter(
            id=result["Id"],
            description=result["Description"],
            subject=result["Subject"],
            created_date=result["CreatedDate"],
            activity_date=result["ActivityDate"],
            what_id=result["WhatId"],
            who_id=result["WhoId"],
            status=result["Status"],
        )

    @staticmethod
    def save_task_to_salesforce(data, access_token, custom_base):
        json_data = json.dumps(data)
        url = sf_consts.SALESFORCE_WRITE_URI(custom_base, sf_consts.SALESFORCE_RESOURCE_TASK, "")
        token_header = sf_consts.SALESFORCE_BEARER_AUTH_HEADER(access_token)
        with Client as client:
            r = client.post(
                url, data=json_data, headers={**sf_consts.SALESFORCE_JSON_HEADER, **token_header},
            )
            return SalesforceAuthAccountAdapter._handle_response(r)

    @property
    def as_dict(self):
        return vars(self)
