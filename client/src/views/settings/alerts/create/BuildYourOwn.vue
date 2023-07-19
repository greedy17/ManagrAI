<template>
  <div class="alerts-page">
    <section v-if="!oldAlert">
      <div class="title">
        <h4 class="title__head">General</h4>

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
              <span v-for="(day, i) in weeklyOpts" :key="i">
                <input
                  type="checkbox"
                  @input="setDay($event.target.value, form)"
                  :id="day.value"
                  :value="day.value"
                />
                <label
                  :for="day.value"
                  :class="
                    form.field.recurrenceDays.value.includes(day.value) ? 'active-option' : ''
                  "
                  >{{ day.key.charAt(0) }}</label
                >
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

          <div class="custom-checkbox" v-else>
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
                  <p
                    v-if="userChannelOpts.nextCursor"
                    class="multi-slot__more"
                    @click="listUserChannels(userChannelOpts.nextCursor)"
                  >
                    Load More
                    <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                  </p>
                  <p v-else></p>
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
            :custom-label="fullOrEmailLabel"
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
              class="white_button"
              :disabled="
                !(
                  alertTemplateForm.field.alertGroups.groups.length < 3 &&
                  validateAlertOperands(alertTemplateForm.field.alertGroups.groups)
                )
              "
              @click="onAddAlertGroup(), scrollToElement()"
            >
              Add group
            </button>
          </div>
        </div>
        <div ref="bottom"></div>
      </div>

      <div style="margin-bottom: 8px; display: flex" class="title">
        <div style="">
          <h4 class="title__head">Slack Message</h4>
          <section class="title__body">
            <p style="margin-bottom: 0">
              This is the message you'll recieve in slack with your workflow.
            </p>
          </section>
          <div style="display: flex; overflow-y: auto; height: 28.75vh">
            <div style="margin-bottom: 1rem">
              <div v-if="formattedSlackMessage.length">
                <draggable
                  v-model="formattedSlackMessage"
                  group="fields"
                  @start="drag = true"
                  @end="dragEnd"
                  class="drag-section"
                >
                  <div
                    v-for="(message, i) in formattedSlackMessage"
                    :key="i"
                    style="
                      margin: 0.5rem 1rem;
                      padding: 6px 12px;
                      display: flex;
                      justify-content: space-between;
                      align-items: center;
                      width: 27.5vw;
                      border: 1px solid #eeeeee;
                      border-radius: 8px;
                      cursor: pointer;
                    "
                  >
                    <div style="justify-self: start">
                      <div style="font-weight: 900; font-size: 0.75rem; display: flex;">
                        <img src="@/assets/images/drag.svg" alt="" />
                        <div style="margin-top: 0.25rem; margin-left: 0.5rem;">{{ message.title }}</div>
                      </div>
                      <!-- <div style="font-size: .6rem;">{ {{message.val}} }</div> -->
                    </div>
                    <div @click="removeMessage(i, message)">
                      <img src="@/assets/images/remove.svg" style="height: 1.2rem" />
                    </div>
                  </div>
                </draggable>
              </div>
              <div
                v-else
                style="
                  margin: 0.5rem 1rem;
                  padding: 6px 12px;
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  width: 27.5vw;
                  border: 1px solid #eeeeee;
                  border-radius: 8px;
                "
              >
                <div style="justify-self: start">
                  <div style="font-weight: 900; font-size: 0.75rem; margin-bottom: 0.1rem">
                    Please Select an Option from the List
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div style="margin-right: 8px; height: fit-content" class="start">
          <section style="max-width: 19vw;">
            <div class="search-bar">
              <img src="@/assets/images/search.svg" style="height: 18px" alt="" />
              <input
                @input="searchFields"
                type="search"
                :placeholder="`Search Fields`"
                v-model="filterText"
              />
            </div>

            <div class="field-section__fields">
              <div>
                <p v-for="(field, i) in filteredFields" :key="field.id" style="margin: 4px 0">
                  <input @click="onAddField(field)" type="checkbox" :id="i" :value="field" />
                  <label :for="i"></label>
                  {{ field.label == 'Price Book Entry ID' ? 'Products' : field.label }}
                </p>
              </div>
            </div>
          </section>
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
import { CollectionManager } from '@thinknimble/tn-models'
import { SOBJECTS_LIST } from '@/services/salesforce'
import { ObjectField } from '@/services/crm'
import draggable from 'vuedraggable'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
import { decryptData } from '../../../../encryption'
export default {
  name: 'AlertsPage',
  components: {
    AlertGroup,
    ToggleCheckBox,
    FormField,
    PulseLoadingSpinnerButton,
    SlackNotificationTemplate,
    Modal,
    AlertsEditPanel,
    draggable,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      resources: [],
      dropdownLoading: false,
      selectedChannel: null,
      userChannelOpts: new SlackListResponse(),
      channelName: '',
      selectedUsers: null,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      filterText: '',
      savingTemplate: false,
      addedFields: [],
      create: false,
      directToUsers: true,
      channelCreated: false,
      setDaysBool: false,
      slackMessage: [],
      formattedSlackMessage: [],
      fields: CollectionManager.create({
        ModelClass: ObjectField,
        filters: {
          crmObject: alert.resourceType,
          forAlerts: true,
        },
        pagination: { size: 1000 },
      }),
      users: CollectionManager.create({ ModelClass: User }),
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
      await this.users.refresh()
      await this.listUserChannels()
    }
    this.resources =
      this.userCRM === 'SALESFORCE'
        ? ['Opportunity', 'Account', 'Contact', 'Lead']
        : ['Deal', 'Contact', 'Company']
    this.slackMessage =
      this.alertTemplateForm.field.alertMessages.groups[0].field.body.value.split('\n\n')
    const slackFormat = []
    for (let i = 0; i < this.slackMessage.length; i++) {
      const titleAndVal = this.slackMessage[i].split('\n')
      const titleFormatted = titleAndVal[0].slice(8, titleAndVal[0].length - 10)
      const valFormatted = titleAndVal[1].slice(3, titleAndVal[1].length - 2)
      // valFormatted is needed for addedFieldNames, since it is more precise than just the title for filtering
      slackFormat.push({ title: titleFormatted, val: valFormatted })
    }
    this.formattedSlackMessage = slackFormat
  },
  watch: {
    alertIsValid: 'activateSave',
    setDaysBool: 'activateSave',
    selectedResourceType: {
      immediate: true,
      async handler(val, prev) {
        if (prev && val !== prev) {
          // this.alertTemplateForm = this.alertTemplateForm.reset()
          this.selectedResourceType = val
        }
        if (this.selectedResourceType) {
          this.fields.filters.crmObject = this.selectedResourceType
          this.fields.filters.page = 1
          await this.fields.refresh()
          this.changeDefaultSlackMessage()
        }
      },
      directToUsers: 'setDefaultChannel',
    },
  },
  props: {
    oldAlert: {},
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    searchFields() {
      this.fields = CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 1000 },
        filters: {
          crmObject: this.selectedResourceType,
          search: this.filterText,
        },
      })
      this.fields.refresh()
    },
    checkForChannel() {
      !this.hasRecapChannel ? (this.directToUsers = false) : (this.directToUsers = true)
    },
    validateAlertOperands(operands) {
      for (let i = 0; i < operands.length; i++) {
        const operandGroup = operands[i].field.alertOperands.groups
        for (let j = 0; j < operandGroup.length; j++) {
          if (!operandGroup[j].field.operandIdentifier.isValid) {
            return false
          }
          if (!operandGroup[j].field.operandOperator.isValid) {
            return false
          }
          if (!operandGroup[j].isValid) {
            return false
          }
        }
      }
      return true
    },
    async onSave() {
      this.savingTemplate = true
      this.alertTemplateForm.validate()
      if (this.alertTemplateForm.isValid && this.setDaysBool) {
        try {
          const res = await AlertTemplate.api.createAlertTemplate({
            ...this.alertTemplateForm.toAPI,
            user: this.user.id,
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
    onAddField(field) {
      this.addedFields.push({ ...field, order: this.addedFields.length, includeInRecap: true })
      this.bindText(`${this.selectedResourceType}.${field.apiName}`, `${field.label}`)
    },
    activateSave() {
      this.$emit('can-save', (!!this.alertIsValid && this.setDaysBool))
    },
    scrollToTop() {
      this.$refs.top ? this.$refs.top.scrollIntoView({ behavior: 'smooth' }) : null
    },
    scrollToElement() {
      this.$refs.bottom ? this.$refs.bottom.scrollIntoView({ behavior: 'smooth' }) : null
    },
    fullOrEmailLabel(props) {
      if (!props.fullName.trim()) {
        return props.email
      }
      return props.fullName
    },
    // changeFrequency() {
    //   this.alertFrequency == 'WEEKLY'
    //     ? (this.alertFrequency = 'MONTHLY')
    //     : (this.alertFrequency = 'WEEKLY')

    //   this.alertFrequency == 'MONTHLY'
    //     ? (this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value = [0])
    //     : (this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value = [])
    // },
    mapIds() {
      let mappedIds = this.selectedUsers.map((user) => user.id)
      this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value = mappedIds
    },
    setDefaultChannel() {
      this.directToUsers
        ? (this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = ['default'])
        : (this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = null)
    },
    repsPipeline() {
      if (
        this.user.userLevel !== 'MANAGER' &&
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value.length < 1
      ) {
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value.push('SELF')
        this.setPipelines({
          fullName: 'MYSELF',
          id: 'SELF',
        })
      }
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
    async listUserChannels(cursor) {
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
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = [res.channel.id]
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
    changeDefaultSlackMessage() {
      if (this.selectedResourceType === 'Deal') {
        this.slackMessage = ["<strong>Deal Name</strong> \n { Deal.dealname }"]
      } else if (this.selectedResourceType === 'Company') {
        this.slackMessage = ["<strong>Company Name</strong> \n { Company.name }"]
      } else if (this.selectedResourceType === 'Contact' && this.userCRM === 'HUBSPOT') {
        this.slackMessage = ["<strong>Email</strong> \n { Contact.email }"]
      } else if (this.selectedResourceType === 'Opportunity') {
        this.slackMessage = ["<strong>Opportunity Name</strong> \n { Opportunity.Name }"]
      } else if (this.selectedResourceType === 'Account') {
        this.slackMessage = ["<strong>Account Name</strong> \n { Account.Name }"]
      } else if (this.selectedResourceType === 'Contact' && this.userCRM === 'SALESFORCE') {
        this.slackMessage = ["<strong>Email</strong> \n { Contact.Email }"]
      } else if (this.selectedResourceType === 'Lead') {
        this.slackMessage = ["<strong>Email</strong> \n { Lead.Email }"]
      }
      this.alertTemplateForm.field.alertMessages.groups[0].field.body.value = this.slackMessage[0]
      const slackFormat = []
      for (let i = 0; i < this.slackMessage.length; i++) {
        const titleAndVal = this.slackMessage[i].split('\n')
        const titleFormatted = titleAndVal[0].slice(8, titleAndVal[0].length - 10)
        const valFormatted = titleAndVal[1].slice(3, titleAndVal[1].length - 2)
        // valFormatted is needed for addedFieldNames, since it is more precise than just the title for filtering
        slackFormat.push({ title: titleFormatted, val: valFormatted })
      }
      this.formattedSlackMessage = slackFormat
    },
    dragEnd() {
      const slackMesArr = []
      const slackBindingsArr = []
      for (let i = 0; i < this.formattedSlackMessage.length; i++) {
        slackMesArr.push('<strong>' + this.formattedSlackMessage[i].title + '</strong> \n { ' + this.formattedSlackMessage[i].val + ' }')
        slackBindingsArr.push(` ${this.formattedSlackMessage[i].val} `)
      }
      this.slackMessage = slackMesArr
      this.alertTemplateForm.field.alertMessages.groups[0].field.body.value = this.slackMessage.join('\n\n')
      this.alertTemplateForm.field.alertMessages.groups[0].field.bindings.value = slackBindingsArr
      this.drag = false
    },
    bindText(val, title) {
      const addedStr = `<strong>${title}</strong> \n { ${val} }`
      this.slackMessage.push(addedStr)
      this.formattedSlackMessage.push({ title, val })
      this.alertTemplateForm.field.alertMessages.groups[0].field.body.value =
        this.slackMessage.join('\n\n')
      if (!this.alertTemplateForm.field.alertMessages.groups[0].field.bindings.value) {
        this.alertTemplateForm.field.alertMessages.groups[0].field.bindings.value = [` ${val} `]
      } else {
        this.alertTemplateForm.field.alertMessages.groups[0].field.bindings.value.push(` ${val} `)
      }
    },
    removeMessage(i, removedField) {
      this.slackMessage = this.slackMessage.filter((mes, j) => j !== i)
      this.formattedSlackMessage = this.formattedSlackMessage.filter((mes, j) => j !== i)
      this.alertTemplateForm.field.alertMessages.groups[0].field.bindings.value = this.alertTemplateForm.field.alertMessages.groups[0].field.bindings.value.filter(
        (mes, j) => j !== i,
      )
      this.alertTemplateForm.field.alertMessages.groups[0].field.body.value =
        this.slackMessage.join('\n\n')
      this.addedFields = [...this.addedFields.filter((f) => f.id != removedField.id)]
    },
    setPipelines(obj) {
      if (this.alertTemplateForm.field.alertConfig.groups[0].field._alertTargets.value.length < 1) {
        this.alertTemplateForm.field.alertConfig.groups[0].field._alertTargets.value.push(obj)
      }
    },
    setRecipient() {
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value =
        this.selectedChannel
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = [
        this.selectedChannel.id,
      ]
    },
    setDay(n, form) {
      const recurrenceDays = form.field.recurrenceDays.value
      let index
      for (let i = 0; i < recurrenceDays.length; i++) {
        const day = recurrenceDays[i]
        if (day === n) {
          index = i
          break;
        }
      }
      if (index !== undefined) {
        // if it exists in the array, remove
        form.field.recurrenceDays.value = recurrenceDays.filter((day, i) => i !== index)
      } else {
        // if it doesn't exist, add
        form.field.recurrenceDays.value.push(n)
      }
      this.setDaysBool = !!form.field.recurrenceDays.value.length
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
    async onUsersNextPage() {
      this.dropdownLoading = true
      await this.users.addNextPage()
      setTimeout(() => {
        this.dropdownLoading = false
      }, 1000)
    },
  },
  computed: {
    hasRecapChannel() {
      return this.user.slackAccount
        ? this.user.slackAccount.recapChannel
        : null
    },
    filteredFields() {
      return this.fields.list.filter(
        (field) => !this.addedFieldNames.includes(`${this.selectedResourceType}.${field.apiName}`)
      )
    },
    addedFieldNames() {
      return this.formattedSlackMessage.map((field) => {
        return field.val.trim()
      })
    },
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
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      console.log('this.$stote', this.$store)
      return this.$store.state.user.crm
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
    this.checkForChannel()
    this.setDefaultChannel()
  },
  beforeMount() {
    this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value = 'SLACK_CHANNEL'
    this.alertTemplateForm.field.alertMessages.groups[0].field.body.value =
      this.userCRM === 'SALESFORCE'
        ? '<strong>Opportunity Name</strong> \n { Opportunity.Name }'
        : '<strong>Deal Name</strong> \n { Deal.dealname }'
    this.alertTemplateForm.field.alertMessages.groups[0].field.bindings.value =
      this.userCRM === 'SALESFORCE'
        ? [' Opportunity.Name ']
        : [' Deal.dealname ']
    this.alertTemplateForm.field.resourceType.value =
      this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal'
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
.active-option {
  color: $base-gray !important;
  border: 1px solid $base-gray !important;
}
// .andOr {
//   border: 1px solid $soft-gray;
//   padding: 6px 8px;
//   border-radius: 6px;
//   cursor: pointer;
//   width: fit-content;
//   color: $base-gray;
// }
// .inactive {
//   color: $very-light-gray;
//   font-size: 9px;
//   border-radius: 4px;
// }
// .space-s {
//   margin: 0 4px;
// }
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
.start {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
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
::placeholder {
  color: $very-light-gray;
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
.invert {
  filter: invert(99%);
}
.white_button {
  @include white-button();
  font-size: 13px;
  margin-right: 12px;
  padding: 6px 8px;
  margin-top: 24px;
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
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 13px;
}
.week-row {
  display: flex;
  flex-direction: row;
  align-items: center !important;
  width: 25vw;
  overflow-x: scroll;
  margin-top: 16px;

  span {
    transition: all 0.2s;
  }
  label {
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
  }
  input {
    display: none;
  }

  span:hover {
    transform: scale(1.15);
    color: $base-gray;
  }
}
.gold__button {
  @include primary-button();
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  font-size: 14px;
  margin-top: 8px;
  // margin-bottom: -8px;
}
::v-deep .input-content {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
::v-deep .input-form__active {
  border: none;
}
.search-bar {
  background-color: white;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: 8px;
  margin-top: 16px;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
input[type='search'] {
  width: 15vw;
  letter-spacing: 0.75px;
  border: none;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
.field-section {
  width: 20vw;
  background-color: white;
  height: 100%;
  margin-top: 28px;
  margin-left: 16px;
  padding: 0px 32px;
  border-radius: 6px;
  letter-spacing: 0.75px;

  &__title {
    letter-spacing: 0.75px;
  }
  &__fields {
    h4 {
      font-size: 13px;
      font-weight: 400;
      margin-bottom: 8px;
    }
    p {
      font-size: 12px;
      letter-spacing: 0.75px;
    }
    div {
      outline: 1px solid $soft-gray;
      border-radius: 6px;
      padding: 4px 16px;
      margin-top: 16px;
      height: 32vh;
      overflow: scroll;
      section {
        span {
          color: $coral;
          margin-left: 4px;
        }
      }
    }
  }
}
</style>
