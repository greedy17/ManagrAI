import logging
import requests
import textwrap
import json
import uuid
import httpx
from django.utils import timezone
import calendar
from django.core import serializers
from managr.utils.misc import get_site_url
from dateutil.parser import parse
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.template.exceptions import TemplateDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from background_task.models import CompletedTask
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import (
    filters,
    permissions,
    generics,
    mixins,
    status,
    viewsets,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from managr.api.emails import send_html_email
from managr.api.models import ManagrToken
from managr.utils import sites as site_utils
from managr.core.utils import pull_usage_data, get_user_totals
from managr.slack.helpers import requests as slack_requests, block_builders
from .nylas.auth import get_access_token, get_account_details
from .models import User, NylasAuthAccount, NoteTemplate
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserInvitationSerializer,
    UserRegistrationSerializer,
    NoteTemplateSerializer,
)
from managr.organization.models import Team
from .permissions import IsStaff
from managr.core.background import emit_process_calendar_meetings, emit_process_submit_chat_prompt

from .nylas.emails import (
    return_file_id_from_nylas,
    download_file_from_nylas,
)
from managr.salesforce.cron import (
    queue_users_sf_resource,
    queue_users_sf_fields,
)
from managr.hubspot.cron import queue_users_hs_fields, queue_users_hs_resource
from .nylas.models import NylasAccountStatusList
from managr.utils.client import Client, Variable_Client
from ..core import constants as core_consts

logger = logging.getLogger("managr")

