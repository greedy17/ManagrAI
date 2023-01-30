<template>
  <div class="onboarder">
    <Modal
      dimmed
      v-if="formModalOpen"
      @close-modal="
        () => {
          toggleFormModal()
        }
      "
    >
      <div v-if="resource == 'Opportunity'" class="form-modal">
        <UpdateOppForm @close-form-modal="toggleFormModal()" />
      </div>
      <div v-else-if="resource == 'Contact'" class="form-modal">
        <CreateContactForm @close-form-modal="toggleFormModal()" />
      </div>
    </Modal>
    <Modal
      dimmed
      v-if="workflowModalOpen"
      @close-modal="
        () => {
          toggleWorkflowModal()
        }
      "
    >
      <div class="meeting-modal">
        <LogZoom @close-form-modal="toggleWorkflowModal()" />
      </div>
    </Modal>
    <div class="header">
      <h1>Welcome {{ user.firstName }}!</h1>
      <p>
        Lets start automating your sales process so you can
        <span class="gray">reclaim your time and focus on selling.</span>
      </p>
    </div>

    <article :class="hasSalesforceIntegration && hasNylasIntegration ? 'green-border' : ''">
      <div :class="hasSalesforceIntegration && hasNylasIntegration ? 'green-bg' : ''" class="step1">
        1
      </div>
      <small>3 SIMPLE STEPS</small>
      <h3 v-if="!hasSalesforceIntegration && !hasNylasIntegration">Step 1: Integrations</h3>

      <div v-else>
        <h3>Step 1: Completed <span>✅</span></h3>
        <!-- <p class="gray-blue">Integrations</p> -->
      </div>

      <div class="section">
        <section class="section__body">
          <div class="card">
            <div class="card__header vlb-bg" style="padding-left: 32px; padding-right: 32px">
              <img style="height: 30px; width: auto" src="@/assets/images/salesforce.png" />
            </div>

            <div class="card__body">
              <h3>Salesforce</h3>
              <p style="font-size: 12px" class="card-text">
                Sync Accounts, Opportunities, & Contacts
              </p>
              <div>
                <PulseLoadingSpinnerButton
                  v-if="!hasSalesforceIntegration"
                  @click="onGetAuthLink('SALESFORCE')"
                  class="secondary-button"
                  text="Connect"
                  :loading="generatingToken"
                  >Connect</PulseLoadingSpinnerButton
                >

                <div v-else>
                  <p class="green">Connected</p>
                </div>
              </div>
            </div>
          </div>
          <div class="card">
            <div class="card__header lbp-bg">
              <img src="@/assets/images/gmailCal.png" style="margin-right: 16px; height: 32px" />
              <img src="@/assets/images/outlookMail.png" style="height: 32px" />
            </div>

            <div class="card__body">
              <h3>Calendar</h3>
              <p class="card-text">Accesses your upcoming meetings</p>
              <div>
                <PulseLoadingSpinnerButton
                  v-if="!hasNylasIntegration"
                  @click="onGetAuthLink('NYLAS')"
                  class="secondary-button"
                  text="Connect"
                  :loading="generatingToken"
                  >Connect</PulseLoadingSpinnerButton
                >
                <div v-else>
                  <p class="green">Connected</p>
                </div>
              </div>
            </div>
          </div>
          <div class="card">
            <div class="card__header lr-bg" style="padding-left: 32px; padding-right: 32px">
              <img style="height: 38px" src="@/assets/images/slackLogo.png" />
            </div>

            <div class="card__body">
              <h3>Slack</h3>
              <p class="card-text">Suggested for optimal experience</p>
              <div>
                <PulseLoadingSpinnerButton
                  v-if="!hasSlackIntegration"
                  :disabled="
                    (!orgHasSlackIntegration && !userCanIntegrateSlack) || hasSlackIntegration
                  "
                  @click="onIntegrateSlack"
                  class="secondary-button"
                  text="Connect"
                  :loading="generatingToken"
                  >Connect</PulseLoadingSpinnerButton
                >

                <div v-else>
                  <p class="green">Connected</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </article>

    <article
      :class="
        updateOpportunityFields &&
        updateOpportunityFields.length > 2 &&
        createContactFields &&
        createContactFields.length > 0
          ? 'green-border'
          : ''
      "
    >
      <div
        :class="
          updateOpportunityFields &&
          updateOpportunityFields.length > 2 &&
          createContactFields &&
          createContactFields.length > 0
            ? 'green-bg'
            : ''
        "
        class="step1"
      >
        2
      </div>
      <small>3 SIMPLE STEPS</small>

      <h3
        v-if="
          updateOpportunityFields &&
          updateOpportunityFields.length > 2 &&
          createContactFields &&
          createContactFields.length > 0
            ? 'green-bg'
            : ''
        "
      >
        Step 2: Completed <span>✅</span>
      </h3>

      <h3 v-else>Step 2: Forms</h3>

      <section class="section">
        <div class="section__body">
          <div style="width: 390px" class="card">
            <div style="margin-left: 0" class="card__body">
              <h3>Update Opportunity</h3>
              <p>View/edit opportunities via Managr</p>
              <button
                v-if="updateOpportunityFields && updateOpportunityFields.length < 3"
                @click="toggleFormModal('CREATE', 'Opportunity')"
                class="secondary-button"
              >
                Activate
              </button>
              <div v-else>
                <p class="green">Active</p>
              </div>
            </div>
          </div>

          <div style="width: 390px" class="card">
            <div style="margin-left: 0" class="card__body">
              <h3>Create Contact</h3>
              <p>Update/create Contacts via Managr</p>
              <button
                v-if="createContactFields && createContactFields.length < 1"
                @click="toggleFormModal('UPDATE', 'Contact')"
                class="secondary-button"
              >
                Activate
              </button>

              <div v-else>
                <p class="green">Active</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </article>

    <article :class="hasZoomChannel ? 'green-border' : ''">
      <div :class="hasZoomChannel ? 'green-bg' : ''" class="step1">3</div>
      <small>3 SIMPLE STEPS</small>
      <h3 v-if="!hasZoomChannel">Step 3: Workflows</h3>
      <h3>Step 3: Completed <span>✅</span></h3>

      <section class="section">
        <div class="section__body">
          <div style="width: 390px" class="card">
            <div style="margin-left: 0" class="card__body">
              <h3>Log Meeting</h3>
              <p>Let Managr keep track of all of your meetings.</p>
              <button v-if="!hasZoomChannel" @click="toggleWorkflowModal" class="secondary-button">
                Activate
              </button>
              <div v-else>
                <p class="green">Active</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </article>

    <!-- <footer>
      <button class="secondary-button">Continue</button>
    </footer> -->
  </div>
