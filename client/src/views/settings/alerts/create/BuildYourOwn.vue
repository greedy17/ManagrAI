<template>
  <div class="alerts-page">
    <Modal style="margin-top: 8rem" ref="templateModal">
      <template v-slot:header>
        <h2 style="color: #4d4e4c">Popular Message Template</h2>
      </template>

      <template v-slot:body>
        <div>
          <div style="display: flex; flex-direction: row">
            <textarea
              style="
                height: 3rem;
                width: 90%;
                font-size: 0.75rem;
                margin-right: 0.25rem;
                border: none;
                box-shadow: 3px 4px 7px #c2c4ca;
              "
              name=""
              id=""
              cols="20"
              rows="10"
            >
          Hey { __Recipient.full_name }, your deal { Opportunity.Name } ...continue writing here
          </textarea
            >
            <button
              style="border: none; border: none; cursor: pointer; background: transparent"
              v-clipboard:copy="message"
              v-clipboard:success="onCopy"
              v-clipboard:error="onError"
            >
              <img src="@/assets/images/copy.png" style="height: 1.25rem" alt="" />
            </button>
          </div>
        </div>
      </template>
    </Modal>

    <div class="alert__row">
      <div v-show="pageNumber === 0" class="alert__column" style="margin-bottom: 1rem">
        <div class="workflow-header">
          <h3>Create a Custom Workflow</h3>
          <div class="button-space">
            <button class="plus_button" @click="onAddAlertGroup">
              <img src="@/assets/images/plusOne.svg" class="filtered" alt="" />
              Add Group
            </button>
          </div>
        </div>

        <div v-show="pageNumber === 0">
          <h5 style="text-align: center; margin-top: -0.75rem; color: #4d4e4c" class="title">
            {{ alertTemplateForm.field.resourceType.value }} Selected. Switch to
            <span
              v-if="selectedResourceType !== 'Account'"
              v-on:click="accountResource"
              style="border-bottom: 2px solid #41b883; cursor: pointer"
              >Account</span
            >
            <span v-if="selectedResourceType !== 'Account'">,</span>
            <span
              v-if="selectedResourceType !== 'Contact'"
              v-on:click="contactResource"
              style="border-bottom: 2px solid #41b883; cursor: pointer"
              >Contact</span
            >
            <span v-if="selectedResourceType !== 'Contact'">,</span>
            <span
              style="margin-left: 0.1rem; margin-right: 0.1rem"
              v-if="selectedResourceType == 'Lead'"
              >or</span
            >
            <span
              v-if="selectedResourceType !== 'Opportunity'"
              v-on:click="opportunityResource"
              style="border-bottom: 2px solid #41b883; cursor: pointer"
              >Opporunity</span
            >
            <span
              style="margin-left: 0.1rem; margin-right: 0.1rem"
              v-if="selectedResourceType !== 'Lead'"
              >or</span
            >
            <span
              v-if="selectedResourceType !== 'Lead'"
              v-on:click="leadResource"
              style="border-bottom: 2px solid #41b883; cursor: pointer"
              >Lead</span
            >
          </h5>
        </div>
        <div :key="index" v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups">
          <div class="sf__collection">
            <AlertGroup
              :form="alertGroup"
              :resourceType="alertTemplateForm.field.resourceType.value"
            />

            <p
              v-if="
                alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  .operandIdentifier.value &&
                (alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  ._operandIdentifier.value.dataType === 'Date' ||
                  alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                    ._operandIdentifier.value.dataType === 'DateTime') &&
                index == 0
              "
              class="fixed__center"
            >
              We'll alert you when the
              {{
                alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  .operandIdentifier.value
                  ? alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                      .field.operandIdentifier.value
                  : '___'
              }}
              is
              {{
                alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  .operandOperator.value
                  ? alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                      .field._operandOperator.value.label
                  : '___'
              }}
              <span style="color: #4d4e4c">{{
                alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                  .operandValue.value
                  ? positiveDay(
                      alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                        .field.operandValue.value,
                    )
                  : '___'
              }}</span>
            </p>

            <div class="fixed__right" v-if="alertTemplateForm.field.alertGroups.groups.length > 1">
              <button class="remove__group" @click="onRemoveAlertGroup(index)">
                <img src="@/assets/images/trash.png" style="height: 0.85rem" alt="" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-show="pageNumber === 2" class="alert__column">
        <h3>Construct your Message</h3>
        <div class="collection__fields">
          <div class="message_titles">
            <FormField
              id="message"
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
                      'Write your message from scratch, or build on top of the template...',
                    theme: 'snow',
                  }"
                  class="message__box"
                />
              </template>
            </FormField>

            <p
              @click="viewingTemplate = !viewingTemplate"
              style="cursor: pointer; border-bottom: 2px solid #41b883; font-size: 13px"
            >
              View Template
            </p>

            <div class="template-card" v-if="viewingTemplate">
              <div class="template-card__header">
                <h3>Popular Message Template</h3>
                <img
                  @click="viewingTemplate = !viewingTemplate"
                  style="height: 1rem"
                  src="@/assets/images/close.svg"
                  alt=""
                />
              </div>

              <div class="template-card__body">
                <textarea
                  style="
                    height: 3rem;
                    width: 90%;
                    font-size: 12px;
                    margin-right: 0.25rem;
                    border: 1px solid #e8e8e8;
                  "
                  cols="20"
                  rows="10"
                >
              Hey { __Recipient.full_name }, your deal { Opportunity.Name } ...continue writing here
              </textarea
                >
                <button
                  style="border: none; border: none; cursor: pointer; background: transparent"
                  v-clipboard:copy="message"
                  v-clipboard:success="onCopy"
                  v-clipboard:error="onError"
                >
                  <img src="@/assets/images/copy.png" style="height: 1.25rem" alt="" />
                </button>
              </div>
            </div>
          </div>

          <div class="crm">
            <h4 style="margin-top: 1rem">Add CRM Field Values:</h4>
            <div @click="addCount()">
              <Multiselect
                placeholder="Select field"
                v-model="crmValue"
                @input="bindText(`${selectedResourceType}.${$event.apiName}`)"
                :options="fields.list"
                openDirection="below"
                style="width: 14vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="fieldNextPage">Load More</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Field
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>
      </div>

      <div v-show="pageNumber === 1" class="alert__column">
        <h3>Select Delivery Options</h3>
        <div class="sf__collection">
          <template>
            <div
              class="delivery__row"
              :key="i"
              v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
            >
              <div>
                <div class="row__">
                  <label :class="form.field.recurrenceFrequency.value == 'WEEKLY' ? 'green' : ''"
                    >Weekly</label
                  >
                  <ToggleCheckBox
                    style="margin: 0.25rem"
                    @input="
                      form.field.recurrenceFrequency.value == 'WEEKLY'
                        ? (form.field.recurrenceFrequency.value = 'MONTHLY')
                        : (form.field.recurrenceFrequency.value = 'WEEKLY')
                    "
                    :value="form.field.recurrenceFrequency.value !== 'WEEKLY'"
                    offColor="#41b883"
                    onColor="#41b883"
                  />
                  <label :class="form.field.recurrenceFrequency.value == 'MONTHLY' ? 'green' : ''"
                    >Monthly</label
                  >
                </div>

                <div>
                  <div v-if="form.field.recurrenceFrequency.value == 'WEEKLY'">
                    <FormField>
                      <template v-slot:input>
                        <Multiselect
                          placeholder="Select a Day"
                          v-model="selectedDay"
                          @input="setDay($event)"
                          :options="weeklyOpts"
                          openDirection="below"
                          style="width: 14vw"
                          selectLabel="Enter"
                          track-by="value"
                          label="key"
                          :multiple="true"
                          :closeOnSelect="false"
                        >
                          <template slot="noResult">
                            <p class="multi-slot">No results.</p>
                          </template>
                          <template slot="placeholder">
                            <p class="slot-icon">
                              <img src="@/assets/images/search.svg" alt="" />
                              Select a Day
                            </p>
                          </template>
                        </Multiselect>
                      </template>
                    </FormField>
                  </div>

                  <FormField
                    v-if="form.field.recurrenceFrequency.value == 'MONTHLY'"
                    placeholder="Day of month"
                    :errors="form.field.recurrenceDay.errors"
                    @blur="form.field.recurrenceDay.validate()"
                    v-model="form.field.recurrenceDay.value"
                    small
                  />
                </div>
              </div>

              <div
                v-if="user.userLevel == 'MANAGER'"
                style="
                  display: flex;
                  flex-direction: column;
                  align-items: flex-start;
                  justify-content: space-evenly;
                  padding: 0.5rem;
                "
              >
                <span style="font-size: 13px; margin-bottom: 0.3rem">Select pipelines</span>
                <FormField :errors="form.field.alertTargets.errors">
                  <template v-slot:input>
                    <Multiselect
                      placeholder="Select Users"
                      @input="mapIds"
                      v-model="selectedUsers"
                      :options="userTargetsOpts"
                      openDirection="below"
                      style="width: 14vw"
                      selectLabel="Enter"
                      track-by="id"
                      label="fullName"
                      :multiple="true"
                      :closeOnSelect="false"
                      :loading="dropdownLoading"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results. Try loading more</p>
                      </template>
                      <template slot="afterList">
                        <p class="multi-slot__more" @click="onUsersNextPage">
                          Load More
                          <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                        </p>
                      </template>
                      <template slot="placeholder">
                        <p class="slot-icon">
                          <img src="@/assets/images/search.svg" alt="" />
                          Select Users
                        </p>
                      </template>
                    </Multiselect>
                  </template>
                </FormField>
              </div>

              <div>
                <div v-if="!channelName" class="row__">
                  <label :class="!create ? 'green' : ''">Select #channel</label>
                  <ToggleCheckBox
                    style="margin: 0.25rem"
                    @input="changeCreate"
                    :value="create"
                    offColor="#41b883"
                    onColor="#41b883"
                  />
                  <label :class="create ? 'green' : ''">Create #channel</label>
                </div>

                <label v-else for="channel" style="font-weight: bold"
                  >Alert will send to
                  <span style="color: #41b883; font-size: 1.2rem">{{ channelName }}</span>
                  channel</label
                >
                <div
                  style="
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                  "
                  v-if="create"
                >
                  <input
                    v-model="channelName"
                    class="search__input"
                    type="text"
                    name="channel"
                    id="channel"
                    placeholder="Name your channel"
                    @input="logNewName(channelName)"
                  />

                  <div v-if="!channelCreated" v style="margin-top: 1.25rem">
                    <button
                      v-if="channelName"
                      @click="createChannel(channelName)"
                      class="gold__button bouncy"
                    >
                      Create Channel
                    </button>
                    <button v-else class="disabled__button">Create Channel</button>
                  </div>
                </div>

                <div v-else>
                  <template>
                    <Multiselect
                      v-if="!directToUsers"
                      placeholder="Select Channel"
                      v-model="selectedChannel"
                      @input="setRecipient"
                      :options="userChannelOpts.channels"
                      openDirection="below"
                      style="width: 14vw"
                      selectLabel="Enter"
                      track-by="id"
                      label="name"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results. Try loading more</p>
                      </template>
                      <template slot="afterList">
                        <p
                          class="multi-slot__more"
                          @click="listUserChannels(userChannelOpts.nextCursor)"
                        >
                          Load More
                          <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                        </p>
                      </template>
                      <template slot="placeholder">
                        <p class="slot-icon">
                          <img src="@/assets/images/search.svg" alt="" />
                          Select Channel
                        </p>
                      </template>
                    </Multiselect>
                  </template>
                  <div v-if="user.userLevel !== 'REP'" class="sendAll">
                    <input type="checkbox" id="allUsers" v-model="directToUsers" />
                    <label for="allUsers">Send directly to users</label>
                  </div>

                  <div v-else class="sendAll">
                    <input type="checkbox" id="allUsers" v-model="directToUsers" />
                    <label for="allUsers">Send to primary channel</label>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <div class="alert__column" v-show="pageNumber === 3">
        <h3>Name and save your workflow</h3>
        <template>
          <div
            style="display: flex; justify-content: center; align-items: center"
            class="sf__collection"
          >
            <h2>
              {{ alertTemplateForm.field.title.value ? alertTemplateForm.field.title.value : '' }}
            </h2>
            <FormField
              id="alert-title"
              v-model="alertTemplateForm.field.title.value"
              placeholder="Name your workflow"
              :errors="alertTemplateForm.field.title.errors"
              @blur="alertTemplateForm.field.title.validate()"
            />
          </div>
        </template>
      </div>
    </div>
    <div class="bottom_locked">
      <button
        @click="onPreviousPage"
        :class="pageNumber === 0 ? 'disabled__button' : 'prev-button'"
        style="margin-right: 0.5rem"
      >
        Prev
      </button>
      <div v-if="pageNumber < 3">
        <div v-if="pageNumber === 0">
          <button
            v-if="
              !alertTemplateForm.field.alertGroups.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
            @click="onNextPage"
            class="gold__button"
          >
            Next
          </button>
          <div class="tooltip" v-else>
            <button class="disabled__button tooltip__icon">Next</button>
            <div class="tooltip__popup">
              <div class="tip">Complete this section to continue.</div>
            </div>
          </div>
        </div>

        <div v-if="pageNumber === 1">
          <button
            v-if="
              !alertTemplateForm.field.alertConfig.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
            @click="onNextPage"
            class="gold__button"
          >
            Next
          </button>
          <div class="tooltip" v-else>
            <button class="disabled__button tooltip__icon">Next</button>
            <div class="tooltip__popup">
              <div class="tip">Complete this section to continue.</div>
            </div>
          </div>
        </div>
        <div v-if="pageNumber === 2">
          <button
            v-if="
              !alertTemplateForm.field.alertMessages.groups
                .map((fields) => fields.isValid)
                .includes(false)
            "
            @click="onNextPage"
            class="gold__button"
          >
            Next
          </button>
          <div class="tooltip" v-else>
            <button class="disabled__button tooltip__icon">Next</button>
            <div class="tooltip__popup">
              <div class="tip">Complete this section to continue.</div>
            </div>
          </div>
        </div>
      </div>

      <div v-else>
        <PulseLoadingSpinnerButton
          v-if="alertTemplateForm.isValid || savingTemplate"
          :loading="savingTemplate"
          class="gold__button"
          text="Save Alert"
          @click.stop="onSave"
        />

        <div class="tooltip" v-else>
          <button class="disabled__button tooltip__icon">Save Alert</button>
          <div class="tooltip__popup">
            <div class="tip">Alert title required.</div>
          </div>
        </div>
      </div>
    </div>
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
import Modal from '@/components/Modal'