WORD_TO_NUMBER = {
    "a": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

TIME_TO_NUMBER = {"week": 7, "weeks": 7, "month": 30, "months": 30, "year": 365, "tomorrow": 1}
DAYS_TO_NUMBER = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def swap_submitted_data_labels(data, fields):
    api_key_data = {}
    for label in data.keys():
        try:
            field_list = fields.filter(label__icontains=label)
            field = None
            for field_value in field_list:
                if len(field_value.label) == len(label):
                    field = field_value
                    break
            api_key_data[field.api_name] = data[label]
        except Exception as e:
            continue
    return api_key_data


def name_list_processor(resource_list, chat_response_name):
    most_count = 0
    most_matching = None
    chat_set = set(chat_response_name)
    for resource in resource_list:
        cleaned_string = (
            resource.display_value.lower()
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .split(" ")
        )
        same_set = set(chat_set).intersection(cleaned_string)
        if len(same_set) > most_count:
            most_count = len(same_set)
            most_matching = resource.display_value
    return most_matching


def convert_date_string(date_string, value):
    if value is None:
        value = datetime.now().date()
    else:
        value = value.split("T")[0]
    split_date_string = date_string.lower().split(" ")
    time_key = None
    number_key = 1
    if any("push" in s for s in split_date_string) or any("move" in s for s in split_date_string):
        for key in split_date_string:
            if key in TIME_TO_NUMBER.keys():
                time_key = TIME_TO_NUMBER[key]
            if key in WORD_TO_NUMBER:
                number_key = WORD_TO_NUMBER[key]
    elif any(key in split_date_string for key in DAYS_TO_NUMBER.keys()):
        for key in split_date_string:
            if key in DAYS_TO_NUMBER.keys():
                current = datetime.now()
                start = current - timezone.timedelta(days=current.weekday())
                day_value = start + timezone.timedelta(days=DAYS_TO_NUMBER[key])
                if any("next" in s for s in split_date_string):
                    day_value = day_value + timezone.timedelta(days=7)
                return day_value
    elif any("end" in s for s in split_date_string):
        if any("week" in s for s in split_date_string):
            current = datetime.strptime(value, "%Y-%m-%d")
            start = current - timezone.timedelta(days=current.weekday())
            return start + timezone.timedelta(days=4)
        elif any("month" in s for s in split_date_string):
            current = datetime.strptime(value, "%Y-%m-%d")
            last_of_month = calendar.monthrange(current.year, current.month)[1]
            return current.replace(day=last_of_month)
    elif any("week" in s for s in split_date_string):
        current = datetime.strptime(value, "%Y-%m-%d")
        return current + timezone.timedelta(days=7)
    if "back" in date_string:
        new_value = datetime.strptime(value, "%Y-%m-%d") - timezone.timedelta(
            days=(time_key * number_key)
        )
    else:
        if time_key:
            new_value = datetime.strptime(value, "%Y-%m-%d") + timezone.timedelta(
                days=(time_key * number_key)
            )
        else:
            try:
                date_parsed = parse(date_string)
                new_value = date_parsed
            except Exception as e:
                print(e)
                new_value = value
    return new_value


def clean_prompt_return_data(data, fields, crm, resource=None):
    cleaned_data = dict(data)
    notes = cleaned_data.pop("meeting_comments", None)
    subject = cleaned_data.pop("meeting_type", None)
    for key in cleaned_data.keys():
        try:
            field = fields.get(api_name=key)
            if resource and field.api_name in ["Name", "dealname"]:
                cleaned_data[key] = resource.secondary_data[key]
            if cleaned_data[key] is None or cleaned_data[key] == "":
                if resource:
                    cleaned_data[key] = resource.secondary_data[key]
                continue
            elif field.data_type == "TextArea":
                if resource and data[key] is not None:
                    current_value = (
                        resource.secondary_data[key]
                        if resource.secondary_data[key] is not None
                        else " "
                    )
                    cleaned_data[key] = f"{data[key]}\n\n{current_value}"
            elif field.data_type in ["Date", "DateTime"]:
                data_value = data[key]
                current_value = resource.secondary_data[key] if resource else None
                new_value = convert_date_string(data_value, current_value)
                if isinstance(new_value, str):
                    if resource:
                        cleaned_data[key] = resource.secondary_data[key]
                    else:
                        cleaned_data[key] = None
                else:
                    cleaned_data[key] = (
                        str(new_value.date())
                        if crm == "SALESFORCE"
                        else (str(new_value.date()) + "T00:00:00.000Z")
                    )
            elif field.api_name == "dealstage":
                if resource:
                    pipeline = field.options[0][resource.secondary_data["pipeline"]]
                    if pipeline:
                        stage_value = data[key].lower()
                        stage = [
                            stage
                            for stage in pipeline["stages"]
                            if stage["label"].lower() == stage_value
                        ]
                        if len(stage):
                            cleaned_data[key] = stage[0]["id"]
                        else:
                            cleaned_data[key] = resource.secondary_data["dealstage"]
            elif field.api_name in ["Amount", "amount"]:
                if isinstance(cleaned_data[key], int):
                    continue
                amount = cleaned_data[key]
                if "k" in amount:
                    amount = amount.replace("k", "000.0")
                if "$" in amount:
                    amount = amount.replace("$", "")
                cleaned_data[key] = amount
            elif field.data_type == "Picklist":
                if crm == "HUBSPOT":
                    options = field.options
                else:
                    options = field.crm_picklist_options.values
                value_found = False
                for value in options:
                    lowered_value = cleaned_data[key].lower()
                    current_value_label = value["label"].lower()
                    if lowered_value in current_value_label:
                        value_found = True
                        cleaned_data[key] = value["value"]
                if not value_found:
                    if resource:
                        cleaned_data[key] = resource.secondary_data[key]
                    else:
                        cleaned_data[key] = None
        except ValueError:
            continue
    cleaned_data["meeting_comments"] = notes
    cleaned_data["meeting_type"] = subject
    # logger.info(f"CLEAN PROMPT DEBUGGER: {cleaned_data}")
    return cleaned_data


def clean_prompt_string(prompt_string):
    random_bracket_insert_check = prompt_string[:5].find("}")
    if random_bracket_insert_check == 0:
        prompt_string = prompt_string[1:]
    cleaned_string = (
        prompt_string[prompt_string.index("{") : prompt_string.index("}") + 1]
        .replace("\n\n", "")
        .replace("\n ", "")
        .replace("\n", "")
        .replace("'s", "@s")
        .replace(" @s", " 's")
        .replace("', '", '", "')
        .replace("': '", '": "')
    )
    while "  " in cleaned_string:
        cleaned_string = cleaned_string.replace("  ", "")
    while "{  " in cleaned_string:
        cleaned_string = cleaned_string.replace("{  ", "{ ")
    cleaned_string = cleaned_string.replace("{ '", '{ "').replace("'}", '"}')
    return cleaned_string


def set_name_field(resource, crm):
    if resource in ["Opportunity", "Account"]:
        return "Name"
    elif resource == "Company":
        return "Company name"
    elif resource == "Deal":
        return "Deal Name"
    elif resource == "Contact":
        return "Email"
    return None


def set_owner_field(resource, crm):
    if resource in ["Opportunity", "Account", "Contact"] and crm == "SALESFORCE":
        return "Owner ID"
    elif resource == "Company":
        return "Company owner"
    elif resource == "Contact" and crm == "HUBSPOT":
        return "Contact owner"
    elif resource == "Deal":
        return "Deal owner"
    return None


def correct_data_keys(data):
    if "Company Name" in data.keys():
        data["Company name"] = data["Company Name"]
        del data["Company Name"]
    return data


def clean_data_for_summary(user_id, data, integration_id, resource_type):
    from managr.hubspot.routes import routes as hs_routes
    from managr.salesforce.routes import routes as sf_routes

    cleaned_data = dict(data)
    CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}
    user = User.objects.get(id=user_id)
    owner_field = "hubspot_owner_id" if user.crm == "HUBSPOT" else "OwnerId"
    try:
        cleaned_data.pop(owner_field)
    except KeyError:
        owner_field = None
    if "meeting_comments" in data.keys() and data["meeting_comments"] is None:
        cleaned_data.pop("meeting_comments")
        cleaned_data.pop("meeting_type")
    fields = user.object_fields.filter(api_name__in=cleaned_data.keys())
    ref_fields = fields.filter(data_type="Reference", crm_object=resource_type)
    if user.crm == "HUBSPOT":
        if "dealstage" in data.keys():
            found_stage = False
            field = fields.filter(api_name="dealstage").first()
            for pipeline in field.options[0].keys():
                if found_stage:
                    break
                current_pipeline = field.options[0][pipeline]["stages"]
                for stage in current_pipeline:
                    if stage["id"] == cleaned_data["dealstage"]:
                        cleaned_data["dealstage"] = stage["label"]
                        found_stage = True
    if len(ref_fields):
        for field in ref_fields:
            relationship = field.reference_to_infos[0]["api_name"]
            try:
                reference_record = (
                    CRM_SWITCHER[user.crm][relationship]["model"]
                    .objects.filter(integration_id=cleaned_data[field.api_name])
                    .first()
                ).display_value

            except Exception as e:
                logger.info(e)
                reference_record = integration_id
                pass
            cleaned_data[field.api_name] = reference_record
    return cleaned_data


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def submit_chat_prompt(request):
    from .constants import (
        OPEN_AI_COMPLETIONS_BODY,
        OPEN_AI_UPDATE_PROMPT,
        OPEN_AI_COMPLETIONS_URI,
        OPEN_AI_HEADERS,
    )
    from ..slack.models import OrgCustomSlackFormInstance
    from managr.salesforce.routes import routes as sf_routes
    from managr.hubspot.routes import routes as hs_routes

    user = User.objects.get(id=request.data["user_id"])
    CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}

    form_type = "CREATE" if "create" in request.data["prompt"].lower() else "UPDATE"
    form_template = user.team.team_forms.filter(
        form_type=form_type, resource=request.data["resource_type"]
    ).first()
    form = OrgCustomSlackFormInstance.objects.create(
        template=form_template,
        user=user,
        update_source="chat",
        chat_submission=request.data["prompt"],
    )
    fields = form_template.custom_fields.all()
    field_list = list(fields.values_list("label", flat=True))
    full_prompt = OPEN_AI_UPDATE_PROMPT(field_list, request.data["prompt"], datetime.now())
    url = OPEN_AI_COMPLETIONS_URI
    attempts = 1
    has_error = False
    resource_check = None
    token_amount = 500
    timeout = 30.0
    while True:
        message = None
        try:
            body = OPEN_AI_COMPLETIONS_BODY(
                user.email, full_prompt, token_amount=token_amount, top_p=0.1
            )
            # logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: body <{body}>")
            Client = Variable_Client(timeout)
            with Client as client:
                r = client.post(url, data=json.dumps(body), headers=OPEN_AI_HEADERS,)
            if r.status_code == 200:
                r = r.json()

                # logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: response <{r}>")
                choice = r["choices"][0]
                stop_reason = choice["finish_reason"]
                if stop_reason == "length":
                    if token_amount <= 2000:
                        message = {
                            "value": "Look like your prompt message is too long to process. Try removing white spaces!",
                        }
                    else:
                        token_amount += 500
                        continue
                text = choice["text"]
                cleaned_choice = clean_prompt_string(text)
                data = eval(cleaned_choice)
                name_field = set_name_field(request.data["resource_type"], user.crm)
                data = correct_data_keys(data)
                resource_check = data[name_field].lower().split(" ")
                lowered_type = request.data["resource_type"].lower()
                resource = None
                if lowered_type in resource_check:
                    resource_check.remove(lowered_type)
                if form_type == "CREATE" or len(resource_check):
                    if form_type == "UPDATE":
                        resource = None
                        for word in resource_check:
                            if request.data["resource_type"] not in ["Contact", "Lead"]:
                                query = (
                                    CRM_SWITCHER[user.crm][request.data["resource_type"]]["model"]
                                    .objects.for_user(user)
                                    .filter(name__icontains=word)
                                )
                                if query:
                                    if len(query) > 1:
                                        most_matching = name_list_processor(query, resource_check)
                                        resource = query.filter(name=most_matching).first()
                                    else:
                                        resource = query.first()
                                    break
                            else:
                                query = (
                                    CRM_SWITCHER[user.crm][request.data["resource_type"]]["model"]
                                    .objects.for_user(user)
                                    .filter(email__icontains=word)
                                )
                                if query:
                                    if len(query) > 1:
                                        most_matching = name_list_processor(query, resource_check)
                                        resource = query.filter(email=most_matching).first()
                                    else:
                                        resource = query.first()
                                    break
                        if resource:
                            # logger.info(f"SUBMIT CHAT PROMPT DEBUGGER: resource <{resource}>")
                            form.resource_id = str(resource.id)
                            form.save()
                        else:
                            has_error = True
                            message = 'Invalid Submission'
                            break
                    else:
                        if user.crm == "SALESFORCE":
                            if request.data["resource_type"] in ["Opportunity", "Account"]:
                                data["Name"] = resource_check
                        else:
                            if request.data["resource_type"] == "Deal":
                                data["Deal Name"] = resource_check
                        resource = None
                    owner_field = set_owner_field(request.data["resource_type"], user.crm)
                    data[owner_field] = user.crm_account.crm_id
                    swapped_field_data = swap_submitted_data_labels(data, fields)
                    cleaned_data = clean_prompt_return_data(
                        swapped_field_data, fields, user.crm, resource
                    )
                    form.save_form(cleaned_data, False)
                else:
                    has_error = True
                    message = ''
                break
            else:
                if attempts >= 5:
                    break
                else:
                    attempts += 1
                    continue
        except httpx.ReadTimeout as e:
            timeout += 30.0
            if attempts >= 2:
                has_error = True
                message = "There was an error communicating with Open AI"
                logger.exception(f"Read timeout from Open AI {e}")
            else:
                attempts += 1
                continue
        except Exception as e:
            logger.exception(f"Exception from Open AI response {e}")
            has_error = True
            message = (
                f" Looks like we ran into an issue with your prompt, try removing things like quotes and ampersands"
                if resource_check is None
                else f" We could not find a {data['resource_type']} named {resource_check} because of {e}"
            )

    if has_error:
        res = {"value": f"There was an error processing chat submission: {message}"}
        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
    if not has_error:
        res_text = (f"{resource.display_value} has been updated, please review",)

    return Response(
        data={
            **r,
            "form": form.id,
            "data": cleaned_data,
            "resource": {resource.display_value},
            "res": res_text,
            "resourceId": resource.id,
            "integrationId": resource.integration_id,
            "formType": form_type,
            "resourceType": request.data["resource_type"],
        },
        status=status.HTTP_200_OK
    )


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def draft_follow_up(request):

    user = User.objects.get(id=request.data["id"])
    instructions = request.data["instructions"]
    if not instructions:
        prompt = core_consts.OPEN_AI_MEETING_EMAIL_DRAFT(request.data["notes"])
        body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, prompt, 500, temperature=0.2)
    else:
        prompt = core_consts.OPEN_AI_EMAIL_DRAFT_WITH_INSTRUCTIONS(request.data["notes"], instructions)
        body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, prompt, 1000)    
    
    attempts = 1

    while True:
        try:
            with Client as client:
                url = core_consts.OPEN_AI_COMPLETIONS_URI
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            if r.status_code == 200:
                r = r.json()
                text = r.get("choices")[0].get("text")
                return Response(data={**r, "res": text})
        except Exception as e:
            res = {"value": f"error drafting email: {e}"}
            return Response(data=res)        


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def chat_next_steps(request):
    user = User.objects.get(id=request.data["id"])

    prompt = core_consts.OPEN_AI_NEXT_STEPS(request.data["notes"])
    body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, prompt, 500, temperature=0.2)
    attempts = 1
    while True:
        try:
            with Client as client:
                url = core_consts.OPEN_AI_COMPLETIONS_URI
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            if r.status_code == 200:
                r = r.json()
                text = r.get("choices")[0].get("text")
                return Response(data={**r, "res": text})
        except Exception as e:
            res = {"value": f"error getting next steps: {e}"}
            return Response(data=res)


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def get_chat_summary(request):

    user = User.objects.get(id=request.data["id"])

    cleaned_data = clean_data_for_summary(
        str(user.id), request.data["data"], request.data["integrationId"], request.data["resource"],
    )
    try:
        summary_prompt = core_consts.OPEN_AI_SUMMARY_PROMPT(cleaned_data)
        body = core_consts.OPEN_AI_COMPLETIONS_BODY(user.email, summary_prompt, 500, top_p=0.1)
        url = core_consts.OPEN_AI_COMPLETIONS_URI
        with Client as client:
            r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
            if r.status_code == 200:
                r = r.json()
                message_string_for_recap = r["choices"][0]["text"]
                return Response(data={**r, "res": message_string_for_recap})
    except Exception as e:
        res = {"value": f"error getting summary: {e}"}
        return Response(data=res)


