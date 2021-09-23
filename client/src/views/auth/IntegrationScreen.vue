<template>
  <div class="integrations">
    <h2 class="title">Connect your apps to Managr</h2>
    <p style="font-weight: bold; margin-top: -0.5rem; margin-bottom: 2rem; color: #beb5cc">
      Managr utilizes a secure oAuth connection
    </p>

    <!-- <div
      v-if="!hasSalesforceIntegration && user.isAdmin"
      class="slack-button slack-button--disabled"
      text="Continue to Slack Form Builder"
    >
      Slack Form Builder
    </div> -->

    <div class="integrations__cards">
      <div class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/salesforce.png" />
          <h3 class="card__title">Salesforce</h3>
          <PulseLoadingSpinnerButton
            v-if="!hasSalesforceIntegration"
            @click="onGetAuthLink('SALESFORCE')"
            class="orange_button"
            style="margin-left: 0.5rem"
            text="Connect"
            :loading="generatingToken && selectedIntegration == 'SALESFORCE'"
            >Connect</PulseLoadingSpinnerButton
          >
          <PulseLoadingSpinnerButton
            text="Revoke"
            :loading="generatingToken && selectedIntegration == 'SALESFORCE'"
            @click="onRevoke('SALESFORCE')"
            v-else
            class="revoke"
          ></PulseLoadingSpinnerButton>
        </div>
        <p v-if="!hasSalesforceIntegration" class="card-text">
          Sync Accounts, Opportunities, & Contacts
        </p>
        <p v-else class="connected">Connected</p>
      </div>

      <div class="card">
        <div class="card__header">
          <img
            class="card-img card-img__radius"
            src="@/assets/images/zoom.png"
            style="height: 3rem; width: 3rem"
          />
          <h3 class="card__title" style="margin-right: 1rem">Zoom</h3>
          <PulseLoadingSpinnerButton
            v-if="!hasZoomIntegration"
            :disabled="hasZoomIntegration"
            @click="onGetAuthLink('ZOOM')"
            class="orange_button"
            text="Connect"
            :loading="generatingToken && selectedIntegration == 'ZOOM'"
          ></PulseLoadingSpinnerButton>
          <div v-else>
            <PulseLoadingSpinnerButton
              text="Revoke"
              :loading="generatingToken && selectedIntegration == 'ZOOM'"
              @click="onRevoke('ZOOM')"
              class="revoke__"
            ></PulseLoadingSpinnerButton>
            <PulseLoadingSpinnerButton
              text="Refresh"
              :loading="generatingToken && selectedIntegration == 'ZOOM'"
              @click="onGetAuthLink('ZOOM')"
              class="orange__button"
            ></PulseLoadingSpinnerButton>
          </div>
        </div>

        <p v-if="!hasZoomIntegration" class="card-text">
          Activates the meeting workflow automation.
        </p>
        <p v-else class="connected">Connected</p>
      </div>

      <div class="card">
        <div class="card__header">
          <img style="height: 3rem" src="@/assets/images/slackLogo.png" />
          <h3 class="card__title" style="margin-right: 1rem">Slack</h3>
          <PulseLoadingSpinnerButton
            v-if="
              (!orgHasSlackIntegration && userCanIntegrateSlack) ||
              (orgHasSlackIntegration && !hasSlackIntegration)
            "
            :disabled="(!orgHasSlackIntegration && !userCanIntegrateSlack) || hasSlackIntegration"
            @click="onIntegrateSlack"
            class="orange_button"
            :text="slackButtonMessage"
            :loading="generatingToken && selectedIntegration == 'SLACK'"
          ></PulseLoadingSpinnerButton>
          <div v-else-if="hasSlackIntegration && orgHasSlackIntegration">
            <PulseLoadingSpinnerButton
              @click="onRevoke('SLACK')"
              class="revoke__"
              text="Revoke"
              :loading="generatingToken && selectedIntegration == 'SLACK'"
            ></PulseLoadingSpinnerButton>
            <PulseLoadingSpinnerButton
              v-if="userCanIntegrateSlack"
              @click="onRefreshSlack"
              class="orange__button"
              text="Refresh"
              :loading="generatingToken && selectedIntegration == 'SLACK'"
            ></PulseLoadingSpinnerButton>
          </div>
        </div>

        <p
          v-if="
            (!orgHasSlackIntegration && userCanIntegrateSlack) ||
            (orgHasSlackIntegration && !hasSlackIntegration)
          "
          class="card-text"
        >
          Connect your company or personal worskspace
        </p>
        <p v-else class="connected">Connected</p>
      </div>

      <div class="card">
        <div class="card__header">
          <img
            class="card-img"
            src="@/assets/images/gmailCal.png"
            style="margin-right: 1rem; height: 2.5rem; width: 2.5rem"
          />
          <img class="card-img" src="@/assets/images/outlookMail.png" style="height: 3rem" />
          <h3 class="card__title">Calendar</h3>
          <PulseLoadingSpinnerButton
            v-if="!hasNylasIntegration"
            @click="onGetAuthLink('NYLAS')"
            style="margin-left: 1rem"
            class="orange_button"
            text="Connect"
            :loading="generatingToken && selectedIntegration == 'NYLAS'"
          ></PulseLoadingSpinnerButton>
          <PulseLoadingSpinnerButton
            text="Revoke"
            :loading="generatingToken && selectedIntegration == 'NYLAS'"
            v-else
            @click="onRevoke('NYLAS')"
            class="revoke"
          ></PulseLoadingSpinnerButton>
        </div>

        <p v-if="!hasNylasIntegration" class="card-text">
          Accesses your upcoming meetings + attendees
        </p>
        <p v-else class="connected">Connected</p>
        <!-- <div style="margin-bottom: 0.5rem; width: 15rem">
          <GoogleButton
            @click="onGetAuthLink('NYLAS')"
            :loading="generatingToken && selectedIntegration == 'NYLAS'"
            v-if="!hasNylasIntegration"
          />
        </div> -->
      </div>

      <div class="card">
        <div class="card__header">
          <img style="height: 1.5rem" src="@/assets/images/salesloftLogo.jpeg" />
          <h3 class="card__title">Salesloft</h3>
          <p class="card-text" style="margin-left: 1rem; font-size: 16px">Coming Soon...</p>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <img style="height: 3rem" src="@/assets/images/gong.png" />
          <h3 class="card__title">Gong</h3>
          <p class="card-text" style="margin-left: 1rem; font-size: 16px">Coming Soon...</p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <img style="height: 6rem" src="@/assets/images/hubspott.png" />
          <h3 class="card__title">Hubspot</h3>
          <p class="card-text" style="margin-left: 1rem; font-size: 16px">Coming Soon...</p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <img
            class="card-img card-img__radius"
            src="@/assets/images/salesloft.png"
            style="height: 3rem; width: 3rem"
          />
          <h3 class="card__title">Salesloft</h3>
        </div>
        <p class="card-text">Put Contacts right into a Cadence from Slack</p>
        <PulseLoadingSpinnerButton
          v-if="!hasSalesloftIntegration && user.isAdmin"
          :disabled="hasSalesloftIntegration"
          @click="onGetAuthLink('SALESLOFT')"
          class="primary-button"
          text="Connect"
          :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
        ></PulseLoadingSpinnerButton>
        <div
          v-else-if="hasSalesloftIntegration && user.isAdmin"
          style="display: flex; justify-content: space-between"
        >
          <PulseLoadingSpinnerButton
            text="Revoke"
            :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
            @click="onRevoke('SALESLOFT')"
            class="btn btn--danger"
          ></PulseLoadingSpinnerButton>
          <PulseLoadingSpinnerButton
            text="Refresh Token"
            :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
            @click="onGetAuthLink('SALESLOFT')"
            class="secondary-button"
          ></PulseLoadingSpinnerButton>
        </div>
        <p v-else-if="hasSalesloftIntegration && !user.isAdmin">Salesloft is connected!</p>
        <p v-else>Contact your organization admin to add Salesloft</p>
      </div>

      <div class="card">
        <div class="card__header">
          <img style="height: 3.5rem" src="@/assets/images/teamsLogo.png" />
          <h3 class="card__title">Teams</h3>
          <p class="card-text" style="margin-left: 1rem; font-size: 16px">Coming Soon...</p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <img style="height: 3rem" src="@/assets/images/googleDrive.png" />
          Google Drive
          <p class="card-text" style="margin-left: 1rem; font-size: 16px">Coming Soon...</p>
        </div>
      </div>

      <div>
        <PulseLoadingSpinnerButton
          v-if="hasSalesforceIntegration && user.isAdmin"
          @click="goToSlackFormBuilder"
          class="slack-button"
          text="Continue"
          :loading="false"
        ></PulseLoadingSpinnerButton>
        <PulseLoadingSpinnerButton
          v-if="!hasSalesforceIntegration && user.isAdmin"
          class="disabled-button"
          text="Continue"
          :loading="false"
        ></PulseLoadingSpinnerButton>
      </div>

      <div>
        <PulseLoadingSpinnerButton
          v-if="hasSalesforceIntegration && !user.isAdmin"
          @click="goToSlackFormBuilder"
          class="slack-button"
          text="Continue"
          :loading="false"
        ></PulseLoadingSpinnerButton>
        <PulseLoadingSpinnerButton
          v-if="!hasSalesforceIntegration && !user.isAdmin"
          class="disabled-button"
          text="Continue"
          :loading="false"
        ></PulseLoadingSpinnerButton>
      </div>
    </div>

    <img class="lock" src="@/assets/images/whiteLock.png" />
    <p class="privacy"><strong>SOC2</strong> certified, and <strong>GDPR</strong> compliant</p>
    <!-- <p>
      <a href="https://managr.ai/terms-of-service" target="_blank">Terms of Service</a>
      |
      <a href="https://managr.ai/documentation" target="_blank">Documentation</a>
      |
      <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
    </p> -->
  </div>
