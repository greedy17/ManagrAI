<template>
  <div class="alerts-template-list">
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
          <h4>
            {{ activeWorkflow.title }}
            <!-- <span> {{ activeWorkflow.sobjectInstances.length }}</span> -->
          </h4>

          <button
            style="margin-left: 16px"
            class="green_button"
            @click="goToPipeline(activeWorkflow.id, activeWorkflow.resourceType)"
          >
            Open in Pipeline
          </button>
        </div>

        <div v-if="activeWorkflow.sobjectInstances && activeWorkflow.sobjectInstances.length">
          <section
            class="workflow__modal__body"
            :key="opp.id"
            v-for="opp in activeWorkflow.sobjectInstances"
          >
            <div class="title" @click="test(activeWorkflow)">
              <div
                v-if="
                  activeWorkflow.resourceType === 'Opportunity' ||
                  activeWorkflow.resourceType === 'Deal'
                "
              >
                <h4>
                  {{ userCRM === 'SALESFORCE' ? opp.Name : opp.dealname }}
                </h4>
                <p>
                  Stage:
                  {{ userCRM === 'SALESFORCE' ? opp.StageName : hsStages[opp.dealstage].label }}
                </p>
                <p>
                  Close Date:
                  {{ userCRM === 'SALESFORCE' ? opp.CloseDate : opp.closedate.split('T')[0] }}
                </p>
              </div>
              <div
                v-else-if="
                  activeWorkflow.resourceType === 'Account' ||
                  activeWorkflow.resourceType === 'Company'
                "
              >
                <h4>
                  {{ userCRM === 'SALESFORCE' ? opp.Name : opp.name }}
                </h4>
              </div>
              <div
                v-else-if="
                  activeWorkflow.resourceType === 'Contact' ||
                  activeWorkflow.resourceType === 'Lead'
                "
              >
                <h4>
                  {{ userCRM === 'SALESFORCE' ? opp.Name : opp.firstname + ' ' + opp.lastname }}
                </h4>
                <p>
                  Email:
                  {{ userCRM === 'SALESFORCE' ? opp.Email : opp.email }}
                </p>
              </div>
            </div>
          </section>
        </div>
        <div v-else>
          <section class="workflow__modal__body">
            <div class="title">
              <div>
                <h4>No Results</h4>
              </div>
            </div>
          </section>
        </div>
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
          <h4>Meetings</h4>

          <button style="margin-left: 16px" class="green_button" @click="goToMeetings">
            Open in Meetings
          </button>
        </div>
        <div class="workflow__modal__body" v-for="meeting in meetings" :key="meeting.id">
          <div class="title">
            <div>
              <h4>{{ meeting.meeting_ref.topic ? meeting.meeting_ref.topic : 'Meeting' }}</h4>
              <p>
                Participants:
                {{ meeting.meeting_ref.participants && meething.meeting_ref.participants.length }}
              </p>
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

    <Modal v-if="commandModalOpen" dimmed>
      <div class="command-modal">
        <header>
          <h2>
            Managr meets you where you are
            <img
              src="@/assets/images/slackLogo.png"
              style="margin-left: 8px"
              height="16px"
              alt=""
            />
          </h2>
          <p>You can access Managr from anywhere in Slack using commands.</p>
        </header>
        <section>
          <div>
            <h5><span>Commands</span></h5>
            <p>Use '/' to start commands in any conversation</p>
          </div>
          <div>
            <h5><span>/managr-actions</span></h5>
            <p>Launch an action through Managr</p>
          </div>
          <div>
            <h5>
              <span>/managr-update</span>
              {{
                userCRM === 'SALESFORCE'
                  ? 'opportunity , account, contact, lead'
                  : 'deal, account, contact'
              }}
            </h5>
            <p>Updates a resource</p>
          </div>
          <div>
            <h5>
              <span>/managr-create</span>
              {{
                userCRM === 'SALESFORCE'
                  ? 'opportunity , account, contact, lead'
                  : 'deal, account, contact'
              }}
            </h5>
            <p>Creates a new resource</p>
          </div>
        </section>
        <footer>
          <button @click="closeCommandModal()">Got it</button>
        </footer>
      </div>
    </Modal>

    <template v-if="!templates.refreshing && !isOnboarding">
      <!-- <transition name="fade">
      </transition> -->

      <div style="margin-top: 5.5rem" v-if="editing" class="alert_cards">
        <!-- <div v-if="!zoomChannel" class="added-collection yellow-shadow">
          <div class="added-collection__header">
            <div id="gray">
              <img src="@/assets/images/logo.png" height="28px" alt="" />
            </div>

            <div>
              <p class="gray">Meeting Template</p>
              <h4>Log Meeting</h4>
            </div>
          </div>

          <div class="added-collection__body">
            <p class="gray">Recieve actionable alerts as soon as your meetings end.</p>
            <p style="height: 32px"></p>
          </div>
          <div class="added-collection__footer">
            <div class="row__">
              <button @click="goToLogZoom" class="white_button">Activate</button>
            </div>
          </div>
        </div> -->
        <div v-if="!zoomChannel" class="card">
          <div class="card__header lg-bg" style="padding-left: 32px; padding-right: 32px">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>
          <div class="card__body">
            <h4>Log Meeting</h4>
            <small class="card-text">Recieve actionable alerts as soon as your meetings end.</small>
            <div class="card__body__between">
              <p></p>
              <button @click="goToLogZoom" class="white_button">Activate</button>
            </div>
          </div>
        </div>
        <!-- <div v-if="!hasRecapChannel && userLevel !== 'REP'" class="added-collection yellow-shadow">
          <div class="added-collection__header">
            <div id="gray">
              <img src="@/assets/images/logo.png" height="28px" alt="" />
            </div>

            <div>
              <p class="gray">Meeting Template</p>
              <h4>Meeting Recaps</h4>
            </div>
          </div>

          <div class="added-collection__body">
            <p class="gray">Recieve alerts that give you insight on your teams meetings.</p>
            <p style="height: 32px"></p>
          </div>
          <div class="added-collection__footer">
            <button @click="goToRecap" class="white_button">Activate</button>
          </div>
        </div> -->

        <div :key="alert.id" v-for="alert in leaderTemplatesFirst" class="card">
          <div class="card__header lb-bg" style="padding-left: 32px; padding-right: 32px">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>

          <div class="card__body">
            <div>
              <h4>
                {{ alert.title }}
              </h4>
              <div v-if="user.id !== alert.user" class="small-text">Created by Leadership</div>
            </div>
            <p class="card-text" @click="test(alert)">
              Results: {{ alert && alert.sobjectInstances ? alert.sobjectInstances.length : 0 }}
            </p>

            <div class="card__body__between">
              <div class="row__">
                <div class="tooltip">
                  <button
                    style="margin-right: 8px"
                    :disabled="clicked.includes(alert.id) || !hasSlackIntegration"
                    @click.stop="
                      onRunAlertTemplateNow(alert.id, user.id !== alert.user ? true : false)
                    "
                    class="img-border"
                  >
                    <img src="@/assets/images/slackLogo.png" height="14px" alt="" />
                  </button>
                  <span class="tooltiptext">Send to Slack</span>
                </div>

                <button
                  v-if="userCRM"
                  @click="openList(alert)"
                  style="margin-right: 8px"
                  class="img-border"
                >
                  <img
                    src="@/assets/images/listed.svg"
                    style="filter: invert(40%)"
                    height="14px"
                    alt=""
                  />
                </button>
                <button
                  class="img-border"
                  @click="editWorkflow(alert)"
                  v-if="user.id === alert.user"
                >
                  <img
                    src="@/assets/images/edit.svg"
                    style="filter: invert(40%)"
                    height="14px"
                    alt=""
                  />
                </button>
              </div>
              <div v-if="hasSlackIntegration">
                <ToggleCheckBox
                  @input="onToggleAlert(alert.id, alert.isActive)"
                  v-model="alert.isActive"
                  offColor="#aaaaaa"
                  :onColor="'#41b883'"
                />
                <!-- templatedAlerts.includes(alert.title) ? '#41b883' : '#7fc4fb' -->
              </div>
            </div>
          </div>
        </div>

        <div v-if="zoomChannel" class="card">
          <div class="card__header lb-bg" style="padding-left: 32px; padding-right: 32px">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>
          <div class="card__body">
            <h4>Log Meeting</h4>
            <p class="card-text">Meetings: {{ meetings.length }}</p>

            <div class="card__body__between">
              <button v-if="userCRM === 'SALESFORCE'" @click="openMeetings" class="img-border">
                <img
                  src="@/assets/images/listed.svg"
                  style="filter: invert(40%)"
                  height="14px"
                  alt=""
                />
              </button>
              <div v-else style="width: 5px; height: 5px"></div>

              <button @click="goToLogZoom" class="white_button">Change Channel</button>
              <!-- <small>{{ currentZoomChannel }}</small> -->
            </div>
          </div>
        </div>

        <div v-if="hasRecapChannel && userLevel !== 'REP'" class="card">
          <div class="card__header lb-bg" style="padding-left: 32px; padding-right: 32px">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>
          <div class="card__body">
            <h4>Meeting Recaps</h4>
            <p class="card-text">Meetings: {{ meetings.length }}</p>

            <div class="card__body__between">
              <button v-if="userCRM === 'SALESFORCE'" @click="openMeetings" class="img-border">
                <img
                  src="@/assets/images/listed.svg"
                  style="filter: invert(40%)"
                  height="14px"
                  alt=""
                />
              </button>
              <div v-else style="width: 5px; height: 5px"></div>

              <button @click="goToRecap" class="white_button">Change Channel</button>
              <!-- <small> {{ currentRecapChannel }}</small> -->
            </div>
          </div>
        </div>

        <div
          v-for="config in filteredConfigs"
          :key="config.id"
          class="card"
          v-show="!templateTitles.includes(config.title)"
        >
          <div class="card__header lg-bg" style="padding-left: 32px; padding-right: 32px">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>

          <div class="card__body">
            <h4>{{ config.title }}</h4>
            <small style="margin-top: 8px" class="card-text">{{ config.subtitle }}</small>
            <div
              v-if="config.title !== 'Empty Field'"
              class="card__body__between"
              style="margin-top: 8px"
            >
              <p></p>
              <button @click="goToWorkflow(config.title)" class="white_button">Activate</button>
            </div>

            <div v-else class="card__body__between" style="margin-top: 8px">
              <p></p>
              <button
                v-if="isPaid && userLevel == 'MANAGER'"
                @click="goToWorkflow(config.title)"
                class="white_button"
              >
                Activate
              </button>
              <div v-else class="tooltip-left">
                <img
                  class="shimmer"
                  style="filter: invert(40%)"
                  src="@/assets/images/lock.svg"
                  height="16px"
                  alt=""
                />
                <small class="tooltiptext-left">Upgrade your plan</small>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!hasRecapChannel && userLevel !== 'REP'" class="card">
          <div class="card__header lg-bg" style="padding-left: 32px; padding-right: 32px">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>

          <div class="card__body">
            <h4>Meeting Recaps</h4>
            <small class="card-text"
              >Recieve alerts that give you insight on your teams meetings.</small
            >
            <div class="card__body__between">
              <p></p>
              <button @click="goToRecap" class="white_button">Activate</button>
            </div>
          </div>
        </div>
      </div>

      <div class="alert_cards" v-if="editing"></div>
    </template>

    <div v-else-if="isOnboarding">
      <Onboarder @refresh-workflows="refreshWorkflows" />
    </div>

    <div class="center-loader" v-else>
      <Loader style="margin-top: 44vh" loaderText="Gathering your workflows" />
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import ToggleCheckBox from '@thinknimble/togglecheckbox'