@api_view(["post"])
@permission_classes([permissions.IsAuthenticated])
def log_chat_meeting(request):
    from managr.salesforce.models import MeetingWorkflow
    from managr.slack.models import OrgCustomSlackFormInstance
    from managr.core.exceptions import _handle_response, StopReasonLength
    from managr.salesforce.routes import routes as sf_routes
    from managr.hubspot.routes import routes as hs_routes

    CRM_SWITCHER = {"SALESFORCE": sf_routes, "HUBSPOT": hs_routes}

    user = User.objects.get(id=request.data["user_id"])
    workflow_id = request.data["workflow_id"]
    resource_type = request.data["resource_type"]
    workflow = MeetingWorkflow.objects.get(id=workflow_id)
    workflow.save()

    prompt = request.data["prompt"]
    form_type = (
        "CREATE" if ("create" in prompt.lower() and "update" not in prompt.lower()) else "UPDATE"
    )
    form_template = user.team.team_forms.filter(form_type=form_type, resource=resource_type).first()
    form = OrgCustomSlackFormInstance.objects.create(
        template=form_template, user=user, update_source="chat", chat_submission=prompt
    )
    fields = form_template.custom_fields.all()
    field_list = list(fields.values_list("label", flat=True))
    full_prompt = core_consts.OPEN_AI_UPDATE_PROMPT(field_list, prompt, datetime.now())
    url = core_consts.OPEN_AI_COMPLETIONS_URI
    attempts = 1
    has_error = False
    resource_check = None
    token_amount = 500
    timeout = 60.0
    while True:
        message = None
        try:
            body = core_consts.OPEN_AI_COMPLETIONS_BODY(
                user.email, full_prompt, token_amount=token_amount, top_p=0.1
            )
            Client = Variable_Client(timeout)
            with Client as client:
                r = client.post(url, data=json.dumps(body), headers=core_consts.OPEN_AI_HEADERS,)
                r = _handle_response(r)
                choice = r["choices"][0]
                text = choice["text"]
                cleaned_choice = clean_prompt_string(text)
                data = eval(cleaned_choice)
                name_field = set_name_field(resource_type, user.crm)
                data = correct_data_keys(data)
                resource_check = data[name_field].lower().split(" ")
                lowered_type = resource_type.lower()
                resource = None
                if lowered_type in resource_check:
                    resource_check.remove(lowered_type)
                if form_type == "CREATE" or len(resource_check):
                    if form_type == "UPDATE":
                        resource = None
                        for word in resource_check:
                            if resource_type not in ["Contact", "Lead"]:
                                query = (
                                    CRM_SWITCHER[user.crm][resource_type]["model"]
                                    .objects.for_user(user)
                                    .filter(name__icontains=word)
                                )
                                if query:
                                    if len(query) > 1:
                                        most_matching = name_list_processor(query, resource_check)
                                        resource = query.filter(name=most_matching).first()
                                    else:
                                        resource = query.first()
                                    break
                            else:
                                query = (
                                    CRM_SWITCHER[user.crm][resource_type]["model"]
                                    .objects.for_user(user)
                                    .filter(email__icontains=word)
                                )
                                if query:
                                    if len(query) > 1:
                                        most_matching = name_list_processor(query, resource_check)
                                        resource = query.filter(email=most_matching).first()
                                    else:
                                        resource = query.first()
                                    break
                        if resource:
                            form.resource_id = str(resource.id)
                            form.save()
                        else:
                            has_error = True
                            break
                    else:
                        if user.crm == "SALESFORCE":
                            if resource_type in ["Opportunity", "Account"]:
                                data["Name"] = resource_check
                        else:
                            if resource_type == "Deal":
                                data["Deal Name"] = resource_check
                        resource = None
                    owner_field = set_owner_field(resource_type, user.crm)
                    data[owner_field] = user.crm_account.crm_id
                    swapped_field_data = swap_submitted_data_labels(data, fields)
                    cleaned_data = clean_prompt_return_data(
                        swapped_field_data, fields, user.crm, resource
                    )
                    form.save_form(cleaned_data, False)
                else:
                    has_error = True
                break

        except StopReasonLength:
            if token_amount <= 2000:
                return Response(
                    data={
                        "data": "Look like your prompt message is too long to process. Try removing white spaces!",
                    }
                )
            else:
                token_amount += 500
                continue
        except httpx.ReadTimeout as e:
            timeout += 30.0
            if timeout >= 120.0:
                has_error = True
                message = "There was an error communicating with Open AI"
                logger.exception(f"Read timeout from Open AI {e}")
                break
            else:
                attempts += 1
                continue
        except Exception as e:
            logger.exception(f"Exception from Open AI response {e}")
            has_error = True
            message = (
                f"Looks like we ran into an issue with your prompt, try removing things like quotes and ampersands"
                if resource_check is None
                else f"We could not find a {resource_type} named {resource_check} because of {e}"
            )
            break
    if has_error:
        if workflow_id:
            logger.exception(
                f"There was an error processing chat submission for workflow {workflow} {message}"
            )
            workflow.failed_task_description.append(
                f"There was an error processing chat submission {message}"
            )
            workflow.save()
        return Response(data={"data": message,})

    if not has_error:

        if workflow_id:
            if not has_error:
                form.workflow = workflow
                form.update_source = "meeting (chat)"
                form.save()
                workflow.resource_type = resource_type
                workflow.resource_id = str(resource.id)
                workflow.save()
    return Response(data={**r, "data": cleaned_data,})


