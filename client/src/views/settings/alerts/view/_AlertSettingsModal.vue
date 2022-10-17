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
          offColor="#41b883"
          onColor="#41b883"
        />
        <label class="alerts-page__settings__frequency-label">Monthly</label>
      </div>
    </div>
    <div class="alerts-page__settings">
      <div style="margin-bottom: 16px" class="alerts-page__settings__day">
        <p>Select day:</p>
        <div style="margin-top: -1.75rem" v-if="weeklyOrMonthly == 'WEEKLY'">
          <FormField>
            <template v-slot:input>
              <Multiselect
                placeholder="Select Days"
                @input="setDay($event)"
                v-model="selectedDay"
                :options="weeklyOpts"
                openDirection="below"
                style="width: 16vw; margin-top: 1rem"
                selectLabel="Enter"
                track-by="value"
                label="key"
                :multiple="true"
                :closeOnSelect="false"
              >
                <template slot="noResult">
                  <p>No results.</p>
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
        <div v-else-if="weeklyOrMonthly == 'MONTHLY'">
          <FormField
            placeholder="Day of month"
            @blur="form.field.recurrenceDay.validate()"
            v-model="form.field.recurrenceDay.value"
            small
          />
        </div>
      </div>
      <div style="margin-bottom: 16px" class="alerts-page__settings__target-users">
        <p>Select Users:</p>
        <FormField style="margin-top: -1.75rem" :errors="form.field.alertTargets.errors">
          <template v-slot:input>
            <Multiselect
              placeholder="Select Users"
              @input="mapIds"
              v-model="selectedUsers"
              :options="userTargetsOpts"
              openDirection="below"
              style="width: 16vw; margin-top: 1rem"
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
                  <img src="@/assets/images/search.svg" alt="" />
                  Select Users
                </p>
              </template>
            </Multiselect>
          </template>
        </FormField>
      </div>
      <div style="margin-top: 2rem" class="alerts-page__settings__recipients">
        <div class="alerts-page__settings__recipient-type">
          <div v-if="!channelName" class="row__">
            <label>Select channel</label>
            <ToggleCheckBox
              style="margin: 0.25rem"
              @input="changeCreate"
              :value="create"
              offColor="#41b883"
              onColor="#41b883"
            />
            <label>Create channel</label>
          </div>
          <label v-else for="channel" style="font-weight: bold"
            >Alert will send to
            <span style="color: #41b883; font-size: 14px">{{ channelName }}</span>
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
            placeholder="Channel name"
            class="search__input"
            type="text"
            name="channel"
            id="channel"
            @input="logNewName(channelName)"
          />

          <div v-if="!channelCreated">
            <button v-if="channelName" @click="createChannel(channelName)" class="purple__button">
              Create Channel
            </button>
            <button v-else class="disabled__button">Create Channel</button>
          </div>
        </div>

        <div v-else>
          <FormField>
            <template v-slot:input>
              <Multiselect
                placeholder="Select Channel"
                v-model="selectedChannel"
                @input="setRecipient($event)"
                :options="userChannelOpts.channels"
                openDirection="below"
                style="width: 16vw; margin-top: 0.5rem"
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
                    Select Channel
                  </p>
                </template>
              </Multiselect>
            </template></FormField
          >
        </div>
      </div>
      <div style="margin-top: -24px" class="save-button">
        <PulseLoadingSpinnerButton
          text="save"
          @click="onSave"
          class="primary-button"
          :loading="isSaving"
          :disabled="!form.isValid"
        />
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
import FormField from '@/components/forms/FormField'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
/**
 * Services
 */
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
import { AlertConfigForm, AlertConfig } from '@/services/alerts/'
import { CollectionManager } from '@thinknimble/tn-models'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertSettingsModal',
  components: {
    ToggleCheckBox,
    FormField,
    PulseLoadingSpinnerButton,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    form: { type: AlertConfigForm },
    resourceType: { type: String },
  },
  data() {
    return {
      dropdownLoading: false,
      userChannelOpts: new SlackListResponse(),
      create: true,
      channelName: '',
      channelCreated: false,
      searchQuery: '',
      searchText: '',
      searchChannels: '',
      selectedDay: null,
      selectedUsers: null,
      selectedChannel: null,
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
  beforeMount() {
    this.form.field.recurrenceDay.value = 0
    this.form.field.recurrenceDays.value = [0]
  },
  methods: {
    async onSave() {
      this.isSaving = true
      this.form.validate()
      if (this.form.isValid) {
        try {
          const res = await AlertConfig.api.createConfig(this.form.toAPI)
          this.$toast('Successfully added new delivery settings', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
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
    setDay(n) {
      this.form.field.recurrenceDay.value = 0
      let days = []
      n.forEach((day) => days.push(day.value))
      let newDays = [...new Set(days)]
      this.form.field.recurrenceDays.value = newDays
    },
    mapIds() {
      let mappedIds = this.selectedUsers.map((user) => user.id)
      this.form.field.alertTargets.value = mappedIds
    },
    setRecipient(n) {
      this.form.field.recipients.value = n.id
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
          console.log(res.error)
        }
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
  align-items: center;
  justify-content: center;
  height: 4rem;
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
.invert {
  filter: invert(80%);
}
::placeholder {
  color: $very-light-gray;
  font-size: 0.75rem;
}
h2 {
  font-weight: 400;
}
.search__input {
  font-family: Lato-Regular, sans-serif;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  font-size: 14px;
  border-radius: 4px;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: #4d4e4c;
  height: 2.5rem;
  background-color: white;
  border: none;
  width: 16vw;
  margin: 0.5rem 0rem;
  box-shadow: 1px 1px 3px 0px $very-light-gray;
}
.primary-button {
  padding: 0.4rem 1.5rem;
  box-shadow: none;
  font-weight: 400;
}
.primary-button:disabled {
  background-color: $soft-gray;
  color: $gray;
}
.alert-settings-modal {
  overflow-y: scroll;
  height: 100%;
  max-height: 100%;
  background-color: $white;
  color: $base-gray;
  font-size: 14px;
  padding: 16px 0px 0px 16px;
  font-family: Lato-Regular, sans-serif;
  &__header {
    outline: 1px solid #e8e8e8;
    font-weight: 400;
    padding: 0.5rem 1rem;
    margin-bottom: 0.5rem;
  }
}
.alerts-page__settings {
  color: $base-gray;
  margin: 0.5rem 1rem;
  &__frequency {
    display: flex;
    align-items: center;
    &-label {
      margin: 0 0.5rem;
    }
  }
}
.save-button {
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  width: 100%;
  padding: 0rem 1rem 0rem 0rem;
  height: 170px;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  label {
    font-weight: 400;
  }
}
.purple__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem 1rem;
  border-radius: 0.3rem;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-size: 1.02rem;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  border-radius: 0.3rem;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  color: $gray;
  cursor: not-allowed;
  font-size: 14px;
}
</style>