</template>

<script>
/**
 * Page that shows a grid of all possible integrations and 'Connect' buttons.
 */

import SlackOAuth from '@/services/slack'
import ZoomAccount from '@/services/zoom/account/'
import Nylas from '@/services/nylas'
import Salesforce from '@/services/salesforce'
import SalesloftAccount from '@/services/salesloft'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import GoogleButton from '@/components/GoogleButton'

export default {
  name: 'Integrations',
  components: { PulseLoadingSpinnerButton, GoogleButton },
  data() {
    return {
      generatingToken: false,
      authLink: null,
      selectedIntegration: null,
    }
  },
  methods: {
    goToSlackFormBuilder() {
      this.$router.push({ name: 'Configure' })
    },
    goToSmartAlerts() {
      this.$router.push({ name: 'ListTemplates' })
    },
    async onGetAuthLink(integration) {
      this.generatingToken = true
      this.selectedIntegration = integration
      const modelClass = this.selectedIntegrationSwitcher
      try {
        const res = await modelClass.api.getAuthLink()
        if (res.link) {
          window.location.href = res.link
        }
      } finally {
        this.generatingToken = false
      }
    },
    async onRevoke(integration) {
      this.generatingToken = true
      this.selectedIntegration = integration
      try {
        await this.selectedIntegrationSwitcher.api.revoke()
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.generatingToken = false
      }
    },
    async onIntegrateSlack() {
      const confirmation = confirm(
        'Integrating Managr to your slack workspace will request access to a channel (you can choose a new one or an existing one) we will post a message letting the members of that channel know they can now integrate their Slack accounts',
      )
      if (!confirmation) {
        return
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
    async onRefreshSlack() {
      const confirmation = confirm('This will refresh the access token for the workspace')
      if (!confirmation) {
        return
      }
      this.generatingToken = true
      if (this.orgHasSlackIntegration && this.userCanIntegrateSlack) {
        try {
          let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.WORKSPACE)
          if (res.link) {
            window.location.href = res.link
          }
        } finally {
          this.generatingToken = false
        }
      }
    },
  },
  async created() {
    // if there is a code assume an integration has begun
    if (this.$route.query.code) {
      this.generatingToken = true
      this.selectedIntegration = this.$route.query.state // state is the current integration name

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
          // auto sends a channel message, will also send a private dm
          await SlackOAuth.api.generateAccessToken(this.$route.query.code)
        }
      } catch (e) {
        let { response } = e
        if (response && response.status >= 400 && response.status < 500 && response.status != 401) {
          let { data } = response
          if (data.timezone) {
            this.$Alert.alert({
              type: 'error',
              message:
                '<h3>We could not retrieve your timezone from zoom, to fix this please login to the zoom.us portal through a browser and return to managr to reintegrate</h3>',
            })
          }
        }
      } finally {
        await this.$store.dispatch('refreshCurrentUser')
        this.generatingToken = false
        this.selectedIntegration = null
        this.$router.replace({
          name: 'Integrations',
          params: {},
        })
      }
    }
  },
  computed: {
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    hasZoomIntegration() {
      return !!this.$store.state.user.zoomAccount && this.$store.state.user.hasZoomIntegration
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
        case 'SALESLOFT':
          return SalesloftAccount
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

.integrations {
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
  }
  &__subtitle {
    font-size: 14px;
    margin-bottom: 2rem;
  }
}

.card {
  background-color: $panther;
  border: none;
  width: 10rem;
  height: 20vh;
  margin-right: 1rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 4px 7px black;
  @media only screen and (min-width: 768px) {
    flex: 1 0 24%;
    min-width: 21rem;
    max-width: 30rem;
  }

  &__header {
    display: flex;

    align-items: center;

    height: 5rem;
  }

  &__title {
    margin: 0 0 0 1rem;
  }
}

.card-img {
  width: 4.5rem;
}

.card-text {
  font-size: 14px;
  font-weight: bold;
  color: $panther-silver;
  text-align: center;
}

.slack-button {
  height: 2.75rem;
  width: 12rem;
  border-radius: 0.5rem;
  margin: 0rem 0 1rem 0;
  font-size: 1.05rem;
  font-weight: bold;
  color: white;
  background-color: $panther-purple;
  border: none;
  cursor: pointer;
}
.disabled-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  margin-bottom: 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $panther-silver;
  color: $panther-gray;
  cursor: not-allowed;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
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

.privacy {
  font-family: #{$bold-font-family};
  font-size: 16px;
}

.lock {
  height: 2rem;
}
.note {
  font: lato-bold;
  font-size: 13px;
  font-weight: 900;
  color: $mid-gray;
  margin-top: -2.5rem;
}
.bold {
  font: lato-bold;
  font-weight: 2rem;
  color: $light-gray-blue;
}
.title {
  font-weight: bold;
  color: white;
}
a {
  text-decoration: none;
  color: $grape;
  font-weight: bold;
}
.alertButton__ {
  height: 2.5rem;
  width: 19rem;
  margin: 0rem 0 2rem 0;
  color: white;
  background-color: $dark-green;
  border: none;
  font-weight: bold;
  font-size: 14px;
  border-radius: 0.25rem;
  cursor: pointer;
}

.end {
  width: 6rem;
  align-self: flex-end;
  color: $panther-silver;
  background: transparent;
  border: none;
}

.orange_button {
  color: $panther-orange;
  background-color: white;
  width: 8vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  border: none;
}
.orange__button {
  color: $panther-purple;
  background-color: white;
  border-radius: 0.25rem;
  font-weight: bold;
  padding: 0.4rem;
  border: none;
  cursor: pointer;
}

.orange_button,
.orange__button:hover {
  background-color: $off-white;
  filter: brightness(0.9);
  cursor: pointer;
}

.connected {
  margin-left: 2rem;
  color: $dark-green;
  font-size: 1.1rem;
  font-weight: bold;
  text-shadow: 0 0 20px $dark-green;
}

.revoke {
  color: $panther-silver;
  background-color: transparent;
  width: 7vw;
  border-radius: 0.25rem;
  padding: 0.25rem;
  margin-left: 1rem;
  font-weight: bold;
  font-size: 14px;
  border: 2px solid $panther-silver;
  cursor: pointer;
}
.revoke__ {
  color: $panther-silver;
  background-color: transparent;
  width: 5vw;
  border-radius: 0.25rem;
  padding: 0.25rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
  font-weight: bold;
  font-size: 14px;
  border: 2px solid $panther-silver;
  cursor: pointer;
}
.revoke,
.revoke__:hover {
  filter: brightness(0.85);
}
</style>

￼
