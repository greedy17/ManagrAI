<template>
  <div class="alerts-page">
    <div class="alerts-header">
      <div>
        <h3>Upcoming Next Step</h3>
        <p style="margin-top: -0.5rem; font-size: 14px">
          View and update all Opportunities with Next Steps due this Week
        </p>
      </div>

      <button @click="$router.push({ name: 'CreateNew' })" class="back-button">
        <img src="@/assets/images/back.png" alt="" />
        Back to workflows
      </button>
    </div>

    <div style="margin-top: 1rem" class="alert__column">
      <template>
        <div class="forecast__collection">
          <div
            class="delivery__row"
            :key="index"
            v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups"
          >
            <span style="margin-bottom: 0.5rem">Select your Next Step Date Field</span>
            <NextAlertGroup
              :form="alertGroup"
              :resourceType="alertTemplateForm.field.resourceType.value"
            />

            <!-- <p
              style="margin-top: -1rem"
              v-if="alertGroup.field.alertOperands.groups[0].field.operandIdentifier.value"
              @click="removeIdentity"
              :class="
                alertGroup.field.alertOperands.groups[0].field.operandIdentifier.value
                  ? 'selected__item'
                  : 'visible'
              "
            >
              <img
                src="@/assets/images/remove.png"
                style="height: 1rem; margin-right: 0.25rem"
                alt=""
              />
              {{ alertGroup.field.alertOperands.groups[0].field.operandIdentifier.value }}
            </p> -->
          </div>

          <div
            class="_row"
            :key="i + 1"
            v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
          >
            <div v-if="userLevel == 'MANAGER'" class="delivery__row">
              <span style="margin-bottom: 0.5rem">Select Users</span>

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
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results.</p>
                    </template>
                    <template slot="placeholder">
                      <p class="slot-icon">
                        <img src="@/assets/images/search.png" alt="" />
                        Select Users
                      </p>
                    </template>
                  </Multiselect>
                </template>
              </FormField>
            </div>

            <div class="delivery__row">
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
                  margin-top: -0.8rem;
                "
                v-if="create"
              >
                <input
                  v-model="channelName"
                  placeholder="Name your Channel"
                  class="search__input"
                  type="text"
                  name="channel"
                  id="channel"
                  @input="logNewName(channelName)"
                />

                <div v-if="!channelCreated" style="margin-top: 0.75rem">
                  <button
                    v-if="channelName"
                    @click="createChannel(channelName)"
                    class="purple__button"
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
                    style="min-width: 13vw"
                    selectLabel="Enter"
                    track-by="id"
                    label="name"
                    :loading="dropdownLoading"
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
                        <img src="@/assets/images/plusOne.png" alt="" />
                      </p>
                    </template>
                    <template slot="placeholder">
                      <p class="slot-icon">
                        <img src="@/assets/images/search.png" alt="" />
                        Select Channel
                      </p>
                    </template>
                  </Multiselect>
                </template>
                <div v-if="userLevel !== 'REP'" class="sendAll">
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
        </div>
      </template>
    </div>

    <div class="bottom_locked">
      <PulseLoadingSpinnerButton
        :loading="savingTemplate"
        :class="
          !alertTemplateForm.isValid || savingTemplate
            ? 'disabled__button'
            : 'purple__button bouncy'
        "
        text="Activate alert"
        @click.stop="onSave"
        :disabled="!alertTemplateForm.isValid"
      />
    </div>
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
import NextAlertGroup from '@/views/settings/alerts/create/NextAlertGroup'
import { UserConfigForm } from '@/services/users/forms'

/**
 * Services
 */

