<template>
  <div class="alert-settings-modal">
    <div class="row__save">
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
      <PulseLoadingSpinnerButton
        text="save"
        @click="onSave"
        class="btn btn--primary"
        :loading="isSaving"
        :disabled="!form.isValid"
      />
    </div>
    <div class="alerts-page__settings">
      <div style="margin-right: 1rem" class="alerts-page__settings__day">
        <p>Select day:</p>
        <div style="margin-top: -1rem" v-if="weeklyOrMonthly == 'WEEKLY'">
          <FormField>
            <template v-slot:input>
              <DropDownSearch
                :items.sync="weeklyOpts"
                :itemsRef.sync="form.field._recurrenceDay.value"
                v-model="form.field.recurrenceDay.value"
                @input="form.field.recurrenceDay.validate()"
                displayKey="key"
                valueKey="value"
                nullDisplay="Days"
                searchable
                local
              />
            </template>
          </FormField>
        </div>
        <div v-else-if="weeklyOrMonthly == 'MONTHLY'">
          <FormField
            placeholder="Day of month"
            @blur="form.field.recurrenceDay.validate()"
            v-model="form.field.recurrenceDay.value"
            small
          />
        </div>
      </div>
      <div style="margin-right: 1rem" class="alerts-page__settings__target-users">
        <p>Select Users:</p>
        <FormField style="margin-top: -1rem" :errors="form.field.alertTargets.errors">
          <template v-slot:input>
            <DropDownSearch
              :items.sync="userTargetsOpts"
              :itemsRef.sync="form.field._alertTargets.value"
              v-model="form.field.alertTargets.value"
              @input="form.field.alertTargets.validate()"
              displayKey="fullName"
              valueKey="id"
              nullDisplay="Users"
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
      <div style="margin-top: 1rem" class="alerts-page__settings__recipients">
        <div class="alerts-page__settings__recipient-type">
          <div v-if="!channelName" class="row__">
            <label>Select #channel</label>
            <ToggleCheckBox
              style="margin: 0.25rem"
              @input="changeCreate"
              :value="create"
              offColor="#199e54"
              onColor="#199e54"
            />
            <label>Create #channel</label>
          </div>
          <label v-else for="channel" style="font-weight: bold"
            >Alert will send to
            <span style="color: #199e54; font-size: 1.2rem">{{ channelName }}</span>
            channel</label
          >
        </div>

        <div
          style="
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
          "
          v-if="create"
        >
          <input
            v-model="channelName"
            class="search__input"
            type="text"
            name="channel"
            id="channel"
            @input="logNewName(channelName)"
          />

          <div v-if="!channelCreated" v style="margin-top: 1.25rem">
            <button v-if="channelName" @click="createChannel(channelName)" class="purple__button">
              Create Channel
            </button>
            <button v-else class="disabled__button">Create Channel</button>
          </div>
        </div>

        <div v-else>
          <FormField>
            <template v-slot:input>
              <DropDownSearch
                :items.sync="userChannelOpts.channels"
                :itemsRef.sync="form.field._recipients.value"
                v-model="form.field.recipients.value"
                @input="form.field.recipients.validate()"
                displayKey="name"
                valueKey="id"
                nullDisplay="Channels"
                :hasNext="!!userChannelOpts.nextCursor"
                @load-more="listChannels(userChannelOpts.nextCursor)"
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

          <p
            v-if="form.field.recipients.value.length > 0"
            @click="removeTarget"
            :class="form.field.recipients.value ? 'selected__item' : 'visible'"
          >
            <img
              src="@/assets/images/remove.png"
              style="height: 1rem; margin-right: 0.25rem"
              alt=""
            />
            {{ form.field._recipients.value.name }}
          </p>
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

import ToggleCheckBox from '@thinknimble/togglecheckbox'

