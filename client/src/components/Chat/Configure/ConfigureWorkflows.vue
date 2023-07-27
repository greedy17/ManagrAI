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
          </h4>
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
      <div class="workflow__modal" style="min-width: 20vw">
        <div class="workflow__modal__header">
          <h4>Meetings</h4>
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
            How to use chatbot 💬
            <img
              src="@/assets/images/slackLogo.png"
              style="margin-left: 6px"
              height="18px"
              alt=""
            />
          </h2>
          <p>Use conversational AI to update CRM and take actions.</p>
        </header>
        <section>
          <div>
            <h5><span>1. Run a command in Slack</span></h5>
            <p>Type '/' into any Slack message box to initiate a command</p>
          </div>
          <div>
            <h5><span>2. Select 1 of 2 chatbot commands</span></h5>
            <p>
              Search for "Managr-update" to update the CRM. Use "Managr-actions" to get real-time
              insights
            </p>
          </div>
          <div style="border-bottom: none; padding-top: 1rem">
            <h5>
              🤖 ☁️
              <span>{{
                `Using Managr-update: make sure to include ${
                  userCRM === 'SALESFORCE' ? 'Opportunity + Opportunity Name.' : 'Deal + Deal Name.'
                }`
              }}</span>
            </h5>
            <p style="padding-left: 2.4rem">
              Ex: Push close date for Opportunity Pied Piper 2 weeks.
            </p>
          </div>
          <div style="padding-top: 1rem">
            <h5>
              🤖 🦾
              <span>Using Managr-actions: select from the dropdown.</span>
            </h5>
            <p style="padding-left: 2.4rem">
              Get a deal summary, run a deal review, or schedule a meeting (coming soon!)
            </p>
          </div>
          <!-- <div>
            <img
              style="border: 1px solid #eeeeee; border-radius: 8px"
              src="@/assets/images/chatbot.png"
              height="300px"
              alt=""
            />
          </div> -->
        </section>
        <footer
          style="
            display: flex;
            flex-direction: row;
            align-items: flex-end;
            justify-content: flex-end;
          "
        >
          <!-- <small class="gray-blue"
            >For best results, avoid using symbols, colons, quotes and dollar signs.</small
          > -->
          <button @click="closeCommandModal()">Got it</button>
        </footer>
      </div>
    </Modal>

    <Modal
      v-if="confirmDeleteModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), closeDeleteModal()
        }
      "
    >
      <!-- modal-form confirm-form -->
      <form
        v-if="true /*hasSlack*/"
        class="invite-form crm-form form-margin-small"
        style="height: 25vh"
      >
        <div class="header-crm">
          <div class="flex-row-wrapper inner-crm">
            <div class="flex-row-modal" style="margin: 0">
              <!-- <img src="@/assets/images/logo.png" class="logo" alt="" /> -->
              <h3 class="invite-form__title">Are you sure?</h3>
            </div>
            <div class="flex-row-modal" style="margin: 0">
              <img
                @click="closeDeleteModal"
                src="@/assets/images/close.svg"
                alt=""
                style="
                  filter: invert(30%);
                  cursor: pointer;
                  width: 20px;
                  height: 20px;
                  margin-right: 5px;
                "
              />
            </div>
          </div>
        </div>
        <div
          class="flex-row-modal inner-crm"
          style="margin: 0; justify-content: flex-start; width: 90%"
        >
          <h4 class="card-text" style="margin-left: 0; margin-top: 0; margin-bottom: 0.75rem">
            By clicking Delete, you will be removing
            {{ this.deleteAlert ? `${this.deleteAlert.title}` : 'this alert' }}.
          </h4>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="confirm-cancel-container" style="width: 90%; margin-bottom: 0.6rem">
            <div
              class="img-border-modal cancel-button"
              @click="closeDeleteModal"
              style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem"
            >
              Cancel
            </div>
            <button
              class="img-border-modal red-button"
              @click="deleteWorkflow(deleteAlert.id)"
              style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem; margin-right: 5%"
            >
              Delete
            </button>
          </div>
          <!-- <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="onRevoke(removeApp)"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Confirm"
                :loading="pulseLoading"
                >Confirm</PulseLoadingSpinnerButton
              >
            </template>
          </div> -->
        </div>
      </form>
    </Modal>

    <template v-if="!templates.refreshing">
      <!-- <transition name="fade">
      </transition> -->
      <!-- <div class="create-workflow-container" style="margin-top: 2rem;">
        <button :disabled="!isPaid" class="green_button right-margin side-wrapper" @click="switchBuildCustom">
          Create Workflow
          <label class="side-icon side-workflow">
            <span class="side-tooltip-single" style="top: -5px; right: 142px; width: 200px;">Upgrade your plan</span>
            <img
              style="filter: invert(40%)"
              src="@/assets/images/lock.svg"
              height="14px"
              alt=""
            />
          </label>
        </button>
      </div> -->

      <div style="margin-top: 5rem" v-if="editing" class="alert_cards">
        <!-- <div v-if="!zoomChannel && hasSlackIntegration" class="card">
          <div class="card__header" style="">
            <img class="gray-logo" style="height: 40px" src="@/assets/images/logo.png" />
          </div>
            <div>
              <h4>Log Meeting</h4>
              <small class="card-text">Recieve actionable alerts as soon as your meetings end.</small>
            </div>
            <div class="separator"></div>
            <div class="card__body__between">
              <p></p>
              <button @click="goToWorkflow('LogZoom')" class="white_button">Activate</button>
            </div>
        </div> -->

        <div :key="alert.id" v-for="alert in leaderTemplatesFirst" class="card">
          <div class="card__header" style="">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>

          <div>
            <div>
              <h4>
                {{ alert.title }}
              </h4>
              <div v-if="user.id !== alert.user" class="small-text">Created by Leadership</div>
            </div>
            <p class="card-text" @click="test(alert)">
              Results: {{ alert && alert.sobjectInstances ? alert.sobjectInstances.length : 0 }}
            </p>
          </div>
          <div class="separator"></div>
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
              <!-- <button
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
                </button> -->
              <button
                class="img-border"
                @click="openDeleteWorkflow(alert)"
                v-if="user.id === alert.user"
              >
                <!-- <img
                    src="@/assets/images/trash.svg"
                    style="filter: invert(40%)"
                    height="14px"
                    alt=""
                  /> -->
                <img
                  src="@/assets/images/chat-trash.svg"
                  class="filtered-red"
                  style="height: 14px"
                  alt=""
                />
              </button>
            </div>
            <div v-if="hasSlackIntegration" class="toggle-container">
              <span>{{ alert.isActive ? 'On' : 'Off' }}</span>
              <ToggleCheckBox
                @input="onToggleAlert(alert.id, alert.isActive)"
                v-model="alert.isActive"
                offColor="#aaaaaa"
                :onColor="'#41b883'"
              />
            </div>
          </div>
        </div>

        <!-- <div v-if="zoomChannel" class="card">
          <div class="card__header" style="">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>
            <div>
              <h4>Log Meeting</h4>
              <p class="card-text">Meetings: {{ meetings.length }}</p>
            </div>
            <div class="separator"></div>
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

              <button @click="goToWorkflow('LogZoom')" class="white_button">Change Channel</button>
            </div>
        </div> -->

        <!-- <div v-if="hasRecapChannel && userLevel !== 'REP' && hasSlackIntegration" class="card">
          <div class="card__header" style="">
            <img style="height: 40px" src="@/assets/images/logo.png" />
          </div>
            <div>
              <h4>Meeting Recaps</h4>
              <p class="card-text">Meetings: {{ meetings.length }}</p>
            </div>
            <div class="separator"></div>
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

              <button @click="goToWorkflow('ZoomRecap')" class="white_button">Change Channel</button>
            </div>
        </div> -->

        <div
          v-for="config in filteredConfigs"
          :key="config.id"
          class="card"
          v-show="!templateTitles.includes(config.title)"
        >
          <div class="card__header" style="">
            <img class="gray-logo" style="height: 40px" src="@/assets/images/logo.png" />
          </div>

          <div>
            <h4>{{ config.title }}</h4>
            <p style="margin-top: 0.25rem" class="card-text">{{ config.subtitle }}</p>
          </div>
          <div class="separator"></div>
          <div v-if="config.title !== 'Empty Field'" class="card__body__between">
            <p></p>
            <button @click="repCheck(config)" class="white_button">Activate</button>
          </div>

          <div v-else class="card__body__between">
            <p></p>
            <button @click="repCheck(config)" class="white_button">Activate</button>
            <!-- <div v-else class="tooltip-left">
                <img
                  class=""
                  style="filter: invert(40%)"
                  src="@/assets/images/chat-lock.svg"
                  height="16px"
                  alt=""
                />
                <small class="tooltiptext-left">Upgrade your plan</small>
              </div> -->
          </div>
        </div>

        <!-- <div v-if="!hasRecapChannel && userLevel !== 'REP' && hasSlackIntegration" class="card">
          <div class="card__header" style="">
            <img class="gray-logo" style="height: 40px" src="@/assets/images/logo.png" />
          </div>

            <div>
              <h4>Meeting Recaps</h4>
              <small class="card-text"
                >Recieve alerts that give you insight on your teams meetings.</small
              >
            </div>
            <div class="separator"></div>
            <div class="card__body__between">
              <p></p>
              <button @click="goToWorkflow('ZoomRecap')" class="white_button">Activate</button>
            </div>
        </div> -->
        <!-- <div class="card">
          <div class="card__header" style="">
            <img class="gray-logo" style="height: 40px" src="@/assets/images/logo.png" />
          </div>

            <div>
              <h4>Create Workflow</h4>
              <small class="card-text"
                >Create a workflow with your own settings.</small
              >
            </div>
            <div class="separator"></div>
            <div class="card__body__between">
              <p></p>
              <button v-if="isPaid" :disabled="!isPaid" class="green_button right-margin" @click="switchBuildCustom">
                Create Workflow
              </button>
              <div v-else class="tooltip-left">
                <img
                  class=""
                  style="filter: invert(40%)"
                  src="@/assets/images/chat-lock.svg"
                  height="16px"
                  alt=""
                />
                <small class="tooltiptext-left">Upgrade your plan</small>
              </div>
            </div>
        </div> -->
      </div>

      <div class="alert_cards" v-if="editing"></div>
    </template>

    <!-- <div v-else-if="isOnboarding && user.isAdmin">
      <Onboarder @refresh-workflows="refreshWorkflows" />
    </div> -->

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
import allConfigs from '@/views/settings/alerts/configs'

