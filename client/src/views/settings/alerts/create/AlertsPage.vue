<template>
  <div class="alerts-page">
    <div class="col">
      <h2 class="title">Smart Alert Templates</h2>
      <p class="sub__">Highly recommended and easy to setup</p>
    </div>

    <div class="alert_cards">
      <div class="card__">
        <div class="card__header">
          <h3><span style="color: #5f8cff">Close Date</span> Approaching</h3>
        </div>
        <button @click="goToCloseDateApproaching" class="orange_button">Activate</button>
      </div>

      <div class="card__">
        <div class="card__header">
          <h3><span style="color: #5f8cff">Close Date</span> Passed</h3>
        </div>
        <button @click="goToCloseDatePassed" class="orange_button">Activate</button>
      </div>

      <div class="card__">
        <div class="card__header">
          <h3><span style="color: #ff7649">Deal</span> Rotting</h3>
        </div>
        <button @click="goToDealRotting" class="orange_button">Activate</button>
      </div>

      <div class="card__">
        <div class="card__header">
          <h3>Update <span style="color: #69e3cd">Forecast</span></h3>
        </div>
        <button class="cs__button">Coming Soon</button>
      </div>
    </div>

    <!-- <ExpandablePanel>
      <template v-slot:panel-header="{ classes, expand }" class="box__header">
        <div :class="classes" @click="expand">
          <span :class="alertTemplateForm.field.resourceType.isValid ? 'slate' : 'gray'">
            1. <strong style="color: #cc3873; font-weight: bold">Select</strong> the Salesforce
            Object that you'd like to build an alert for
          </span>

          <span
            :class="`${classes + '__status' + ' ' + classes + '__status--success'}`"
            v-if="alertTemplateForm.field.resourceType.isValid"
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/checkmark.svg#checkmark" />
            </svg>
            <span>Complete</span>
          </span>
          <span :class="`${classes + '__status' + ' ' + classes + '__status--error'}`" v-else>
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
            <span> Incomplete </span>
          </span>
        </div>
      </template>
      <template slot="panel-content">
        <FormField :errors="alertTemplateForm.field.resourceType.errors">
          <template v-slot:input>
            <DropDownSearch
              :items.sync="SOBJECTS_LIST"
              :itemsRef.sync="alertTemplateForm.field._resourceType.value"
              v-model="alertTemplateForm.field.resourceType.value"
              displayKey="key"
              valueKey="value"
              nullDisplay="Salesforce Objects"
              searchable
              local
              @input="alertTemplateForm.field.resourceType.validate()"
              class="pad"
            />
          </template>
        </FormField>
      </template>
    </ExpandablePanel>
    <ExpandablePanel v-if="alertTemplateForm.field.resourceType.isValid">
      <template v-slot:panel-header="{ classes, expand }" class="box__header">
        <div :class="classes" @click="expand">
          <span
            :class="
              alertTemplateForm.field.title.isValid &&
              !alertTemplateForm.field.alertGroups.groups
                .map((fields) => fields.isValid)
                .includes(false)
                ? 'slate'
                : 'gray'
            "
          >
            2. <strong style="color: #cc3873">Build</strong> your Smart Alert</span
          ><span
            :class="`${classes + '__status' + ' ' + classes + '__status--success'}`"
            v-if="
              alertTemplateForm.field.title.isValid &&
              !alertTemplateForm.field.alertGroups.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/checkmark.svg#checkmark" />
            </svg>
            <span>Complete</span>
          </span>
          <span :class="`${classes + '__status' + ' ' + classes + '__status--error'}`" v-else>
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
            <span> Incomplete </span>
          </span>
        </div>
      </template>
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <div style="display: flex; flex-direction: row">
            <FormField
              id="alert-title"
              v-model="alertTemplateForm.field.title.value"
              placeholder="Name your alert (required)"
              :errors="alertTemplateForm.field.title.errors"
              @blur="alertTemplateForm.field.title.validate()"
            />
          </div>

          <div
            :key="index"
            v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups"
            class="alerts-page__groups__group mar col"
          >
            <AlertGroup
              :form="alertGroup"
              :resourceType="alertTemplateForm.field.resourceType.value"
            />
            <div class="row">
              <div class="group">
                <button class="btn btn--secondary btn--icon" @click="onAddAlertGroup">
                  <svg width="24px" height="24px" viewBox="0 0 24 24">
                    <use fill="#199e54" xlink:href="@/assets/images/add.svg#add" />
                  </svg>
                </button>
                <p class="sub">Group</p>
              </div>
              <div class="group" v-if="alertTemplateForm.field.alertGroups.groups.length > 1">
                <button
                  class="btn btn--danger btn--icon"
                  @click.stop="onRemoveAlertGroup(index)"
                  :disabled="alertTemplateForm.field.alertGroups.groups.length - 1 <= 0"
                >
                  <svg width="24px" height="24px" viewBox="0 0 24 24">
                    <use xlink:href="@/assets/images/remove.svg#remove" />
                  </svg>
                </button>
                <p class="sub">Remove</p>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">Please Select a resource to get started</div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel
      v-if="
        alertTemplateForm.field.title.isValid &&
        !alertTemplateForm.field.alertGroups.groups.map((fields) => fields.isValid).includes(false)
      "
    >
      <template v-slot:panel-header="{ classes, expand }" class="box__header">
        <div :class="classes" @click="expand">
          <span
            :class="
              !alertTemplateForm.field.alertMessages.groups
                .map((fields) => fields.isValid)
                .includes(false)
                ? 'slate'
                : 'gray'
            "
            >3. <strong style="color: #cc3873; font-weight: bold">Construct</strong> your alert
            message
          </span>
          <span
            :class="`${classes + '__status' + ' ' + classes + '__status--success'}`"
            v-if="
              !alertTemplateForm.field.alertMessages.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/checkmark.svg#checkmark" />
            </svg>
            <span>Complete</span>
          </span>
          <span :class="`${classes + '__status' + ' ' + classes + '__status--error'}`" v-else>
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
            <span> Incomplete </span>
          </span>
        </div>
      </template>
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <div class="alerts-page__message" style="height: 60vh">
            <div class="alerts-page__message-options">
              <div class="alerts-page__message-options-body" style="height: 5rem; width: 30rem">
                <FormField
                  :errors="alertTemplateForm.field.alertMessages.groups[0].field.body.errors"
                >
                  <template v-slot:input>
                    <quill-editor
                      @blur="alertTemplateForm.field.alertMessages.groups[0].field.body.validate()"
                      ref="message-body"
                      v-model="alertTemplateForm.field.alertMessages.groups[0].field.body.value"
                      :options="{
                        modules: { toolbar: { container: ['bold', 'italic', 'strike'] } },
                        placeholder:
                          'Type your message here, or copy and paste your favorite template...',
                        theme: 'snow',
                      }"
                      class="bottom"
                    />
                  </template>
                </FormField>
                <div class="alerts-page__message-options-body__bindings">
                  <div class="alerts-page__message-options-body__bindings__fields">
                    <ListContainer v-if="!listVisible" horizontal>
                      <template v-slot:list>
                        <ListItem
                          :key="key"
                          v-for="(val, key) in recipientBindings"
                          :item="val.referenceDisplayLabel"
                          :active="true"
                          @item-selected="bindText(`__Recipient.${val.apiName}`)"
                        />
                      </template>
                    </ListContainer>
                    <DropDownSearch
                      v-if="!dropdownVisible"
                      :items="fields.list"
                      @input="bindText(`${selectedResourceType}.${$event}`)"
                      displayKey="referenceDisplayLabel"
                      valueKey="apiName"
                      nullDisplay="Select field to display"
                      searchable
                      :hasNext="!!fields.pagination.hasNextPage"
                      @load-more="fieldNextPage"
                      @search-term="onSearchFields"
                      auto
                      class="left"
                    />
                  </div>
                  <div style="display: flex; flex-direction: row">
                    <div class="group">
                      <button class="btn btn--secondary btn--icon" @click="showList">
                        <svg width="24px" height="24px" viewBox="0 0 24 24">
                          <use fill="#199e54" xlink:href="@/assets/images/add.svg#add" />
                        </svg>
                      </button>
                      <p class="sub">Recipient name</p>
                    </div>
                    <div class="group">
                      <button class="btn btn--secondary btn--icon" @click="showDropDown">
                        <svg width="24px" height="24px" viewBox="0 0 24 24">
                          <use fill="#199e54" xlink:href="@/assets/images/add.svg#add" />
                        </svg>
                      </button>
                      <p class="sub">Insert Salesforce field</p>
                    </div>
                  </div>
                  <p style="font-size: 14px">
                    <strong class="pink">Pro Tip:</strong> inserting the
                    <strong>Salesforce field</strong> will display the field value in the message.
                  </p>
                </div>
              </div>
            </div>
            <div
              class="alerts-page__message-template"
              style="margin-left: 7.5rem; margin-top: -1rem"
            >
              <h3 class="pink">Templates:</h3>
              <div style="font-size: 14px">
                <div class="templates">
                  <p>
                    Hey <strong>{ __Recipient.full_name }</strong>, your deal
                    <strong>{ Opportunity.Name }</strong> has a passed closed date
                    <strong>{ Opportunity.Name }</strong>. Please update it!
                  </p>
                </div>

                <div class="templates">
                  <p>
                    <strong>{ Opportunity.Name }</strong> is a new Opp booked for this week! The
                    appointment was booked via <strong>{ Opportunity.LeadSource }</strong>!
                  </p>
                  <p>Handoff notes: <strong>{ Opportunity.Handoff_Notes_c }</strong></p>
                  <p style="margin-top: -0.75rem">
                    Using a Competitor: <strong>{ Opportunity.Competitors_c }</strong>
                  </p>
                  <p style="margin-top: -0.75rem">
                    Meeting date:
                    <strong>{ Opportunity.Meeting_Date_c }</strong>
                  </p>
                </div>

                <div class="templates">
                  <p>
                    Please update the forecast for <strong>{ Opportunity.Name }</strong>! it's
                    expected to close on <strong>{ Opportunity.CloseDate }</strong> and forecasted
                    as <strong>{ Opportunity.ForecastCategoryName }</strong> - please ither move to
                    Commit or update the Close Date.
                  </p>
                  <p>Next Step: <strong>{ Opportunity.NextStep }</strong></p>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">Please Select a resource to get started</div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel
      v-if="
        !alertTemplateForm.field.alertMessages.groups
          .map((fields) => fields.isValid)
          .includes(false)
      "
    >
      <template v-slot:panel-header="{ classes, expand }" class="box__header">
        <div :class="classes" @click="expand">
          <span
            :class="
              !alertTemplateForm.field.alertConfig.groups
                .map((fields) => fields.isValid)
                .includes(false)
                ? 'slate'
                : 'gray'
            "
          >
            4. <strong style="color: #cc3873">Choose</strong> your delivery options </span
          ><span> </span>
          <span
            v-if="
              !alertTemplateForm.field.alertConfig.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
            :class="`${classes + '__status' + ' ' + classes + '__status--success'}`"
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/checkmark.svg#checkmark" />
            </svg>
            <span>Complete</span>
          </span>
          <span :class="`${classes + '__status' + ' ' + classes + '__status--error'}`" v-else>
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
            <span> Incomplete </span>
          </span>
        </div>
      </template>
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <div
            class="alerts-page__settings row_"
            :key="i"
            v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
          >
            <div class="alerts-page__settings__day">
              <FormField
                v-if="form.field.recurrenceFrequency.value == 'MONTHLY'"
                placeholder="Day of month"
                :errors="form.field.recurrenceDay.errors"
                @blur="form.field.recurrenceDay.validate()"
                v-model="form.field.recurrenceDay.value"
                small
                style="margin-top: 2rem; margin-bottom: 2rem"
              />
              <FormField
                v-else-if="form.field.recurrenceFrequency.value == 'WEEKLY'"
                :errors="form.field.recurrenceDay.errors"
                style="margin-bottom: 3rem; margin-top: 2rem"
              >
                <template v-slot:input>
                  <DropDownSearch
                    :items.sync="weeklyOpts"
                    :itemsRef.sync="form.field._recurrenceDay.value"
                    v-model="form.field.recurrenceDay.value"
                    @input="form.field.recurrenceDay.validate()"
                    displayKey="key"
                    valueKey="value"
                    nullDisplay="Select Day"
                    searchable
                    local
                  />
                </template>
              </FormField>
              <div class="alerts-page__settings__frequency">
                <label class="alerts-page__settings__frequency-label">Weekly</label>
                <ToggleCheckBox
                  @input="
                    form.field.recurrenceFrequency.value == 'WEEKLY'
                      ? (form.field.recurrenceFrequency.value = 'MONTHLY')
                      : (form.field.recurrenceFrequency.value = 'WEEKLY')
                  "
                  :value="form.field.recurrenceFrequency.value !== 'WEEKLY'"
                  offColor="#199e54"
                  onColor="#199e54"
                />
                <label class="alerts-page__settings__frequency-label">Monthly</label>
              </div>
            </div>
            <div class="alerts-page__settings__target-users" style="margin-bottom: 2rem">
              <span class="muted">
                <em style="margin-left: 0.5rem">Select Pipelines.</em>
              </span>
              <FormField :errors="form.field.alertTargets.errors">
                <template v-slot:input>
                  <DropDownSearch
                    :items.sync="userTargetsOpts"
                    :itemsRef.sync="form.field._alertTargets.value"
                    v-model="form.field.alertTargets.value"
                    @input="form.field.alertTargets.validate()"
                    displayKey="fullName"
                    valueKey="id"
                    nullDisplay="Search"
                    searchable
                    multi
                    medium
                    :loading="users.loadingNextPage"
                    :hasNext="!!users.pagination.hasNextPage"
                    @load-more="onUsersNextPage"
                    @search-term="onSearchUsers"
                  />
                </template>
              </FormField>
            </div>
            <div class="alerts-page__settings__recipients">
              <span
                v-if="
                  form.field._recipients.value && form.field.recipientType.value == 'SLACK_CHANNEL'
                "
                class="muted--link--important"
              >
                Please make sure @managr has been added to
                <em>{{ form.field._recipients.value.name }}</em> channel
              </span>
              <span v-if="form.field.recipientType.value == 'USER_LEVEL'" class="muted">
                <em style="margin-left: 0.5rem; margin-top: 2rem">Select Recipients.</em>
              </span>
              <FormField
                v-if="form.field.recipientType.value == 'USER_LEVEL'"
                :errors="form.field.recipients.errors"
                style="margin-bottom: 2.5rem"
              >
                <template v-slot:input>
                  <DropDownSearch
                    :items.sync="recipientOpts"
                    :itemsRef.sync="form.field._recipients.value"
                    v-model="form.field.recipients.value"
                    @input="form.field.recipients.validate()"
                    displayKey="fullName"
                    valueKey="id"
                    nullDisplay="Search"
                    searchable
                    multi
                    medium
                    :loading="users.loadingNextPage"
                    :hasNext="!!users.pagination.hasNextPage"
                    @load-more="onUsersNextPage"
                    @search-term="onSearchUsers"
                  />
                </template>
              </FormField>

              <FormField
                v-if="form.field.recipientType.value == 'SLACK_CHANNEL'"
                :errors="form.field.recipients.errors"
              >
                <template v-slot:input>
                  <DropDownSearch
                    :items.sync="channelOpts.channels"
                    :itemsRef.sync="form.field._recipients.value"
                    v-model="form.field.recipients.value"
                    @input="form.field.recipients.validate()"
                    displayKey="name"
                    valueKey="id"
                    nullDisplay="Channels"
                    :hasNext="!!channelOpts.nextCursor"
                    @load-more="listChannels(channelOpts.nextCursor)"
                    searchable
                    local
                  >
                    <template v-slot:tn-dropdown-option="{ option }">
                      <img
                        v-if="option.isPrivate == true"
                        class="card-img"
                        style="width: 1rem; height: 1rem; margin-right: 0.2rem"
                        src="@/assets/images/lockAsset.png"
                      />
                      {{ option['name'] }}
                    </template>
                  </DropDownSearch>
                </template>
              </FormField>

              <span
                @click="
                  form.field.recipientType.value = recipientTypeToggle(
                    form.field.recipientType.value,
                  )
                "
                class="bolder"
                v-if="form.field.recipientType.value == 'USER_LEVEL'"
              >
                Send to a <strong class="pink">#channel</strong> instead ?
              </span>

              <span
                @click="
                  form.field.recipientType.value = recipientTypeToggle(
                    form.field.recipientType.value,
                  )
                "
                class="bolder"
                v-else
              >
                Send to a group of users (DM) instead ?
              </span>
            </div>

            <div class="alerts-page__settings-remove">
              <button
                class="btn btn--danger btn--icon"
                @click.stop="onRemoveSetting(i)"
                :disabled="alertTemplateForm.field.alertConfig.groups.length - 1 <= 0"
              >
                <svg width="16px" height="16px" viewBox="0 0 24 24">
                  <use xlink:href="@/assets/images/remove.svg#remove" />
                </svg>
              </button>
            </div>
          </div>
          <div class="add__group">
            <button class="btn btn--secondary btn--icon" @click="onAddAlertSetting">
              <svg width="24px" height="24px" viewBox="0 0 24 24">
                <use fill="#199e54" xlink:href="@/assets/images/add.svg#add" />
              </svg>
            </button>
            <p class="sub">Add a group</p>
          </div>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">Please Select a resource to get started</div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel
      class="pink"
      title="5. Confirm and save your alert"
      v-if="
        !alertTemplateForm.field.alertConfig.groups.map((fields) => fields.isValid).includes(false)
      "
    >
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <AlertSummary :form="alertTemplateForm" />
          <div class="center">
            <PulseLoadingSpinnerButton
              :loading="savingTemplate"
              class="primary-button"
              text="Save alert"
              @click.stop="onSave"
              :disabled="!alertTemplateForm.isValid || savingTemplate"
            />
          </div>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">Please Select a resource to get started</div>
        </template>
      </template>
    </ExpandablePanel> -->
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'