</template>

<script>
import Modal from '@/components/InviteModal'
import SlackOAuth from '@/services/slack'
import UpdateOppForm from '@/views/settings/UpdateOppForm'
import CreateContactForm from '@/views/settings/CreateContactForm'
import LogZoom from '@/views/settings/OnboardingLogMeeting'
import ZoomAccount from '@/services/zoom/account/'
import Nylas from '@/services/nylas'
import Salesforce from '@/services/salesforce'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

export default {
  name: 'Onboarder',
  components: {
    Modal,
    UpdateOppForm,
    CreateContactForm,
    LogZoom,
    PulseLoadingSpinnerButton,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      selectedIntegration: null,
      formModalOpen: false,
      workflowModalOpen: false,
      updateOpportunityFields: null,
      createContactFields: null,
      resource: 'Opportunity',
      generatingToken: false,
      type: 'UPDATE',
    }
  },
  async created() {
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
      }
    }

    this.getAllForms()
  },
  methods: {
    toggleFormModal(type, resource) {
      this.type = type
      this.resource = resource
      this.formModalOpen = !this.formModalOpen
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
        this.generatingToken = false
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
            this.generatingToken = false
          }
        }
      }
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.createContactFields = res.filter(
          (form) => form.formType === 'CREATE' && form.resource === 'Contact',
        )[0].fieldsRef

        this.updateOpportunityFields = res.filter(
          (form) => form.formType === 'UPDATE' && form.resource === 'Opportunity',
        )[0].fieldsRef
      } catch (e) {
        console.log(e)
      }
    },
  },
  computed: {
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.secondary-button {
  box-shadow: none;
  font-size: 13px;
  border: 1px solid $soft-gray;
  background-color: white;
  color: $base-gray;
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
// .gray-blue {
//   color: $light-gray-blue;
// }
.header {
  letter-spacing: 0.75px;
  color: $base-gray;
  border-bottom: 1px solid $soft-gray;
  width: 87vw;
  padding-bottom: 16px;
  margin-bottom: 32px;

  p {
    color: $light-gray-blue;
  }
  h1 {
    font-weight: bold;
    letter-spacing: 1px;
  }
}
small {
  font-size: 11px;
  color: $dark-green;
}
.section {
  color: $base-gray;
  width: 87vw;

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
.step1 {
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
.card {
  background-color: $white;
  padding: 16px 24px;
  border: 1px solid #e8e8e8;
  margin-right: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: row;
  width: 420px;
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
.form-modal {
  border-radius: 8px;
  padding: 4px 16px;
  height: 100%;
  width: auto;
  overflow: scroll;
  background-color: white;
  position: relative;

  &__footer {
    position: absolute;
    bottom: 0;
    right: 0;
    z-index: 10;
    padding: 16px;
  }
}
.meeting-modal {
  border-radius: 8px;
  padding: 4px 16px;
  height: 75%;
  width: auto;
  overflow: hidden;
  background-color: white;
  position: relative;

  &__footer {
    position: absolute;
    bottom: 0;
    right: 0;
    z-index: 10;
    padding: 16px;
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
</style>