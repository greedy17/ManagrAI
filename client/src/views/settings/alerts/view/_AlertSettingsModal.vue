<template>
  <div class="alert-settings-modal">
    <div class="alerts-page__settings">
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
      <div class="alerts-page__settings__day">
        <FormField
          v-if="form.field.recurrenceFrequency.value == 'MONTHLY'"
          placeholder="Day of month"
          :errors="form.field.recurrenceDay.errors"
          @blur="form.field.recurrenceDay.validate()"
          v-model="form.field.recurrenceDay.value"
          small
        />
        <FormField
          v-else-if="form.field.recurrenceFrequency.value == 'WEEKLY'"
          :errors="form.field.recurrenceDay.errors"
        >
          <template v-slot:input>
            <DropDownSearch
              :items.sync="weeklyOpts"
              :itemsRef.sync="form.field._recurrenceDay.value"
              v-model="form.field.recurrenceDay.value"
              @input="form.field.recurrenceDay.validate()"
              displayKey="key"
              valueKey="value"
              nullDisplay="Select"
              searchable
              local
            />
          </template>
        </FormField>
      </div>
      <div class="alerts-page__settings__target-users">
        <FormField
          :errors="form.field.alertTargets.errors"
          label="select one/multiple users/groups to include in the search"
        >
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
              local
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
          v-if="form.field._recipients.value && form.field.recipientType.value == 'SLACK_CHANNEL'"
          class="muted--link--important"
        >
          Please make sure @managr has been added to
          <em>{{ form.field._recipients.value.name }}</em> channel
        </span>
        <FormField
          v-if="form.field.recipientType.value == 'USER_LEVEL'"
          :errors="form.field.recipients.errors"
          :label="
            form.field.recipientType.value == 'USER_LEVEL'
              ? 'select one or multiple user groups'
              : ''
          "
        >
          <template v-slot:input>
            <DropDownSearch
              :items.sync="recipientOpts"
              :itemsRef.sync="form.field._recipients.value"
              v-model="form.field.recipients.value"
              @input="form.field.recipients.validate()"
              displayKey="key"
              valueKey="value"
              nullDisplay="Select user groups"
              searchable
              local
              multi
              medium
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
            >
              <template v-slot:tn-dropdown-option="{ option }">
                <img
                  v-if="option.isPrivate == true"
                  class="card-img"
                  style="width:1rem;height:1rem;margin-right:0.2rem;"
                  src="@/assets/images/lockAsset.png"
                />
                {{ option['name'] }}
              </template>
            </DropDownSearch>
          </template>
        </FormField>
      </div>
      <div class="alerts-page__settings__recipient-type">
        <span
          @click="
            form.field.recipientType.value = recipientTypeToggle(form.field.recipientType.value)
          "
          class="muted--link"
          v-if="form.field.recipientType.value == 'USER_LEVEL'"
          >Send to a channel instead ?</span
        >

        <span
          @click="
            form.field.recipientType.value = recipientTypeToggle(form.field.recipientType.value)
          "
          class="muted--link"
          v-else
        >
          Send to a group of users (DM) instead ?
        </span>
      </div>
    </div>
    <PulseLoadingSpinnerButton
      text="save"
      @click="onSave"
      class="btn btn--primary"
      :loading="isSaving"
    />
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
      channelOpts: new SlackListResponse(),
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
      await this.listChannels()
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
        return 'USER_LEVEL'
      }
      return value
    },
    async onSearchUsers(v) {
      this.users.pagination = new Pagination()
      this.users.filters = {
        ...this.users.filters,
        search: v,
      }
      await this.fields.refresh()
    },
    async onUsersNextPage() {
      await this.users.addNextPage()
    },
  },
  computed: {
    userTargetsOpts() {
      if (this.user.userLevel == 'MANAGER') {
        return [
          ...this.alertTargetOpts.map(opt => {
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
        return this.alertRecipientOpts
      } else {
        return [{ key: 'Myself', value: 'SELF' }]
      }
    },
    user() {
      return this.$store.state.user
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
  padding: 0.5rem;
  height: 100%;
  overflow-y: scroll;
  max-height: 100%;
}
::v-deep .dropdown-search {
  margin: 1rem 0rem;
}
</style>
