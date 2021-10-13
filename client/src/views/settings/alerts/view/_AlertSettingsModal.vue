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
        <p style="color: #ff7649">Day:</p>
        <div style="margin-top: 1rem; margin-bottom: 1rem" v-if="weeklyOrMonthly == 'WEEKLY'">
          <!-- <div :key="value" v-for="(key, value) in weeklyOpts">
            <input
              :value="key.value"
              v-model="form.field.recurrenceDay.value"
              id="value"
              type="radio"
            />
            <label for="value">{{ key.key }}</label>
          </div> -->
          <FormField>
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
        </div>
        <div v-else-if="weeklyOrMonthly == 'MONTHLY'">
          <!-- <FormField
            placeholder="Day of month"
            :errors="form.field.recurrenceDay.errors"
            @blur="form.field.recurrenceDay.validate()"
            v-model="form.field.recurrenceDay.value"
            large
          /> -->
          <FormField
            placeholder="Day of month"
            @blur="form.field.recurrenceDay.validate()"
            v-model="form.field.recurrenceDay.value"
            small
          />
        </div>
      </div>
      <div style="margin-right: 1rem" class="alerts-page__settings__target-users">
        <p style="color: #ff7649">Select Pipelines:</p>

        <!-- <input
          class="search__input"
          type="text"
          v-model="searchQuery"
          placeholder="Search pipelines..."
        />

        <div :key="value" v-for="(key, value) in filteredUserTargets">
          <input
            v-model="form.field.alertTargets.value"
            :value="key.id"
            id="value"
            type="checkbox"
          />
          <label for="value">{{ key.fullName }}</label>
        </div> -->

        <FormField :errors="form.field.alertTargets.errors">
          <template v-slot:input>
            <DropDownSearch
              :items.sync="userTargetsOpts"
              :itemsRef.sync="form.field._alertTargets.value"
              v-model="form.field.alertTargets.value"
              @input="form.field.alertTargets.validate()"
              displayKey="fullName"
              valueKey="id"
              nullDisplay="Select pipelines"
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
        <p style="color: #ff7649">Recipients:</p>
        <div class="alerts-page__settings__recipient-type">
          <div
            class="row__"
            style="
              margin-bottom: 0.75rem;
              margin-top: 2rem;
              display: flex;
              align-items: center;
              justify-content: center;
            "
          >
            <label>DM users</label>
            <ToggleCheckBox
              style="margin: 0.25rem"
              @input="
                form.field.recipientType.value == 'USER_LEVEL'
                  ? (form.field.recipientType.value = recipientTypeToggle(
                      form.field.recipientType.value,
                    ))
                  : (form.field.recipientType.value = recipientTypeToggle('SLACK_CHANNEL'))
              "
              :value="form.field.recipientType.value !== 'USER_LEVEL'"
              offColor="#199e54"
              onColor="#199e54"
            />
            <label>Send to #Channel</label>
          </div>
        </div>

        <div v-if="form.field.recipientType.value == 'USER_LEVEL'">
          <!-- <input
            class="search__input"
            type="text"
            v-model="searchText"
            placeholder="Search Recipients..."
          />

          <div :key="value" v-for="(key, value) in filteredRecipients">
            <input
              type="checkbox"
              id="value"
              :value="key.id"
              v-model="form.field.recipients.value"
              @click="setRecipients(key)"
            />
            <label for="value">{{ key.fullName }}</label>
          </div> -->

          <FormField :errors="form.field.recipients.errors">
            <template v-slot:input>
              <DropDownSearch
                :items.sync="recipientOpts"
                :itemsRef.sync="form.field._recipients.value"
                v-model="form.field.recipients.value"
                @input="form.field.recipients.validate()"
                displayKey="fullName"
                valueKey="id"
                nullDisplay="Select Recipients"
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

        <div v-if="form.field.recipientType.value == 'SLACK_CHANNEL'">
          <!-- <div :key="value" v-for="(key, value) in filteredChannels">
            <input
              @click="setRecipient(key)"
              v-model="form.field.recipients.value"
              :value="key.id"
              type="radio"
              id="value"
              style="height: 1rem; margin-top: 0.5rem"
            />
            <label style="margin-bottom: 1rem" for="value">{{ key.name }}</label>
          </div> -->

          <FormField :errors="form.field.recipients.errors">
            <template v-slot:input>
              <DropDownSearch
                :items.sync="reversedChannels"
                :itemsRef.sync="form.field._recipients.value"
                v-model="form.field.recipients.value"
                @input="form.field.recipients.validate()"
                displayKey="name"
                valueKey="id"
                nullDisplay="Search Channels"
                :hasNext="!!reversedChannels.nextCursor"
                @load-more="listChannels(reversedChannels.nextCursor)"
                searchable
                local
              >
                <template v-slot:tn-dropdown-option="{ option }">
                  <!-- <img
                            v-if="option.isPrivate == true"
                            class="card-img"
                            src="@/assets/images/lockAsset.png"
                          /> -->
                  {{ option['name'] }}
                </template>
              </DropDownSearch>
            </template>
          </FormField>
        </div>

        <!-- <FormField
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
        </FormField> -->
      </div>
    </div>

    <!-- <PulseLoadingSpinnerButton
      text="save"
      @click="onSave"
      class="btn btn--primary"
      :loading="isSaving"
      :disabled="!form.isValid"
    /> -->
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
  color: #4d4e4c;
  height: 2.5rem;
  background-color: #beb5cc;
  border: 1px solid #5d5e5e;
  width: 70%;
  // padding: 0 0 0 1rem;
  margin: 1rem;
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
</style>