def field_syncs():
    queue_users_sf_fields()
    queue_users_hs_fields()
    return


def resource_syncs():
    queue_users_sf_resource()
    queue_users_hs_resource()
    return


def GET_COMMAND_OBJECTS():
    field_sync = field_syncs
    resource_sync = resource_syncs
    commands = {
        "SALESFORCE_FIELDS": field_sync,
        "SALESFORCE_RESOURCES": resource_sync,
        "PULL_USAGE_DATA": pull_usage_data,
    }
    return commands


def index(request):
    try:
        return render(request, "index.html", {})
    except TemplateDoesNotExist:
        return render(request, "core/index-placeholder.html", {})


class UserLoginView(mixins.CreateModelMixin, generics.GenericAPIView):
    """
    For admin login.
    """

    authentication_classes = ()
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """Validate user credentials.

        Return serialized user and auth token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If the serializer is valid, then the email/password combo is valid.
        # Get the user entity, from which we can get (or create) the auth token
        user = authenticate(**serializer.validated_data)
        if user is None:
            raise ValidationError(
                {
                    "non_field_errors": [
                        ("Incorrect email and password combination. " "Please try again")
                    ],
                }
            )
        login(request, user)
        # create token if one does not exist
        ManagrToken.objects.get_or_create(user=user, assigned_user=user)
        if user.access_token.is_expired:
            user.access_token.refresh(user.access_token)
        # Build and send the response
        u = User.objects.get(pk=user.id)
        serializer = UserSerializer(u, context={"request": request})
        response_data = serializer.data
        response_data["token"] = user.access_token.key
        return Response(response_data)


class UserLogoutView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        user = self.request.user
        url = get_site_url()
        redirect(f"{url}/login")
        logout(request)
        user.access_token.revoke()
        return


class UserRegistrationView(mixins.CreateModelMixin, generics.GenericAPIView):
    """Allow admins to create new user accounts and an organization"""

    authentication_classes = ()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """Validate user credentials.

        Return serialized user and auth token.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance

        # Log in the user server-side and make sure the response includes their
        # token so that they don't have to log in after plugging in their email
        # and password in this step.
        response_data = UserLoginSerializer.login(user, request)
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):

    serializer_class = UserSerializer
    filter_fields = ("organization",)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )

    search_fields = ("first_name", "last_name", "email")

    def get_queryset(self):
        return User.objects.for_user(self.request.user)

    def update(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs["pk"])
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # if request.data does not include quota/commit/upside,
        # then user should not be able to update another user's data
        for field in serializer.read_only_fields:
            # remove read_only_fields
            serializer.validated_data.pop(field, None)
        self.perform_update(serializer)
        user = serializer.instance

        serializer = UserSerializer(user, context={"request": request})
        response_data = serializer.data

        return Response(response_data)

    @action(
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
        detail=True,
        url_path="profile-photo",
    )
    def update_profile_photo(self, request, *args, **kwargs):
        photo = request.data.get("file")
        pk = kwargs.get("pk", None)
        u = User.objects.filter(pk=pk).first()
        if not u:
            raise ValidationError({"user": "invalid user id"})
        u.profile_photo = photo
        u.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _is_kpi_update(self, request):
        if request.data.get("quota") or request.data.get("commit") or request.data.get("upside"):
            return True
        return False

    @action(
        methods=["get"],
        permission_classes=[permissions.AllowAny],
        detail=False,
        url_path="retrieve-email",
    )
    def retrieve_email(self, request, *args, **kwargs):
        """retrieve's a users email to display in field on activation"""
        params = request.query_params
        pk = params.get("id")
        magic_token = params.get("token")

        try:
            user = User.objects.get(pk=pk)
            if str(user.magic_token) == str(magic_token) and user.is_invited:
                if user.is_active:
                    raise ValidationError(
                        {
                            "detail": [
                                (
                                    "It looks like you have already activate your account, click forgot password to reset it"
                                )
                            ]
                        }
                    )
                return Response({"email": user.email, "organization": user.organization.name})

            else:
                return Response(
                    {"non_field_errors": ("Invalid Link or Token")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=["post"],
        permission_classes=[permissions.AllowAny],
        detail=True,
        url_path="activate",
    )
    def activate(self, request, *args, **kwargs):
        # users should only be able to activate if they are in an invited state
        magic_token = request.data.get("token", None)
        password = request.data.get("password", None)
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        timezone = request.data.get("timezone", None)
        pk = kwargs.get("pk", None)
        if not password or not magic_token or not pk:
            raise ValidationError({"detail": [("A magic token, id, and password are required")]})
        try:
            user = User.objects.get(pk=pk)
            if str(user.magic_token) == str(magic_token) and user.is_invited:
                if user.is_active:
                    raise ValidationError(
                        {
                            "detail": [
                                (
                                    "It looks like you have already activate your account, click forgot password to reset it"
                                )
                            ]
                        }
                    )
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
                user.timezone = timezone
                # expire old magic token and create a new one for other uses
                user.regen_magic_token()
                if user.organization.is_paid is False:
                    user_team = Team.objects.create(
                        name=user.first_name, organization=user.organization, team_lead=user
                    )
                    user.team = user_team
                user.save()
                login(request, user)
                # create token if one does not exist
                ManagrToken.objects.get_or_create(user=user)

                # Build and send the response
                serializer = UserSerializer(user, context={"request": request})

                response_data = serializer.data
                response_data["token"] = user.access_token.key
                return Response(response_data)

            else:
                return Response(
                    {"non_field_errors": ("Invalid Link or Token")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="attach-file",
    )
    def attach_file(self, request, *args, **kwargs):
        """
        Attaches a file and returns file_id
        https://docs.nylas.com/reference#metadata
        """
        user = request.user
        file_object = request.FILES["file"]
        response = return_file_id_from_nylas(user=user, file_object=file_object)

        return Response(response, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsStaff],
        detail=False,
        url_path="staff/commands",
    )
    def launch_command(self, request, *args, **kwargs):
        COMMANDS = GET_COMMAND_OBJECTS()
        data = request.data
        command = data.get("command")
        command_function = COMMANDS[command]
        if command == "SALESFORCE_FIELDS":
            command_function()
            response_data = {
                "success": True,
                "message": "Successfully started field sync for users",
            }
        elif command == "SALESFORCE_RESOURCES":
            command_function()
            response_data = {
                "success": True,
                "message": "Successfully started resource sync for users",
            }
        else:
            # Here
            response_data = {
                "success": True,
                "message": "Successfully started resource sync for users",
                "data": command_function(),
            }
        return Response(data=response_data)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="modify-forecast",
    )
    def modify_forecast(self, request, *args, **kwargs):
        from managr.opportunity.models import Opportunity

        user = request.user
        action = request.data.get("action")
        ids = request.data.get("ids")
        if action == "add":
            for id in ids:
                user.current_forecast.add_to_state(id)
        else:
            for id in ids:
                user.current_forecast.remove_from_state(id)
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="get-forecast-values",
    )
    def get_forecast_values(self, request, *args, **kwargs):
        from managr.opportunity.serializers import OpportunitySerializer

        user = request.user
        res = user.current_forecast.get_current_values()
        logger.info(f"FORECAST VALUES ENDPOINT: {res}")
        opps = []
        for item in res:
            serializer = OpportunitySerializer(data=item.as_dict)
            serializer.is_valid()
            opps.append(serializer.data)
        return Response(data=opps, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        # permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="update-user-info",
    )
    def update_user_info(self, request, *args, **kwargs):
        """endpoint to update the Event Calendar ID, the Fake Meeting ID, the Zoom Channel, the Recap Receiver, and the Realtime Alert Config sections"""
        d = request.data
        event_calendar_id = d.get("event_calendar_id")
        fake_meeting_id = d.get("fake_meeting_id")
        zoom_channel = d.get("zoom_channel")
        recap_receivers = d.get("recap_receivers")
        realtime_alert_config = d.get("realtime_alert_config")
        user_id = d.get("user_id")
        user = User.objects.get(id=user_id)
        if user.event_calendar_id != event_calendar_id:
            user.event_calendar_id = event_calendar_id
        if user.fake_meeting_id != fake_meeting_id:
            user.fake_meeting_id = fake_meeting_id
        if user.zoom_channel != zoom_channel:
            user.zoom_channel = zoom_channel
        if user.recap_receivers != recap_receivers:
            user.recap_receivers = recap_receivers
        # Uncomment this when it's working
        # if user.realtime_alert_config != realtime_alert_config:
        #     user.realtime_alert_config = realtime_alert_config
        user.save()
        return Response(data=status.HTTP_200_OK)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="refresh-calendar-events",
    )
    def refresh_calendar_events(self, request, *args, **kwargs):
        import uuid

        user = self.request.user
        emit_process_calendar_meetings(
            str(user.id), f"calendar-meetings-{user.email}-{str(uuid.uuid4())}"
        )
        return Response(data={"success": True})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="remove-user",
    )
    def remove_user(self, request, *args, **kwargs):
        remove_id = request.data.get("remove_id")
        try:
            remove_user = User.objects.get(id=remove_id)
            remove_user.deactivate_user()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Remove user error: {e}")
            return Response(data={"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["GET"], permission_classes=(IsStaff,), detail=False, url_path="admin-tasks",
    )
    def admin_tasks(self, request, *args, **kwargs):
        tasks = CompletedTask.objects.all()[:100]
        dict_tasks = serializers.serialize("json", tasks)
        return Response(data={"tasks": dict_tasks})

    @action(
        methods=["GET"], permission_classes=(IsStaff,), detail=False, url_path="admin-users",
    )
    def admin_users(self, request, *args, **kwargs):
        param = request.query_params.get("org_id", None)
        users = User.objects.filter(organization=param)
        serialized = self.get_serializer(users, many=True).data
        return Response(serialized)

    @action(
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="performance-report",
    )
    def performance_report(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id", None)
        data = get_user_totals(user_id)
        return Response(data=data)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="get-trial-users",
    )
    def get_trial_users(self, request, *args, **kwargs):
        from managr.core.serializers import UserTrialSerializer

        users = User.objects.filter(is_active=True)
        serialized = UserTrialSerializer(users, many=True)
        return Response(data=serialized.data, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="revoke-token",
    )
    def revoke_token(self, request, *args, **kwargs):
        token = request.data.get("token", None)
        if not token:
            raise ValidationError(
                {"detail": {"key": "field_error", "message": "Token is required", "field": "token"}}
            )
        user_id = request.data.get("user_id", None)
        if not user_id:
            raise ValidationError(
                {
                    "detail": {
                        "key": "field_error",
                        "message": "user id is required",
                        "field": "user_id",
                    }
                }
            )
        user = User.objects.filter(id=user_id)
        token = user.access_token.revoke()
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="refresh-token",
    )
    def refresh_token(self, request, *args, **kwargs):
        token = request.data.get("token", None)
        if not token:
            raise ValidationError(
                {"detail": {"key": "field_error", "message": "Token is required", "field": "token"}}
            )
        user_id = request.data.get("user_id", None)
        if not user_id:
            raise ValidationError(
                {
                    "detail": {
                        "key": "field_error",
                        "message": "user id is required",
                        "field": "user_id",
                    }
                }
            )
        user = User.objects.filter(id=user_id)
        token = user.access_token.refresh(user.access_token)
        return Response({"detail": "User token has been successfully refreshed"})