import AlertTemplate, {
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
} from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import { SObjectField, NON_FIELD_ALERT_OPTS, SOBJECTS_LIST } from '@/services/salesforce'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'NextStep',
  components: {
    NextAlertGroup,

    ToggleCheckBox,
    FormField,

    PulseLoadingSpinnerButton,

    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      dropdownLoading: false,
      selectedUsers: [],
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
    getUser(userInfo) {
      if (this.userIds.includes(userInfo)) {
        let selectedUser = this.users.list.filter((user) => user.id === userInfo)

        return selectedUser[0].fullName
      } else {
        return userInfo
      }
    },
    setDefaultChannel() {
      this.directToUsers
        ? (this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = 'default')
        : (this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = null)
    },
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
    removeDay() {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recurrenceDay.value = ''
    },
    removeTarget() {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = []
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = []
    },
    removeItemFromTargetArray(item) {
      this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value =
        this.alertTemplateForm.field.alertConfig.groups[0].field.alertTargets.value.filter(
          (i) => i !== item,
        )
    },
    removeItemFromRecipientArray(item) {
      this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value =
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value.filter(
          (i) => i !== item,
        )
    },
    removeIdentity() {
      this.alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field.operandIdentifier.value =
        ''
      this.alertTemplateForm.field.alertGroups.groups[0].field.alertOperands.groups[0].field._operandIdentifier.value =
        {}
    },
    onConvert(val) {
      let newVal = ''
      if (val == 0) {
        newVal = 'Monday'
      } else if (val == 1) {
        newVal = 'Tuesday'
      } else if (val == 2) {
        newVal = 'Wednesday'
      } else if (val == 3) {
        newVal = 'Thursday'
      } else if (val == 4) {
        newVal = 'Friday'
      } else if (val == 5) {
        newVal = 'Saturday'
      } else if (val == 6) {
        newVal = 'Sunday'
      }
      return newVal
    },
    onNextPage() {
      this.pageNumber <= 0 ? (this.pageNumber += 1) : (this.pageNumber = this.pageNumber)
    },
    onPreviousPage() {
      this.pageNumber >= 1 ? (this.pageNumber -= 1) : (this.pageNumber = this.pageNumber)
    },
    goToTemplates() {
      this.$router.push({ name: 'CreateNew' })
    },
    async createChannel(name) {
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
    recipientTypeToggle(value) {
      if (!this.user.slackRef) {
        this.$Alert.alert({ type: 'error', message: 'Slack Not Integrated', timeout: 2000 })
        return 'USER_LEVEL'
      }
      if (value == 'USER_LEVEL') {
        return 'SLACK_CHANNEL'
      } else if (value == 'SLACK_CHANNEL') {
        this.alertTemplateForm.field.alertConfig.groups[0].field.recipients.value = []
        this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = []
        return 'USER_LEVEL'
      }
      return value
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
            directToUsers: this.directToUsers,
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
    setAlertValues(date, name) {
      this.alertTemplateForm.field.title = name
      this.alertTemplateForm.alertGroups.groups[0].fields.alertOperands.groups[0].fields.operandValue.value =
        date
      this.alertTemplateForm.alertGroups.groups[0].fields.alertOperands.groups[0].fields.operandOperator.value =
        '<='
      if (date >= 0) {
        this.alertGroups.groups[0].fields.alertOperands.groups[0].fields.field.operandOperator.value =
          '='
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
    userIds() {
      return this.users.list.map((field) => {
        return field.id
      })
    },
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
    recipientOpts() {
      if (this.userLevel == 'MANAGER') {
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
    filteredUserTargets() {
      if (this.searchQuery) {
        return this.userTargetsOpts.filter((key) => {
          return key.fullName.toLowerCase().startsWith(this.searchQuery.toLowerCase())
        })
      } else {
        return this.userTargetsOpts
      }
    },
    filteredRecipients() {
      if (this.searchText) {
        return this.recipientOpts.filter((key) => {
          return key.fullName.toLowerCase().startsWith(this.searchText.toLowerCase())
        })
      } else {
        return this.recipientOpts
      }
    },
    filteredChannels() {
      if (this.searchChannels) {
        return this.reversedChannels.filter((key) => {
          return key.name.toLowerCase().startsWith(this.searchChannels.toLowerCase())
        })
      } else {
        return this.reversedChannels
      }
    },
    reversedChannels() {
      return this.channelOpts.channels.reverse()
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
    this.alertTemplateForm.field.title.value = 'Upcoming Next Step'
    this.alertTemplateForm.field.isActive.value = true
    this.alertTemplateForm.field.alertMessages.groups[0].field.body.value =
      'Hey <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong> has an upcoming Next Step Date due this week.'
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
.load-more {
  text-align: center;
  font-size: 13px;
}
.load-more:hover {
  color: $dark-green;
  cursor: pointer;
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
  color: $panther-silver;
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
::v-deep .input-content {
  width: 12vw;
  background-color: white;
  color: $panther;
}
::v-deep .input-form__large {
  width: 12vw;
  background-color: white;
  color: $panther;
}
.invisible {
  display: none;
}
.selected__item {
  padding: 0.5rem;
  border: none;
  box-shadow: 3px 4px 7px $very-light-gray;
  border-radius: 0.3rem;
  width: 96%;
  text-align: center;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: flex-start;
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
.channels_height {
  height: 22vh;
  overflow-y: scroll;
}
.bottom__middle {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  filter: drop-shadow(8px 10px 7px black);
}
.collection__fields {
  background-color: $panther;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  flex-direction: row;
  padding: 1rem;
  border-radius: 0.5rem;
  height: 46vh;
  width: 50vw;
  overflow-x: scroll;
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
  background-color: $panther;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
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
.collection {
  background-color: $panther;
  margin-top: 1rem;
  padding: 2rem;
  border-radius: 0.5rem;
  width: 60vw;
  box-shadow: 3px 4px 7px black;
  display: flex;
  flex-direction: column;
}
.bottom {
  margin-bottom: 2rem;
  height: 24vh;
  width: 26vw;
  margin-top: 1rem;
}
.message {
  width: 20vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-bottom: 1.5rem;
}
.row {
  display: flex;
  flex-direction: row;
  font-weight: bold;
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
.column {
  display: flex;
  flex-direction: column;
  margin: 1rem;
}
.centered__ {
  display: flex;
  justify-content: center;
  align-items: center;
}
.visible {
  visibility: hidden;
}
.continue__button {
  margin: 0.2rem;
  padding: 0.35rem;
  width: 10vw;
  background-color: $panther-purple;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 2rem;
}
.back__button {
  margin: 0.2rem;
  padding: 0.35rem;
  width: 10vw;
  background-color: $panther-gold;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 2rem;
}
.disabled__continue {
  margin: 0.2rem;
  padding: 0.35rem;
  width: 10vw;
  background-color: $panther-silver;
  color: $panther;
  border: none;
  border-radius: 0.5rem;
  font-weight: bold;
  cursor: not-allowed;
  margin-top: 2rem;
}
.days__start {
  display: flex;
  flex-direction: column;
}
.alert__column {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}
.alert__row {
  display: flex;
  flex-direction: column;
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
.items_height {
  overflow-y: scroll;
  max-height: 30vh;
  width: 100%;
}
.recipients_height {
  overflow-y: scroll;
  max-height: 30vh;
  width: 80%;
}
.fields_title {
  background-color: $panther;
  margin: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  width: 100%;
}
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
  height: 100vh;
  color: $base-gray;
  margin-top: 4rem;
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
// .alerts-page__message-options-body__bindings__fields {
//   margin: 3rem 0rem;
//   width: 40rem;
// }
.green {
  color: #41b883;
}
.red {
  color: red;
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
.row_ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 2rem;
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
// ::-webkit-scrollbar {
//   background-color: $panther;
//   -webkit-appearance: none;
//   width: 4px;
//   height: 100%;
// }
// ::-webkit-scrollbar-thumb {
//   border-radius: 2px;
//   background-color: $panther-silver;
// }
</style>