/**
 * Services
 *
 */
import { CollectionManager } from '@thinknimble/tn-models'
import SlackOAuth from '@/services/slack'
import Onboarder from '@/views/settings/Onboarder'
// import { UserConfigForm } from '@/services/users/forms'
import User from '@/services/users'
import { ObjectField } from '@/services/crm'

import AlertTemplate from '@/services/alerts/'
import allConfigs from '../configs'

export default {
  name: 'AlertsTemplateList',
  components: {
    ToggleCheckBox,
    Onboarder,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  data() {
    return {
      // templatedAlerts: [
      //   'Close Date Passed',
      //   '90 Day Pipeline',
      //   'Upcoming Next Step',
      //   'Requird Field Empty',
      //   'Large Opportunities',
      //   'Team Pipeline',
      //   'Deal Review',
      //   'Close Date Approaching',
      // ],
      commandModalOpen: false,
      meetingListOpen: false,
      activeWorkflow: null,
      allConfigs,
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
      templateTitles: [],
      workflowListOpen: false,
      deleteId: '',
      deleteTitle: '',
      editing: true,
      // userConfigForm: new UserConfigForm({}),
      currentZoomChannel: '',
      currentRecapChannel: '',
      clicked: [],
      hsStages: {},
    }
  },
  async created() {
    this.templates.refresh()
    // if (this.zoomChannel) {
    //   this.getZoomChannel()
    // }
    if (this.hasRecapChannel) {
      this.getRecapChannel()
    }
    if (this.userCRM === 'HUBSPOT') {
      this.getHSStages()
    }
  },
  beforeUpdate() {
    if (this.templates.list.length) {
      this.getActiveTemplateTitles()
    }
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    closeCommandModal() {
      this.templates.refresh()
      setTimeout(() => {
        this.commandModalOpen = false
      }, 300)
    },
    refreshWorkflows() {
      this.templates.refresh()
      setTimeout(() => {
        this.$toast("You're all set! Onboarding complete", {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }, 500)

      setTimeout(() => {
        this.commandModalOpen = true
      }, 2500)
    },
    editWorkflow(alert) {
      this.$emit('edit-workflow', alert)
    },
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
    async getHSStages() {
      const res = await ObjectField.api.listFields({
        crmObject: this.DEAL,
        search: 'Deal Stage',
      })
      let dealStages = []
      for (let i = 0; i < res.length; i++) {
        if (res[i].apiName === 'dealstage') {
          dealStages = res[i]
          break
        }
      }
      let dealStage = {}
      if (dealStages.optionsRef.length) {
        for (let i = 0; i < dealStages.optionsRef.length; i++) {
          for (let j = 0; j < dealStages.optionsRef[i].length; j++) {
            const stage = dealStages.optionsRef[i][j]
            dealStage[stage.id] = stage
          }
        }
      }
      this.hsStages = dealStage ? dealStage : {}
    },
    openList(alert) {
      this.activeWorkflow = alert
      this.workflowListOpen = true
    },
    openMeetings() {
      this.meetingListOpen = true
    },
    goToMeetings() {
      this.$router.push({ name: 'Meetings' })
    },
    goToPipeline(id, title) {
      this.$router.push({ name: 'Pipelines', params: { id: id, title: title } })
    },
    goToWorkflow(name) {
      let newName = name.replace(/\s/g, '')
      if (newName === 'LargeDeals') {
        newName = 'LargeOpportunities'
      }
      this.$router.push({ name: newName })
    },
    getActiveTemplateTitles() {
      this.templateTitles = this.templates.list.map((template) => template.title)
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
    goToLogZoom() {
      this.$router.push({ name: 'LogZoom' })
    },
    goToRecap() {
      this.$router.push({ name: 'ZoomRecap' })
    },
    async onToggleAlert(id, value) {
      try {
        await AlertTemplate.api.updateAlertTemplate(id, { is_active: value })
        // await this.templates.refresh()

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
    async onRunAlertTemplateNow(id, from_workflow) {
      try {
        await AlertTemplate.api.runAlertTemplateNow(id, from_workflow)
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
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
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
    filteredConfigs() {
      let filtered = []
      for (let key in this.allConfigs) {
        if (this.allConfigs[key].crm === this.userCRM) {
          filtered.push(this.allConfigs[key])
        }
      }
      return filtered
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    userLevel() {
      return this.$store.state.user.userLevel
    },
    meetings() {
      return this.$store.state.meetings
    },
    isOnboarding() {
      return this.$store.state.user.onboarding
    },
    leaderTemplatesFirst() {
      const originalList = this.templates.list
      const leaders = []
      const own = []
      if (originalList) {
        for (let i = 0; i < originalList.length; i++) {
          this.user.id !== originalList[i].user
            ? leaders.push(originalList[i])
            : own.push(originalList[i])
        }
      }
      return [...leaders, ...own]
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

.shimmer {
  display: inline-block;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  max-width: 200px;
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
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
.tooltip-left {
  position: relative;
  display: inline-block;
}
/* Tooltip text */
.tooltip-left .tooltiptext-left {
  visibility: hidden;
  width: 160px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  opacity: 0.7;

  /* Position the tooltip text - */
  position: absolute;
  z-index: 1;
  top: 1px;
  right: 105%;
}
/* Show the tooltip text when you mouse over the tooltip container */
.tooltip-left:hover .tooltiptext-left {
  visibility: visible;
}
.img-border {
  @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  margin-right: 8px;
}
.card {
  letter-spacing: 0.75px;
  background-color: $white;
  padding: 16px 24px;
  border: 1px solid #e8e8e8;
  margin-right: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: row;
  width: 425px;
  min-height: 144px;
  transition: all 0.25s;

  &__header {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px 16px;
    border-radius: 6px;

    img {
      padding: 0;
      margin: 0;
    }
  }

  &__body {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: space-evenly;
    margin-left: 12px;
    width: 100%;
    h4 {
      margin: 0;
      padding: 0;
    }
    p {
      font-size: 12px;
    }

    &__between {
      display: flex;
      align-items: center;
      justify-content: space-between;

      width: 260px;
    }
  }
}
.card-text {
  font-size: 11px;
  color: $light-gray-blue;
}
.lb-bg {
  // background: rgb(242, 242, 242);
  // background: rgb(242, 242, 242);
  // background: linear-gradient(
  //   90deg,
  //   rgba(242, 242, 242, 1) 0%,
  //   rgba(238, 255, 247, 1) 0%,
  //   rgba(208, 251, 232, 1) 100%
  // );
  background-color: $off-white;
  border: 1px solid $off-white;
}
.lg-bg {
  background-color: $off-white;
  border: 1px solid $off-white;
  img {
    filter: grayscale(99%);
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
h2 {
  font-size: 1.4rem;
}
button:disabled {
  background-color: $soft-gray;
  cursor: not-allowed;
  img {
    filter: grayscale(98%);
  }
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 12px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 100px;
  top: 100%;
  left: 50%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
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
  width: 30vw;
  letter-spacing: 0.75px;
  &__header {
    padding: 0px 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 400;
    img {
      margin-top: -1rem;
      cursor: pointer;
    }
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0px 8px 8px 0px;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 8px 0px;
  }
}
.delete {
  // @include white-button-danger();
  background-color: white !important;
  border: 1px solid $coral !important;
  border-radius: 0.25rem;
  color: $coral !important;
  cursor: pointer;
  padding: 8px 16px;
  margin-right: 8px;
}
.no__button {
  background-color: white;
  border: 1px solid $soft-gray;
  border-radius: 0.25rem;
  color: $base-gray;
  cursor: pointer;
  padding: 8px 16px;
  margin-right: 8px;
}
.alerts-template-list {
  // margin: 16px 0px;
  height: 100vh;
  padding-left: 24px;
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.alert_cards {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
  flex-wrap: wrap;
  width: 100%;
  border-radius: 6px;
  margin-top: 16px;
  margin-left: -8px;
}

// .added-collection:hover {
//   box-shadow: 1px 2px 2px $very-light-gray;
//   transform: scale(1.015);
// }

.green-shadow {
  box-shadow: 1px 2px 6px $very-light-gray;
  border: 0.5px solid $soft-gray;
}
// .yellow-shadow {
//   border: 1px solid $soft-gray;
// }
// .gray {
//   color: $light-gray-blue !important;
// }
// .added-collection {
//   background-color: white;
//   border-radius: 9px;
//   // border: 1px solid #e8e8e8;
//   width: 20.5vw;
//   height: 175px;
//   margin-bottom: 1rem;
//   margin-right: 1rem;
//   padding-bottom: 0;
//   transition: all 0.25s;
//   font-size: 12px;
//   &__header {
//     max-height: 50px;
//     display: flex;
//     flex-direction: row;
//     align-items: center;
//     margin-top: 8px;
//     span {
//       margin-left: auto;
//       margin-right: 16px;
//       font-size: 14px;
//       color: $light-gray-blue !important;
//     }
//     div {
//       display: flex;
//       flex-direction: column;
//       align-items: flex-start;
//       justify-content: flex-start;
//       margin-left: 8px;
//       p,
//       h4 {
//         margin: 0;
//         padding: 0;
//       }
//       p {
//         font-size: 10px;
//         color: $light-gray-blue;
//       }
//     }
//   }
//   &__body {
//     display: flex;
//     align-items: flex-start;
//     margin-left: 16px;
//     padding-right: 8px;
//     margin-top: 8px;
//     font-size: 12px;
//     letter-spacing: 0.75px;
//   }
//   &__footer {
//     display: flex;
//     flex-direction: row;
//     align-items: center;
//     justify-content: space-between;
//     height: 50px;
//     margin-left: 16px;
//   }
// }
a {
  text-decoration: none;
  color: white;
  cursor: pointer;
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
.green_button {
  @include primary-button();
  padding: 8px 12px;
  font-size: 12px;
  text-align: center;
}
.white_button {
  @include white-button();
  border: 1px solid $soft-gray;
  padding: 8px 12px;
  text-align: center;
}
.center-loader {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 70vh;
  width: 100%;
}
.small-text {
  font-size: 10px;
  color: $dark-green;
  margin-top: 4px;
}
.command-modal {
  background-color: $white;
  overflow-y: scroll;
  overflow-x: hidden;
  width: 32vw;
  height: 70vh;
  align-items: center;
  border-radius: 4px;
  padding: 24px;
  position: relative;

  header {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    width: 100%;
    border-bottom: 1px solid $soft-gray;
    h2 {
      text-align: left;
      font-weight: normal;
      letter-spacing: 0.3px;
      padding: 0;
      margin: 0;
    }
    p {
      letter-spacing: 0.3px;
      font-size: 13px;
      padding: 0;
      color: $light-gray-blue;
    }
  }

  section {
    width: 100%;
    padding-top: 8px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;

    div {
      margin: 0;
      border-bottom: 1px solid $soft-gray;
      width: 100%;
      padding: 12px 0px 0px 4px;
      h5 {
        margin: 0;
        font-size: 15px;
        font-weight: normal;
        span {
          font-weight: bold;
          letter-spacing: 0.3px;
          color: black;
        }
      }
      p {
        font-size: 14px;
        padding: 0;
        color: $light-gray-blue;
      }
    }
  }

  &__section {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 16px;
    button {
      background-color: $grape;
      color: white;
      height: 30px;
      width: auto;
      padding: 0 8px;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 6px;

      span {
        color: $mid-gray !important;
        padding: 0 2px;
      }
    }
  }

  footer {
    width: 100%;
    position: absolute;
    bottom: 0;
    padding: 16px 32px;
    background-color: white;

    display: flex;
    flex-direction: row;
    align-items: flex-end;
    justify-content: flex-end;

    button {
      background-color: $dark-green;
      padding: 11px;
      font-size: 13px;
      border-radius: 4px;
      border: none;
      margin: 0px 16px;
      color: $white;
      cursor: pointer;
      transition: all 0.25s;
    }

    button:hover {
      box-shadow: 0 6px 6px rgba(0, 0, 0, 0.1);
      transform: scale(1.025);
    }
  }
}

.absolute-img {
  position: absolute;
  right: 76px;
  bottom: 16px;
  box-shadow: none !important;
}
</style>
