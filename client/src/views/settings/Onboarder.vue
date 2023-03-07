<template>
  <div class="onboarder">
    <Modal v-if="showModal" dimmed>
      <div class="modal">
        <header>
          <h2>Almost there! 🙌</h2>
          <p>Create a "Managr Pipeline" section for your 2 new channels. Follow the steps below.</p>
        </header>
        <section style="position: relative">
          <img src="@/assets/images/slackSection.png" width="100%" height="auto" alt="" />
          <img class="absolute-img" src="@/assets/images/slackLogo.png" height="16px" alt="" />
        </section>

        <!-- <section>
          <p class="gray-blue">Now test your workflows by clicking "Send to Slack"</p>
          <div class="modal__section" v-for="(workflow, i) in workflows.list" :key="i">
            <div>
              <p>
                {{ workflow.title }}
              </p>
              <p>{{ workflow.subtitle }}</p>
            </div>

            <PipelineLoader style="margin-left: 8px" v-if="pressed && pressedIndex === i" />

            <button v-else :disabled="pressed" @click="onRunAlertTemplateNow(workflow.id, i)">
              Send to Slack <span>|</span>
              <img src="@/assets/images/slackLogo.png" height="10px" alt="" />
            </button>
          </div>
        </section> -->
        <footer>
          <button @click="completeOnboarding()">Finish Onboarding</button>
        </footer>
      </div>
    </Modal>
    <div class="header row">
      <div>
        <h1>Welcome {{ user.firstName }}! 🎉</h1>
        <p>
          Lets start automating your sales process so you can
          <span>reclaim your time and focus on selling.</span>
        </p>
      </div>
      <div style="margin-top: 3rem" class="wrapper">
        <label class="icon workflow">
          <span style="width: 200px" class="tooltip"
            >Having trouble? Send us an email: cx@mymanagr.com</span
          >
          <span>?</span>
        </label>
      </div>
    </div>

    <article
      ref="slack"
      :class="{ 'green-border': userCRM === 'HUBSPOT' || userCRM === 'SALESFORCE' }"
    >
      <div
        :class="{ 'green-bg': userCRM === 'HUBSPOT' || userCRM === 'SALESFORCE' }"
        class="red-bg"
      >
        1
      </div>
      <small>4 SIMPLE STEPS</small>
      <h3 v-if="!userCRM">Step 1: Connect your CRM</h3>

      <div v-else>
        <h3>Step 1: Complete <span></span></h3>
      </div>

      <div class="section">
        <section class="section__body">
          <div class="card" v-if="userCRM === 'SALESFORCE'">
            <div class="card__header vlb-bg" style="padding-left: 32px; padding-right: 32px">
              <img style="height: 30px; width: auto" src="@/assets/images/salesforce.png" />
            </div>

            <div class="card__body">
              <h3>Salesforce</h3>
              <p class="card-text">Sync Accounts, Opportunities, & Contacts</p>
              <div>
                <div>
                  <small>Connected</small>
                </div>
              </div>
            </div>
          </div>
          <div class="card" v-else-if="userCRM === 'HUBSPOT'">
            <div class="card__header lo-bg">
              <img style="height: 80px" src="@/assets/images/hubspott.png" />
            </div>

            <div class="card__body">
              <h3 class="card__title">Hubspot</h3>
              <p class="card-text">Sync Companies, Deals, and Contacts</p>
              <div>
                <div>
                  <small>Connected</small>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="!userCRM" class="card">
            <div class="card__header og-bg" style="padding-left: 18px; padding-right: 18px">
              <img style="height: 30px; width: auto" src="@/assets/images/salesforce.png" />
              <img style="height: 30px" src="@/assets/images/hubspot-single-logo.svg" />
            </div>
            <div
              class="card__body"
              v-if="
                generatingToken &&
                (selectedIntegration == 'SALESFORCE' || selectedIntegration === 'HUBSPOT')
              "
            >
              <PipelineLoader />
            </div>
            <div v-else>
              <div class="card__body">
                <div style="display: flex">
                  <h3 class="card__title">CRM</h3>
                </div>
                <p class="card-text">Which CRM would you like to link ?</p>
                <div>
                  <Multiselect
                    placeholder="Select CRM"
                    @input="onGetAuthLink($event.value)"
                    :v-model="selectedCRM"
                    :options="crmList"
                    openDirection="below"
                    style="width: 14rem"
                    selectLabel="Enter"
                    track-by="value"
                    label="label"
                  >
                    <template slot="noResult">
                      <p class="multi-slot">No results. Try loading more</p>
                    </template>
                    <template slot="placeholder">
                      <p class="slot-icon">
                        <img src="@/assets/images/search.svg" alt="" />
                        Select CRM
                      </p>
                    </template>
                  </Multiselect>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </article>

    <article
      ref="stepThree"
      :class="{ 'green-border': hasZoomChannel && hasSlackIntegration && hasNylasIntegration }"
    >
      <div
        :class="{ 'green-bg': hasZoomChannel && hasSlackIntegration && hasNylasIntegration }"
        class="red-bg"
      >
        2
      </div>
      <small>3 SIMPLE STEPS</small>
      <h3 v-if="!hasZoomChannel || !hasSlackIntegration || !hasNylasIntegration">
        Step 2: Connect Slack & Calendar
      </h3>
      <h3 v-else>Step 2: Complete</h3>

      <section class="section">
        <div class="section__body">
          <div class="card">
            <div class="card__header lr-bg" style="padding-left: 36px; padding-right: 36px">
              <img style="height: 40px" src="@/assets/images/slackLogo.png" />
            </div>

            <div class="card__body">
              <div class="wrapper top-row">
                <h3>Slack</h3>
                <label style="margin-top: 0" class="icon workflow">
                  <span class="tooltip-large">
                    Under "Where should Managr post" find yourself then click "Allow"
                    <img src="@/assets/images/slackExample.png" height="200px" width="auto" alt=""
                  /></span>
                  <span>?</span>
                </label>
              </div>
              <p class="card-text">Interact with Managr through Slack</p>
              <div>
                <PulseLoadingSpinnerButton
                  v-if="!hasSlackIntegration"
                  :disabled="
                    (!orgHasSlackIntegration && !userCanIntegrateSlack) || hasSlackIntegration
                  "
                  @click="onIntegrateSlack"
                  class="orange_button"
                  text="Connect"
                  :loading="generatingToken && selectedIntegration == 'SLACK'"
                ></PulseLoadingSpinnerButton>

                <div class="row" v-else>
                  <small>Connected</small>
                </div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card__header lbp-bg">
              <img src="@/assets/images/gmailCal.png" style="margin-right: 16px; height: 32px" />
              <img src="@/assets/images/outlookMail.png" style="height: 32px" />
              <!-- <img class="filter-dot" src="@/assets/images/dot.svg" v-if="hasNylasIntegration" /> -->
            </div>

            <div class="card__body">
              <div class="wrapper top-row">
                <h3>Calendar</h3>
                <label style="margin-top: 0" class="icon workflow">
                  <span class="tooltip">Please make sure all FOUR box are checked off!</span>
                  <span>?</span>
                </label>
              </div>

              <p class="card-text">Accesses your upcoming meetings</p>
              <div>
                <PulseLoadingSpinnerButton
                  v-if="!hasNylasIntegration"
                  @click="onGetAuthLink('NYLAS')"
                  class="orange_button"
                  text="Connect"
                  :loading="generatingToken && selectedIntegration == 'NYLAS'"
                ></PulseLoadingSpinnerButton>
                <div v-else>
                  <small>Connected</small>
                </div>
              </div>
            </div>
          </div>

          <div class="card wider">
            <div class="card__header og-bg">
              <img src="@/assets/images/slackLogo.png" style="margin-right: 16px; height: 32px" />
              <img src="@/assets/images/outlookMail.png" style="height: 32px" />
            </div>
            <div class="card__body">
              <div class="wrapper top-row">
                <h3>Log Meeting</h3>
                <label style="margin-top: 0" class="icon workflow">
                  <span style="top: -90px" class="tooltip"
                    >This channel will display your upcoming meetings along with the ability to log
                    notes and update fields</span
                  >
                  <span>?</span>
                </label>
              </div>
              <!-- <h3>Log meeting</h3> -->
              <p class="card-text">Create #log-meeting Slack channel</p>
              <div v-if="!hasZoomChannel" class="row">
                <input
                  v-model="meetingChannelName"
                  class="search__input"
                  type="text"
                  name="channel"
                  id="channel"
                  :placeholder="`log-meeting-${userInitials}`"
                  @input="logNewName(meetingChannelName, 'zoom')"
                />
                <button
                  style="margin-left: 12px"
                  v-if="!submitting"
                  :disabled="!meetingChannelName"
                  @click="createChannel(meetingChannelName, 'zoom')"
                >
                  Create
                </button>
                <PipelineLoader v-else />
              </div>
              <div v-else>
                <small>Created</small>
              </div>
            </div>
          </div>
        </div>
      </section>
    </article>

    <article :class="{ 'green-border': updateFields.length }">
      <div :class="{ 'green-bg': updateFields.length }" class="red-bg">3</div>
      <small>ONLY 2 STEPS LEFT</small>

      <div v-if="updateFields.length" class="wrapper">
        <h3>Step 3: Complete</h3>
        <label class="icon workflow">
          <span class="tooltip">
            Your commonly updated
            {{ userCRM === 'SALESFORCE' ? 'fields' : 'properties' }} have already been saved.</span
          >
          <span>?</span>
        </label>
      </div>

      <div v-else-if="userCRM" class="wrapper">
        <h3>
          Step 3: Add the {{ camelize(userCRM) }}
          {{ userCRM === 'SALESFORCE' ? 'fields' : 'properties' }} you regularly update
        </h3>
        <label class="icon workflow">
          <span style="top: -110px" class="tooltip">
            We recommend at least 3 of the following: Name , Stage , Close Date , Next Step , Notes.
            Try searching for them below.</span
          >
          <span>?</span>
        </label>
      </div>

      <h3 v-else>Add the fields/properties you regularly update</h3>

      <section class="section">
        <div>
          <OnboardingForms
            @refresh-fields="refreshFields"
            :customForm="
              this.allForms.find((f) => f.resource == currentResource && f.formType == 'UPDATE')
            "
            :disable="!!workflows.list.length"
          />
        </div>
      </section>
    </article>

    <article :class="{ 'green-border': workflows.list.length && hasRecapChannel }">
      <div :class="{ 'green-bg': workflows.list.length && hasRecapChannel }" class="red-bg">4</div>
      <small>FINAL STEP!</small>

      <h3 v-if="workflows.list.length && hasRecapChannel">Step 4: Complete</h3>

      <div v-else class="wrapper">
        <h3>Step 4: Activate Workflows</h3>
        <label class="icon workflow">
          <span class="tooltip">Activate workflows to help you stay on top of your pipeline.</span>
          <span>?</span>
        </label>
      </div>
      <p
        style="margin-top: -2px"
        v-if="hasRecapChannel && !workflows.list.length"
        class="card-text gray-blue"
      >
        Activate at least 2 workflows
      </p>
      <p
        v-else-if="hasRecapChannel && workflows.list.length"
        style="margin-top: -2px; font-size: 13px"
        class="green"
      >
        Workflows Active
      </p>

      <section v-if="hasRecapChannel" class="section margin-bottom limit-height">
        <div class="top-row" v-for="(config, i) in filteredConfigs" :key="i">
          <span>
            <input
              :disabled="submitting || !!workflows.list.length"
              v-model="selectedWorkflows"
              type="checkbox"
              :id="i"
              :value="config"
            />
            <label :for="i"></label>
          </span>

          <div :class="{ disabled: submitting || workflows.list.length }" class="no-margin">
            <p
              :class="{
                green: selectedWorkflows.includes(config),
              }"
            >
              {{ config.title }}
            </p>
            <span>{{ config.subtitle }}</span>
            <div class="week-row">
              <div v-for="day in weeklyOpts" :key="day.key">
                <label
                  :title="`Deliver on ${day.key}`"
                  @click="workflows.list.length ? '' : setDay(day.value, config, i)"
                  :class="{
                    'active-option': config.newConfigs[0].recurrenceDays.includes(day.value),
                  }"
                  :for="day.key"
                  >{{ day.key.charAt(0) }}</label
                >
              </div>
              <!-- <small class="grape" v-if="selectedWorkflows.includes(config)"
                >Choose delivery days</small
              > -->
            </div>
          </div>
        </div>
      </section>

      <div class="margin-bottom">
        <p v-if="!hasRecapChannel" class="card-text">
          First, create a #my-pipeline Slack channel for your worfklows
        </p>

        <div v-if="!hasRecapChannel" class="top-row">
          <section>
            <input
              v-model="channelName"
              class="search__input wide-input"
              type="text"
              name="channel"
              id="channel"
              :placeholder="`my-pipeline-${userInitials}`"
              :disabled="submitting"
              @input="logNewName(channelName, 'recap')"
            />
          </section>

          <button
            style="margin-left: 12px"
            v-if="!submitting"
            @click="createChannel(channelName, 'recap')"
            :disabled="!channelName"
          >
            Create
          </button>
          <PipelineLoader v-else />
        </div>
        <div ref="channel" v-else>
          <button
            :disabled="selectedWorkflows.length < 2"
            @click="onSaveAllWorkflows()"
            v-if="!submitting"
          >
            Activate workflows
          </button>
          <PipelineLoader v-else />
        </div>
      </div>
    </article>

    <!-- <footer>
      <button class="secondary-button">Continue</button>
    </footer> -->
  </div>
