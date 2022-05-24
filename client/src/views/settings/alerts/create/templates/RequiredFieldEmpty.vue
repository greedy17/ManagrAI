<template>
  <PopularWorkflows
    :selectField="true"
    :config="allConfigs.REQUIRED_FIELD_EMPTY"
  />
</template>

<script>
/**
 * Components
 * */
// Pacakges

import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
//Internal
import PopularWorkflows from '@/views/settings/alerts/create/templates/PopularWorkflows'
import FormField from '@/components/forms/FormField'
import EmptyAlertGroup from '@/views/settings/alerts/create/EmptyAlertGroup'
import { UserConfigForm } from '@/services/users/forms'
import allConfigs from '../../configs'

/**
 * Services
 */

import AlertTemplate, { AlertTemplateForm } from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjectField, NON_FIELD_ALERT_OPTS, SOBJECTS_LIST } from '@/services/salesforce'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'RequiredFieldEmpty',
  components: {
    PopularWorkflows,
    EmptyAlertGroup,
    ToggleCheckBox,
    FormField,
    PulseLoadingSpinnerButton,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      dropdownLoading: false,
      selectedUsers: [],
      recurrenceDays: [0, 1, 2, 3, 4, 5],
      allConfigs: allConfigs,
      selectedChannel: null,
      channelOpts: new SlackListResponse(),
      userChannelOpts: new SlackListResponse(),
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      channelCreated: false,
      create: false,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      newChannel: {},
      channelName: '',
      OPPORTUNITY: 'Opportunity',
      operandDate: '',
      searchQuery: '',
      searchText: '',
      recurrenceDay: '',
      searchChannels: '',
      SOBJECTS_LIST,
      pageNumber: 0,
      configName: '',
      directToUsers: true,
      userConfigForm: new UserConfigForm({}),
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
      await this.listUserChannels()
    }
    if (this.userLevel == 'MANAGER') {
      await this.users.refresh()
    }
    this.userConfigForm = new UserConfigForm({
      activatedManagrConfigs: this.user.activatedManagrConfigs,
    })
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
    directToUsers: 'setDefaultChannel',
  },
  methods: {
    handleUpdate() {
      this.loading = true

      User.api
        .update(this.user.id, this.userConfigForm.value)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
    },
    changeCreate() {
      this.create = !this.create
    },
    setDefaultChannel() {
      this.directToUsers
        ? (this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = 'default')
        : (this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = null)
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
    async listChannels(cursor = null) {
      const res = await SlackOAuth.api.listChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.channelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.channelOpts = results
    },
    setRecipient() {
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value =
        this.selectedChannel
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value =
        this.selectedChannel.id
    },
    mapIds() {
      let mappedIds = this.selectedUsers.map((user) => user.id)

      this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value = mappedIds
    },
    setPipelines(obj) {
      this.alertTemplateForm.field.alertConfig.groups[0].field._alertTargets.value.push(obj)
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
          this.userConfigForm.field.activatedManagrConfigs.value.push(res.title)
          this.handleUpdate()
          this.$router.push({ name: 'CreateNew' })
          this.$Alert.alert({
            message: 'Workflow saved succcessfully!',
            timeout: 2000,
            type: 'success',
          })
        } catch (e) {
          this.$Alert.alert({
            message: 'Error, one or more of your users do not have slack connected',
            timeout: 3000,
            type: 'error',
          })
        } finally {
          this.savingTemplate = false
        }
      }
    },
    repsPipeline() {
      if (this.userLevel !== 'MANAGER') {
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value.push('SELF')
        this.setPipelines({
          fullName: 'MYSELF',
          id: 'SELF',
        })
      }
    },
  },
  computed: {
    userTargetsOpts() {
      if (this.userLevel == 'MANAGER') {
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
    user() {
      return this.$store.state.user
    },
    userLevel() {
      return this.$store.state.user.userLevel
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
    this.alertTemplateForm.field.alertConfig.groups[0].field.recipientType.value = 'SLACK_CHANNEL'
    this.alertTemplateForm.field.title.value = 'Required Field Empty'
    this.alertTemplateForm.field.isActive.value = true
    this.alertTemplateForm.field.alertMessages.groups[0].field.body.value =
      'Hey <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong> has a required field that has not been filled out. Please update it.'
    this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceFrequency.value = 'WEEKLY'
    this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDay.value = 0
    this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDays.value = [
      0, 1, 2, 3, 4, 5,
    ]
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
.back-button {
  font-size: 14px;
  color: $dark-green;
  background-color: transparent;
  display: flex;
  align-items: center;
  border: none;
  cursor: pointer;
  margin: 1rem 0rem 0rem 0rem;

  img {
    height: 1rem;
    margin-right: 0.5rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
.alerts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
  padding: 0vw 12vw;
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
  font-size: 0.75rem;
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

.bouncy {
  animation: bounce 0.2s infinite alternate;
}
img {
  filter: invert(60%);
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
  border: 1px solid #e8e8e8;
  width: 75%;
  text-align: center;
  margin-top: 1rem;
}
.purple__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem 1rem;
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
  font-weight: bold;
  font-size: 1.02rem;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  color: $gray;
  cursor: not-allowed;
  font-size: 14px;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: 100%;
}
._row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-evenly;
  width: 66%;
}
input {
  cursor: pointer;
}
.alert__column {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}
.bottom_locked {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: auto;
  margin-bottom: -2rem;
}
.delivery__row {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
}
.forecast__collection {
  display: flex;
  align-items: flex-start;
  justify-content: space-evenly;
  flex-direction: row;
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  width: 75vw;
  padding: 2rem 2rem 1rem 5rem;
  margin-bottom: 1rem;
}
.alerts-page {
  height: 100vh;
  color: $base-gray;
  margin-top: 4rem;
}
.green {
  color: #41b883;
}
</style>