//Internal
import ListContainer from '@/components/ListContainer'
import FormField from '@/components/forms/FormField'
import DropDownSearch from '@/components/DropDownSearch'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
/**
 * Services
 */
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
import { AlertConfigForm, AlertConfig } from '@/services/alerts/'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertSettingsModal',
  components: {
    ListContainer,
    ToggleCheckBox,
    DropDownSearch,
    FormField,
    PulseLoadingSpinnerButton,
  },
  props: {
    form: { type: AlertConfigForm },
    resourceType: { type: String },
  },
  data() {
    return {
      userChannelOpts: new SlackListResponse(),
      create: true,
      channelName: '',
      channelCreated: false,
      searchQuery: '',
      searchText: '',
      searchChannels: '',
      users: CollectionManager.create({ ModelClass: User }),
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
      isSaving: false,
    }
  },
  async created() {
    if (this.user.slackRef) {
      await this.listUserChannels()
    }
    if (this.user.userLevel == 'MANAGER') {
      await this.users.refresh()
    }
  },
  methods: {
    async onSave() {
      this.isSaving = true
      this.form.validate()
      if (this.form.isValid) {
        try {
          const res = await AlertConfig.api.createConfig(this.form.toAPI)
          this.$Alert.alert({
            message: 'Successfully Added new settings',
            type: 'success',
            timeout: 2000,
          })
          this.createdObj = res
          this.$modal.hide('alert-settings-modal', { createdObj: this.createdObj })
          this.isSaving = false
        } finally {
          this.isSaving = false
        }
      }
      this.isSaving = false
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
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
    },
    logNewName(str) {
      let new_str = ''
      new_str = str.replace(/\s+/g, '-').toLowerCase()
      this.channelName = new_str
    },
    changeCreate() {
      this.create = !this.create
      if (this.form.field.recipientType.value !== 'SLACK_CHANNEL') {
        this.form.field.recipientType.value = 'SLACK_CHANNEL'
      }
    },
    async createChannel(name) {
      this.form.field.recipientType.value = 'SLACK_CHANNEL'
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        this.form.field._recipients.value = res.channel
        this.form.field.recipients.value = res.channel.id
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
    removeTarget() {
      this.form.field.recipients.value = []
      this.form.field._recipients.value = []
    },
    recipientTypeToggle(value) {
      if (!this.user.slackRef) {
        this.$Alert.alert({ type: 'error', message: 'Slack Not Integrated', timeout: 2000 })
        return 'USER_LEVEL'
      }
      if (value == 'USER_LEVEL') {
        return 'SLACK_CHANNEL'
      } else if (value == 'SLACK_CHANNEL') {
        this.form.field.recipients.value = []
        this.form.field._recipients.value = []
        return 'USER_LEVEL'
      }
      return value
    },
    setRecipient(obj) {
      this.form.field._recipients.value = obj
    },
    setRecipients(obj) {
      this.form.field._recipients.value.push(obj)
    },
    async onSearchUsers(v) {
      this.users.pagination = new Pagination()
      this.users.filters = {
        ...this.users.filters,
        search: v,
      }
      console.log(this.users.filters)
      await this.users.refresh()
    },
    async onUsersNextPage() {
      await this.users.addNextPage()
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
    user() {
      return this.$store.state.user
    },
    weeklyOrMonthly() {
      return this.form.field.recurrenceFrequency.value
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

.row__save {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.channels_height {
  height: 22vh;
  overflow-y: scroll;
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
  // padding: 0 0 0 1rem;
  margin-top: 1rem;
  -webkit-box-shadow: 1px 4px 7px black;
  box-shadow: 1px 4px 7px black;
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
.alert-settings-modal {
  padding: 1rem;
  overflow-y: scroll;
  height: 100%;
  max-height: 100%;
  background-color: $panther;
  color: white;
  font-family: $bold-font-family;
}
::v-deep .dropdown-search {
  margin: 1rem 0rem;
}
.alerts-page__settings {
  margin: 2rem;
  &__frequency {
    display: flex;
    align-items: center;
    &-label {
      color: $panther-silver;
      font-size: 0.75rem;
      margin: 0 0.5rem;
    }
  }
  &-remove {
    justify-self: end;
  }
}
.invisible {
  display: none;
}
.selected__item {
  padding: 0.5rem 1.2rem;
  background-color: transparent;
  border: 3px solid white;
  color: white;
  border-radius: 0.3rem;
  width: 50%;
  text-align: center;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
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
  padding: 1.25rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $panther-silver;
  color: $panther-gray;
  cursor: not-allowed;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
}
</style>