</template>

<script>
import Modal from '@/components/InviteModal'
import SlackOAuth from '@/services/slack'
import User from '@/services/users'
import UpdateOppForm from '@/views/settings/UpdateOppForm'
import CreateContactForm from '@/views/settings/CreateContactForm'
import LogZoom from '@/views/settings/OnboardingLogMeeting'
import CollectionManager from '@/services/collectionManager'
import ZoomAccount from '@/services/zoom/account/'
import Nylas from '@/services/nylas'
import Salesforce from '@/services/salesforce'
import Hubspot from '@/services/hubspot'
import AlertTemplate from '@/services/alerts/'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import OnboardingForms from '@/components/OnboardingForms'
import allConfigs from '@/views/settings/alerts/completeConfigs'
import { UserOnboardingForm } from '@/services/users/forms'
import { mapActions } from 'vuex'

export default {
  name: 'Onboarder',
  components: {
    Modal,
    UpdateOppForm,
    CreateContactForm,
    LogZoom,
    PulseLoadingSpinnerButton,
    OnboardingForms,
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      pressedIndex: null,
      pressed: false,
      tested: false,
      showModal: false,
      submitting: false,
      selectedIntegration: null,
      updateOpportunityFields: null,
      createContactFields: null,
      resource: 'Opportunity',
      meetingChannelName: null,
      generatingToken: false,
      type: 'UPDATE',
      selectedCRM: null,
      addedFields: [],
      allForms: [],
      selectedForm: null,
      currentResource: '',
      updateFields: [],
      selectedWorkflows: [],
      userOnboardingForm: new UserOnboardingForm({}),
      crmList: [
        { label: 'Salesforce', value: 'SALESFORCE' },
        { label: 'Hubspot', value: 'HUBSPOT' },
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
      workflows: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
      fieldSelected: false,
      hasSelectedFields: false,
      channelName: null,
      allConfigs,
      savingTemplate: false,
    }
  },
  watch: {
    updateForm: 'filterUpdateFields',
    // selectedWorkflows: 'scrollToChannel',
  },
  mounted() {
    setTimeout(() => {
      this.checkOnboardStatus()
    }, 5000)

    // this.checkCrm()
  },
  async created() {
    try {
      if (this.userCRM === 'HUBSPOT') {
        this.currentResource = 'Deal'
      } else if (this.userCRM === 'SALESFORCE') {
        this.currentResource = 'Opportunity'
      }
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
    } catch (e) {
      console.log(e)
    }

    if (this.$route.query.code) {
      this.generatingToken = true
      this.selectedIntegration = this.$route.query.state
      try {
        const modelClass = this.selectedIntegrationSwitcher
        if (this.selectedIntegration == 'SALESLOFT') {
          await modelClass.api.authenticate(
            this.$route.query.code,
            this.$route.query.context,
            this.$route.query.scope,
          )
        } else if (this.selectedIntegration != 'SLACK' && this.selectedIntegration != 'SALESLOFT') {
          await modelClass.api.authenticate(this.$route.query.code)
        } else {
          await SlackOAuth.api.generateAccessToken(this.$route.query.code)
        }
      } catch (e) {
        let { response } = e
        if (response && response.status >= 400 && response.status < 500 && response.status != 401) {
          let { data } = response
          if (data.timezone) {
            this.$toast(
              'We could not retrieve your timezone from zoom, to fix this please login to the zoom.us portal through a browser and return to managr to reintegrate',
              {
                timeout: 2000,
                position: 'top-left',
                type: 'success',
                toastClassName: 'custom',
                bodyClassName: ['custom'],
              },
            )
          }
        }
      } finally {
        await this.$store.dispatch('refreshCurrentUser')
        this.generatingToken = false
        this.selectedIntegration = null
        this.$router.replace({
          name: 'ListTemplates',
          params: {},
        })
        this.checkCrm()
      }
    }
    this.workflows.refresh()
    // this.getAllForms()
  },
  methods: {
    test() {
      console.log(this.user)
    },
    refreshFields() {
      this.getAllForms()
    },
    checkCrm() {
      if (this.userCRM) {
        setTimeout(() => {
          this.$refs.slack ? this.$refs.slack.scrollIntoView({ behavior: 'smooth' }) : ''
        }, 100)
      }
    },
    checkOnboardStatus() {
      if (
        this.userCRM &&
        this.hasSlackIntegration &&
        this.hasNylasIntegration &&
        this.hasZoomChannel &&
        this.updateFields.length &&
        this.hasRecapChannel &&
        this.workflows.list.length
      ) {
        this.showModal = true
      }
    },
    async onRunAlertTemplateNow(id, index) {
      this.pressed = true
      this.pressedIndex = index
      try {
        await AlertTemplate.api.runAlertTemplateNow(id, false)
        this.tested = true
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.pressed = false
        }, 3000)
      }
    },
    ...mapActions(['refreshCurrentUser']),
    completeOnboarding() {
      this.userOnboardingForm.field.onboarding.value = false
      User.api.update(this.user.id, this.userOnboardingForm.value)
      this.handleUpdate()
      this.$emit('refresh-workflows')
      this.$toast("You're all set! Onboarding complete", {
        timeout: 2000,
        position: 'top-left',
        type: 'success',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
    },
    filterUpdateFields() {
      this.updateFields = this.updateForm.fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
    },

    async getAllForms() {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
    },
    logNewName(str, type) {
      let new_str = ''
      new_str = str.replace(/\s+/g, '-').toLowerCase()

      if (type === 'recap') {
        this.channelName = new_str
      } else {
        this.meetingChannelName = new_str
      }
    },
    setDay(n, config, i) {
      if (config.newConfigs[0].recurrenceDays.includes(n)) {
        this.filteredConfigs[i].newConfigs[0].recurrenceDays = this.filteredConfigs[
          i
        ].newConfigs[0].recurrenceDays.filter((day) => day !== n)
      } else {
        this.filteredConfigs[i].newConfigs[0].recurrenceDays.push(n)
      }
    },
    fieldSelection(lst) {
      if (lst.length) {
        this.hasSelectedFields = true
        this.addedFields = lst.map((field) => field.apiName)
      } else {
        this.hasSelectedFields = false
        this.addedFields = []
      }
      console.log(this.hasSelectedFields)
    },
    camelize(str) {
      return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function (match, index) {
        if (+match === 0) return ''
        return index === 0 ? match.toUpperCase() : match.toLowerCase()
      })
    },
    scrollToChannel() {
      if (this.selectedWorkflows.length) {
        setTimeout(() => {
          this.$refs.channel ? this.$refs.channel.scrollIntoView({ behavior: 'smooth' }) : ''
        }, 100)
      } else {
        return
      }
    },

    toggleWorkflowModal() {
      this.workflowModalOpen = !this.workflowModalOpen
    },

    async onGetAuthLink(integration) {
      integration === 'NYLAS'
        ? confirm(
            'You must check all permission boxes in order for Managr to successfully connect to your calendar!',
          )
        : ''
      this.generatingToken = true
      this.selectedIntegration = integration

      let modelClass = this.selectedIntegrationSwitcher
      try {
        const res = await modelClass.api.getAuthLink()

        if (res.link) {
          window.location.href = res.link
        }
      } finally {
        setTimeout(() => {
          this.generatingToken = false
        }, 2000)
      }
    },

    async onIntegrateSlack() {
      if (this.user.isAdmin) {
        const confirmation = confirm(
          'Integrating Managr to your slack workspace will request access to a channel (you can choose a new one or an existing one) we will post a message letting the members of that channel know they can now integrate their Slack accounts',
        )
        if (!confirmation) {
          return
        }
      }
      this.generatingToken = true
      if (!this.orgHasSlackIntegration) {
        if (this.userCanIntegrateSlack) {
          try {
            let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.WORKSPACE)
            if (res.link) {
              window.location.href = res.link
            }
          } finally {
            this.generatingToken = false
          }
        }
      } else {
        if (!this.hasSlackIntegration) {
          try {
            let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.USER)
            if (res.link) {
              window.location.href = res.link
            }
          } catch (e) {
          } finally {
            setTImeout(() => {
              this.generatingToken = false
            }, 2000)
          }
        }
      }
    },
    async handleZoomUpdate(zoom_channel) {
      try {
        const res = await SlackOAuth.api.updateZoomChannel(this.slackId, zoom_channel).then(() => {
          User.api.getUser(this.user.id).then((response) => {
            this.$store.commit('UPDATE_USER', response)
          })
        })
      } finally {
        this.$toast('Success! Channel created', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        setTimeout(() => {
          this.$refs.stepThree ? this.$refs.stepThree.scrollIntoView({ behavior: 'smooth' }) : ''
        }, 100)
      }
    },
    async handleRecapUpdate(recap_channel) {
      try {
        const res = await SlackOAuth.api
          .updateRecapChannel(this.slackId, recap_channel, [this.user.id])
          .then(() => {
            User.api.getUser(this.user.id).then((response) => {
              this.$store.commit('UPDATE_USER', response)
            })
          })
      } finally {
        this.$toast('Success! Channel created', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        setTimeout(() => {
          this.$refs.channel ? this.$refs.channel.scrollIntoView({ behavior: 'smooth' }) : ''
        }, 100)
      }
    },

    handleUpdate() {
      User.api
        .update(this.user.id)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
    },

    onSaveAllWorkflows() {
      this.submitting = true
      let userId = this.$store.state.user.id
      this.selectedWorkflows.forEach(async function (item, i) {
        try {
          const res = await AlertTemplate.api
            .createAlertTemplate({
              ...item,
              user: userId,
              directToUsers: true,
            })
            .then(() => {
              User.api.getUser(this.user.id).then((response) => {
                this.$store.commit('UPDATE_USER', response)
              })
            })
        } catch (e) {
          console.log(e)
        }
      })
      setTimeout(() => {
        this.workflows.refresh()
      }, 3000)

      setTimeout(() => {
        this.showModal = true
        this.submitting = false
        this.selectedWorkflows = []
      }, 4000)
    },
    async createChannel(name, type) {
      this.submitting = true
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        if (type === 'zoom') {
          this.handleZoomUpdate(res.channel.id)
        } else {
          this.handleRecapUpdate(res.channel.id)
        }
      } else {
        this.channelName = ''
        this.meetingChannelName = ''
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
        }
      }
      this.submitting = false
    },
  },
  computed: {
    slackId() {
      return this.$store.state.user.slackRef.slackId
    },
    updateForm() {
      return this.allForms
        ? this.allForms.find((f) => f.resource == this.currentResource && f.formType == 'UPDATE')
        : null
    },
    userInitials() {
      return this.user.firstName[0] + (this.user.lastName ? this.user.lastName[0] : '')
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
    hasHubspotIntegration() {
      return !!this.$store.state.user.hubspotAccount
    },
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    orgHasSlackIntegration() {
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    hasNylasIntegration() {
      return !!this.$store.state.user.nylas
    },
    userCanIntegrateSlack() {
      return this.$store.state.user.isAdmin
    },
    selectedIntegrationSwitcher() {
      switch (this.selectedIntegration) {
        case 'SALESFORCE':
          return Salesforce
        case 'HUBSPOT':
          return Hubspot
        case 'ZOOM':
          return ZoomAccount
        case 'NYLAS':
          return Nylas
        case 'SLACK':
          return SlackOAuth
        default:
          return null
      }
    },
    user() {
      return this.$store.state.user
    },
    hasZoomChannel() {
      return this.$store.state.user.slackAccount
        ? this.$store.state.user.slackAccount.zoomChannel
        : null
    },
    hasRecapChannel() {
      return this.user.slackAccount ? this.user.slackAccount.recapChannel : null
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

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
.pulse {
  box-shadow: 0 0 0 0 $dark-green;
  transform: scale(1);
  animation: pulse 1.25s infinite;
}
.limit-height {
  height: 50vh;
  overflow-y: auto;
  max-width: fit-content;
}
.modal {
  background-color: $white;
  overflow-y: scroll;
  overflow-x: hidden;
  width: 42vw;
  height: 70vh;
  align-items: center;
  border-radius: 4px;
  padding: 16px;
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
    padding-top: 32px;

    p {
      letter-spacing: 0.3px;
      font-size: 14px;
      padding: 0;
      color: $base-gray;
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
    padding: 16px;
    background-color: white;

    display: flex;
    flex-direction: row;
    align-items: flex-end;
    justify-content: flex-end;
  }
}
::v-deep .multiselect__tag {
  display: none;
}
.wrapper {
  // display: inline-flex;
  display: flex;
  flex-direction: row;
}

.wrapper .icon {
  position: relative;
  background: #ffffff;
  border-radius: 50%;
  padding: 10px;
  margin: 20px 12px 0px 12px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  outline: 1px solid $mid-gray;
  // box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.wrapper .tooltip {
  display: block;
  width: 250px;
  height: auto;
  position: absolute;
  top: 0;
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
.wrapper .tooltip-large {
  display: block;
  width: fit-content;
  height: auto;
  position: absolute;
  top: 0;
  font-size: 14px;
  background: $grape;
  color: $white;
  padding: 8px 16px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);

  img {
    border-radius: 4px;
    margin-top: 8px;
  }
}
.wrapper .tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: -3px;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.wrapper .tooltip-large::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: -3px;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.wrapper .icon:hover .tooltip {
  top: -70px;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.wrapper .icon:hover .tooltip-large {
  top: -290px;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}

.wrapper .icon:hover span,
.wrapper .icon:hover .tooltip {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}

.wrapper .icon:hover span,
.wrapper .icon:hover .tooltip-large {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}

.wrapper .workflow:hover,
.wrapper .workflow:hover .tooltip,
.wrapper .workflow:hover .tooltip::before {
  background: $grape;
  color: #ffffff;
}

.wrapper .workflow:hover,
.wrapper .workflow:hover .tooltip,
.wrapper .workflow:hover .tooltip-large::before {
  background: $grape;
  color: white;
}

::placeholder {
  color: $very-light-gray;
}

.onboarder {
  margin-left: -4px;
  // width: 100%;
}

article {
  border-left: 1px solid $coral;
  padding-left: 32px;
  position: relative;
}
.gray {
  color: $base-gray;
  opacity: 0.9;
}
.gray-blue {
  color: $light-gray-blue !important;
}
.onboard-complete {
  padding: 0;
  margin: 0;
  button {
    position: absolute;
    right: 0;
    top: 64px;
  }
}
.row {
  display: flex;
  flex-direction: row;
}
.header {
  letter-spacing: 0.5px;
  color: $base-gray;
  border-bottom: 1px solid $soft-gray;
  width: 100%;
  padding: 1px 16px 8px 16px;
  margin-bottom: 24px;
  margin-left: -16px;
  margin-top: 0;
  position: sticky;
  top: 00px;
  background-color: $off-white;
  z-index: 10;
  // p {
  //   color: $light-gray-blue;
  // }
  h1 {
    font-weight: bold;
    letter-spacing: 1px;
  }
}
.space-between {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
}
small {
  font-size: 11px;
  color: $dark-green;
}
.grape {
  font-size: 12px;
  color: $grape;
}
.section {
  color: $base-gray;
  width: 90vw;

  &__head {
    padding: 8px 12px;
    background-color: white;
    margin-bottom: 0;
  }
  &__body {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    gap: 16px;
    font-size: 11px;
    // color: $light-gray-blue;
  }
}
.red-bg {
  background-color: $coral;
  border-radius: 100%;
  height: 26px;
  width: 26px;
  color: white;
  position: absolute;
  top: 40px;
  left: -14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.wider {
  width: 27.5vw !important;
}
.absolute-img {
  position: absolute;
  right: 16px;
  bottom: 20px;
}
.card {
  background-color: $white;
  padding: 16px 24px;
  border: 1px solid #e8e8e8;
  margin-right: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: row;
  width: 27vw;
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
    h3 {
      margin: 0;
      padding: 0;
      font-size: 16px;
    }
    p {
      font-size: 13px;
      color: $light-gray-blue;
    }
  }
}

.green {
  color: $dark-green !important;
}
.green-border {
  border-left: 1px solid $dark-green;
}
.green-bg {
  background-color: $dark-green !important;
  color: white !important;
}
.lr-bg {
  background: rgb(251, 165, 192);
  background: linear-gradient(90deg, rgba(251, 165, 192, 1) 1%, rgba(247, 109, 152, 1) 100%);
  border: 1px solid $light-red;
}
.lbp-bg {
  background: rgb(147, 162, 247);
  background: linear-gradient(90deg, rgb(181, 191, 244) 0%, rgb(176, 185, 245) 32%);
  border: 1px solid $very-light-blue;
}
.vlb-bg {
  background: rgb(181, 222, 255);
  background: linear-gradient(90deg, rgba(181, 222, 255, 1) 1%, rgba(127, 196, 251, 1) 100%);
  border: 1px solid $very-light-blue;
}
footer {
  padding-left: 32px;
}
// .gray {
//   color: $light-gray-blue;
// }
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
.og-bg {
  background: rgb(233, 233, 233);
  background: linear-gradient(90deg, rgba(233, 233, 233, 1) 1%, rgb(227, 231, 235) 100%);
  border: 1px solid rgba(233, 233, 233, 1);
}
.lo-bg {
  background: rgb(255, 197, 158);
  background: linear-gradient(90deg, rgba(255, 197, 158, 1) 1%, rgba(255, 156, 89, 1) 78%);
  border: 1px solid $light-orange;
}
.search__input {
  min-height: 40px;
  display: block;
  padding: 8px 40px 8px 8px;
  border-radius: 5px;
  border: 1px solid #e8e8e8;
  background: #fff;
  font-size: 14px;
  box-shadow: none;
  width: 70%;
}
.wide-input {
  width: 27vw;
}
.subtitle-area {
  display: block;
  width: 27vw;
  font-size: 13px;
  color: $light-gray-blue;
  margin-left: 4px;
  margin-top: 4px;
  margin-bottom: 1.5rem;

  span {
    color: $dark-green;
  }
}
input[type='text']:focus {
  outline: 1px solid $dark-green;
}

span > input[type='checkbox']:checked + label::after {
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

span > input[type='checkbox'] {
  line-height: 2.1ex;
}

span > input[type='checkbox'] {
  position: absolute;
  left: -999em;
}

span > input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

span > input[type='checkbox'] + label::before {
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
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.top-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}
.margin-left {
  margin-left: 8px;
}
.grayscale {
  filter: grayscale(100%);
}
.margin-top {
  margin-top: 1rem;
}
.margin-bottom {
  margin-bottom: 1rem;
}
.no-margin {
  p {
    margin-bottom: 0;
    margin-top: 0;
  }
  span {
    color: $light-gray-blue;
    font-size: 13px;
  }
}

button {
  background-color: $dark-green;
  padding: 11px 6px;
  font-size: 13px;
  border-radius: 4px;
  border: none;
  // outline: 1px solid $dark-green;
  color: $white;

  cursor: pointer;
  transition: all 0.25s;
}
button:hover {
  box-shadow: 0 6px 6px rgba(0, 0, 0, 0.1);
  transform: scale(1.025);
}
button:disabled {
  background-color: $soft-gray;
  color: $light-gray-blue;
  outline: none;
}
.week-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 25vw;
  overflow-x: scroll;
  margin-top: 8px;

  div {
    transition: all 0.2s;
    font-size: 13px;
  }
  label {
    cursor: pointer;
    color: $light-gray-blue;
    margin-right: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 26px;
    width: 26px;
    border-radius: 100%;
    border: 1px solid $soft-gray;
    transition: all 0.2s;
  }
  span {
    display: none;
  }

  div:hover {
    transform: scale(1.15);
    color: $base-gray;
  }
}
.active-option {
  color: $base-gray !important;
  border: 1px solid $light-gray-blue !important;
}
.neg-mar-top {
  margin-top: -4px;
}
.disabled {
  opacity: 0.6;
  cursor: text !important;
}
</style>