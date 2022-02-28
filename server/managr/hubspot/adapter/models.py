import os.path
import logging
from requests.exceptions import HTTPError
from managr.utils.client import Client
from .exceptions import CustomAPIException, CustomXMLException
from .. import constants as hubspot_consts

logger = logging.getLogger("managr")


class HubspotAuthAccountAdapter:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.salesforce_id = kwargs.get("salesforce_id", None)
        self.user = kwargs.get("user", None)

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

    @staticmethod
    def _handle_xml_response(response, fn_name=None):
        if not hasattr(response, "status_code"):
            raise ValueError

        elif response.status_code >= 200 and response.status_code < 300:
            if response.status_code == 204:
                return {}
            try:
                xmldict = process_xml_dict(response.content)
                print(f"SUCCESS XMLDICT: {xmldict}")
            except Exception as e:
                CustomAPIException(e, fn_name)
        else:
            xmldict = process_xml_dict(response.content)
            print(f"FAIL XMLDICT: {xmldict}")
            status_code = response.status_code
            error_data = xmldict["error_data"]
            error_code = None
            if status_code == 400:
                error_param = error_data["faultcode"]
                error_message = error_data["faultstring"]
            else:
                error_param = error_data["faultcode"]
                error_message = error_data["faultstring"]
            kwargs = {
                "status_code": status_code,
                "error_code": error_code,
                "error_param": error_param,
                "error_message": error_message,
            }
            CustomXMLException(HTTPError(kwargs), fn_name)
        return xmldict

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
        data["sobjects"] = OrderedDict(
            {
                sf_consts.RESOURCE_SYNC_ACCOUNT: True,
                sf_consts.RESOURCE_SYNC_CONTACT: True,
                sf_consts.RESOURCE_SYNC_LEAD: True,
                sf_consts.RESOURCE_SYNC_OPPORTUNITY: True,
                sf_consts.RESOURCE_SYNC_PRODUCT2: True,
                sf_consts.RESOURCE_SYNC_PRICEBOOK2: True,
                sf_consts.RESOURCE_SYNC_PRICEBOOKENTRY: True,
                sf_consts.RESOURCE_SYNC_OPPORTUNITYLINEITEM: True,
            }
        )
        return HubspotAuthAccountAdapter(**data)

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
            return HubspotAuthAccountAdapter._handle_response(res)

    def refresh(self):
        data = sf_consts.REAUTHENTICATION_BODY(self.refresh_token)
        with Client as client:
            res = client.post(
                f"{sf_consts.REFRESH_URI}", data=data, headers=sf_consts.AUTHENTICATION_HEADERS,
            )

            return HubspotAuthAccountAdapter._handle_response(res)

    def list_fields(self, resource):
        """Uses the UI API to list fields for a resource using this endpoint only returns fields a user has access to"""
        url = f"{self.instance_url}{sf_consts.SALESFORCE_FIELDS_URI(resource)}"
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

        add_filters = kwargs.get("filter", None)
        resource_class = routes.get(resource)
        relationships = resource_class.get_child_rels()
        additional_filters = (
            resource_class.additional_filters() if add_filters is None else add_filters
        )
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
            # regardless of the offset if the data is too large Hubspot will paginate
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
        print(url)
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

