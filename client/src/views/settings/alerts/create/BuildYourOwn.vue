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
              <img src="@/assets/images/copy.svg" class="invert" style="height: 1.25rem" alt="" />
            </button>
          </div>
        </div>
      </template>
    </Modal>

    <section class="row">
      <div class="workflow-content">
        <div :key="i" v-for="(form, i) in alertTemplateForm.field.alertConfig.groups">
          <div style="padding-bottom: 16px" class="title">
            <h4 class="title__head">Workflow Conditions</h4>

            <section class="title__body">
              <p>We'll alert you when these conditions are met.</p>
              <!-- Send this workflow to {{ selectedUsers ? getUsers(selectedUsers) : '' }}
              {{ getFrequency(form.field.recurrenceFrequency.value) }}
              {{ selectedDay ? getDays(selectedDay) : '' }} -->
              <!-- SEPERATORRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR-->
              <!-- <p>
                For all Opportunities with a
                <span>
                  {{
                    alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                      .field.operandIdentifier.value
                      ? alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                          .field.operandIdentifier.value
                      : ''
                  }}
                </span>

                {{
                  alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                    .operandOperator.value
                    ? alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                        .field._operandOperator.value.label
                    : ''
                }}
                {{
                  alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
                    .operandValue.value
                    ? alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0]
                        .field.operandValue.value
                    : ''
                }}
              </p> -->
            </section>
            <div
              :key="index"
              v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups"
            >
              <AlertGroup
                :form="alertGroup"
                :resourceType="alertTemplateForm.field.resourceType.value"
              />
              <div
                class="fixed__right"
                v-if="alertTemplateForm.field.alertGroups.groups.length > 1"
              >
                <button class="remove__group" @click="onRemoveAlertGroup(index)">
                  <img
                    src="@/assets/images/trash.svg"
                    style="height: 0.85rem; filter: invert(50%)"
                    alt=""
                  />
                </button>
              </div>
            </div>
          </div>

          <div class="column">
            <small>|</small>
          </div>

          <div class="center">
            <button class="plus_button" @click="onAddAlertGroup">+</button>
          </div>
        </div>
      </div>

      <div class="dash-row">
        <small class="rotated">|</small>
        <small class="rotated">|</small>
        <small class="rotated">|</small>
      </div>

      <div
        style="margin-left: -8px"
        class="workflow-content"
        :key="i"
        v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
      >
        <section>
          <div>
            <div class="title">
              <h4 class="title__head">User Pipelines</h4>
              <section class="title__body">
                <p>Who's Opps are we checking ?</p>
              </section>
              <section class="title__body">
                <div v-if="user.userLevel == 'MANAGER'">
                  <div class="selector-row">
                    <p v-for="(user, i) in userTargetsOpts" :key="i">{{ user.fullName }}</p>
                  </div>
                  <!-- <FormField :errors="form.field.alertTargets.errors">
                    
                    <template v-slot:input>
                      <Multiselect
                        placeholder="Users"
                        @input="mapIds"
                        v-model="selectedUsers"
                        :options="userTargetsOpts"
                        openDirection="below"
                        style="width: 20vw"
                        selectLabel="Enter"
                        track-by="id"
                        label="fullName"
                        :multiple="true"
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
                            Users
                          </p>
                        </template>
                      </Multiselect>
                    </template>
                  </FormField> -->
                </div>
              </section>
            </div>
          </div>

          <div class="column">
            <small>|</small>
          </div>

          <div style="margin-top: -18px; padding-bottom: 16px" class="title">
            <h4 class="title__head">Delivery Days</h4>
            <section class="title__body">
              <p>When would you like to be notified ?</p>
            </section>
            <div class="title__body">
              <div>
                <p class="andOr">Weekly <span class="l-gray">|</span> Monthly</p>
                <!-- <FormField>
                  <template v-slot:input>
                    <Multiselect
                      placeholder="Weekly or monthly"
                      @input="setFrequency($event)"
                      v-model="form.field.recurrenceFrequency.value"
                      :options="frequencies"
                      openDirection="below"
                      style="width: 20vw"
                      selectLabel="Enter"
                    >
                    </Multiselect>
                  </template>
                </FormField> -->
              </div>

              <div>
                <div>
                  <div v-if="form.field.recurrenceFrequency.value !== 'MONTHLY'">
                    <div class="selector-row">
                      <p v-for="(day, i) in weeklyOpts" :key="i">{{ day.key }}</p>
                    </div>
                    <!-- <FormField>
                      <template v-slot:input>
                        <Multiselect
                          placeholder="Select a Day"
                          v-model="selectedDay"
                          @input="setDay($event)"
                          :options="weeklyOpts"
                          openDirection="below"
                          style="width: 20vw"
                          selectLabel="Enter"
                          track-by="value"
                          label="key"
                          :multiple="true"
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
                    </FormField> -->
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

              <!-- <div>
                <div v-if="!channelName && !directToUsers" class="row__">
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
                      style="width: 20vw"
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
                  <div v-if="user.userLevel !== 'REP'">
                    <input type="checkbox" id="allUsers" v-model="directToUsers" />
                    <label for="allUsers">Send directly to users</label>
                  </div>

                  <div v-else>
                    <input type="checkbox" id="allUsers" v-model="directToUsers" />
                    <label for="allUsers">Send to primary channel</label>
                  </div>
                </div>
              </div> -->
            </div>
          </div>

          <div class="column">
            <small>|</small>
          </div>

          <div class="title" style="margin-top: -18px; padding-bottom: 16px">
            <h4 class="title__head">Delivery Options</h4>
            <section class="title__body">
              <p>Where would you like to be notified ?</p>
            </section>

            <div style="margin-top: -8px" class="title__body">
              <div v-if="user.userLevel !== 'REP'">
                <input type="checkbox" id="allUsers" v-model="directToUsers" />
                <label for="allUsers">Send directly to users</label>
              </div>

              <div v-else>
                <input type="checkbox" id="allUsers" v-model="directToUsers" />
                <label for="allUsers">Send to primary channel</label>
              </div>
              <div v-if="!channelName && !directToUsers" class="row__">
                <!-- <label :class="!create ? 'green' : ''">Select #channel</label>
                <ToggleCheckBox
                  style="margin: 0.25rem"
                  @input="changeCreate"
                  :value="create"
                  offColor="#41b883"
                  onColor="#41b883"
                />
                <label :class="create ? 'green' : ''">Create #channel</label> -->

                <!-- <small class="andOr"
                  >Select Channel <span class="l-gray">|</span> Create Channel</small
                > -->
              </div>

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
                    placeholder="Search Channels"
                    v-model="selectedChannel"
                    @input="setRecipient"
                    :options="userChannelOpts.channels"
                    openDirection="below"
                    style="width: 25vw; margin-top: 12px"
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
                        Search Channels
                      </p>
                    </template>
                  </Multiselect>
                </template>
              </div>
            </div>
          </div>
        </section>
      </div>
      <div class="dash-row">
        <small class="rotated">|</small>
        <small class="rotated">|</small>
        <small class="rotated">|</small>
      </div>

      <section style="margin-top: 26px; margin-left: 4px" class="container-large">
        <div class="workflow-content__header">
          <input
            type="text"
            class="input-field"
            placeholder="Name your workflow"
            :errors="alertTemplateForm.field.title.errors"
            autofocus
          />
        </div>

        <div>
          <FormField id="message">
            <template v-slot:input>
              <quill-editor
                @blur="alertTemplateForm.field.alertMessages.groups[0].field.body.validate()"
                ref="message-body"
                v-model="alertTemplateForm.field.alertMessages.groups[0].field.body.value"
                :options="{
                  modules: { toolbar: { container: ['bold', 'italic', 'strike'] } },
                  placeholder: 'Create a custom Slack message.',
                  theme: 'snow',
                }"
                class="message__box"
              />
            </template>
          </FormField>
          <div class="end">
            <p class="gray neg-mar">+</p>

            <!-- <Multiselect
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
            </Multiselect> -->
          </div>
        </div>
      </section>
    </section>
    <!-- <h3 class="summary-pill">Summary</h3>
    <div class="bottom_locked">
      <p
        v-show="
          alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field
            .operandValue.value
        "
        class="large-font auto-left"
      >
        Send <span class="green">Edward Roberson</span> an alert every
        <span class="green">Monday</span> for all Opportunities with an
        <span class="green">amount </span>
        <span class="green">greater than </span>
        <span class="green"> $475,000</span>
      </p>
      <div class="auto-left">
       
        <PulseLoadingSpinnerButton
           v-if="alertTemplateForm.isValid || savingTemplate"
          :loading="savingTemplate"
          class="gold__button"
          text="Create"
          @click.stop="onSave"
        />

        <button v-else class="disabled__button">Create</button>
      </div>
    </div> -->
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
import SlackNotificationTemplate from '@/views/settings/alerts/create/SlackNotificationTemplate'
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
    SlackNotificationTemplate,
    Modal,
    quillEditor,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      frequencies: ['WEEKLY', 'MONTHLY'],
      resources: ['Opportunity', 'Account', 'Contact', 'Lead'],
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
          // this.alertTemplateForm = this.alertTemplateForm.reset()
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
    setFrequency(val) {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceFrequency.value = val
    },
    getFrequency(val) {
      let newVal = ''
      val === 'WEEKLY'
        ? (newVal = 'every week on')
        : val === 'Monthly'
        ? (newVal = 'every month on')
        : (newVal = '')
      return newVal
    },
    getDays(arr) {
      let days = []
      for (let i = 0; i < arr.length; i++) {
        days.push(Object.values(arr[i]))
      }
      return days.map((day) => day[0]).toString()
    },
    getUsers(arr) {
      return arr.map((user) => user.fullName).toString()
    },
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
      this.$toast('Copied', {
        timeout: 2000,
        position: 'top-left',
        type: 'success',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
    },
    onError: function () {
      this.$toast('Error copying template', {
        timeout: 2000,
        position: 'top-left',
        type: 'error',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
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
          this.$toast('Channel name already taken', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'invalid_name_maxlength') {
          this.$toast('Channel name exceeds max-length', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'restricted_action') {
          this.$toast('A team preference is preventing you from creating channels', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'invalid_name_specials') {
          this.$toast(
            'The only special characters allowed are hyphens and underscores. Channel names must also begin with a letter ',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'org_login_required') {
          this.$toast(
            'The workspace is undergoing an enterprise migration and will not be available until migration is complete.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'too_many_convos_for_team') {
          this.$toast('The workspace has exceeded its limit of public and private channels.', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'no_permission') {
          this.$toast(
            'The workspace token used in this request does not have the permissions necessary to complete the request. Make sure your app is a member of the conversation its attempting to post a message to.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'team_access_not_granted') {
          this.$toast(
            'You are not granted the specific workspace access required to complete this request.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'invalid_name') {
          this.$toast('Channel name invalid. Please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Something went wrong, please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
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
          this.$toast('An error occured saving template', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
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
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = [
        this.selectedChannel.id,
      ]
    },
    onAddAlertGroup() {
      // length determines order
      const order = this.alertTemplateForm.field.alertGroups.groups.length
      if (order >= 3) {
        this.$toast('You can only add 3 groups', {
          timeout: 2000,
          position: 'top-left',
          type: 'default',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
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
    this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceFrequency.value = ''
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

.selector-row {
  display: flex;
  flex-direction: row;
  align-items: center !important;
  width: 25vw;
  overflow-x: scroll;
  outline: 1px solid $soft-gray;
  padding: 20px 4px 0px 4px;
  border-radius: 6px;
  margin-bottom: 8px;
  background-color: $off-white;

  p {
    background-color: $white;
    color: $base-gray;
    margin-right: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    white-space: nowrap;
    transition: all 0.2s;
  }
  p:hover {
    transform: scale(1.15);
    color: $dark-green;
    cursor: pointer;
  }
}
.negative-left {
  margin-left: -68px !important;
}
.andOr {
  border: 1px solid $soft-gray;
  padding: 6px 8px;
  border-radius: 6px;
  width: fit-content;
}
.arrow-div {
  border-radius: 100%;
  border: 1px solid $soft-gray;
  box-shadow: 0 1px 6px rgba($soft-gray, 50%);
  padding: 11px;
  margin-top: 20vh;
  // margin-bottom: auto;
  margin-right: 24px;
  img {
    filter: invert(50%);
  }
}
.auto-left {
  margin-left: auto;
}
.margin-left {
  margin-left: 16px;
}
.margin-left-large {
  margin-left: 32px;
}
.light-gray {
  color: $very-light-gray;
  opacity: 0.5;
}
.container {
  background-color: white;
  outline: 1px solid $soft-gray;
  padding: 8px 12px;
  color: $base-gray;
  border-radius: 6px;
  margin-top: 0;
  width: 28vw;
  height: 34vh;
  overflow: scroll;
  letter-spacing: 0.75px;
}
.container-large {
  background-color: white;
  outline: 1px solid $soft-gray;
  padding: 8px 12px;
  color: $base-gray;
  border-radius: 6px;
  margin-top: 0;
  width: 28vw;
  height: 44vh;
  overflow: scroll;
  letter-spacing: 0.75px;
}
.title {
  background-color: white;
  // box-shadow: 0 6px 20px rgba($soft-gray, 50%);
  outline: 1px solid $soft-gray;
  color: $base-gray;
  border-radius: 6px;
  width: 28vw;
  letter-spacing: 0.75px;
  &__head {
    padding: 8px 12px;
    background-color: white;
    margin-bottom: 0;
    color: $very-light-gray;
  }
  &__body {
    padding: 6px 12px;
    background-color: white;
    font-size: 11px;
    p {
      margin-top: 0;
    }
  }
}
.title-small {
  background-color: white;
  // box-shadow: 0 6px 20px rgba($soft-gray, 50%);
  outline: 1px solid $soft-gray;
  color: $base-gray;
  border-radius: 6px;
  width: 22vw;
  letter-spacing: 0.75px;
  &__head {
    padding: 8px 12px;
    background-color: white;
    margin-bottom: 0;
    color: $very-light-gray;
  }
  &__body {
    padding: 6px 12px;
    background-color: white;
    font-size: 11px;
    p {
      margin-top: 0;
    }
  }
}
.input-field {
  border: none;
  letter-spacing: 0.8px;
  padding: 8px;
  color: $base-gray;
  margin-left: 6px;
}
input,
input::placeholder {
  font: 14px $base-font-family;
}
.workflow-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  margin: 0px 16px 16px 0px;
  padding: 8px 12px;
  width: 32%;
  height: 88vh;
  overflow: scroll;
  // border-right: 1px solid $soft-gray;
}
.workflow-content::-webkit-scrollbar {
  width: 0px; /* Mostly for vertical scrollbars */
  height: 2px; /* Mostly for horizontal scrollbars */
}
.workflow-content::-webkit-scrollbar-thumb {
  background-color: $coral;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 0.3rem;
}
.workflow-content::-webkit-scrollbar-track-piece {
  margin-top: 0.25rem;
}

::v-deep .ql-toolbar.ql-snow {
  display: none;
}
::v-deep .ql-container.ql-snow {
  // outline: 1px solid $soft-gray;
  border: none;
  border-radius: 4px;
}
::v-deep .ql-editor p {
  color: $base-gray;
}
::v-deep .ql-editor.ql-blank::before {
  color: $very-light-gray;
}
// ::v-deep .ql-container.ql-snow:hover {
//   outline: 1px solid $soft-gray;
//   border-radius: 4px;
// }
.end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  margin-top: -16px;
}
.gray {
  color: $very-light-gray;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
}
.gray:hover {
  background-color: $off-white;
  color: $very-light-gray;
  border-radius: 4px;
}
.neg-mar {
  margin-top: -6px;
}
.neg-mar-large {
  margin-top: -20px;
}

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
  padding: 8px 20px 16px 24px;
  width: 100%;
}
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
::placeholder {
  color: $very-light-gray;
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
  padding: 8px 16px;
  width: 100%;
  height: 100px;
  position: sticky;
  border-top: 2px solid $soft-gray;
  bottom: 0;
  background-color: white;
}
.summary-pill {
  position: absolute;
  left: 0;
  right: 0;
  margin-left: auto;
  margin-right: auto;
  bottom: 84px;
  background-color: white;
  outline: 1px solid $soft-gray;
  color: $base-gray;
  padding: 8px;
  border-radius: 16px;
  width: 200px;
  z-index: 1;
  text-align: center;
  letter-spacing: 0.75px;
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
.center {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: center;
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
  width: 100vw;
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
.column {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: -2px;
  color: $very-light-gray;
}
.rotated {
  transform: rotate(-90deg);
  color: $very-light-gray;
  margin-right: 8px;
}

.button-space {
  padding: 2.5rem 1rem 0rem 0rem;
}
.plus_button {
  background-color: $dark-green;
  border: none;
  border-radius: 100%;
  color: white;
  font-size: 18px;
}

textarea {
  @extend .textarea;
}
.alerts-page {
  height: 90vh;
  overflow: scroll;
  color: $base-gray;
  padding: 0 12px;
}
.green {
  // color: $dark-green;
  font-weight: bold;
}
.green-bg {
  color: $dark-green;
  background-color: $white-green;
  padding: 6px 8px;
  font-weight: bold;
  border-radius: 4px;
}
.large-font {
  font-size: 18px;
  font-weight: 400;
  letter-spacing: 0.75px !important;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 13px;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
}
.dash-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin: 16px -8px 0px -16px;
  padding: 20px 0px;
}
.message__box {
  height: 30vh;
  width: 26vw;
  background-color: transparent;
}

.gold__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  border-radius: 8px;
  letter-spacing: 0.75px;
  border: none;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  font-size: 16px;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid $soft-gray;
  letter-spacing: 0.75px;
  background-color: white;
  color: $base-gray;
  cursor: text;
  font-size: 16px;
}
.tooltip {
  position: relative;
  &__icon {
    height: 2rem;
  }

  &__popup {
    width: 18rem;
    visibility: hidden;
    padding: 10px 18px;
    border-radius: 6px;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    // border: solid 2px $very-light-gray;
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
::v-deep .input-content {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
::v-deep .input-form__active {
  border: none;
}
</style>