export default {
  name: 'ConfigureWorkflows',
  components: {
    ToggleCheckBox,
    Onboarder,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  props: {
    // templates: {
    //   type: Object
    // },
    config: {
      type: Object,
    },
    switchBuildCustom: {
      type: Function,
    },
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
      deleteAlert: null,
      templateTitles: [],
      workflowListOpen: false,
      confirmDeleteModal: false,
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

    // if (!this.userCRM) {
    //   this.$router.replace({
    //     name: 'Integrations',
    //     params: {},
    //   })
    // }
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
    refreshTemplates() {
      this.templates.refresh()
    },
    repCheck(config) {
      console.log('this.hasSlackIntegration', this.hasSlackIntegration)
      if (this.hasSlackIntegration) {
        this.goToWorkflow(config.title)
        return
      }
      if (
        config.title === 'Large Opportunities' ||
        config.title === 'Large Deals' ||
        config.title === 'Empty Field' ||
        config.title === 'Upcoming Next Step' ||
        this.user.userLevel === 'MANAGR'
      ) {
        this.goToWorkflow(config.title)
        // if (this.user.userLevel === 'MANAGER') {
        //   this.goToWorkflow(config.title)
        // } else  {
        //   // Make function to automatically save workflow
        //   // this.goToWorkflow(config.title)
        //   this.saveRepWorkflow(config)
        // }
      } else {
        // this.goToWorkflow(config.title)
        this.saveRepWorkflow(config)
      }
    },
    async saveRepWorkflow(config) {
      const newConfigs = config.newConfigs[0]
      if (newConfigs.alertTargets.length) {
        try {
          const res = await AlertTemplate.api
            .createAlertTemplate({
              ...config,
              user: this.user.id,
              directToUsers: true,
            })
            .then((response) => {
              this.templates.refresh()
              this.handleUpdate()
            })
        } catch (e) {
          console.log('e', e)
          this.$toast(`Something went wrong. Please try again.`, {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      }
    },
    handleUpdate() {
      return User.api
        .update(this.user.id)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
    },
    closeCommandModal() {
      this.templates.refresh()
      setTimeout(() => {
        this.commandModalOpen = false
      }, 300)
    },
    openDeleteWorkflow(alert) {
      this.deleteAlert = alert
      this.confirmDeleteModal = true
    },
    closeDeleteModal() {
      this.deleteAlert = null
      this.confirmDeleteModal = false
    },
    async deleteWorkflow(id) {
      try {
        await AlertTemplate.api.deleteAlertTemplate(id)
      } catch (e) {
        console.log(e)
        this.$toast('Error removing workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    deletedTitle(id) {
      let newList = []
      newList = this.templates.list.filter((val) => val.id === id)
      this.deleteTitle = newList[0].title
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
    goToWorkflow(name) {
      let newName = name.replace(/\s/g, '')
      if (newName === 'LargeDeals') {
        newName = 'LargeOpportunities'
      }
      this.$emit('create-template', newName)
      // this.$router.push({ name: newName })
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
@import '@/styles/modals';

.shimmer {
  display: inline-block;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  max-width: 200px;
}

.gray-blue {
  color: $light-gray-blue;
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
  top: -5px;
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
  flex-direction: column;
  justify-content: space-between;
  width: 20vw;
  min-height: 25vh;
  transition: all 0.25s;

  h4 {
    margin: 0.25rem 0;
    padding: 0;
  }
  p {
    margin-top: 0.25rem;
    font-size: 12px;
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    // padding: 4px 16px;
    padding: 4px 0;
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

      // width: 260px;
      width: 100%;
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
  @include base-modal();
  color: $base-gray;
  min-height: 25vh;
  max-height: 70vh;
  padding: 0 1rem;
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
  // height: 100vh;
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
.create-workflow-container {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  button {
    margin-right: 3rem;
  }
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
.center {
  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: center;
  // width: 100%;
  // padding: 8px 0px !important;
  // margin-bottom: 16px;
  // background: rgba(0, 0, 0, 0.7);
  // outline: 1px solid $soft-gray;
  // border-radius: 6px;
}
.small-text {
  font-size: 10px;
  color: $dark-green;
  margin-top: 4px;
}
.command-modal {
  @include wide-modal();
  overflow-x: hidden;
  height: 100%;
  align-items: center;
  padding: 0px 24px 0px 24px;
  position: relative;
  color: $base-gray;

  header {
    position: sticky;
    top: 0;
    padding-top: 24px;
    background-color: white;
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
    position: sticky;
    bottom: 0;
    margin-top: 16px;
    background-color: white;
    padding-bottom: 16px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;

    button {
      background-color: $dark-green;
      padding: 11px;
      font-size: 13px;
      border-radius: 4px;
      border: none;

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
.separator {
  border-top: 1px solid $soft-gray;
  width: 16.5vw;
  margin-bottom: 0.5rem;
  // margin: 0rem 0 0.1rem 0;
}
::v-deep .multiselect * {
  font-size: 13px;
  font-family: $base-font-family;
  border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}
::v-deep .multiselect__content-wrapper {
  border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

// Tooltip
.side-wrapper {
  display: flex;
  flex-direction: row;
}
.side-wrapper .side-icon {
  position: relative;
  // background: #FFFFFF;
  border-radius: 50%;
  // padding: 12px;
  // padding: 8px 16px;
  // margin: 20px 12px 0px 10px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  // outline: 1px solid $mid-gray;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip,
.side-wrapper .side-tooltip-single {
  display: block;
  width: 250px;
  height: auto;
  position: absolute;
  top: -10px; // for double line
  // top: 0; // for single line
  right: 30px;
  font-size: 14px;
  background: #ffffff;
  color: #ffffff;
  padding: 6px 8px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip-single {
  width: 100px;
}
.side-wrapper .side-tooltip::before,
.side-wrapper .side-tooltip-single::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: 50%;
  right: -4%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip-single::before {
  bottom: 40%;
}
.side-wrapper:hover .side-icon .side-tooltip,
.side-wrapper:hover .side-icon .side-tooltip-single {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.side-wrapper:hover .side-icon span,
.side-wrapper:hover .side-icon .side-tooltip,
.side-wrapper:hover .side-icon .side-tooltip-single {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}
// .side-wrapper .side-workflow:hover,
.side-wrapper:hover .side-workflow .side-tooltip,
.side-wrapper:hover .side-workflow .side-tooltip::before,
.side-wrapper:hover .side-workflow .side-tooltip-single,
.side-wrapper:hover .side-workflow .side-tooltip-single::before {
  // margin-top: 1rem;
  background: $black;
  color: #ffffff;
}
.side-icon:hover {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  img {
    filter: invert(90%);
  }
}
.toggle-container {
  display: flex;
  align-items: center;
  // margin-right: 1.25rem;
  span {
    font-size: 12px;
    color: $light-gray-blue;
    margin-right: 0.5rem;
  }
}
.gray-logo {
  filter: invert(40%);
}
.invite-form {
  @include small-modal();
  min-width: 37vw;
  // min-height: 64vh;
  align-items: center;
  justify-content: space-between;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
    font-size: 22px;
  }
  &__subtitle {
    text-align: left;
    font-size: 16px;
    margin-left: 1rem;
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    // margin-top: -4rem;
  }
  &__inner_actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    border-top: 1px solid $soft-gray;
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
  }
}
.crm-form {
  height: 60vh;
  width: 32vw;
}
.form-margin-small {
  margin-top: 10rem;
}
.header-crm {
  // background-color: $soft-gray;
  width: 100%;
  // border-bottom: 1px solid $soft-gray;
  position: relative;
  border-top-right-radius: 4px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-top-left-radius: 4px;
  display: flex;
  justify-content: center;
  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: flex-start;

  h3 {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $base-gray;
  }
}
.flex-row-wrapper {
  display: flex;
  justify-content: space-between;
}
.inner-crm {
  border-bottom: 1px solid $soft-gray;
  width: 90%;
  padding-bottom: 0.4rem;
  overflow-y: auto;
}
.flex-row-modal {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  margin: 0 5%;
  letter-spacing: 1px;
}
.confirm-cancel-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 94%;
}
.img-border-modal {
  // @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  // padding: 4px 6px;
  margin-right: 8px;
  margin-top: 0.5rem;
}
.cancel-button {
  @include gray-button();
}
.red-button {
  @include button-danger();
}
.filtered-red {
  filter: invert(43%) sepia(45%) saturate(682%) hue-rotate(308deg) brightness(109%) contrast(106%);
}
</style>
