<template>
  <div class="alerts-page">
    <div class="alerts-header">
      <div>
        <h3>{{ config.title }}</h3>
        <p style="margin-top: -0.5rem; font-size: 14px; color: #9b9b9b">
          {{ config.subtitle }}
        </p>
      </div>

      <button @click="$router.push({ name: 'CreateNew' })" class="back-button">
        <img class="invert" src="@/assets/images/back.svg" alt="" />
        Back to workflows
      </button>
    </div>
    <div style="margin-top: 1rem" class="alert__column container">
      <div
        class="forecast__collection"
        :key="i"
        v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
      >
        <div v-if="selectField">
          <div
            class="delivery__row"
            :key="index"
            v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups"
          >
            <div v-if="largeOpps">
              <span style="margin-bottom: 0.5rem">Select your "Amount" Field</span>
              <div>
                <div class="alert-group-row__operands">
                  <div
                    :key="i"
                    v-for="(alertOperand, i) in alertGroup.field.alertOperands.groups"
                    class="alert-group-row__operands__row rows"
                  >
                    <div :class="i > 0 ? 'visible' : ''">
                      <div>
                        <div>
                          <FormField>
                            <template v-slot:input>
                              <Multiselect
                                placeholder="Select Field"
                                v-model="largeOpp"
                                :options="objectFields.list"
                                openDirection="below"
                                style="min-width: 13vw"
                                selectLabel="Enter"
                                track-by="apiName"
                                label="referenceDisplayLabel"
                              >
                                <template slot="noResult">
                                  <p class="multi-slot">No results. Try loading more</p>
                                </template>
                                <template slot="afterList">
                                  <p class="multi-slot__more" @click="objectFieldNextPage">
                                    Load More
                                    <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                                  </p>
                                </template>
                                <template slot="placeholder">
                                  <p class="slot-icon">
                                    <img src="@/assets/images/search.svg" alt="" />
                                    Select Field
                                  </p>
                                </template>
                              </Multiselect>
                            </template>
                          </FormField>
                        </div>

                        <div class="alert-operand-row__value">
                          <span style="margin-bottom: 0.5rem">"Amount" is greater than:</span>
                          <template>
                            <div>
                              <FormField
                                :errors="alertOperand.field.operandValue.errors"
                                v-model="largeOppValue"
                                :inputType="
                                  getInputType(alertOperand.field._operandIdentifier.value)
                                "
                                large
                                bordered
                                placeholder="Enter a value"
                              />
                            </div>
                          </template>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else>
              <span>Select your Field</span>
              <Multiselect
                placeholder="Select Field"
                v-model="identity"
                :options="objectFields.list"
                openDirection="below"
                style="min-width: 13vw; margin-top: 0.75rem"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="objectFieldNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                  </p>
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
        <div v-else class="delivery__row" :errors="form.field.recurrenceDay.errors">
          <div style="margin-bottom: 0.5rem" class="row__">
            <label :class="config.newConfigs[0].recurrenceFrequency == 'WEEKLY' ? 'green' : ''"
              >Weekly</label
            >
            <ToggleCheckBox
              @input="
                config.newConfigs[0].recurrenceFrequency == 'WEEKLY'
                  ? (config.newConfigs[0].recurrenceFrequency = 'MONTHLY')
                  : (config.newConfigs[0].recurrenceFrequency = 'WEEKLY')
              "
              :value="config.newConfigs[0].recurrenceFrequency !== 'WEEKLY'"
              offColor="#41b883"
              onColor="#41b883"
              style="margin-left: 0.25rem; margin-right: 0.25rem"
            />
            <label :class="config.newConfigs[0].recurrenceFrequency == 'MONTHLY' ? 'green' : ''"
              >Monthly</label
            >
          </div>
          <div v-if="config.newConfigs[0].recurrenceFrequency == 'WEEKLY'">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select Day"
                  @input="setDay($event)"
                  v-model="selectedDays"
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
                      Select Days
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
          <FormField
            id="delivery"
            v-if="config.newConfigs[0].recurrenceFrequency == 'MONTHLY'"
            placeholder="Day of month"
            v-model="config.newConfigs[0].recurrenceDay"
            small
          />
        </div>
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
                :closeOnSelect="false"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
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
        <div
          style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
          "
        >
          <div v-if="!channelName" class="row__">
            <label :class="!create ? 'green' : ''">Select #channel</label>
            <ToggleCheckBox
              style="margin-left: 0.25rem; margin-right: 0.25rem"
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
                class="purple__button bouncy"
              >
                Create Channel
              </button>
              <button v-else class="disabled__button">Create Channel</button>
            </div>
          </div>
          <div style="margin-top: 0.5rem" v-else>
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
                  <p class="multi-slot__more" @click="listUserChannels(userChannelOpts.nextCursor)">
                    Load More
                    <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Channels
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
      <div v-if="!hasSlack" class="overlay">
        <p class="text">
          <!-- <img src="@/assets/images/slackLogo.png" height="10px" class="margin-right-s" alt="" /> -->
          <span class="link" @click="goToConnect"> Connect Slack</span>
          in order to recieve notifications.
        </p>
      </div>
    </div>

    <div v-if="hasSlack" class="bottom_locked margin-top">
      <PulseLoadingSpinnerButton
        :loading="savingTemplate"
        :class="!verifySubmit() || savingTemplate ? 'disabled__button' : 'purple__button bouncy'"
        text="Activate alert"
        @click.stop="onSave"
        :disabled="!verifySubmit() || savingTemplate"
      />
    </div>

    <div class="bottom_locked margin-top" v-else>
      <button @click="noSlackSave" class="purple__button bouncy">Activate without Slack</button>
    </div>
  </div>