class ActivationLinkView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None, **kwargs):
        user = None

        try:
            user = User.objects.get(email=kwargs["email"])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user and user.is_active:
            return Response(
                data={"activation_link": user.activation_link}, status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes(
    [permissions.IsAuthenticated,]
)
def get_email_authorization_link(request):
    u = request.user
    return Response({"link": u.email_auth_link})
    # generate link


class GetFileView(View):
    def get(self, request, file_id):
        """This endpoint returns a file from nylas using an nylas ID"""
        user = request.user
        response = download_file_from_nylas(user=user, file_id=file_id)
        return response


"""
TODO 2021-01-15 William: Need to determine whether we still need this viewset.

class NotificationSettingsViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationOptionSerializer

    def get_queryset(self):
        return NotificationOption.objects.for_user(self.request.user)

    def list(self, request, *args, **kwargs):
        # qs = NotificationOption.objects.for_user(request.user)
        qs = self.get_queryset()
        resource_param = request.query_params.get("resource", None)
        if resource_param:
            qs = qs.filter(resource=resource_param)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = NotificationOptionSerializer(
                qs, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = NotificationOptionSerializer(
            qs, many=True, context={"request": request}
        )
        return Response()

    @action(
        methods=["PATCH"],
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
        url_path="update-settings",
    )
    def update_settings(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        selections = data.get("selections", [])
        for sel in selections:
            selection, created = NotificationSelection.objects.get_or_create(
                option=sel["option"], user=user
            )
            selection.value = sel["value"]
            selection.save()
        return Response()
 """


class NylasAccountWebhook(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """Respond to Nylas verification webhook"""
        challenge = request.query_params.get("challenge", None)
        if challenge:
            return HttpResponse(content=challenge)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """
        This endpoint will have to eventually be handled by a different instance.
        Unlike the messages endpoint we cannot grab an id and pass it to the async
        we can however track the delta and check the api for that delta or we
        can save it in the cache.
        """
        data = request.data
        deltas = data.get("deltas", [])
        # a list class wrapper around custom NylasAccountStatus class
        nylas_data = NylasAccountStatusList(deltas)
        # calling .values on the NylasAccStatList returns a list of lists using
        # the object keys passed
        values = [
            # details is position 0 in the first entry and 1 is resource_status
            (item[0]["account_id"], item[1])
            for item in nylas_data.values("details", "resource_status")
        ]
        email_accounts = []
        for v in values:
            email_account = NylasAuthAccount.objects.filter(account_id=v[0]).first()
            if email_account:
                if email_account.sync_state != v[1]:
                    email_account.sync_state = v[1]
                    email_accounts.append(email_account)
                    # 2021-01-16 William: The following function is not defined.
                    # emit_email_sync_event(str(email_account.user.id), v[1])
                # if the account is having problems send an email and a notification
                # we will be removing accounts from our db and from nylas if it has
                # been inactive for 5 days

        NylasAuthAccount.objects.bulk_update(email_accounts, ["sync_state"])

        return Response()


@api_view(["POST"])
@permission_classes(
    [permissions.IsAuthenticated,]
)
def email_auth_token(request):
    u = request.user
    # if user already has a token revoke it this will make sure we do not have duplicates on Nylas
    try:
        u.nylas.revoke()
    except NylasAuthAccount.DoesNotExist:
        # pass here since user does not already have a token to revoke
        pass
    except requests.exceptions.HTTPError as e:
        if 401 in e.args:
            # delete the record so we can create a new link
            u.nylas.delete()
            # we have out of sync data, pass
            # we have a cron job running every 24 hours to remove all old
            # tokens which are not in sync
            pass

    code = request.data.get("code", None)

    if not code:
        raise ValidationError({"detail": "Code parameter missing"})

    if code:
        # ask nylas for user account and create a new model entry
        # returns nylas object that has account and token needed to populate model
        # note nylas error on sdk when code is invalid does not return a proper error,
        # we may need to catch the error as an exception or not use the api sdk
        try:
            access_token = get_access_token(code)
            details = get_account_details(access_token)

            account = details["account"]
            calendar_data = details["calendars"]
            email_check = [cal for cal in calendar_data if cal["name"] == account["email_address"]]
            calendar = [cal for cal in calendar_data if cal["read_only"] is False]
            if len(email_check):
                calendar_id = email_check[0]["id"]
            else:
                if len(calendar):
                    calendar_id = calendar[0]["id"]
                else:
                    calendar_id = None
            logger.info(
                textwrap.dedent(
                    f"""
                ---------------------------
                NYLAS CALENAR ACCOUNT CREATION INFO: \n
                ----------------------\n
                ACCOUNT INFO: {account}\n
                CALENDAR INFO:{calendar_data}\n
                EMAIL CHECK: {email_check} \n 
                CALENDAR CHECK: {calendar} \n
                FOUND CALENDAR ID: {calendar_id}\n
                -----------------------"""
                )
            )
            NylasAuthAccount.objects.create(
                access_token=access_token,
                account_id=account["account_id"],
                email_address=account["email_address"],
                provider=account["provider"],
                sync_state=account["sync_state"],
                name=account["name"],
                user=request.user,
                event_calendar_id=calendar_id,
            )
            emit_process_calendar_meetings(
                str(request.user.id), f"calendar-meetings-{request.user.email}-{str(uuid.uuid4())}"
            )
        except requests.exceptions.HTTPError as e:
            if 400 in e.args:
                raise ValidationError(
                    {"non_field_errors": {"code": "Code invalid or expired please try again"}}
                )

    else:
        raise ValidationError({"detail": {"code": "code is a required field"}})
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def revoke_access_token(request):
    """endpoint to revoke access for a token
    currently users can only revoke their own access
    if an account needs to revoke someone elses they may
    email the superuser, when we create a list of admins
    for each org they will have access to delete their user's tokens
    alternatively they can set a user to is_active=false and this will
    call the revoke endpoint for the user in an org
    """
    if request.user.nylas.access_token:
        try:
            request.user.nylas.revoke()
            return Response(status=status.HTTP_200_OK)
        except NylasAuthAccount.DoesNotExist:
            # pass here since user does not already have a token to revoke
            pass
        except requests.exceptions.HTTPError as e:
            if 401 in e.args:
                # delete the record so we can create a new link
                request.user.nylas.delete()
                # we have out of sync data, pass
                # we have a cron job running every 24 hours to remove all old
                #  tokens which are not in sync
                pass
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        raise ValidationError({"non_form_errors": {"no_token": "user has not authorized nylas"}})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_account_status(request):
    """Check whether a User account associated with a given email is active."""
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)

    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if user.is_active:
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserInvitationView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserInvitationSerializer
    # permission_classes = (IsSuperUser | IsOrganizationManager,)

    def create(self, request, *args, **kwargs):
        u = request.user
        if not u.is_superuser:
            if str(u.organization.id) != str(request.data["organization"]):
                # allow custom organization in request only for SuperUsers
                return Response(status=status.HTTP_403_FORBIDDEN)
        if len(u.organization.users.all()) >= u.organization.number_of_allowed_users:
            return Response(status=status.HTTP_426_UPGRADE_REQUIRED)
        slack_id = request.data.get("slack_id", False)

        make_team_lead = request.data.pop("team_lead")
        if make_team_lead:
            request.data["make_team_lead"] = True
        team = Team.objects.get(id=request.data.pop("team"))
        request.data["team"] = team.id
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance
        serializer = UserSerializer(user, context={"request": request})
        response_data = serializer.data
        if slack_id:
            text = f"{u.full_name} has invited you to join the Managr! Activate your account here"
            channel_res = slack_requests.request_user_dm_channel(
                slack_id, u.organization.slack_integration.access_token
            ).json()
            channel = channel_res.get("channel", {}).get("id")
            logger.info(f"User {user.id} activation link: {user.activation_link}")
            blocks = [
                block_builders.section_with_button_block(
                    "Register", "register", text, url=user.activation_link
                )
            ]
            if hasattr(u.organization, "slack_integration"):
                slack_requests.send_channel_message(
                    channel,
                    u.organization.slack_integration.access_token,
                    text="You've been invited to Managr!",
                    block_set=blocks,
                )
        return Response(response_data)


class UserPasswordManagmentView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """endpoint to reset a password that is forgotten"""
        token = request.data.get("token", None)
        if not token:
            raise ValidationError(
                {"detail": {"key": "field_error", "message": "Token is required", "field": "token"}}
            )
        user_id = request.data.get("user_id", None)
        if not user_id:
            raise ValidationError(
                {
                    "detail": {
                        "key": "field_error",
                        "message": "user id is required",
                        "field": "user_id",
                    }
                }
            )
        password = request.data.get("password", None)
        if not password:
            raise ValidationError(
                {
                    "detail": {
                        "key": "field_error",
                        "message": "new password is required",
                        "field": "password",
                    }
                }
            )
        user = User.objects.filter(id=user_id)
        if not user.exists():
            raise ValidationError(
                {
                    "detail": {
                        "key": "not_found",
                        "message": f"User with {user_id} not found in system",
                        "field": "user_id",
                    }
                }
            )
        else:

            user_account = user.first()
            token_valid = default_token_generator.check_token(user_account, token)
            if not token_valid:
                raise ValidationError(
                    {
                        "detail": {
                            "key": "invalid_or_expired_token",
                            "message": "The token is either invalid or expired",
                            "field": "token",
                        }
                    }
                )
            user_account.set_password(password)
            user_account.save()
            UserLoginSerializer.login(user_account, request)

            return Response({"detail": "password successfully reset"})


@api_view(["POST"])
@permission_classes(
    [permissions.AllowAny,]
)
def request_reset_link(request):
    """endpoint to request a password reset email (forgot password)"""
    email = request.data.get("email", None)
    # if no email is provided return validation error
    if email is None:
        raise ValidationError(
            {"detail": {"key": "field_error", "message": "Email Is Required", "field": "email"}}
        )
    # regardless of whether an email exists for a user return a 200 res
    # so that we can avoid phishing attempts
    user = User.objects.filter(email=email)
    if user.exists():
        user_account = user.first()
        context = {
            "site_url": site_utils.get_site_url(),
            "user_id": user_account.id,
            "token": default_token_generator.make_token(user_account),
        }
        subject = render_to_string("registration/password_reset_subject.txt")
        send_html_email(
            subject,
            "registration/password_reset_email.html",
            settings.DEFAULT_FROM_EMAIL,
            [user_account.email],
            context=context,
        )

    return Response({"detail": "password reset email sent"})


@api_view(["GET"])
@permission_classes(
    [permissions.AllowAny,]
)
def get_task_status(request):
    data = {}
    verbose_name = request.GET.get("verbose_name", None)
    if verbose_name:
        try:
            task = CompletedTask.objects.get(verbose_name=verbose_name)
            if task:
                data = {"completed": True}
        except CompletedTask.DoesNotExist:
            data = {"completed": False}
        except Exception as e:
            logger.exception(f"Uncaught exception on task status: {e}")
    logger.info(f"Task status for: {verbose_name}, {data}")
    return Response(data=data)


class NoteTemplateViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):

    serializer_class = NoteTemplateSerializer

    def get_queryset(self):
        return NoteTemplate.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            logger.exception(f"Error validating data for note template <{e}>")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.request.data
        serializer = self.serializer_class(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_200_OK)
