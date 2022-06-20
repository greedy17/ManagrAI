<template>
  <div class="alerts-page">
    <div class="description">
      <div>
        <h4>Stage Advanced</h4>
        <p>Recieve alerts when deals advances to your selected stage</p>
      </div>

      <button @click="$router.push({ name: 'RealTime' })" class="back-button">
        <img class="invert" src="@/assets/images/back.svg" alt="" />
        Back to Instant Updates
      </button>
    </div>

    <div v-if="pageNumber === 0" class="alert__column">
      <template>
        <div class="forecast__collection">
          <div class="delivery__row">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select Users"
                  @input="mapIds"
                  v-model="selectedUsers"
                  :options="userList"
                  openDirection="below"
                  style="width: 18vw"
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

          <div style="margin-bottom: 2.5rem; margin-top: 0.5rem" class="delivery__row">
            <Multiselect
              :placeholder="advancedStage ? advancedStage : 'Select Stage'"
              @input="setStage($event)"
              :options="stages"
              openDirection="below"
              style="width: 18vw"
              selectLabel="Enter"
              track-by="value"
              label="label"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>

              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  {{ advancedStage ? advancedStage : 'Select Stage' }}
                </p>
              </template>
            </Multiselect>
          </div>

          <div
            style="
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: flex-start;
              margin-top: -1rem;
            "
          >
            <p>Slack Channel:</p>
            <div v-if="!channelName" class="row__">
              <label :class="!create ? 'green' : ''">Select Channel</label>
              <ToggleCheckBox
                style="margin-left: 0.5rem; margin-right: 0.5rem"
                @input="changeCreate"
                :value="create"
                offColor="#199e54"
                onColor="#199e54"
              />
              <label :class="create ? 'green' : ''">Create Channel</label>
            </div>

            <label v-else for="channel" style="font-weight: bold"
              >Alert will send to
              <span style="color: #199e54">{{ channelName }}</span>
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

              <div v-if="!channelCreated" v style="margin-top: 1rem">
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
              <FormField>
                <template v-slot:input>
                  <Multiselect
                    placeholder="Select Channel"
                    v-model="selectedChannel"
                    @input="setRecipient"
                    :options="userChannelOpts.channels"
                    openDirection="below"
                    style="width: 18vw"
                    selectLabel="Enter"
                    track-by="id"
                    label="name"
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results.</p>
                    </template>

                    <template slot="placeholder">
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        Select Channel
                      </p>
                    </template>
                    <template slot="afterList">
                      <p
                        class="multi-slot__more"
                        @click="listUserChannels(userChannelOpts.nextCursor)"
                      >
                        Load More
                      </p>
                    </template>
                  </Multiselect>
                </template>
              </FormField>
            </div>
          </div>
          <div v-if="realTimeAlertForm.isValid" class="centered__">
            <PulseLoadingSpinnerButton
              :loading="savingTemplate"
              class="purple__button bouncy"
              text="Activate alert"
              @click.stop="onSave"
            />
          </div>
        </div>
      </template>
    </div>
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

import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
//Internal
import FormField from '@/components/forms/FormField'
import { UserConfigForm } from '@/services/users/forms'

/**
 * Services
 */