</template>

<script>
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import FormField from '@/components/forms/FormField'
import { UserConfigForm } from '@/services/users/forms'
import AlertTemplate, { AlertTemplateForm } from '@/services/alerts/'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjectField } from '@/services/salesforce'
import { INPUT_TYPE_MAP } from '@/services/salesforce/models'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'PopularWorkflows',
  props: ['selectField', 'largeOpps', 'config'],
  components: {
    ToggleCheckBox,
    FormField,
    PulseLoadingSpinnerButton,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      objectFields: CollectionManager.create({
        ModelClass: SObjectField,
        pagination: { size: 200 },
        filters: { forAlerts: true, filterable: true, page: 1 },
      }),
      dropdownLoading: null,
      selectedUsers: [],
      selectedDays: null,
      selectedChannel: null,
      userChannelOpts: new SlackListResponse(),
      create: false,
      channelCreated: false,
      savingTemplate: false,
      channelName: '',
      identity: '',
      largeOpp: null,
      largeOppValue: '',
      setDaysBool: false,
      largeOppsBool: false,
      selectFieldBool: false,
      selectUsersBool: false,
      directToUsers: true,
      userConfigForm: new UserConfigForm({}),
      alertTemplateForm: new AlertTemplateForm(),
      fields: CollectionManager.create({ ModelClass: SObjectField }),
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
      await this.listUserChannels()
    }
    if (this.user.userLevel == 'MANAGER') {
      await this.users.refresh()
    }
    this.userConfigForm = new UserConfigForm({
      activatedManagrConfigs: this.user.activatedManagrConfigs,
    })
    this.objectFields.filters = {
      ...this.objectFields.filters,
      salesforceObject: this.resourceType,
    }
    await this.objectFields.refresh()
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
    resourceType: {
      async handler(val) {
        this.objectFields.filters = {
          ...this.objectFields.filters,
          forAlerts: true,
          filterable: true,
          salesforceObject: val,
        }
        this.objectFields.refresh()
      },
    },
    largeOpp: function () {
      if (this.largeOpp) {
        this.config.newGroups[0].newOperands[0].operandIdentifier = this.largeOpp.apiName
        this.config.newGroups[0].newOperands[0].dataType = this.largeOpp.dataType
        this.selectFieldBool = true
      } else {
        this.config.newGroups[0].newOperands[0].operandIdentifier = ''
        this.selectFieldBool = false
      }
    },
    identity: function () {
      if (this.identity) {
        this.config.newGroups[0].newOperands[0].operandIdentifier = this.identity.apiName
        this.selectFieldBool = true
      } else {
        this.config.newGroups[0].newOperands[0].operandIdentifier = ''
        this.selectFieldBool = false
      }
    },
    largeOppValue: function () {
      if (this.largeOppValue) {
        this.config.newGroups[0].newOperands[0].operandValue = this.largeOppValue
        this.largeOppsBool = true
      } else {
        this.config.newGroups[0].newOperands[0].operandValue = ''
        this.largeOppsBool = false
      }
    },
    directToUsers: 'setDefaultChannel',
  },
  methods: {
    goToConnect() {
      this.$router.push({ name: 'Integrations' })
    },
    test() {
      console.log(this.config)
    },
    setDefaultChannel() {
      this.directToUsers
        ? (this.config.newConfigs[0].recipients = 'default')
        : (this.config.newConfigs[0].recipients = null)
    },
    verifySubmit() {
      if (this.largeOpps) {
        return (
          this.config.newGroups[0].newOperands[0].operandIdentifier &&
          this.config.newGroups[0].newOperands[0].operandValue &&
          this.config.newConfigs[0].alertTargets.length &&
          this.selectUsersBool &&
          this.selectFieldBool &&
          this.largeOppsBool
        )
      } else {
        return (
          (this.config.newConfigs[0].recurrenceDays.length ||
            this.config.newGroups[0].newOperands[0].operandIdentifier) &&
          this.config.newConfigs[0].alertTargets.length &&
          this.selectUsersBool &&
          (this.setDaysBool || this.selectFieldBool)
        )
      }
    },
    getInputType(type) {
      if (type && INPUT_TYPE_MAP[type.dataType]) {
        return INPUT_TYPE_MAP[type.dataType]
      }
      return 'text'
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
    async objectFieldNextPage() {
      await this.objectFields.addNextPage()
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
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value = res.channel
        this.config.newConfigs[0].recipients = res.channel.id
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
    setRecipient() {
      this.alertTemplateForm.field.alertConfig.groups[0].field._recipients.value =
        this.selectedChannel
      this.config.newConfigs[0].recipients = this.selectedChannel.id
    },
    setDay(n) {
      this.config.newConfigs[0].recurrenceDay = 0
      let days = []
      n.forEach((day) => days.push(day.value))
      let newDays = [...new Set(days)]
      this.config.newConfigs[0].recurrenceDays = newDays
      this.setDaysBool = true
    },
    mapIds() {
      let mappedIds = this.selectedUsers.map((user) => user.id)
      this.config.newConfigs[0].alertTargets = mappedIds
      this.selectUsersBool = true
    },
    async noSlackSave() {
      this.savingTemplate = true
      try {
        console.log(this.config)
        const res = await AlertTemplate.api.createAlertTemplate({
          ...this.config,
          user: this.$store.state.user.id,
          directToUsers: true,
        })
        console.log(res)
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
    },
    async onSave() {
      this.savingTemplate = true
      const newConfigs = this.config.newConfigs[0]
      const operandIden = this.config.newGroups[0].newOperands[0].operandIdentifier
      let largeOpsCheck = true
      if (this.largeOpps) {
        largeOpsCheck = false
        if (this.largeOppsBool) {
          largeOpsCheck = true
        }
      }
      if (
        (newConfigs.recurrenceDays.length || operandIden) &&
        newConfigs.alertTargets.length &&
        this.selectUsersBool &&
        largeOpsCheck &&
        (this.setDaysBool || this.selectFieldBool)
      ) {
        try {
          const res = await AlertTemplate.api.createAlertTemplate({
            ...this.config,
            user: this.$store.state.user.id,
            directToUsers: this.directToUsers,
          })
          console.log(res)
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
  },

  computed: {
    userLevel() {
      return this.$store.state.user.userLevel
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
    hasSlack() {
      return !!this.$store.state.user.slackRef
    },
    user() {
      return this.$store.state.user
    },
    selectedResourceType: {
      get() {
        return this.config.resourceType
      },
      set(val) {
        this.config.resourceType = val
      },
    },
  },
  mounted() {
    this.setDefaultChannel()
  },
  beforeMount() {},
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

::v-deep .input-content {
  width: 13vw;
  border: 1px solid #e8e8e8 !important;
  border-radius: 0.3rem;
  background-color: white;
  box-shadow: none !important;
}
::v-deep .input-form {
  width: 13vw;
}
::v-deep .input-form__active {
  border: none;
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
.alerts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
  padding: 0vw 12vw;
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
.bouncy {
  animation: bounce 0.2s infinite alternate;
}

::placeholder {
  color: $very-light-gray;
  font-size: 0.75rem;
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
  margin-top: 1rem;
  width: 75%;
  text-align: center;
  box-shadow: 1px 1px 3px 0px $very-light-gray;
}
input[type='text']:focus {
  outline: none;
}
.purple__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 0.3rem;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  min-width: 10rem;
  font-size: 14px;
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
}
input {
  cursor: pointer;
}
.visible {
  visibility: hidden;
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
  margin-bottom: 0.5rem;
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
  background-color: $white;
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  width: 75vw;
  padding: 2rem;
  margin-bottom: 1rem;
}
img {
  filter: invert(60%);
}
.invert {
  filter: invert(80%);
}
.alerts-page {
  height: 100vh;
  color: $base-gray;
  margin-top: 4rem;
}
.green {
  color: $dark-green;
}
.spacer {
  height: 20vh;
}
.overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  // left: 0;
  // right: 0;
  height: 100%;
  width: 80%;
  padding-left: 10vw;
  padding-right: 10vw;
  opacity: 0;
  transition: 0.5s ease;
  background-color: $dark-green;
  border-radius: 5px;
}
.container {
  position: relative;
}
.container:hover .overlay {
  opacity: 0.85;
}
.text {
  color: white;
  font-size: 16px;
  position: absolute;
  top: 50%;
  left: 50%;
  -webkit-transform: translate(-50%, -50%);
  -ms-transform: translate(-50%, -50%);
  transform: translate(-50%, -50%);
  text-align: center;
}
.margin-right-s {
  margin-right: 0.5rem;
}
.link {
  border-bottom: 1px solid white;
  cursor: pointer;
}
.margin-top {
  margin-top: 3rem;
}
</style>
