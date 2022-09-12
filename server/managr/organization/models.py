from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import JSONField, ArrayField
from django.forms import CharField

from managr.salesforce.adapter.models import (
    Product2Adapter,
    Pricebook2Adapter,
    ContactAdapter,
    AccountAdapter,
    PricebookEntryAdapter,
    OpportunityLineItemAdapter,
)
from managr.utils.misc import datetime_appended_filepath
from managr.core.models import TimeStampModel, IntegrationModel, User
from managr.salesforce.exceptions import ResourceAlreadyImported
from managr.slack.helpers import block_builders
from managr.opportunity import constants as opp_consts
from . import constants as org_consts


class OrganizationQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(pk=user.organization_id)
        else:
            return None


class Organization(TimeStampModel):
    """
    Main Organization Model, Users are attached to this model
    Users can either be limited, or Manager (possibly also have a main admin for the org)
    """

    name = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to=datetime_appended_filepath, max_length=255, blank=True)
    state = models.CharField(
        max_length=255, choices=org_consts.STATE_CHOCIES, default=org_consts.STATE_ACTIVE,
    )
    is_trial = models.BooleanField(default=False)
    ignore_emails = ArrayField(
        models.CharField(max_length=255),
        default=list,
        help_text="Email to ignore in meeting reviews",
        blank=True,
    )
    has_products = models.BooleanField(default=False)
    number_of_allowed_users = models.IntegerField(default=1)
    objects = OrganizationQuerySet.as_manager()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def deactivate_all_users(self):
        # TODO: When deleting an org also remember to revoke nylas tokens and request delete
        """helper method to deactivate all users if their org is deactivated"""
        users = User.objects.filter(organization=self)
        for u in users:
            u.state = org_consts.STATE_INACTIVE
            u.save()

    def change_admin_user(self, user, preserve_fields=False):
        """Method to change the is_admin user for an organization"""
        templates = user.team.team_forms.all()

        if preserve_fields:
            for form in templates:
                new_admin = user
                current_admin = self.users.filter(is_admin=True).first()
                fields = form.fields.filter(is_public=False)
                form_fields = fields.values_list("api_name", flat=True)
                new_admin_fields = new_admin.imported_sobjectfield.filter(
                    api_name__in=[form_fields], salesforce_object=form.resource
                )
                form_field_set = form.formfield_set.all()
                for formfield in form_field_set:
                    new_field = new_admin_fields.filter(api_name=formfield.field.api_name).first()
                    if new_field:
                        formfield.field = new_field
                        formfield.save()
        else:
            for form in templates:
                form.fields.filter(is_public=False).delete()
        admin_team = current_admin.team
        current_admin.is_admin = False
        current_admin.save()
        new_admin.is_admin = True
        new_admin.user_level = "MANAGER"
        new_admin.save()
        admin_team.team_lead = new_admin
        admin_team.save()
        return new_admin

    def update_has_settings(self, type):
        if type == "products":
            self.has_products = True
            self.save()

    def create_initial_team(self):
        admin = self.users.filter(is_admin=True).first()
        team = Team.objects.create(name=self.name, organization=self, team_lead=admin)
        forms = self.custom_slack_forms
        forms.update(team=team)
        users = self.users
        users.update(team=team)

    def add_to_admin_team(self, user_email):
        user = self.users.filter(email=user_email).first()
        admin = self.users.filter(is_admin=True).first()
        user.team = admin.team
        user.save()
        return


class AccountQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(owner__team=user.team)
            else:
                return self.filter(organization=user.organization, owner=user)
        else:
            return None