/**
 * Services
 */

import AlertTemplate, { AlertGroupForm, AlertTemplateForm } from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjectField, NON_FIELD_ALERT_OPTS, SOBJECTS_LIST } from '@/services/salesforce'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'AlertsPage',
  components: {
    AlertGroup,
    ToggleCheckBox,
    FormField,
    PulseLoadingSpinnerButton,
    Modal,
    quillEditor,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      dropdownLoading: false,
      selectedDay: null,
      selectedChannel: null,
      crmValue: null,
      viewingTemplate: false,
      channelOpts: new SlackListResponse(),
      userChannelOpts: new SlackListResponse(),
      channelName: '',
      message: 'Hey { __Recipient.full_name }, your deal { Opportunity.Name }',
      templateBounce: true,
      selectedUsers: null,
      fieldBounce: true,
      clickCount: 0,
      newChannel: {},
      showMenu: true,
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: [],
      pageNumber: 0,
      searchQuery: '',
      searchText: '',
      searchChannels: '',
      create: false,
      directToUsers: true,
      channelCreated: false,
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
      await this.listUserChannels()
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
      directToUsers: 'setDefaultChannel',
    },
  },
  methods: {
    mapIds() {
      let mappedIds = this.selectedUsers.map((user) => user.id)
      this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value = mappedIds
    },
    setDefaultChannel() {
      this.directToUsers
        ? (this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = 'default')
        : (this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = null)
    },
    positiveDay(num) {
      if (num < 0) {
        return (num *= -1) + ' days in the past.'
      } else if (num == 0) {
        return ' the day of your selected delivery day.'
      } else {
        return num + ' days in the future.'
      }
    },
    repsPipeline() {
      if (
        this.user.userLevel !== 'MANAGER' &&
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value.length < 1
      ) {
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value.push('SELF')
        console.log('test')
        this.setPipelines({
          fullName: 'MYSELF',
          id: 'SELF',
        })
      }
    },
    addCount() {
      this.clickCount += 1
    },
    onCopy: function () {
      this.$Alert.alert({
        message: 'Message Copied to clipboard successfully',
        type: 'success',
        timeout: 2000,
      })
    },
    onError: function () {
      this.$Alert.alert({
        message: 'error copying template',
        type: 'error',
        timeout: 2000,
      })
    },
    changeCreate() {
      this.create = !this.create
      if (
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value !==
        'SLACK_CHANNEL'
      ) {
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value =
          'SLACK_CHANNEL'
      }
    },
    async listChannels(cursor = null) {
      const res = await SlackOAuth.api.listChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.channelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.channelOpts = results
    },
    async listUserChannels(cursor = null) {
      this.dropdownLoading = true
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
      setTimeout(() => {
        this.dropdownLoading = false
      }, 500)
    },
    async createChannel(name) {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value = 'SLACK_CHANNEL'
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = res.channel
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = res.channel.id
        this.channelCreated = !this.channelCreated
      } else {
        console.log(res.error)
        this.channelName = ''
        if (res.error == 'name_taken') {
          this.$Alert.alert({
            message: 'Channel name already taken',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name_maxlength') {
          this.$Alert.alert({
            message: 'Channel name exceeds maximum length',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'restricted_action') {
          this.$Alert.alert({
            message: 'A team preference is preventing you from creating channels',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name_specials') {
          this.$Alert.alert({
            message:
              'The only special characters allowed are hyphens and underscores. Channel names must also begin with a letter ',
            type: 'error',
            timeout: 3000,
          })
        } else if (res.error == 'org_login_required') {
          this.$Alert.alert({
            message:
              'The workspace is undergoing an enterprise migration and will not be available until migration is complete.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'ekm_access_denied') {
          this.$Alert.alert({
            message: 'Administrators have suspended the ability to post a message.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'too_many_convos_for_team') {
          this.$Alert.alert({
            message: 'The workspace has exceeded its limit of public and private channels.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'no_permission') {
          this.$Alert.alert({
            message:
              'The workspace token used in this request does not have the permissions necessary to complete the request. Make sure your app is a member of the conversation its attempting to post a message to.',
            type: 'error',
            timeout: 4000,
          })
        } else if (res.error == 'team_access_not_granted') {
          this.$Alert.alert({
            message:
              'You are not granted the specific workspace access required to complete this request.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name') {
          this.$Alert.alert({
            message: 'Channel name invalid. Please try again',
            type: 'error',
            timeout: 2000,
          })
        } else {
          this.$Alert.alert({
            message: 'Something went wrong..Please try again',
            type: 'error',
            timeout: 2000,
          })
          console.log(res.error)
        }
      }
    },
    logNewName(str) {
      let new_str = ''
      new_str = str.replace(/\s+/g, '-').toLowerCase()
      this.channelName = new_str
    },
    accountResource() {
      this.alertTemplateForm.field.resourceType.value = 'Account'
    },
    leadResource() {
      this.alertTemplateForm.field.resourceType.value = 'Lead'
    },
    opportunityResource() {
      this.alertTemplateForm.field.resourceType.value = 'Opportunity'
    },
    contactResource() {
      this.alertTemplateForm.field.resourceType.value = 'Contact'
    },

    async onSave() {
      this.savingTemplate = true
      this.alertTemplateForm.validate()
      if (this.alertTemplateForm.isValid) {
        try {
          const res = await AlertTemplate.api.createAlertTemplate({
            ...this.alertTemplateForm.toAPI,
            user: this.$store.state.user.id,
            directToUsers: this.directToUsers,
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
    onNextPage() {
      this.pageNumber <= 2 ? (this.pageNumber += 1) : (this.pageNumber = this.pageNumber)
    },
    onPreviousPage() {
      this.pageNumber >= 1 ? (this.pageNumber -= 1) : (this.pageNumber = this.pageNumber)
    },
    setDay(n) {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDay.value = 0
      let days = []
      n.forEach((day) => days.push(day.value))
      let newDays = [...new Set(days)]
      this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value = newDays
      console.log(this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value)
    },
    setPipelines(obj) {
      if (this.alertTemplateForm.field.alertConfig.groups[0].field._alertTargets.value.lenght < 1) {
        this.alertTemplateForm.field.alertConfig.groups[0].field._alertTargets.value.push(obj)
        console.log(
          this.alertTemplateForm.field.alertConfig.groups[0].field._alertTargets.value.push(obj),
        )
      }
    },
    setRecipient() {
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value =
        this.selectedChannel
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value =
        this.selectedChannel.id
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
    async fieldNextPage() {
      await this.fields.addNextPage()
    },
    async onUsersNextPage() {
      this.dropdownLoading = true
      await this.users.addNextPage()
      setTimeout(() => {
        this.dropdownLoading = false
      }, 1000)
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
    editor() {
      return this.$refs['message-body'].quill
    },
    selection() {
      return this.editor.selection.lastRange
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
  mounted() {
    this.setDefaultChannel()
  },
  beforeMount() {
    this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value = 'SLACK_CHANNEL'
    this.alertTemplateForm.field.resourceType.value = 'Opportunity'
    this.repsPipeline()
    this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value = [0]
    this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDay.value = 0
  },
  updated() {
    this.alertTemplateForm.field.isActive.value = true
    this.repsPipeline()
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

input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 0.9ex;
  left: 0.4ex;
  border: 2px solid $dark-green;
  border-top: none;
  border-right: none;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}
input[type='checkbox'] {
  line-height: 2.1ex;
}
input[type='checkbox'] {
  position: absolute;
  left: -999em;
}
input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}
input[type='checkbox'] + label::before {
  content: '';
  display: inline-block;
  vertical-align: -22%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}
.sendAll {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: $base-gray;
  margin-top: 1rem;
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
input:focus {
  outline: none !important;
}
.template-card {
  position: absolute;
  height: 20vh;
  top: 40vh;
  width: 100%;
  background: white;
  border-radius: 0.25rem;
  box-shadow: 2px 2px 3px 2px $very-light-gray;
  &__header {
    padding-left: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    img {
      padding-right: 0.5rem;
      padding-top: -0.2rem;
    }
  }
  &__body {
    height: 3rem;
    padding: 1.25rem;
    display: flex;
    align-items: center;
  }
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.workflow-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
::placeholder {
  color: $very-light-gray;
  font-size: 0.75rem;
}
.prev-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $base-gray;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-size: 12px;
}
.search__input {
  font-family: Lato-Regular, sans-serif;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  font-size: 16px;
  border-radius: 4px;
  line-height: 1.29;
  letter-spacing: 0.5px;
  height: 2.5rem;
  background-color: white;
  border: none;
  width: 14vw;
  border: 1px solid #e8e8e8;
}
.bottom_locked {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: auto;
  margin-bottom: 0.5rem;
}
.remove__group {
  padding: 0.25rem;
  border: 1px solid #e8e8e8;
  background-color: transparent;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  cursor: pointer;
}
button img {
  filter: invert(90%);
}
.fixed__right {
  align-self: flex-end;
  margin-top: -2rem;
}
.fixed__center {
  align-self: center;
  color: $very-light-gray;
}
.message_titles {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  flex-direction: column;
  position: relative;
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.crm {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
}
.filtered {
  filter: invert(99%);
  height: 1rem;
}
.invert {
  filter: invert(99%);
}
.alert__column {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  border-radius: 0.5rem;
}
.alert__row {
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.delivery__row {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: flex-start;
}
.sf__collection {
  display: flex;
  align-items: space-evenly;
  justify-content: center;
  flex-direction: column;
  background-color: $white;
  border-radius: 0.2rem;
  border: 1px solid #e8e8e8;
  width: 75vw;
  padding: 2rem;
  margin-bottom: 1rem;
}
.collection__fields {
  background-color: $white;
  display: flex;
  justify-content: space-evenly;
  flex-direction: row;
  padding: 1rem;
  border-radius: 0.5rem;
  height: 46vh;
  width: 70vw;
  border: 1px solid #e8e8e8;
}
.button-space {
  padding: 2.5rem 1rem 0rem 0rem;
}
.plus_button {
  border: none;
  background-color: $dark-green;
  border-radius: 0.3rem;
  padding: 0.4rem 1rem;
  display: flex;
  align-items: center;
  font-size: 12px;
  cursor: pointer;
  color: white;
}

textarea {
  @extend .textarea;
}
.alerts-page {
  height: 88vh;
  color: $base-gray;
  margin-left: 18vw;
  margin-top: 3.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.green {
  color: $dark-green;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 13px;
}
.message__box {
  margin-bottom: 2rem;
  height: 24vh;
  width: 32vw;
  border-radius: 0.25rem;
  background-color: transparent;
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
.gold__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-size: 12px;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  color: $base-gray;
  cursor: not-allowed;
  height: 2rem;
  width: 10rem;
  font-size: 12px;
}
.tooltip {
  position: relative;
  &__icon {
    height: 2rem;
  }

  &__popup {
    width: 18rem;
    visibility: hidden;

    padding: 13px 21px;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    border: solid 2px $very-light-gray;
    background-color: $base-gray;
    color: white;
    position: absolute;
    bottom: -5px;
    left: 105%;
  }
}
.tooltip:hover .tooltip__popup {
  visibility: visible;
}
</style>