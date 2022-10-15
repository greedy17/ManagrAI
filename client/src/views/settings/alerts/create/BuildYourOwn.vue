<template>
  <div class="alerts-page">
    <section v-if="!oldAlert">
      <div class="title">
        <h4 @click="test" class="title__head">General</h4>

        <section class="title__body">
          <p>What type of workflow are you building ?</p>
        </section>

        <label class="label" for="name">Name your Workflow </label>
        <input
          id="name"
          type="text"
          class="input-field"
          placeholder="Name"
          v-model="alertTemplateForm.field.title.value"
          :errors="alertTemplateForm.field.title.errors"
          autofocus
        />

        <div style="margin-top: 16px">
          <label class="label" for="type">Select Record </label>
          <Multiselect
            placeholder="Record types"
            :options="resources"
            openDirection="below"
            style="width: 94%; margin-left: 12px; margin-top: 8px"
            v-model="selectedResourceType"
            selectLabel="Enter"
          >
          </Multiselect>
        </div>
      </div>

      <div class="title">
        <h4 class="title__head">Delivery Day</h4>
        <section class="title__body">
          <p>When would you like to be notified ?</p>
        </section>

        <div
          class="title__body"
          :key="i"
          v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
        >
          <!-- <p @click="changeFrequency" class="andOr">
            <span :class="alertFrequency !== 'WEEKLY' ? 'inactive' : ''">Weekly</span>
            <span class="space-s">|</span>
            <span :class="alertFrequency !== 'MONTHLY' ? 'inactive' : ''">Monthly</span>
          </p> -->
          <div class="row__">
            <label :class="form.field.recurrenceFrequency.value == 'WEEKLY' ? 'gray' : ''"
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
            <label :class="form.field.recurrenceFrequency.value == 'MONTHLY' ? 'gray' : ''"
              >Monthly</label
            >
          </div>

          <div v-if="form.field.recurrenceFrequency.value !== 'MONTHLY'">
            <div class="week-row">
              <span
                v-for="(day, i) in weeklyOpts"
                :key="i"
                :class="form.field.recurrenceDays.value.includes(day.value) ? 'active-option' : ''"
              >
                <input
                  type="checkbox"
                  :id="day.value"
                  :value="day.value"
                  v-model="form.field.recurrenceDays.value"
                />
                <label :for="day.value">{{ day.key.charAt(0) }}</label>
              </span>
            </div>
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

      <div class="title">
        <h4 class="title__head">Delivery Method</h4>
        <section class="title__body">
          <p>Where would you like to be notified ?</p>
        </section>

        <div style="margin-top: -8px" class="title__body">
          <div class="custom-checkbox" v-if="user.userLevel !== 'REP'">
            <input type="checkbox" id="allUsers" v-model="directToUsers" />
            <label for="allUsers">Send directly to users</label>
          </div>

          <div v-else>
            <input type="checkbox" id="allUsers" v-model="directToUsers" />
            <label for="allUsers">Send to primary channel</label>
          </div>
          <div style="margin-top: 16px" v-if="!channelName && !directToUsers" class="row__">
            <label :class="!create ? 'gray' : ''">Select Channel</label>
            <ToggleCheckBox
              style="margin: 0.25rem"
              @input="changeCreate"
              :value="create"
              offColor="#41b883"
              onColor="#41b883"
            />
            <label :class="create ? 'gray' : ''">Create Channel</label>

            <!-- <small @click="changeCreate" style="margin-top: 12px" class="andOr">
              <span :class="create ? 'inactive' : ''">Select Channel</span>
              <span class="space-s">|</span>
              <span :class="!create ? 'inactive' : ''">Create Channel</span>
            </small> -->
          </div>

          <div v-if="create && !directToUsers">
            <input
              style="margin-top: 8px"
              v-model="channelName"
              class="search__input"
              type="text"
              name="channel"
              id="channel"
              placeholder="Name your channel"
              @input="logNewName(channelName)"
            />

            <div v-if="!channelCreated">
              <button
                @click="createChannel(channelName)"
                class="gold__button"
                :class="channelName ? 'pulse' : ''"
                :disabled="!channelName"
              >
                Create Channel
              </button>
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
                  <p class="multi-slot__more" @click="listUserChannels(userChannelOpts.nextCursor)">
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

      <div class="title">
        <h4 class="title__head">Pipelines</h4>
        <section class="title__body">
          <p>Whose {{ selectedResourceType }}'s are we checking ?</p>
        </section>
        <div class="title__body">
          <Multiselect
            placeholder="Select Users"
            @input="mapIds"
            v-model="selectedUsers"
            :options="userTargetsOpts"
            openDirection="below"
            style="width: 25vw"
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
        </div>
      </div>

      <div ref="top" class="title">
        <h4 class="title__head">Conditions</h4>
        <section class="title__body">
          <p>We'll alert you when these conditions are met</p>
        </section>

        <div :key="i" v-for="(form, i) in alertTemplateForm.field.alertConfig.groups">
          <div
            :key="index"
            v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups"
            :class="index > 0 ? 'margin-top border-top' : ''"
            class="title__body"
          >
            <div>
              <div
                style="margin-top: 16px"
                class="end"
                v-show="index !== 0"
                v-if="alertTemplateForm.field.alertGroups.groups.length > 1"
              >
                <small class="remove__group" @click="onRemoveAlertGroup(index), scrollToTop()">
                  <!-- Group {{ index + 1 }} -->
                  <img
                    src="@/assets/images/close.svg"
                    height="16px"
                    style="margin-left: 4px"
                    alt=""
                  />
                </small>
              </div>
              <AlertGroup
                :form="alertGroup"
                :resourceType="alertTemplateForm.field.resourceType.value"
                @scroll-to-view="scrollToElement"
              />
            </div>
          </div>

          <div class="flex-end">
            <button
              v-if="alertTemplateForm.field.alertGroups.groups.length < 3"
              class="group_button"
              @click="onAddAlertGroup(), scrollToElement()"
            >
              Add group
            </button>
          </div>
        </div>
        <div ref="bottom"></div>
      </div>

      <div style="margin-bottom: 8px" class="title">
        <h4 class="title__head">Slack Message</h4>
        <section class="title__body">
          <p>This is the message you'll recieve in slack with your workflow.</p>
        </section>

        <!-- <label class="label" for="message">Message </label> -->
        <FormField id="message">
          <template v-slot:input>
            <quill-editor
              @blur="alertTemplateForm.field.alertMessages.groups[0].field.body.validate()"
              ref="message-body"
              v-model="alertTemplateForm.field.alertMessages.groups[0].field.body.value"
              :options="{
                modules: { toolbar: { container: ['bold', 'italic', 'strike'] } },
                placeholder: 'Write your message.',
                theme: 'snow',
              }"
              class="message__box"
            />
          </template>
        </FormField>
        <div style="margin-right: 8px" class="end">
          <Multiselect
            placeholder="Select field"
            v-model="crmValue"
            @input="bindText(`${selectedResourceType}.${$event.apiName}`, `${$event.label}`)"
            :options="fields.list"
            openDirection="above"
            style="width: 18vw; margin-right: 4px"
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
                Insert Value { }
              </p>
            </template>
          </Multiselect>
        </div>
      </div>
    </section>

    <section v-else></section>
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
import AlertsEditPanel from '@/views/settings/alerts/view/_AlertsEditPanel.vue'
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
    AlertsEditPanel,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      updatedAlert: this.oldAlert,
      addingFields: false,
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
    alertIsValid: 'activateSave',
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
  props: {
    oldAlert: {},
  },
  methods: {
    test() {
      console.log(this.alertTemplateForm.isValid)
    },
    activateSave() {
      this.$emit('can-save', !!this.alertIsValid)
    },
    scrollToTop() {
      this.$refs.top ? this.$refs.top.scrollIntoView({ behavior: 'smooth' }) : null
    },
    scrollToElement() {
      this.$refs.bottom ? this.$refs.bottom.scrollIntoView({ behavior: 'smooth' }) : null
    },
    changeFrequency() {
      this.alertFrequency == 'WEEKLY'
        ? (this.alertFrequency = 'MONTHLY')
        : (this.alertFrequency = 'WEEKLY')

      this.alertFrequency == 'MONTHLY'
        ? (this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value = [0])
        : (this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value = [])
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
          this.$emit('close-builder')
          this.$router.go()
        } catch (e) {
          this.$toast('An error occured while trying to save your workflow', {
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
    bindText(val, title) {
      this.$refs['message-body'].quill.focus()
      let start = 0
      if (this.editor.selection.lastRange) {
        start = this.editor.selection.lastRange.index
      }
      this.editor.insertText(start, `${title}: { ${val} } \n \n`)
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
      if (this.alertTemplateForm.field.alertConfig.groups[0].field._alertTargets.value.length < 1) {
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
    setOldAlertValues() {
      if (this.oldAlert) {
        console.log('SAVED ALERT', this.oldAlert)
        console.log('ALERT TEMPLATE FORM', this.alertTemplateForm)

        this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value =
          this.oldAlert.configsRef[0].recipientType
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value =
          this.oldAlert.configsRef[0].recipients
        this.alertTemplateForm.field.resourceType.value = this.oldAlert.resourceType
        this.alertTemplateForm.field.title.value = this.oldAlert.title
        this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDay.value =
          this.oldAlert.configsRef[0].recurrenceDay
        this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value =
          this.oldAlert.configsRef[0].recurrenceDays
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value =
          this.oldAlert.configsRef[0].alertTargetsRef.map((target) => target.value)
        this.alertTemplateForm.field.alertMessages.groups[0].field.body =
          this.oldAlert.messageTemplateRef.body

        // for (let i = 0; i < this.oldAlert.groupsRef.length; i++) {
        //   this.alertTemplateForm.field.alertGroups.groups[i].fields.alertOperands.group[
        //     i
        //   ].fields.operandCondition.value =
        //     this.oldAlert.groupsRef[i].operandsRef[i].operandCondition

        //   this.alertTemplateForm.field.alertGroups.groups[i].fields.alertOperands.group[
        //     i
        //   ].fields.operandIdentifier.value =
        //     this.oldAlert.groupsRef[i].operandsRef[i].operandIdentifier

        //   this.alertTemplateForm.field.alertGroups.groups[i].fields.alertOperands.group[
        //     i
        //   ].fields.operandOrder.value = this.oldAlert.groupsRef[i].operandsRef[i].operandOrder

        //   this.alertTemplateForm.field.alertGroups.groups[i].fields.alertOperands.group[
        //     i
        //   ].fields.operandType.value = this.oldAlert.groupsRef[i].operandsRef[i].operandType

        //   this.alertTemplateForm.field.alertGroups.groups[i].fields.alertOperands.group[
        //     i
        //   ].fields.operandOperator.value = this.oldAlert.groupsRef[i].operandsRef[i].operandOperator

        //   this.alertTemplateForm.field.alertGroups.groups[i].fields.alertOperands.group[
        //     i
        //   ].fields.operandValue.value = this.oldAlert.groupsRef[i].operandsRef[i].operandValue
        // }
      }
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
    alertIsValid() {
      return this.alertTemplateForm.isValid
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
    alertFrequency: {
      get() {
        return this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceFrequency.value
      },
      set(val) {
        this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceFrequency.value = val
      },
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
    console.log('SAVED ALERT', this.oldAlert)
    console.log('ALERT TEMPLATE FORM', this.alertTemplateForm)
    // this.updatedAlert.groupsRef

    // this.setOldAlertValues()
  },
  beforeMount() {
    this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value = 'SLACK_CHANNEL'
    this.alertTemplateForm.field.alertMessages.groups[0].field.body.value =
      'Hey { __Recipient.full_name },'
    this.alertTemplateForm.field.resourceType.value = 'Opportunity'
    this.repsPipeline()
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

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 $dark-green;
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
  }
}
.pulse {
  box-shadow: 0 0 0 0 $dark-green;
  transform: scale(1);
  animation: pulse 1.25s infinite;
}
::v-deep .multiselect__content-wrapper {
  min-width: 18vw;
}
::v-deep .multiselect__single {
  white-space: nowrap;
  overflow: hidden;
  color: $base-gray;
  font-size: 12px;
}
.gray-bottom {
  border-bottom: 1px solid $soft-gray;
  padding-bottom: 8px;
}
.red {
  color: $coral;
}
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

  span {
    background-color: $white;
    cursor: pointer;
    color: $base-gray;
    margin-right: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    white-space: nowrap;
    transition: all 0.2s;
    input {
      display: none;
    }
  }

  p {
    background-color: $white;
    color: $base-gray;
    margin-right: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    white-space: nowrap;
    transition: all 0.2s;
  }
  span:hover,
  p:hover {
    transform: scale(1.15);
    opacity: 0.5;
  }
}
.active-option {
  color: $base-gray !important;
  border: 1px solid $base-gray !important;
}
.negative-left {
  margin-left: -68px !important;
}
.andOr {
  border: 1px solid $soft-gray;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  width: fit-content;
  color: $base-gray;
}
.inactive {
  color: $very-light-gray;
  font-size: 9px;
  border-radius: 4px;
}
.space-s {
  margin: 0 4px;
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
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-right: 16px;
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
  min-height: 44vh;
  overflow: scroll;
  letter-spacing: 0.75px;
}
.increase-height {
  min-height: 84vh;
}
.title {
  background-color: white;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  border: 1px solid $soft-gray;
  color: $base-gray;
  border-radius: 6px;
  width: 50vw;
  // min-height: 25vh;
  letter-spacing: 0.75px;
  padding: 0px 0px 32px 0px;
  margin-top: 16px;
  &__head {
    padding: 8px 12px;
    background-color: white;
    margin-bottom: 0;
    // color: $very-light-gray;
  }
  &__body {
    padding: 6px 12px;
    background-color: white;
    font-size: 11px;
    color: $light-gray-blue;
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
.label {
  color: $base-gray;
  font-size: 12px;
  margin-left: 12px;
}
.input-field {
  border: none;
  letter-spacing: 0.8px;
  padding: 8px;
  color: $base-gray;
  margin-left: 12px;
  width: 94%;
  border: 1px solid $soft-gray;
  border-radius: 4px;
  margin-top: 8px;
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
  overflow: scroll;
  min-height: 80vh;
  // border-right: 1px solid $soft-gray;
}

::v-deep .ql-toolbar.ql-snow {
  display: none;
}
::v-deep .ql-container.ql-snow {
  outline: 1px solid $soft-gray;
  border: none;
  border-radius: 4px;
  margin-left: 12px;
  width: 48vw;
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
}
.flex-end {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-end;
  margin-right: 8px;
}
.gray {
  color: $base-gray;
  font-weight: bold;
}
.gray:hover {
  opacity: 0.5;
  border-radius: 4px;
}
.neg-mar {
  margin-top: -6px;
}
.neg-mar-large {
  margin-top: -20px;
}

.border-top {
  border-top: 1px solid $soft-gray;
}

.custom-checkbox > input[type='checkbox']:checked + label::after {
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
.custom-checkbox > input[type='checkbox'] {
  line-height: 2.1ex;
}
.custom-checkbox > input[type='checkbox'] {
  position: absolute;
  left: -999em;
}
.custom-checkbox > input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}
.custom-checkbox > input[type='checkbox'] + label::before {
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
.margin-top {
  margin-top: 16px;
}
.remove__group {
  background-color: $off-white;
  border-radius: 4px;
  cursor: pointer;
  padding: 3px 6px;
  margin-left: 8px;
  display: flex;
  align-items: center;
  width: fit-content;
  color: $base-gray;
  // img {
  //   filter: invert(48%) sepia(24%) saturate(1368%) hue-rotate(309deg) brightness(105%) contrast(96%);
  // }
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
  align-items: center;
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
.group_button {
  font-size: 13px;
  margin-right: 12px;
  padding: 6px 8px;
  border-radius: 4px;
  border: none;
  background-color: $dark-green;
  color: white;
  margin-top: 24px;
}
.group_button2 {
  font-size: 13px;
  margin-right: 12px;
  padding: 6px 8px;
  border-radius: 4px;
  border: none;
  background-color: $dark-green;
  color: white;
}
textarea {
  @extend .textarea;
}
.alerts-page {
  height: 94vh;
  overflow: scroll;
  color: $base-gray;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
// ::-webkit-scrollbar {
//   width: 3px;
//   height: 0px;
//   margin-right: 8px;
// }
// ::-webkit-scrollbar-thumb {
//   background-color: $off-white;
//   box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
//   border-radius: 0.3rem;
// }
// ::-webkit-scrollbar-track {
//   box-shadow: inset 2px 2px 4px 0 $very-light-gray;
//   border-radius: 0.3rem;
// }
// ::-webkit-scrollbar-track-piece {
//   margin-top: 24px;
// }
.green {
  color: $dark-green;
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
.week-row {
  display: flex;
  flex-direction: row;
  align-items: center !important;
  width: 25vw;
  overflow-x: scroll;
  margin-top: 16px;

  span {
    cursor: pointer;
    color: $light-gray-blue;
    margin-right: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 26px;
    width: 26px;
    border-radius: 100%;
    border: 1px solid $soft-gray;
    transition: all 0.2s;
    input {
      display: none;
    }
  }

  span:hover {
    transform: scale(1.15);
    color: $base-gray;
  }
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
  padding: 6px 10px;
  border-radius: 4px;
  letter-spacing: 0.75px;
  border: none;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  font-size: 14px;
  margin-top: 8px;
  // margin-bottom: -8px;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid $soft-gray;
  letter-spacing: 0.75px;
  background-color: white;
  color: $very-light-gray;
  cursor: text;
  font-size: 14px;
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
