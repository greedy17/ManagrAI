<template>
  <div class="alerts-template-list">
    <Modal v-if="deleteOpen" dimmed>
      <div class="delete_modal">
        <div class="delete_modal__header">
          <h2>Delete Workflow</h2>
          <img @click="deleteOpen = !deleteOpen" src="@/assets/images/close.svg" alt="" />
        </div>

        <div class="delete_modal__body">
          <p>This action cannot be undone, are you sure ?</p>
        </div>

        <div class="delete_modal__footer">
          <button class="no__button" @click="deleteClose">No</button>
          <button class="yes__button" @click.stop="onDeleteTemplate(deleteId)">Yes</button>
        </div>
      </div>
    </Modal>

    <Modal
      v-if="workflowListOpen"
      @close-modal="
        () => {
          $emit('cancel'), (workflowListOpen = false)
        }
      "
    >
      <div class="workflow__modal">
        <div class="workflow__modal__header">
          <p>
            {{ activeWorkflow.title }}
            <!-- <span> {{ activeWorkflow.sobjectInstances.length }}</span> -->
          </p>

          <button style="margin-left: 16px" class="green_button">Open in Pipeline</button>
        </div>

        <section
          class="workflow__modal__body"
          :key="i"
          v-for="(opp, i) in activeWorkflow.sobjectInstances"
        >
          <div class="title">
            <div>
              <h4>
                {{ opp.Name }}
              </h4>
              <p>Stage: {{ opp.StageName }}</p>
              <p>Close Date: {{ opp.CloseDate }}</p>
            </div>
          </div>
          <!-- <section class="button-section">
            <div>
              <button class="green-button">Update Record</button>
              <img src="@/assets/images/note.svg" height="14px" alt="" />
              <img src="@/assets/images/pipeline.svg" height="14px" alt="" />
            </div>
          </section> -->
        </section>
      </div>
    </Modal>

    <Modal
      v-if="meetingListOpen"
      @close-modal="
        () => {
          $emit('cancel'), (meetingListOpen = false)
        }
      "
    >
      <div class="workflow__modal">
        <div class="workflow__modal__header">
          <p>Meetings</p>

          <button class="green_button">Open in Meetings</button>
        </div>
        <div class="workflow__modal__body" v-for="(meeting, i) in meetings" :key="i">
          <div class="title">
            <div>
              <h4>{{ meeting.meeting_ref.topic ? meeting.meeting_ref.topic : 'Meeting' }}</h4>
              <p>Participants: {{ meeting.meeting_ref.participants.length }}</p>
              <p>
                {{
                  meeting.meeting_ref.start_time
                    ? formatDateTimeToTime(meeting.meeting_ref.start_time)
                    : ''
                }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <template v-if="!templates.refreshing">
      <transition name="fade">
        <div v-if="!editing" class="edit__modal">
          <AlertsEditPanel :alert="currentAlert" />
          <div class="edit__modal__button">
            <button @click="closeEdit">Done</button>
          </div>
        </div>
      </transition>

      <div v-if="editing" class="alert_cards">
        <div
          v-for="(config, i) in allConfigs"
          :key="i"
          class="added-collection gray-shadow"
          v-show="!templateTitles.includes(config.title)"
        >
          <div class="added-collection__header">
            <div id="gray">
              <img src="@/assets/images/logo.png" height="28px" alt="" />
            </div>

            <div>
              <p class="gray">Managr Template</p>
              <h3>{{ config.title }}</h3>
            </div>
          </div>

          <div class="added-collection__body">
            <p class="gray">{{ config.subtitle }}</p>
          </div>
          <div class="added-collection__footer">
            <button @click="goToWorkflow(config.title)" class="green_button pulse">Activate</button>
          </div>
        </div>
        <div v-if="!zoomChannel" class="added-collection yellow-shadow">
          <div class="added-collection__header">
            <div id="gray">
              <img src="@/assets/images/logo.png" height="28px" alt="" />
            </div>

            <div>
              <p class="gray">Meeting Template</p>
              <h3>Log Meeting</h3>
            </div>
          </div>

          <div class="added-collection__body">
            <p class="gray">Recieve actionable alerts as soon as your meetings end.</p>
            <p style="height: 32px"></p>
          </div>
          <div class="added-collection__footer">
            <div class="row__">
              <button @click="goToLogZoom" class="green_button pulse">Activate</button>
            </div>
          </div>
        </div>
        <div v-if="!hasRecapChannel && userLevel !== 'REP'" class="added-collection yellow-shadow">
          <div class="added-collection__header">
            <div id="gray">
              <img src="@/assets/images/logo.png" height="28px" alt="" />
            </div>

            <div>
              <p class="gray">Meeting Template</p>
              <h3>Meeting Recaps</h3>
            </div>
          </div>

          <div class="added-collection__body">
            <p class="gray">Recieve alerts that give you insight on your teams meetings.</p>
            <p style="height: 32px"></p>
          </div>
          <div class="added-collection__footer">
            <button @click="goToRecap" class="green_button pulse">Activate</button>
          </div>
        </div>

        <div :key="i" v-for="(alert, i) in templates.list" class="added-collection green-shadow">
          <div class="added-collection__header" :data-key="alert.id">
            <div class="green-bg" :class="!templatedAlerts.includes(alert.title) ? 'blue-bg' : ''">
              <img src="@/assets/images/logo.png" height="28px" alt="" />
            </div>

            <div>
              <p class="green" v-if="templatedAlerts.includes(alert.title)">Managr Template</p>
              <p class="blue" v-else>Custom Workflow</p>
              <h3>
                {{ alert.title }}
              </h3>
            </div>
            <span>{{ alert.sobjectInstances.length }}</span>
          </div>
          <div class="added-collection__body">
            <p>Recieve notifications when important close dates have passed</p>
          </div>
          <div class="added-collection__footer">
            <div class="row__">
              <button
                style="margin-right: 8px"
                :disabled="clicked.includes(alert.id) || !hasSlackIntegration"
                @click.stop="onRunAlertTemplateNow(alert.id)"
                class="white_button"
              >
                <img src="@/assets/images/slackLogo.png" height="14px" alt="" />
              </button>
              <button @click="openList(alert)" style="margin-right: 8px" class="white_button">
                <img
                  src="@/assets/images/listed.svg"
                  style="filter: invert(40%)"
                  height="14px"
                  alt=""
                />
              </button>
              <button class="white_button" @click="makeAlertCurrent(alert)">
                <img
                  src="@/assets/images/build.svg"
                  style="filter: invert(40%)"
                  height="14px"
                  alt=""
                />
              </button>
            </div>

            <div v-if="hasSlackIntegration" class="row__">
              <ToggleCheckBox
                @input="onToggleAlert(alert.id, alert.isActive)"
                v-model="alert.isActive"
                offColor="#aaaaaa"
                :onColor="templatedAlerts.includes(alert.title) ? '#41b883' : '#7fc4fb'"
              />
            </div>
          </div>

          <template slot="panel-content">
            <div>
              <AlertsEditPanel :alert="alert" />
            </div>
          </template>
        </div>

        <div v-if="zoomChannel" class="added-collection green-shadow">
          <div class="added-collection__header">
            <div id="yellow">
              <img src="@/assets/images/logo.png" height="28px" alt="" />
            </div>

            <div>
              <p class="yellow">Meetings</p>
              <h3>Log Meeting</h3>
            </div>

            <span>{{ meetings.length }}</span>
          </div>

          <div class="added-collection__body">
            <p>{{ currentZoomChannel }}</p>
            <p style="height: 32px"></p>
          </div>
          <div class="added-collection__footer">
            <div class="row__">
              <button @click="goToLogZoom" class="yellow_button_full">Change Channel</button>
              <button @click="openMeetings" style="margin-left: 8px" class="white_button">
                <img
                  src="@/assets/images/listed.svg"
                  style="filter: invert(40%)"
                  height="14px"
                  alt=""
                />
              </button>
            </div>
          </div>
        </div>

        <div v-if="hasRecapChannel && userLevel !== 'REP'" class="added-collection green-shadow">
          <div class="added-collection__header">
            <div id="yellow">
              <img src="@/assets/images/logo.png" height="28px" alt="" />
            </div>

            <div>
              <p class="yellow">Meetings</p>
              <h3>Meeting Recaps</h3>
            </div>

            <span>{{ meetings.length }}</span>
          </div>

          <div class="added-collection__body">
            <p>
              {{ currentRecapChannel }}
            </p>
            <p style="height: 32px"></p>
          </div>
          <div class="added-collection__footer">
            <div class="row__">
              <button @click="goToRecap" class="yellow_button_full">Change Channel</button>
              <button @click="openMeetings" style="margin-left: 8px" class="white_button">
                <img
                  src="@/assets/images/listed.svg"
                  style="filter: invert(40%)"
                  height="14px"
                  alt=""
                />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="alert_cards" v-if="editing"></div>
    </template>

    <div class="center-loader" v-else>
      <Loader loaderText="Gathering your workflows" />
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
import AlertsEditPanel from '@/views/settings/alerts/view/_AlertsEditPanel'
/**
 * Services
 *
 */
import { CollectionManager } from '@thinknimble/tn-models'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
// import { UserConfigForm } from '@/services/users/forms'
import User from '@/services/users'

import AlertTemplate from '@/services/alerts/'
import allConfigs from '../configs'

export default {
  name: 'AlertsTemplateList',
  components: {
    ToggleCheckBox,
    AlertsEditPanel,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  data() {
    return {
      templatedAlerts: [
        'Close Date Passed',
        '90 Day Pipeline',
        'Upcoming Next Step',
        'Requird Field Empty',
        'Large Opportunities',
        'Deal Review',
        'Close Date Approaching',
      ],
      meetingListOpen: false,
      activeWorkflow: null,
      allConfigs,
      userChannelOpts: new SlackListResponse(),
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
      users: CollectionManager.create({ ModelClass: User }),
      templateTitles: [],
      deleteOpen: false,
      workflowListOpen: false,
      deleteId: '',
      deleteTitle: '',
      currentAlert: {},
      editing: true,
      isHiding: false,
      // userConfigForm: new UserConfigForm({}),
      configName: '',
      configArray: [],
      currentZoomChannel: '',
      currentRecapChannel: '',
      clicked: [],
      pageLoaded: false,
    }
  },
  async created() {
    this.templates.refresh()
    if (this.zoomChannel) {
      this.getZoomChannel()
    }
    if (this.hasRecapChannel) {
      this.getRecapChannel()
    }
    await this.listUserChannels()
  },
  beforeUpdate() {
    this.getActiveTemplateTitles()
  },
  methods: {
    formatDateTimeToTime(input) {
      let preDate = new Date(input)
      let newTime = preDate.toLocaleTimeString('en-US')
      let amPm = newTime.split(' ')[1]
      let hour = newTime.split(':')[0]
      let noSeconds = newTime.replace(':', ' ')
      let noAmPm = newTime.replace(amPm, '')
      let noAmPmSeconds = noAmPm.replace(':', ' ')

      if (parseInt(hour) < 10) {
        newTime = '0' + newTime
        noAmPm = '0' + noAmPm
        noSeconds = '0' + noSeconds
        noAmPmSeconds = '0' + noAmPmSeconds
      }
      noSeconds = noSeconds.replace(' ', ':')
      noSeconds = noSeconds.split(':')
      noSeconds = noSeconds[0] + ':' + noSeconds[1] + amPm
      return noSeconds
    },
    openList(alert) {
      this.activeWorkflow = alert
      this.workflowListOpen = true
    },
    openMeetings() {
      this.meetingListOpen = true
      console.log(this.meetings)
    },
    goToWorkflow(name) {
      let newName = name.replace(/\s/g, '')
      this.$router.push({ name: newName })
    },
    getActiveTemplateTitles() {
      this.templateTitles = this.templates.list.map((template) => template.title)
      console.log(this.templates.list)
    },
    async getRecapChannel() {
      const res = await SlackOAuth.api.channelDetails(this.hasRecapChannel)
      this.currentRecapChannel = res.channel.name
    },
    async getZoomChannel() {
      const res = await SlackOAuth.api.channelDetails(this.zoomChannel)
      this.currentZoomChannel = res.channel.name
    },
    deletedTitle(id) {
      let newList = []
      newList = this.templates.list.filter((val) => val.id === id)
      this.deleteTitle = newList[0].title
    },
    handleUpdate() {
      // this.loading = true
      User.api
        .update(this.user.id)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
    },
    alertsCount(num) {
      if (this.zoomChannel && !this.hasRecapChannel) {
        return num + 1
      } else if (this.hasRecapChannel && !this.zoomChannel) {
        return num + 1
      } else if (this.hasRecapChannel && this.zoomChannel) {
        return num + 2
      } else {
        return num
      }
    },
    goToLogZoom() {
      this.$router.push({ name: 'LogZoom' })
    },
    goToRecap() {
      this.$router.push({ name: 'ZoomRecap' })
    },
    goToConnect() {
      this.$router.push({ name: 'Integrations' })
    },
    makeAlertCurrent(val) {
      this.currentAlert = val
      this.editing = !this.editing
    },
    deleteClosed(val) {
      this.deleteOpen === false ? (this.deleteOpen = true) : (this.deleteOpen = false)
      this.deleteId = val
    },
    deleteClose() {
      this.deleteOpen === false ? (this.deleteOpen = true) : (this.deleteOpen = false)
    },
    closeEdit() {
      this.editing = !this.editing
    },
    async listUserChannels(cursor = null) {
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
    },
    async onDeleteTemplate(id) {
      this.deletedTitle(id)
      try {
        await AlertTemplate.api.deleteAlertTemplate(id)
        await this.templates.refresh()
        this.handleUpdate()

        this.deleteOpen = !this.deleteOpen
        this.$toast('Workflow removed', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch {
        this.$toast('Error removing workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async onToggleAlert(id, value) {
      try {
        await AlertTemplate.api.updateAlertTemplate(id, { is_active: value })
        await this.templates.refresh()

        this.$toast(`Alert is now ${value ? 'active' : 'inactive'}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch {
        this.$toast('Error toggling workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async onRunAlertTemplateNow(id) {
      try {
        await AlertTemplate.api.runAlertTemplateNow(id)
        this.$toast('Workflow initiated', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.clicked.push(id)
      } catch {
        this.$toast('Error removing workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    hasRecapChannel() {
      return this.$store.state.user.slackAccount
        ? this.$store.state.user.slackAccount.recapChannel
        : null
    },
    zoomChannel() {
      return this.$store.state.user.slackAccount
        ? this.$store.state.user.slackAccount.zoomChannel
        : null
    },
    userLevel() {
      return this.$store.state.user.userLevel
    },
    meetings() {
      return this.$store.state.meetings
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

@keyframes dotFlashing {
  0% {
    background-color: $dark-green;
  }
  50%,
  100% {
    background-color: $lighter-green;
  }
}

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
@keyframes pulseYellow {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 $yellow;
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
.yellow_pulse {
  box-shadow: 0 0 0 0 $yellow;
  transform: scale(1);
  animation: pulseYellow 1.25s infinite;
}

#yellow {
  padding: 4px 8px;
  margin-left: 16px;
  margin-top: 4px;
  border-radius: 6px;
  background-color: $light-yellow;
  img {
    filter: brightness(0%) invert(83%) sepia(28%) saturate(7222%) hue-rotate(6deg) brightness(103%)
      contrast(104%);
  }
}
#gray {
  padding: 4px 8px;
  margin-left: 16px;
  margin-top: 4px;
  border-radius: 6px;
  background-color: $soft-gray;
  img {
    filter: brightness(0%) invert(63%) sepia(13%) saturate(553%) hue-rotate(200deg) brightness(95%)
      contrast(86%);
  }
}

.yellow {
  color: $yellow !important;
  background-color: white;
}
.red {
  background-color: $light-red;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
  color: $coral;
  padding: 4px 6px;
}
h2 {
  font-size: 1.4rem;
}
button:disabled {
  background-color: $very-light-gray;
  cursor: not-allowed;
}
.titles {
  color: $base-gray;
  font-weight: bold;
}
.workflow__modal {
  background-color: $white;
  color: $base-gray;
  border-radius: 6px;
  min-height: 25vh;
  max-height: 70vh;
  padding: 0 1rem;
  overflow: scroll;
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    background-color: white;
    z-index: 2;
    top: 0;
    p {
      font-size: 16px;
    }
  }

  &__body {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    margin-bottom: 16px;
    width: 100%;

    div {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
      h4 {
        font-weight: 900;
        font-size: 13px;
        margin: 0;
        padding: 0;
        min-width: 32vw;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;

        span {
          // background-color: $off-white;
          color: $light-gray-blue;
          padding: 4px 8px;
          border-radius: 4px;
          margin-left: 12px;
          font-size: 13px;
          opacity: 0.9;
        }
      }

      p {
        font-weight: bold;
        font-size: 13px;
        color: $light-gray-blue;
        padding: 0;
        margin: 0;
        margin-top: 4px;
      }
    }
  }
}
.delete_modal {
  background-color: $white;
  color: $base-gray;
  border-radius: 0.3rem;
  width: 40vw;
  padding: 1rem;
  &__header {
    height: 3rem;
    padding: 1rem 0rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 400;
    border-bottom: 1px solid $soft-gray;
    img {
      height: 1rem;
      margin-top: -1rem;
      cursor: pointer;
    }
  }
  &__body {
    height: 4rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  &__footer {
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
.edit__modal {
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  color: $base-gray;
  width: 84vw;
  height: 74vh;
  overflow: scroll;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
  padding: none;

  &__button {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    padding: 0rem 2rem 1rem 0rem;
    width: 100%;

    button {
      background-color: $dark-green;
      border: none;
      border-radius: 0.25rem;
      color: white;
      cursor: pointer;
      padding: 0.5rem 2rem;
    }
  }
}

.no__button {
  background-color: $soft-gray;
  outline: 1px solid $soft-gray;
  border: none;
  font-size: 16px;
  border-radius: 0.3rem;
  cursor: pointer;
  padding: 0.4rem 2rem;
  margin-right: 0.5rem;
  color: $base-gray;
}
.yes__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 2rem;
  border-radius: 0.3rem;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $dark-green;
  outline: 1px solid $dark-green;
  cursor: pointer;
  font-size: 16px;
}
.alerts-template-list {
  height: 88vh;
  overflow: scroll;
  margin: 16px 8px;
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-left: 24px;
}

.alert_cards {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
  flex-wrap: wrap;
  width: 100%;
  border-radius: 6px;
}

// .added-collection:hover {
//   box-shadow: 1px 2px 2px $very-light-gray;
//   transform: scale(1.015);
// }

.green-shadow {
  box-shadow: 1px 2px 6px $very-light-gray;
  border: 0.5px solid $soft-gray;
}
.yellow-shadow {
  border: 1px solid $soft-gray;
}
.gray-shadow {
  // box-shadow: 2px 2px 6px $very-light-gray;
  border: 1px solid $soft-gray;
}
.gray {
  color: $light-gray-blue !important;
}
.added-collection {
  background-color: white;
  border-radius: 9px;
  // border: 1px solid #e8e8e8;
  width: 20.5vw;
  height: 175px;
  margin-bottom: 1rem;
  margin-right: 1rem;
  padding-bottom: 0;
  transition: all 0.25s;
  font-size: 12px;
  &__header {
    max-height: 50px;
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-top: 8px;
    span {
      margin-left: auto;
      margin-right: 16px;
      font-size: 14px;
      color: $light-gray-blue !important;
    }
    div {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-start;
      margin-left: 8px;
      p,
      h3 {
        margin: 0;
        padding: 0;
      }
      p {
        font-size: 10px;
        color: $light-gray-blue;
      }
    }
  }
  &__body {
    display: flex;
    align-items: flex-start;
    margin-left: 16px;
    padding-right: 8px;
    margin-top: 8px;
    font-size: 12px;
    letter-spacing: 0.75px;
  }
  &__footer {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    height: 50px;
    margin-left: 16px;
  }
}
a {
  text-decoration: none;
  color: white;
  cursor: pointer;
}
.green-bg {
  padding: 4px 8px;
  margin-left: 16px;
  margin-top: 4px;
  border-radius: 6px;
  background-color: $white-green;
}
.blue-bg {
  padding: 4px 8px;
  margin-left: 16px;
  margin-top: 4px;
  border-radius: 6px;
  background-color: $very-light-blue;

  img {
    filter: brightness(0%) invert(85%) sepia(36%) saturate(7492%) hue-rotate(188deg)
      brightness(113%) contrast(97%);
  }
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin: 0 0.5rem 0 0;
  color: $base-gray;
  font-weight: bold;
}
.img-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
  border-radius: 0.2rem;
  cursor: pointer;
  padding: 0.15rem 0.3rem;
}
.row__two {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  width: 100%;
  img {
    height: 0.8rem;
    cursor: pointer;
    filter: invert(20%);
  }
}
.invert {
  filter: invert(20%);
}
.green_button:disabled {
  background-color: $soft-gray;
  color: $gray;
}
.green_button {
  color: white;
  background-color: $dark-green;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  border: none;
  cursor: pointer;
  text-align: center;
}
.yellow_button {
  color: $yellow;
  opacity: 0.85;
  background-color: white;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  border: 1px solid $yellow;
  cursor: pointer;
  text-align: center;
}
.yellow_button_full {
  color: white;
  opacity: 0.85;
  background-color: $yellow;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  border: 1px solid $yellow;
  cursor: pointer;
  text-align: center;
}
.white_button {
  color: $base-gray;
  background-color: white;
  border-radius: 6px;
  border: 1px solid $soft-gray;
  box-shadow: 1px 1px 1px $very-light-gray;
  padding: 6px 8px;
  font-size: 12px;

  cursor: pointer;
  text-align: center;
}
.gray_button {
  color: white;
  background-color: $light-gray-blue;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  border: none;
  cursor: pointer;
  text-align: center;
}
.green {
  color: $dark-green !important;
}
.blue {
  color: rgb(118, 191, 252) !important;
}
.center__ {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 82vw;
}
.center-loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  width: 100%;
}
.loading-title {
  display: none;
}
.link {
  color: $dark-green;
  border-bottom: 1px solid $dark-green;
  cursor: pointer;
}
</style>
