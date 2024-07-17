<template>
  <div class="integrations">
    <Modal
      v-if="connectModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleConfirmCancel()
        }
      "
    >
      <!-- connectModal -->
      <div class="invite-form crm-form form-margin-small" style="min-width: 0">
        <div class="header-crm">
          <div class="flex-row-wrapper inner-crm">
            <div class="flex-row" style="margin: 0">
              <!-- <img src="@/assets/images/logo.png" class="logo" alt="" /> -->
              <h3 class="invite-form__title" style="margin-bottom: 0.6rem">Connect CRM</h3>
            </div>
            <div class="flex-row" style="margin: 0">
              <img
                @click="handleConfirmCancel"
                src="@/assets/images/close.svg"
                alt=""
                style="
                  filter: invert(30%);
                  cursor: pointer;
                  width: 20px;
                  height: 20px;
                  /* margin-right: 5px; */
                "
                class="crm-exit"
              />
            </div>
          </div>
        </div>
        <div>
          <p class="modal-card-text">Choose your CRM from the options below.</p>
          <div class="flex-row inner-crm">
            <Multiselect
              placeholder="Select CRM"
              v-model="selectedCRM"
              :options="crmList"
              openDirection="below"
              style="width: 34vw; margin-bottom: 1rem"
              class="custom-picklist-font"
              selectLabel="Enter"
              label="label"
            >
              <template slot="noResult">
                <p class="multi-slot custom-picklist-font">No results. Try loading more</p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon custom-picklist-font">
                  <img src="@/assets/images/search.svg" alt="" />
                  Select CRM
                </p>
              </template>
            </Multiselect>
          </div>
        </div>
        <div class="confirm-cancel-container" style="">
          <div
            class="img-border cancel-button"
            @click="handleConfirmCancel"
            style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem"
          >
            Cancel
          </div>
          <button
            class="img-border green-button"
            :disabled="!selectedCRM"
            @click="onGetAuthLink(selectedCRM ? selectedCRM.value : null)"
            style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem"
          >
            Confirm
          </button>
        </div>
      </div>
    </Modal>
    <Modal
      v-if="confirmModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleConfirmCancel()
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
            <div class="flex-row" style="margin: 0">
              <!-- <img src="@/assets/images/logo.png" class="logo" alt="" /> -->
              <h3 class="invite-form__title">Are you sure?</h3>
            </div>
            <div class="flex-row" style="margin: 0">
              <img
                @click="handleConfirmCancel"
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
        <div class="flex-row inner-crm" style="margin: 0; justify-content: flex-start; width: 90%">
          <h4 class="card-text" style="margin-left: 0; margin-top: 0; margin-bottom: 0.75rem">
            By clicking Disconnect, you will be removing
            {{ this.removeAppFormatted ? this.removeAppFormatted : 'this app' }}.
          </h4>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="confirm-cancel-container" style="width: 90%; margin-bottom: 0.6rem">
            <div
              class="img-border cancel-button"
              @click="handleConfirmCancel"
              style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem"
            >
              Cancel
            </div>
            <button
              class="img-border red-button"
              @click="onRevoke(removeApp)"
              style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem; margin-right: 5%"
            >
              Disconnect
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
    <Modal
      v-if="errorSuccessModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleErrSuccCancel()
        }
      "
    >
      <form class="invite-form crm-form form-margin-small" style="height: 30vh; min-width: 0">
        <div class="header-crm" style="width: 107%">
          <div class="flex-row-wrapper inner-crm" style="border: none">
            <div class="flex-row" style="margin: 0">
              <!-- <h3 class="invite-form__title">Are you sure?</h3> -->
            </div>
            <div class="flex-row" style="margin: 0">
              <img
                @click="handleErrSuccCancel"
                src="@/assets/images/close.svg"
                alt=""
                style="
                  filter: invert(30%);
                  cursor: pointer;
                  width: 22px;
                  height: 22px;
                  margin-right: 5px;
                  margin-top: 10px;
                "
              />
            </div>
          </div>
        </div>
        <div
          class="flex-row"
          style="
            flex-direction: column;
            margin: 0;
            width: 96%;
            height: 13vh;
            justify-content: space-between;
          "
        >
          <img
            v-if="errorOrSuccess === 'premium'"
            src="@/assets/images/chat-lock.svg"
            class="filtered-gray"
            style="height: 40px"
          />
          <img
            v-else-if="errorOrSuccess === 'error'"
            src="@/assets/images/rounded_exclamation.svg"
            class="filtered-red"
            style="height: 40px"
          />
          <img
            v-else
            src="@/assets/images/rounded_check.svg"
            class="green-filter"
            style="height: 40px"
          />
          <h4
            class="card-text"
            style="margin-left: 0; margin-top: 0; margin-bottom: 0.75rem; text-align: center"
          >
            {{ errSuccMessage }}
          </h4>
        </div>
        <div class="invite-form__actions" style="justify-content: center">
          <!-- <div style="width: 10vw;"></div> -->
          <div
            class="confirm-cancel-container"
            style="justify-content: center; width: 96%; margin-bottom: 1rem"
          >
            <div
              class="img-border cancel-button"
              @click="handleErrSuccCancel"
              style="font-size: 13px; margin-top: 0rem; margin-right: 0"
            >
              Close this window
            </div>
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
    <!-- <div class="welcome">
      <p class="inactive">Connect Managr to your favorite Apps</p>
    </div> -->

    <div class="pr-integrations-container">
      <div class="title-container">
        <h1 class="no-text-margin">Integrations</h1>
        <p class="sub-text">Connect your apps to expand functionality.</p>
      </div>
      <div class="integrations__cards">
        <!-- Twitter -->
        <div class="card">
          <div class="card__header" style="">
            <img style="height: 40px; margin-left: -12px" src="@/assets/images/twitter-x.svg" />
          </div>
          <div class="card__body">
            <div class="row-center" style="display: flex">
              <h3 class="card__title">X/Twitter</h3>
              <div v-if="hasTwitterIntegration" class="green-dot"></div>
            </div>
            <p class="card-text">Connect to search Twitter</p>
            <div></div>
            <div class="sep-button-container">
              <div class="separator"></div>
              <button
                v-if="hasTwitterIntegration"
                class="long-button connected"
                style="margin-top: 1rem; margin-bottom: 0.5rem"
                @click="revokeTwitter"
              >
                <div style="margin-left: 4px" v-if="revoking" class="loading-small">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>

                <div v-else>Disconnect</div>
              </button>
              <button
                v-else
                class="long-button"
                style="margin-right: 0; margin-top: 1rem; margin-bottom: 0.5rem"
                @click="twitterAuthorization"
                :disabled="(generatingToken && selectedIntegration == 'TWITTER') || connecting"
              >
                <div
                  style="margin-left: 4px"
                  v-if="generatingToken && selectedIntegration == 'TWITTER'"
                  class="loading-small"
                >
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>

                <div v-else>Connect</div>
              </button>
            </div>
          </div>
        </div>

        <!-- <div class="card">
          <div class="card__header" style="">
            <img style="height: 40px" src="@/assets/images/instagram-11.svg" />
          </div>
          <div class="card__body">
            <div class="row-center" style="display: flex">
              <h3 class="card__title">Instagram</h3>
              <div v-if="hasIgIntegration" class="green-dot"></div>
            </div>
            <p class="card-text">Connect to search Instagram</p>
            <div></div>
            <div class="sep-button-container">
              <div class="separator"></div>

              <button
                v-if="hasIgIntegration"
                class="long-button connected"
                style="margin-top: 1rem; margin-bottom: 0.5rem"
                @click="revokeIg"
              >
                <div style="margin-left: 4px" v-if="revoking" class="loading-small">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>

                <div v-else>Disconnect</div>
              </button>
              <button
                v-else
                class="long-button"
                style="margin-right: 0; margin-top: 1rem; margin-bottom: 0.5rem"
                @click="instagramAuthorization"
                :disabled="(generatingToken && selectedIntegration == 'INSTAGRAM') || connecting"
              >
                <div
                  style="margin-left: 4px"
                  v-if="generatingToken && selectedIntegration == 'INSTAGRAM'"
                  class="loading-small"
                >
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>

                <div v-else>Connect</div>
              </button>
            </div>
          </div>
        </div> -->

        <div class="card">
          <div class="card__header" style="">
            <img style="height: 40px; margin-left: -12px" src="@/assets/images/google.svg" />
          </div>
          <div class="card__body">
            <div class="row-center" style="display: flex">
              <h3 class="card__title">Email</h3>
              <div v-if="hasEmailIntegration" class="green-dot"></div>
            </div>
            <p class="card-text">Connect to send emails</p>
            <div></div>
            <div class="sep-button-container">
              <div class="separator"></div>
              <button
                v-if="hasEmailIntegration"
                class="long-button connected"
                style="margin-top: 1rem; margin-bottom: 0.5rem"
                @click="revokeEmail"
              >
                <div style="margin-left: 4px" v-if="revoking" class="loading-small">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>

                <div v-else>Disconnect</div>
              </button>
              <button
                v-else
                class="long-button"
                style="margin-right: 0; margin-top: 1rem; margin-bottom: 0.5rem"
                @click="emailAuthorization"
                :disabled="(generatingToken && selectedIntegration == 'GOOGLE') || connecting"
              >
                <div
                  style="margin-left: 4px"
                  v-if="generatingToken && selectedIntegration == 'GOOGLE'"
                  class="loading-small"
                >
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>

                <div v-else>Connect</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import SlackOAuth from '@/services/slack'