class Account(TimeStampModel, IntegrationModel):
    """
    Accounts are potential and exisiting clients that
    can be made into leads and added to lists

    """

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "Organization", related_name="accounts", on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "organization.Account",
        on_delete=models.SET_NULL,
        related_name="parent_account",
        blank=True,
        null=True,
    )
    parent_integration_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="UUID from integration for parent account, saved in case of errors",
    )
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="accounts", blank=True, null=True
    )
    external_owner = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = AccountQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} {self.organization}"

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def title(self):
        """Returns the name as a title using common fields as we have with leads and opps"""
        return self.name

    def save(self, *args, **kwargs):
        """In case of duplicates update not save"""
        obj = (
            Account.objects.filter(
                integration_id=self.integration_id, organization=self.organization
            )
            .exclude(id=self.id)
            .first()
        )
        if obj:
            return

        return super(Account, self).save(*args, **kwargs)

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    def update_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Account"
            ).values_list("api_name", flat=True)
            res = AccountAdapter.update_account(
                data, token, base_url, self.integration_id, object_fields
            )
            self.is_stale = True
            self.save()
            return res

    def create_in_salesforce(self, data=None, user_id=None):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Account"
            ).values_list("api_name", flat=True)
            res = AccountAdapter.create_account(
                data, token, base_url, self.integration_id, object_fields
            )
            from managr.salesforce.routes import routes

            serializer = routes["Account"]["serializer"](data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance

    def get_current_values(self, *args, **kwargs):
        integration_id = self.integration_id
        token = self.owner.salesforce_account.access_token
        base_url = self.owner.salesforce_account.instance_url
        return AccountAdapter.get_current_values(integration_id, token, base_url, self.owner.id)

    def update_database_values(self, data, *args, **kwargs):
        data.pop("meeting_comments", None)
        data.pop("meeting_type", None)
        self.secondary_data.update(data)
        return self.save()


class ContactQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.organization and user.is_active:
            if user.user_level in ["SDR", "MANAGER"]:
                return self.filter(owner__team=user.team)
            else:
                return self.filter(owner=user)
        else:
            return None


class Contact(TimeStampModel, IntegrationModel):

    email = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="contacts", blank=True, null=True
    )
    account = models.ForeignKey(
        "organization.Account",
        on_delete=models.SET_NULL,
        related_name="contacts",
        null=True,
        blank=True,
    )
    external_owner = models.CharField(max_length=255, blank=True)
    external_account = models.CharField(max_length=255, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = ContactQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        data["owner"] = str(self.owner.id)
        return ContactAdapter(**data)

    @property
    def name(self):
        """returns full name for use with blocksets"""
        email = "N/A"
        first_name = "N/A"
        last_name = "N/A"
        if self.secondary_data.get("Email", None) not in ["", None]:
            email = self.secondary_data.get("Email")
        if self.secondary_data.get("FirstName", None) not in ["", None]:
            first_name = self.secondary_data.get("FirstName")
        if self.secondary_data.get("LastName", None) not in ["", None]:
            last_name = self.secondary_data.get("LastName")
        return f"{first_name} {last_name} <{email}>"

    def __str__(self):
        return f"contact integration: {self.integration_source}: {self.integration_id}, email: {self.email}"

    @property
    def as_slack_option(self):
        return block_builders.option(self.email, str(self.id))

    def save(self, *args, **kwargs):
        # if there is an integration id make sure it is unique
        if self.integration_id:
            existing = (
                Contact.objects.filter(
                    integration_id=self.integration_id, imported_by=self.imported_by
                )
                .exclude(id=self.id)
                .first()
            )
            if existing:
                raise ResourceAlreadyImported()
        return super(Contact, self).save(*args, **kwargs)

    def create_in_salesforce(self, data=None, user_id=None):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Contact"
            ).values_list("api_name", flat=True)
            res = ContactAdapter.create(data, token, base_url, self.integration_id, object_fields)
            from managr.salesforce.routes import routes

            serializer = routes["Contact"]["serializer"](data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance

    def update_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Contact"
            ).values_list("api_name", flat=True)
            res = ContactAdapter.update_contact(
                data, token, base_url, self.integration_id, object_fields
            )
            self.is_stale = True
            self.save()
            return res

    def get_current_values(self, *args, **kwargs):
        integration_id = self.integration_id
        token = self.owner.salesforce_account.access_token
        base_url = self.owner.salesforce_account.instance_url
        return ContactAdapter.get_current_values(integration_id, token, base_url, self.owner.id)

    def update_database_values(self, data, *args, **kwargs):
        data.pop("meeting_comments", None)
        data.pop("meeting_type", None)
        self.secondary_data.update(data)
        return self.save()


class StageQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(Q(organization=user.organization))
        else:
            return self.none()


class Stage(TimeStampModel, IntegrationModel):
    """
    Each Org Will have its own stages on set up
    """

    label = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=255, default="#9B9B9B", help_text="hex code for color")
    value = models.CharField(
        max_length=255, blank=True, help_text="This may be use as a unique value, if it exists"
    )
    organization = models.ForeignKey(
        "Organization", related_name="stages", on_delete=models.CASCADE,
    )
    order = models.IntegerField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    forecast_category = models.CharField(
        max_length=255, choices=opp_consts.FORECAST_CHOICES, blank=True
    )

    objects = StageQuerySet.as_manager()

    @property
    def as_slack_option(self):
        return block_builders.option(self.label, self.id)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Stage ({self.id}) -- label: {self.label}"

    def save(self, *args, **kwargs):
        obj = (
            Stage.objects.filter(integration_id=self.integration_id, organization=self.organization)
            .exclude(id=self.id)
            .first()
        )
        if obj:
            return
        return super(Stage, self).save(*args, **kwargs)


class ActionChoiceQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(organization=user.organization_id)
        else:
            return None


class ActionChoice(TimeStampModel):
    title = models.CharField(max_length=255, blank=True, null=False)
    description = models.CharField(max_length=255, blank=True, null=False)
    organization = models.ForeignKey(
        "organization.Organization", on_delete=models.CASCADE, related_name="action_choices",
    )

    objects = ActionChoiceQuerySet.as_manager()

    @property
    def as_slack_option(self):
        return block_builders.option(self.title, self.title)

    @property
    def as_sf_option(self):
        # model these into sf optiona key value pairs to be then changed into slack options
        return dict(attributes={}, label=self.title, value=self.title, validFor=[])

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f" ActionChoice ({self.id}) -- Title: {self.title}, Organization: {self.organization.name}"


class Pricebook2QuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(organization=user.organization)
        else:
            return None


class Pricebook2(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    last_viewed_date = models.DateTimeField(null=True)
    organization = models.ForeignKey(
        "organization.Organization", on_delete=models.CASCADE, related_name="pricebooks", null=True
    )
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = Pricebook2QuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.id))

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        return Pricebook2Adapter(**data)

    def update_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Pricebook2"
            ).values_list("api_name", flat=True)
            res = Pricebook2Adapter.update_pricebook(
                data, token, base_url, self.integration_id, object_fields
            )
            self.is_stale = True
            self.save()
            return res

    def create_in_salesforce(self, data=None, user_id=None):
        """when synchronous create in db first to be able to use immediately"""
        token = self.owner.salesforce_account.access_token
        base_url = self.owner.salesforce_account.instance_url
        object_fields = self.owner.salesforce_account.object_fields.filter(
            salesforce_object="Opportunity"
        ).values_list("api_name", flat=True)
        if not data:
            data = self.adapter_class

        res = Pricebook2Adapter.create_pricebook(data, token, base_url, object_fields, user_id)
        from managr.salesforce.routes import routes

        serializer = routes["Pricebook2"]["serializer"](data=res.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.instance


class Product2QuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(organization=user.organization)
        else:
            return None


class Product2(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    organization = models.ForeignKey(
        "organization.Organization", on_delete=models.CASCADE, related_name="products", null=True
    )
    objects = Product2QuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        return Product2Adapter(**data)

    def update_in_salesforce(self, data):
        if self.owner and hasattr(self.owner, "salesforce_account"):
            token = self.owner.salesforce_account.access_token
            base_url = self.owner.salesforce_account.instance_url
            object_fields = self.owner.salesforce_account.object_fields.filter(
                salesforce_object="Product2"
            ).values_list("api_name", flat=True)
            res = Product2Adapter.update_product(
                data, token, base_url, self.integration_id, object_fields
            )
            self.is_stale = True
            self.save()
            return res

    def create_in_salesforce(self, data=None, user_id=None):
        """when synchronous create in db first to be able to use immediately"""
        token = self.owner.salesforce_account.access_token
        base_url = self.owner.salesforce_account.instance_url
        object_fields = self.owner.salesforce_account.object_fields.filter(
            salesforce_object="Product2"
        ).values_list("api_name", flat=True)
        if not data:
            data = self.adapter_class

        res = Product2Adapter.create_product(data, token, base_url, object_fields, user_id)
        from managr.salesforce.routes import routes

        serializer = routes["Product2"]["serializer"](data=res.as_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.instance


class PricebookEntryQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(pricebook__organization=user.organization)
        else:
            return None


class PricebookEntry(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=150)
    unit_price = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
    external_pricebook = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    external_product = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    pricebook = models.ForeignKey(
        "organization.Pricebook2", related_name="pricebook_entries", on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        "organization.Product2", related_name="pricebook_entry", on_delete=models.CASCADE,
    )
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = PricebookEntryQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        return PricebookEntryAdapter(**data)

    @property
    def as_slack_option(self):
        return block_builders.option(self.name, str(self.integration_id))

    def get_current_values(self):
        res = self.user.salesforce_account.adapter_class.get_resource_in_list(
            "PricebookEntry", list(self.state.keys())
        )
        return res


class OpportunityLineItemQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(product__organization=user.organization)
        else:
            return None


class OpportunityLineItem(TimeStampModel, IntegrationModel):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    external_pricebookentry = models.CharField(
        max_length=255, blank=True, help_text="value from the integration", null=True
    )
    external_product = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    external_opportunity = models.CharField(
        max_length=255, blank=True, help_text="value from the integration"
    )
    pricebookentry = models.ForeignKey(
        "organization.PricebookEntry",
        related_name="opportunity_line_item",
        on_delete=models.CASCADE,
        null=True,
    )
    product = models.ForeignKey(
        "organization.Product2",
        related_name="opportunity_line_item",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    opportunity = models.ForeignKey(
        "opportunity.Opportunity",
        related_name="opportunity_line_item",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    unit_price = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
    quantity = models.DecimalField(max_digits=13, decimal_places=2, default=0.00, null=True,)
    total_price = models.DecimalField(max_digits=30, decimal_places=15, default=0.00, null=True,)
    secondary_data = JSONField(
        default=dict,
        null=True,
        help_text="All non primary fields that are on the model each org may have its own",
        max_length=500,
    )
    objects = OpportunityLineItemQuerySet.as_manager()

    class Meta:
        ordering = ["-datetime_created"]

    @property
    def adapter_class(self):
        data = self.__dict__
        data["id"] = str(data["id"])
        return OpportunityLineItemAdapter(**data)

    def update_in_salesforce(self, user_id, data):
        user = User.objects.get(id=user_id)
        if user and hasattr(user, "salesforce_account"):
            token = user.salesforce_account.access_token
            base_url = user.salesforce_account.instance_url
            object_fields = user.salesforce_account.object_fields.filter(
                salesforce_object="OpportunityLineItem"
            ).values_list("api_name", flat=True)
            res = OpportunityLineItemAdapter.update_opportunitylineitem(
                data, token, base_url, self.integration_id, object_fields
            )
            self.is_stale = True
            self.save()
            return res

    @staticmethod
    def create_in_salesforce(data=None, user_id=None):
        user = User.objects.get(id=user_id)
        if user and hasattr(user, "salesforce_account"):
            if "UnitPrice" not in data.keys():
                entry = PricebookEntry.objects.get(integration_id=data["PricebookEntryId"])
                data["UnitPrice"] = str(entry.unit_price)
            token = user.salesforce_account.access_token
            base_url = user.salesforce_account.instance_url
            object_fields = user.salesforce_account.object_fields.filter(
                salesforce_object="OpportunityLineItem"
            ).values_list("api_name", flat=True)
            res = OpportunityLineItemAdapter.create(data, token, base_url, object_fields, user_id)
            from managr.salesforce.routes import routes

            serializer = routes["OpportunityLineItem"]["serializer"](data=res.as_dict)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance

    def get_current_values(self, *args, **kwargs):
        integration_id = self.integration_id
        token = self.opportunity.owner.salesforce_account.access_token
        base_url = self.opportunity.owner.salesforce_account.instance_url
        return OpportunityLineItemAdapter.get_current_values(
            integration_id, token, base_url, self.opportunity.owner.id
        )

    def update_database_values(self, data, *args, **kwargs):
        data.pop("meeting_comments", None)
        data.pop("meeting_type", None)
        self.secondary_data.update(data)
        return self.save()


class TeamQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self.all()
        elif user.organization and user.is_active:
            return self.filter(organization=user.organization)
        else:
            return None


class Team(TimeStampModel):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "organization.Organization", related_name="teams", on_delete=models.CASCADE
    )
    team_lead = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="team_lead_of"
    )

    objects = TeamQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} - {self.team_lead.email}"

    def delete(self):
        if self.team_forms:
            for form in self.team_forms.all():
                form.delete()
        admin_team = Team.objects.filter(organization=self.organization).first()
        self.users.all().update(team=admin_team)
        team_lead = self.team_lead
        team_lead.team = admin_team
        self.team_lead.save()
        super(Team, self).delete()

    def change_team_lead(self, user, preserve_fields=False):
        templates = user.organization.custom_slack_forms.all()

        if preserve_fields:
            for form in templates:
                new_team_lead = user
                fields = form.fields.filter(is_public=False)
                form_fields = fields.values_list("api_name", flat=True)
                new_admin_fields = new_team_lead.imported_sobjectfield.filter(
                    api_name__in=[form_fields], salesforce_object=form.resource
                )
                form_field_set = form.formfield_set.all()
                for formfield in form_field_set:
                    new_field = new_admin_fields.filter(api_name=formfield.field.api_name).first()
                    if new_field:
                        formfield.field = new_field
                        formfield.save()
        else:
            for form in templates:
                form.fields.filter(is_public=False).delete()

        self.team_lead = new_team_lead
        self.save()