import { quillEditor } from 'vue-quill-editor'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
//Internal
import FormField from '@/components/forms/FormField'
import AlertGroup from '@/views/settings/alerts/create/_AlertGroup'
import AlertSummary from '@/views/settings/alerts/create/_AlertSummary'
import ListContainer from '@/components/ListContainer'
import ListItem from '@/components/ListItem'
import SlackNotificationTemplate from '@/views/settings/alerts/create/SlackNotificationTemplate'
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'
import DropDownSearch from '@/components/DropDownSearch'
import ExpandablePanel from '@/components/ExpandablePanel'
import Modal from '@/components/Modal'

/**
 * Services
 */

import AlertTemplate, {
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertOperandForm,
} from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import {
  SObjectField,
  SObjectValidations,
  SObjectPicklist,
  NON_FIELD_ALERT_OPTS,
  SOBJECTS_LIST,
} from '@/services/salesforce'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'AlertsPage',
  components: {
    ExpandablePanel,
    DropDownSearch,
    ListContainer,
    ListItem,
    SlackMessagePreview,
    AlertGroup,
    SlackNotificationTemplate,
    quillEditor,
    ToggleCheckBox,
    FormField,
    AlertSummary,
    PulseLoadingSpinnerButton,
    Modal,
  },
  data() {
    return {
      channelOpts: new SlackListResponse(),
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: [],
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      users: CollectionManager.create({ ModelClass: User }),
      recipientBindings: [
        { referenceDisplayLabel: 'Recipient Full Name', apiName: 'full_name' },
        { referenceDisplayLabel: 'Recipient First Name', apiName: 'first_name' },
        { referenceDisplayLabel: 'Recipient Last Name', apiName: 'last_name' },
        { referenceDisplayLabel: 'Recipient Email', apiName: 'email' },
      ],
      alertRecipientOpts: [
        { key: 'Myself', value: 'SELF' },
        { key: 'Owner', value: 'OWNER' },
        { key: 'All Managers', value: 'MANAGERS' },
        { key: 'All Reps', value: 'REPS' },
        { key: 'Everyone', value: 'ALL' },
        { key: 'SDR', value: 'SDR' },
      ],
      alertTargetOpts: [
        { key: 'Myself', value: 'SELF' },
        { key: 'All Managers', value: 'MANAGERS' },
        { key: 'All Reps', value: 'REPS' },
        { key: 'Everyone', value: 'ALL' },
        { key: 'SDR', value: 'SDR' },
      ],
      weeklyOpts: [
        { key: 'Monday', value: '0' },
        { key: 'Tuesday', value: '1' },
        { key: 'Wednesday', value: '2' },
        { key: 'Thursday', value: '3' },
        { key: 'Friday', value: '4' },
        { key: 'Saturday', value: '5' },
        { key: 'Sunday', value: '6' },
      ],
    }
  },
  async created() {
    if (this.user.slackRef) {
      await this.listChannels()
    }
    if (this.user.userLevel == 'MANAGER') {
      await this.users.refresh()
    }
  },
  watch: {
    selectedResourceType: {
      immediate: true,
      async handler(val, prev) {
        if (prev && val !== prev) {
          this.alertTemplateForm = this.alertTemplateForm.reset()
          this.selectedResourceType = val
        }
        if (this.selectedResourceType) {
          this.fields.filters.salesforceObject = this.selectedResourceType
          this.fields.filters.page = 1
          await this.fields.refresh()
        }
      },
    },
  },
  methods: {
    async listChannels(cursor = null) {
      const res = await SlackOAuth.api.listChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.channelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.channelOpts = results
    },
    recipientTypeToggle(value) {
      if (!this.user.slackRef) {
        this.$Alert.alert({ type: 'error', message: 'Slack Not Integrated', timeout: 2000 })
        return 'USER_LEVEL'
      }
      if (value == 'USER_LEVEL') {
        return 'SLACK_CHANNEL'
      } else if (value == 'SLACK_CHANNEL') {
        return 'USER_LEVEL'
      }
      return value
    },
    async onSave() {
      this.savingTemplate = true
      this.alertTemplateForm.validate()
      if (this.alertTemplateForm.isValid) {
        try {
          const res = await AlertTemplate.api.createAlertTemplate({
            ...this.alertTemplateForm.toAPI,
            user: this.$store.state.user.id,
          })
          this.$router.push({ name: 'ListTemplates' })
        } catch (e) {
          this.$Alert.alert({
            message: 'An error occured saving template',
            timeout: 2000,
            type: 'error',
          })
        } finally {
          this.savingTemplate = false
        }
      }
    },
    bindText(val) {
      this.$refs['message-body'].quill.focus()
      let start = 0
      if (this.editor.selection.lastRange) {
        start = this.editor.selection.lastRange.index
      }
      this.editor.insertText(start, `{ ${val} }`)
    },
    onAddAlertGroup() {
      // length determines order
      const order = this.alertTemplateForm.field.alertGroups.groups.length
      if (order >= 3) {
        this.$Alert.alert({ message: 'You can only add 3 groups', timeout: 2000 })
        return
      }
      // set next order

      this.alertTemplateForm.addToArray('alertGroups', new AlertGroupForm())
      this.alertTemplateForm.field.alertGroups.groups[order].field.groupOrder.value = order
    },
    onAddAlertSetting() {
      if (this.alertTemplateForm.field.alertConfig.groups.length >= 3) {
        this.$Alert.alert({ message: 'You can only add 3 configurations', timeout: 2000 })
        return
      }
      this.alertTemplateForm.addToArray('alertConfig', new AlertConfigForm())
    },
    onRemoveAlertGroup(i) {
      // get order and update options

      if (this.alertTemplateForm.field.alertGroups.groups.length - 1 <= 0) {
        return
      }

      const order = this.alertTemplateForm.field.alertGroups.groups[i].field.groupOrder.value

      this.alertTemplateForm.removeFromArray('alertGroups', i)

      let greaterThan = this.alertTemplateForm.field.alertGroups.groups.slice(i)

      greaterThan.forEach((el, index) => {
        el.field.groupOrder.value = order + index
      })
    },
    onRemoveSetting(i) {
      if (this.alertTemplateForm.field.alertConfig.groups.length - 1 <= 0) {
        return
      }
      this.alertTemplateForm.removeFromArray('alertConfig', i)
    },
    async onSearchFields(v) {
      this.fields.pagination = new Pagination()
      this.fields.filters = {
        ...this.fields.filters,
        search: v,
      }
      await this.fields.refresh()
    },
    async fieldNextPage() {
      await this.fields.addNextPage()
    },
    async onSearchUsers(v) {
      this.users.pagination = new Pagination()
      this.users.filters = {
        ...this.users.filters,
        search: v,
      }
      await this.users.refresh()
    },
    async onUsersNextPage() {
      await this.users.addNextPage()
    },
    showList() {
      this.listVisible = !this.listVisible
    },
    showDropDown() {
      this.dropdownVisible = !this.dropdownVisible
    },
    goToCloseDateApproaching() {
      this.$router.push({ name: 'CloseDateApproaching' })
    },
    goToCloseDatePassed() {
      this.$router.push({ name: 'CloseDatePassed' })
    },
    goToDealRotting() {
      this.$router.push({ name: 'DealRotting' })
    },
  },
  computed: {
    userTargetsOpts() {
      if (this.user.userLevel == 'MANAGER') {
        return [
          ...this.alertTargetOpts.map((opt) => {
            return {
              id: opt.value,
              fullName: opt.key,
            }
          }),
          ...this.users.list,
        ]
      } else {
        return [{ fullName: 'Myself', id: 'SELF' }]
      }
    },
    recipientOpts() {
      if (this.user.userLevel == 'MANAGER') {
        return [
          ...this.alertRecipientOpts.map((opt) => {
            return {
              id: opt.value,
              fullName: opt.key,
            }
          }),
          ...this.users.list,
        ]
      } else {
        return [{ fullName: 'Myself', id: 'SELF' }]
      }
    },
    formValue() {
      return this.alertTemplateForm.value
    },
    editor() {
      return this.$refs['message-body'].quill
    },
    selection() {
      return this.editor.selection.lastRange
    },
    alertObj() {
      return {
        title: this.formValue.title,
        message: this.formValue.alertMessages[0].body,
        resourceType: this.selectedResourceType,
      }
    },
    user() {
      return this.$store.state.user
    },
    selectedResourceType: {
      get() {
        return this.alertTemplateForm.field.resourceType.value
      },
      set(val) {
        this.alertTemplateForm.field.resourceType.value = val
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/buttons';
.quill-editor {
  width: 100%;
}

textarea {
  @extend .textarea;
}
.box__header {
  &__status {
    display: flex;
    &--error {
      color: $coral;
      fill: $coral;
    }
    &--success {
      color: $dark-green;
      fill: $dark-green;
    }
  }
}
.alerts-page {
  margin-left: 8vw;
  &__previous-step {
    @include muted-font(12);
  }
  &__groups {
    &__group {
      display: flex;
    }
  }
  &__message {
    display: flex;
    height: 20rem;
    &-template {
      margin: 0rem 1rem;
      &__notification {
        width: 30rem;
        margin: 1rem 0rem;
      }
      &__message {
        width: 40rem;
        margin: 1rem 0rem;
      }
    }
  }
}
.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
  margin-top: 2rem;
  flex-wrap: wrap;
}
.card__ {
  background-color: $panther;
  border: none;
  width: 10rem;
  height: 20vh;
  margin-right: 1rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 3px 4px 7px black;
  color: white;
  @media only screen and (min-width: 768px) {
    flex: 1 0 24%;
    min-width: 21rem;
    max-width: 30rem;
  }

  &header {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 5rem;
  }
}
.alerts-page__settings {
  display: flex;
  align-items: center;
  justify-content: space-evenly;

  &__frequency {
    display: flex;
    align-items: center;
    &-label {
      @include muted-font();
      margin: 0 0.5rem;
    }
  }
  &-remove {
    justify-self: end;
  }
}
.btn {
  &--danger {
    @include button-danger();
  }
  &--primary {
    @include primary-button();
  }
  &--secondary {
    @include secondary-button();
  }

  &--icon {
    @include --icon();
  }
}
.muted--link {
  @include muted-font();
  @include pointer-on-hover();
  &--important {
    color: red;
    font-weight: bold;
    font-size: 11px;
  }
}
.alerts-page__message-options-body__bindings__fields {
  // margin: 3rem 0rem;
  // width: 40rem;
}
.gray {
  color: $gray;
}
.slate {
  color: $slate-gray;
}
.pad {
  padding-bottom: 1rem;
  margin-top: -1rem;
}
.pink {
  color: $candy;
  font-weight: bold;
}
.purple {
  color: $grape;
  font-weight: bold;
}
.mar {
  margin-top: -2rem;
}
.center {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.sub {
  font-size: 12px;
  margin-left: 0.5rem;
}
.sub__ {
  font-size: 16px;
  margin-top: -0.5rem;
  color: $panther-silver;
}
.title {
}
.group {
  display: flex;
  flex-direction: row;
  height: auto;
  margin: 0.5rem;
  padding: 0.5rem;
}
.col {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-top: 1rem;
  border-bottom: 3px solid $silver;
}
.row_ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 2rem;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-top: 10rem;
}
.bottom {
  margin-bottom: 1.25rem;
  height: 170px;
}
.left {
  margin-bottom: 2rem;
}
.space {
  margin-bottom: 0.5rem;
}
.add__group {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-top: 3rem;
  padding-bottom: 1rem;
  border-bottom: 3px solid $mid-gray;
}
.bolder {
  font-size: 16px;
  margin-left: 1rem;
  cursor: pointer;
  color: $base-gray;
}
.bolder:hover {
  border-bottom: 2px solid $candy;
  color: $candy;
}
.alertsModal {
  color: $candy;
  text-decoration: underline;
  cursor: pointer;
}
.modal__container {
  overflow-y: scroll;
}
.blue {
  color: $slate-gray;
}
.top {
  border-top: 3px solid $grape;
}
.templates {
  border-bottom: 1px solid $gray;
}
input {
  width: 130px;
  text-align: center;
  height: 36px;
  border-radius: 0.25rem;
  margin-top: 0.75rem;
  border: none;
  border-bottom: 1px solid $slate-gray;
  font-weight: bold;
}
.orange_button {
  width: 7rem;
  background-color: white;
  color: $panther-orange;
  font-weight: bold;
  font-size: 16px;
  height: 2rem;
  border-radius: 0.5rem;
  border: 2px solid white;
  cursor: pointer;
}
.cs__button {
  width: 9rem;
  background-color: transparent;
  color: $panther-silver;
  font-weight: bold;
  font-size: 16px;
  height: 2rem;
  border-radius: 0.5rem;
  border: none;
  cursor: not-allowed;
}
</style>