import ZoomAccount from '@/services/zoom/account/'
import Nylas from '@/services/nylas'
import Salesforce from '@/services/salesforce'
import Hubspot from '@/services/hubspot'
import SalesloftAccount from '@/services/salesloft'
import GongAccount from '@/services/gong'
import OutreachAccount from '@/services/outreach'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
// import { CollectionManager } from '@thinknimble/tn-models'
import Modal from '@/components/InviteModal'
import Loader from '@/components/Loader'

import CollectionManager from '@/services/collectionManager'
import User from '@/services/users'

export default {
  name: 'ConfigureIntegrations',
  props: {},
  components: {
    PulseLoadingSpinnerButton,
    CollectionManager,
    Modal,
    Loader,
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      generatingToken: false,
      crmList: [
        { label: 'Salesforce', value: 'SALESFORCE' },
        { label: 'Hubspot', value: 'HUBSPOT' },
      ],
      // messengerList: [
      //   { label: 'Slack', value: 'SLACK' },
      //   { label: 'Teams', value: 'TEAMS' },
      // ],
      removeApp: '',
      removeAppFormatted: '',
      confirmModal: false,
      connectModal: false,
      errorSuccessModal: false,
      errorOrSuccess: null,
      errSuccMessage: '',
      pulseLoading: false,
      selectedCRM: null,
      // selectedMessenger: null,
      selectedIntegration: null,
      connecting: false,
      revoking: false,
    }
  },
  methods: {
    test(log) {
      console.log(this.user)
    },
    async revokeTwitter() {
      this.revoking = true
      try {
        await User.api.revokeTwitter().then((res) => {
          console.log(res)
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.$store.dispatch('refreshCurrentUser')

        this.revoking = false
      }
    },
    async revokeIg() {
      this.revoking = true
      try {
        await User.api.revokeInstagram().then((res) => {
          console.log(res)
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.$store.dispatch('refreshCurrentUser')

        this.revoking = false
      }
    },
    async onGetAuthLink(integration) {
      if (!integration) {
        return
      }
      integration === 'NYLAS'
        ? confirm(
            'You must check all permission boxes in order for Managr to successfully connect to your calendar!',
          )
        : ''
      this.generatingToken = true
      this.selectedIntegration = integration

      let modelClass = this.selectedIntegrationSwitcher
      try {
        let res
        if (integration === 'SLACK') {
          res = this.onIntegrateSlack()
        } else {
          res = await modelClass.api.getAuthLink()
        }
        if (res.link) {
          window.location.href = res.link
        }
      } finally {
        this.generatingToken = false
      }
    },
    showErrorSuccessModal(errOrSucc, message) {
      // this.$toast('Pay me, bitch.', {
      //   timeout: 2000,
      //   position: 'top-left',
      //   type: 'error',
      //   toastClassName: 'custom',
      //   bodyClassName: ['custom'],
      // })
      this.errorOrSuccess = errOrSucc
      this.errSuccMessage = message
      this.errorSuccessModal = true
    },
    connectApp(app) {
      if (app === 'CRM') {
        this.connectModal = true
      } else {
        this.onGetAuthLink(app)
      }
    },
    async onRevoke(integration) {
      this.generatingToken = true
      this.pulseLoading = true
      this.selectedIntegration = integration
      try {
        await this.selectedIntegrationSwitcher.api.revoke()
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.generatingToken = false
        this.pulseLoading = false
        this.confirmModal = false
      }
    },
    setRemoveApp(appName) {
      if (appName) {
        this.removeApp = appName
        this.removeAppFormatted = appName[0] + appName.slice(1).toLowerCase()
        this.confirmModal = true
      }
    },
    handleConfirmCancel() {
      this.removeApp = ''
      this.removeAppFormatted = ''
      this.confirmModal = false
      this.connectModal = false
    },
    handleErrSuccCancel() {
      this.errorSuccessModal = false
      this.errorOrSuccess = null
      this.errSuccMessage = ''
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
            return res
          }
        }
      } else {
        // if (!this.hasSlackIntegration) {
        try {
          let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.USER)
          if (res.link) {
            window.location.href = res.link
          }
        } catch (e) {
        } finally {
          this.generatingToken = false
          return res
        }
        // }
      }
    },

    async twitterAuthorization() {
      this.connecting = true
      try {
        await User.api.getTwitterToken().then((res) => {
          if (res.link) {
            window.location.href = res.link
          }
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.connecting = false
      }
    },
    async instagramAuthorization() {
      this.connecting = true
      try {
        await User.api.getIgToken().then((res) => {
          if (res.link) {
            window.location.href = res.link
          }
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.connecting = false
      }
    },
    async emailAuthorization() {
      this.connecting = true
      try {
        const res = await User.api.getGoogleToken()
        console.log('GOOGLE RESPONSE', res)
        if (res.link) {
          window.location.href = res.link
        }
      } catch (e) {
        console.log(e)
      } finally {
        this.connecting = false
      }
    },
  },
  mounted() {
    this.test()
  },
  async created() {
    // if there is a code assume an integration has begun
    if (this.$route.query.code) {
      this.generatingToken = true
      this.selectedIntegration = this.$route.query.state
      try {
        const modelClass = this.selectedIntegrationSwitcher
        if (this.selectedIntegration === 'TWITTER') {
          const data = {
            oauth_token: this.$route.query.token,
            oauth_verifier: this.$route.query.oauth_verifier,
          }
          await modelClass.api.getTwitterAuthentication(data).then((res) => {
            console.log('RESPONSE IS HERE: ', res)
          })
        } else if (this.selectedIntegration == 'SALESLOFT') {
          await modelClass.api.authenticate(
            this.$route.query.code,
            this.$route.query.context,
            this.$route.query.scope,
          )
        } else if (this.selectedIntegration === 'INSTAGRAM') {
          const data = {
            code: this.$route.query.code,
          }
          await modelClass.api.getIgAuthorization(data).then((response) => {
            console.log('IG RESPONSE', response)
          })
        } else if (this.selectedIntegration === 'GOOGLE') {
          const data = {
            code: this.$route.query.code,
          }
          console.log(data)
          // await modelClass.api.getGoogleAuthorization(data).then((response) => {
          //   console.log('IG RESPONSE', response)
          // })
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
      }
    }
  },
  computed: {
    userIsStaff() {
      return !!this.user.IsStaff
    },
    isOnboarding() {
      return this.$store.state.user.onboarding
    },
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    userRole() {
      return this.$store.state.user.role
    },
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    hasHubspotIntegration() {
      return !!this.$store.state.user.hubspotAccount
    },
    hasZoomIntegration() {
      return !!this.$store.state.user.hasZoomIntegration
    },
    hasTwitterIntegration() {
      return !!this.$store.state.user.hasTwitterIntegration
    },
    hasEmailIntegration() {
      return !!this.$store.state.user.hasGoogleIntegration
    },
    hasGongIntegration() {
      return !!this.$store.state.user.gongAccount && this.$store.state.user.hasGongIntegration
    },
    hasOutreachIntegration() {
      return (
        !!this.$store.state.user.outreachAccount && this.$store.state.user.hasOutreachIntegration
      )
    },
    isPR() {
      return this.$store.state.user.role === 'PR'
    },
    hasSalesloftIntegration() {
      return (
        !!this.$store.state.user.salesloftAccount && this.$store.state.user.hasSalesloftIntegration
      )
    },
    orgHasSlackIntegration() {
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    hasIgIntegration() {
      return !!this.$store.state.user.hasInstagramIntegration
    },
    hasNylasIntegration() {
      return !!this.$store.state.user.nylas
    },
    userCanIntegrateSlack() {
      return this.$store.state.user.isAdmin
    },
    userCRM() {
      return this.$store.state.user.crm
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
        case 'SALESLOFT':
          return SalesloftAccount
        case 'GONG':
          return GongAccount
        case 'OUTREACH':
          return OutreachAccount
        case 'TWITTER':
          return User
        case 'INSTAGRAM':
          return User
        case 'GOOGLE':
          return User
        default:
          return null
      }
    },
    user() {
      return this.$store.state.user
    },
    slackButtonMessage() {
      if (!this.orgHasSlackIntegration && this.userCanIntegrateSlack) {
        return 'Connect'
      } else if (this.orgHasSlackIntegration && !this.hasSlackIntegration) {
        return 'Connect'
      } else {
        return 'N/A'
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/modals';

.shimmer {
  display: inline-block;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  max-width: 200px;
  filter: invert(40%);
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}
.right-tooltip {
  position: relative;
  display: inline-block;
}

.right-tooltip .right-tooltiptext {
  visibility: hidden;
  width: 150px;
  background-color: $base-gray;
  opacity: 0.9;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  position: absolute;
  z-index: 1;
  top: -2px;
  left: 115%;
}

/* Show the tooltip text when you mouse over the tooltip container */
.right-tooltip:hover .right-tooltiptext {
  visibility: visible;
}

a {
  text-decoration: none;
  color: white !important;
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.img-border {
  @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 6px;
  margin-right: 8px;
  margin-top: 0.5rem;
}
// .card-button-margin {
//   margin-top: 0.
// }
.coral {
  color: $coral !important;
  border: 1px solid $soft-gray;
  cursor: pointer;
}
.gray {
  color: $light-gray-blue !important;
  border: 1px solid $soft-gray;
  cursor: pointer;
}
.gray:hover {
  scale: 1 !important;
  box-shadow: none !important;
}
.red-button {
  @include button-danger();
}
// .filter-dot {
//   height: 0.4rem;
//   filter: invert(80%);
//   margin-left: 0.5rem;
//   filter: invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg) brightness(93%) contrast(89%);
// }
.filter-loft {
  filter: brightness(0%) invert(7%) sepia(31%) saturate(2639%) hue-rotate(115deg) brightness(92%)
    contrast(91%);
}
.integrations {
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  // padding: 0px 0px 0px 96px;
  margin-top: 4rem;
  overflow-x: auto;
  &__cards {
    display: flex;
    flex-direction: row;
    padding: 0.5rem 1.5rem;
    flex-wrap: wrap;
    justify-content: flex-start;
    // width: 96vw;
    margin-top: 4px;
    @media only screen and (max-width: 600px) {
      flex-direction: column;
    }
  }
  @media only screen and (max-width: 600px) {
    margin-top: 0;
    height: 90vh;
  }
}
// .gold-filter {
//   filter: invert(81%) sepia(35%) saturate(920%) hue-rotate(343deg) brightness(91%) contrast(90%);
//   margin-left: 4px;
// }
.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 116%;
}
// .card:hover {
//   transform: scale(1.015);
//   box-shadow: 1px 2px 2px $very-light-gray;
// }
// .card-outer {
//   border: 2px solid #72FFC1;
//   background-color: #72FFC1;
//   border-radius: 8px;

// }
.card {
  background-color: $white;
  // padding: 16px 24px;
  padding: 16px;
  border: 1px solid $soft-gray;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  margin-right: 1rem;
  margin-bottom: 1rem;
  // width: 420px;
  // width: 320px;
  width: 18.5vw;
  min-height: 144px;
  transition: all 0.25s;
  @media only screen and (max-width: 600px) {
    width: 70vw;
  }

  &__header {
    display: flex;
    align-items: center;
    // justify-content: center;
    padding: 4px 0px;
    border-radius: 6px;
    margin-left: 12px;

    img {
      margin: 0;
      height: 25px;
    }
  }

  &__body {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin-left: 12px;
    h3 {
      margin-top: 0.5rem;
      margin-bottom: 0;
      padding: 0;
      font-size: 18px;
    }
    p {
      font-size: 12px;
    }
  }
}
.card-img-border {
  // padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40px;
  width: 40px;
  // border: 1px solid $soft-gray;
  border-radius: 4px;
  margin-right: 0.15rem;
}
.lb-bg {
  background-color: $very-light-blue;
  border: 1px solid $very-light-blue;
}
.vlb-bg {
  background: rgb(181, 222, 255);
  background: linear-gradient(90deg, rgba(181, 222, 255, 1) 1%, rgba(127, 196, 251, 1) 100%);
  border: 1px solid $very-light-blue;
}
.og-bg {
  background: rgb(233, 233, 233);
  background: linear-gradient(90deg, rgba(233, 233, 233, 1) 1%, rgb(227, 231, 235) 100%);
  border: 1px solid rgba(233, 233, 233, 1);
}
.lg-bg {
  background: rgb(140, 255, 191);
  background: linear-gradient(90deg, rgba(140, 255, 191, 1) 1%, rgba(106, 198, 146, 1) 90%);
  border: 1px solid $white-green;
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

  //   background: rgb(238,174,202);
  // background: radial-gradient(circle, rgba(238,174,202,1) 0%, rgba(148,187,233,1) 100%);
}
.lp-bg {
  background: rgb(221, 184, 255);
  background: linear-gradient(90deg, rgba(221, 184, 255, 1) 1%, rgba(193, 122, 255, 1) 97%);
  border: 1px solid $light-purple;
}
.vlp-bg {
  background: rgb(197, 194, 255);
  background: linear-gradient(90deg, rgba(197, 194, 255, 1) 1%, rgba(145, 139, 255, 1) 97%);
  border: 1px solid $light-purple;
}
.lo-bg {
  background: rgb(255, 197, 158);
  background: linear-gradient(90deg, rgba(255, 197, 158, 1) 1%, rgba(255, 156, 89, 1) 78%);
  border: 1px solid $light-orange;
}
.required {
  filter: invert(50%) sepia(100%) saturate(901%) hue-rotate(323deg) brightness(110%) contrast(96%);
  margin-left: 4px;
}
.card-text {
  font-size: 14px !important;
  color: $light-gray-blue;
  margin-top: 0.5rem;
  // text-align: center;
}
.modal-card-text {
  font-size: 14px;
  color: $light-gray-blue;
  margin-top: 0.5rem;
  margin-left: 5%;
  width: 90%;
}
// .privacy {
//   color: $base-gray;
//   font-size: 12px;
// }
// .lock {
//   height: 1rem;
// }
a {
  text-decoration: none;
  color: $grape;
  font-weight: bold;
}
.inactive {
  color: $light-gray-blue;
  padding: 4px 8px;
}
.welcome {
  margin-top: -4px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 60vw;
  margin-left: 88px;
  padding: 0px 4px;
  overflow: hidden;
  h3 {
    font-size: 19px;
    font-weight: 500;
    margin-left: 28px;
    color: $light-gray-blue;
    letter-spacing: 0.7px;
  }

  p {
    font-size: 14px;
    letter-spacing: 0.1px;
  }
  div {
    display: flex;
    flex-direction: row;
    align-items: center;

    // p {
    //   margin-right: 16px;
    // }
  }
}
.orange_button {
  @include gray-text-button();
  color: $dark-green;
  padding: 6px 12px;
  font-size: 11px;
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
// .modal-form {
//   width: 100%;
//   background-color: $white;
//   height: 40vh;
//   // justify-content: space-evenly;
// }
.confirm-form {
  // width: 37vw;
  height: 24vh;
  z-index: 30;
}
.crm-form {
  height: 34vh;
  width: 32vw;
  @media only screen and (max-width: 600px) {
    width: 70vw;
  }
}
.form-margin-small {
  margin-top: 10rem;
}
.header {
  // background-color: $soft-gray;
  width: 100%;
  // border-bottom: 1px solid $soft-gray;
  position: relative;
  border-top-right-radius: 4px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-top-left-radius: 4px;
  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: flex-start;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $base-gray;
  }
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
.inner-crm {
  border-bottom: 1px solid $soft-gray;
  width: 90%;
  padding-bottom: 0.4rem;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  margin: 0 5%;
  letter-spacing: 1px;
}
.flex-row-wrapper {
  display: flex;
  justify-content: space-between;
}
.logo {
  height: 24px;
  margin-left: 0.25rem;
  margin-right: 0.5rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.invite-button {
  @include primary-button();
  // margin-top: 2.5rem;
  margin-bottom: 1rem;
  width: 15vw;
  font-size: 16px;
}
.modal-button {
  @include primary-button();
  // box-shadow: none;
  margin-top: 1rem;
  // height: 2.5rem;
  // width: 19rem;
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
  padding: 12px;
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
.side-wrapper .side-tooltip {
  display: block;
  width: 180px;
  height: auto;
  position: absolute;
  // top: -10px; // for double line
  top: -5px; // for single line
  left: 30px;
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
.side-wrapper .side-tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: 40%;
  left: 0%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-icon:hover .side-tooltip {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.side-wrapper .side-icon:hover span,
.side-wrapper .side-icon:hover .side-tooltip {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}
.side-wrapper .side-workflow:hover,
.side-wrapper .side-workflow:hover .side-tooltip,
.side-wrapper .side-workflow:hover .side-tooltip::before {
  // margin-top: 1rem;
  background: $grape;
  color: #ffffff;
}
.side-icon:hover {
  transition: all 0.1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  // transition: all .3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  img {
    filter: invert(90%);
  }
}
.filtered-red {
  filter: invert(43%) sepia(45%) saturate(682%) hue-rotate(308deg) brightness(109%) contrast(106%);
}
.filtered-gray {
  filter: invert(45%);
}
.green-filter {
  filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
    contrast(82%);
  height: 14px;
}
.green-text {
  @include white-button();
  // color: $dark-green;
  border: 1px solid $soft-gray;
  cursor: pointer;
}

.connected {
  background-color: white !important;
  color: $coral !important;
}

.long-button {
  @include white-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  cursor: pointer;
  width: 15vw;
  display: flex;
  align-items: center;
  padding: 10px 8px;
  font-family: $thin-font-family;
  color: white;
  background-color: $dark-black-blue;
  @media only screen and (max-width: 600px) {
    width: 60vw;
  }
}

.long-button:disabled {
  padding: 10px 8px;
  background-color: $off-white;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.separator {
  border-top: 1px solid $soft-gray;
  width: 15vw;
  // margin: 0rem 0 0.1rem 0;
  @media only screen and (max-width: 600px) {
    width: 60vw;
  }
}
.confirm-cancel-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 94%;
}
.green-button {
  @include primary-button();
}
.cancel-button {
  @include gray-button();
}
// .custom-picklist-font {
//   font-size: 12px;
// }
// ::v-deep .custom-picklist-font input::placeholder {
//   font-size: 12px;
// }
// ::v-deep .custom-picklist-font span {
//   font-size: 12px;
// }
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
  min-width: 250px;
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}
.sep-button-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.padding-button {
  padding: 0.8rem 1.2rem;
}
.title-container {
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
  margin-top: 2rem;
  margin-bottom: 1rem;
  margin-left: 1.5rem;
  @media only screen and (max-width: 600px) {
    margin-top: 0.55rem;
  }
}
.no-text-margin {
  margin: 0;
}
.sub-text {
  color: $light-gray-blue;
  margin-top: 16px;
  font-size: 14px;
  font-weight: bold;
  font-family: $thin-font-family;
  span {
    font-weight: normal;
    word-wrap: break-word;
  }
}
.pr-integrations-container {
  width: 100vw;
  padding-left: 32px;
  font-family: $thin-font-family;
}
.wrapper {
  display: flex;
  align-items: center;
  // background-color: ;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  // bottom: 100%;
  bottom: 65%;
  color: #fff;
  display: block;
  left: 80px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 120px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}
.loading-small {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 0;
}

.green-dot {
  width: 4px;
  height: 4px;
  background: $dark-green;
  border-radius: 50%;
  margin-left: 8px;
}

.row-center {
  flex-direction: row;
  align-items: center;
}

.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