import { RealTimeAlertForm, RealTime } from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager } from '@thinknimble/tn-models'
import {
  SObjectField,
  NON_FIELD_ALERT_OPTS,
  SOBJECTS_LIST,
  SObjectPicklist,
} from '@/services/salesforce'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'StageAdvanced',
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    ToggleCheckBox,
    FormField,
    PulseLoadingSpinnerButton,
  },
  data() {
    return {
      selectedUsers: null,
      selectedChannel: null,
      channelOpts: new SlackListResponse(),
      userChannelOpts: new SlackListResponse(),
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      channelCreated: false,
      create: true,
      realTimeAlertRecipient: '',
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      newChannel: {},
      channelName: '',
      OPPORTUNITY: 'Opportunity',
      operandDate: '',
      searchQuery: '',
      advancedStage: null,
      searchText: '',
      recurrenceDay: '',
      searchChannels: '',
      SOBJECTS_LIST,
      pageNumber: 0,
      configName: '',
      stages: [],
      allForms: [],
      userConfigForm: new UserConfigForm({}),
      realTimeAlertForm: new RealTimeAlertForm(),
      selectedBindings: [],
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      users: CollectionManager.create({ ModelClass: User }),
      userList: [],
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
      this.userList = this.users.list.filter((user) => user.salesforceAccountRef)
    }
    this.userConfigForm = new UserConfigForm({
      activatedManagrConfigs: this.user.activatedManagrConfigs,
    })
    try {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      await this.listPicklists({
        salesforceObject: this.Opportunity,
        picklistFor: 'StageName',
      })
    } catch (error) {
      console.log(error)
    }
    this.getStageForms()
  },
  mounted() {
    console.log(this.users)
  },
  methods: {
    mapIds() {
      let mappedIds = this.selectedUsers.map((user) => user.id)
      this.realTimeAlertForm.field.pipelines.value = mappedIds
    },
    setStage(n) {
      this.advancedStage = n.value
    },
    setRecipient() {
      this.realTimeAlertForm.field.recipients.value = this.selectedChannel.id
    },
    changeCreate() {
      this.create = !this.create
    },
    async listUserChannels(cursor = null) {
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
    },
    async createChannel(name) {
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        this.realTimeAlertForm.field.recipients.value = res.channel.id
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

    async onSave() {
      this.savingTemplate = true
      try {
        const res = await RealTime.api.createRealTimeAlert({
          ...this.realTimeAlertForm.toAPI,
          user: this.$store.state.user.id,
          config: {
            isActive: true,
            title: 'Stage Advanced',
            operator: '==',
            value: this.advancedStage,
            dataType: 'string',
          },
        })
      } catch (e) {
        this.$toast('Error saving template', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.savingTemplate = false
        this.$toast('Workflow activation successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.$router.push({ name: 'RealTime' })
      }
    },

    getStageForms() {
      // users can only create one form for the stage orderd by stage
      let forms = []
      this.stages.forEach((s) => {
        this.allForms
          .filter((f) => f.formType == this.STAGE_GATING)
          .forEach((sf) => {
            if (sf.stage == s.value) {
              forms.push(sf)
            }
          })
      })

      this.formStages = [...forms]
    },

    async listPicklists(query_params = {}) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)

        this.stages = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    userLevel() {
      return this.$store.state.user.userLevel
    },
  },
  beforeMount() {
    this.realTimeAlertForm.field.apiName.value = 'StageName'
    this.realTimeAlertForm.field.resourceType.value = 'Opportunity'
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

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
::placeholder {
  color: $very-light-gray;
  font-size: 0.75rem;
}
img {
  filter: invert(60%);
}
.title {
  font-weight: bold;
  font-size: 14px;
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
  font-weight: bold;

  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  &__more {
    background-color: $dark-green;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;
  }
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
  width: 18vw;
  text-align: center;
  margin-top: 0.5rem;
  box-shadow: 1px 1px 3px 0px $very-light-gray;
}
.purple__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 3rem;
  border-radius: 0.3rem;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  font-weight: bold;
  font-size: 12px;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 3rem;
  font-weight: bold;
  border-radius: 0.3rem;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  color: $base-gray;
  cursor: text;
  font-size: 12px;
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
.centered__ {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
}
.alert__column {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 1rem;
}
.delivery__row {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
}
.description {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-left: 1rem;
  width: 48vw;
  h4 {
    font-size: 18px;
  }
  p {
    font-size: 14px;
    margin-top: -0.5rem;
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
.invert {
  filter: invert(80%);
}
.forecast__collection {
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 0.5rem;
  width: 48vw;
  padding: 3rem 2rem;
}
.alerts-page {
  margin-top: 5rem;
  margin-left: 24vw;
  font-size: 12px;
  height: 100vh;
  color: $base-gray;
}
.green {
  color: $dark-green;
}
</style>

