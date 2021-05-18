<template>
  <div class="integrations">
    <h2>Integrate your apps</h2>
    <div class="integrations__subtitle">
      Connect with the apps below to sync your sales data for Managr to use.
    </div>

    <PulseLoadingSpinnerButton
      v-if="hasSalesforceIntegration && user.isAdmin"
      @click="goToSlackFormBuilder"
      class="slack-button"
      text="Continue to Slack Form Builder"
      :loading="false"
    ></PulseLoadingSpinnerButton>
    <div
      v-if="!hasSalesforceIntegration && user.isAdmin"
      class="slack-button slack-button--disabled"
      text="Continue to Slack Form Builder"
    >
      Slack Form Builder
    </div>

    <div class="integrations__cards">
      <div class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/salesforce.png" />
          <h3 class="card__title">Salesforce</h3>
        </div>
        <p class="card-text">
          Connect Salesforce to sync Accounts, Opportunities & Contacts with Managr.
        </p>
        <PulseLoadingSpinnerButton
          v-if="!hasSalesforceIntegration"
          @click="onGetAuthLink('SALESFORCE')"
          class="primary-button"
          text="Connect"
          :loading="generatingToken && selectedIntegration == 'SALESFORCE'"
          >Connect</PulseLoadingSpinnerButton
        >
        <PulseLoadingSpinnerButton
          text="Revoke"
          :loading="generatingToken && selectedIntegration == 'SALESFORCE'"
          @click="onRevoke('SALESFORCE')"
          v-else
          class="secondary-button"
        ></PulseLoadingSpinnerButton>
      </div>

      <div class="card">
        <div class="card__header">
          <img class="card-img card-img__radius" src="@/assets/images/zoom.png" />
          <h3 class="card__title">Zoom</h3>
        </div>

        <p class="card-text">Connect Zoom to sync meeting data with Managr.</p>
        <PulseLoadingSpinnerButton
          v-if="!hasZoomIntegration"
          :disabled="hasZoomIntegration"
          @click="onGetAuthLink('ZOOM')"
          class="primary-button"
          text="Connect"
          :loading="generatingToken && selectedIntegration == 'ZOOM'"
        ></PulseLoadingSpinnerButton>
        <PulseLoadingSpinnerButton
          text="Revoke"
          :loading="generatingToken && selectedIntegration == 'ZOOM'"
          v-else
          @click="onRevoke('ZOOM')"
          class="secondary-button"
        ></PulseLoadingSpinnerButton>
      </div>

      <div class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/slack.png" />
          <h3 class="card__title">Slack</h3>
        </div>

        <p class="card-text">Connect Slack to enable messaging between apps.</p>
        <PulseLoadingSpinnerButton
          v-if="
            (!orgHasSlackIntegration && userCanIntegrateSlack) ||
            (orgHasSlackIntegration && !hasSlackIntegration)
          "
          :disabled="(!orgHasSlackIntegration && !userCanIntegrateSlack) || hasSlackIntegration"
          @click="onIntegrateSlack"
          class="primary-button"
          :text="slackButtonMessage"
          :loading="generatingToken && selectedIntegration == 'SLACK'"
        ></PulseLoadingSpinnerButton>
        <PulseLoadingSpinnerButton
          v-else-if="hasSlackIntegration && orgHasSlackIntegration"
          @click="onRevoke('SLACK')"
          class="secondary-button"
          text="Revoke"
          :loading="generatingToken && selectedIntegration == 'SLACK'"
        ></PulseLoadingSpinnerButton>
      </div>

      <div class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/gmail.png" style="margin-right: 1rem" />
          <img class="card-img" src="@/assets/images/outlook.png" />
          <h3 class="card__title">Calendar</h3>
        </div>

        <p class="card-text">Connect Calendar to access upcoming meetings & attendees.</p>
        <div style="margin-bottom: 0.5rem; width: 15rem">
          <GoogleButton
            @click="onGetAuthLink('NYLAS')"
            :loading="generatingToken && selectedIntegration == 'NYLAS'"
            v-if="!hasNylasIntegration"
          />
        </div>

        <PulseLoadingSpinnerButton
          v-if="!hasNylasIntegration"
          @click="onGetAuthLink('NYLAS')"
          class="primary-button"
          text="Connect Other Provider"
          :loading="generatingToken && selectedIntegration == 'NYLAS'"
        ></PulseLoadingSpinnerButton>
        <PulseLoadingSpinnerButton
          text="Revoke"
          :loading="generatingToken && selectedIntegration == 'NYLAS'"
          v-else
          @click="onRevoke('NYLAS')"
          class="secondary-button"
        ></PulseLoadingSpinnerButton>
      </div>
      <div class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/teams.png" />
          <h3 class="card__title">Teams</h3>
        </div>

        <p class="card-text">Coming Soon...</p>
      </div>
      <div class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/hubspot.png" />
          <h3 class="card__title">Hubspot</h3>
        </div>

        <p class="card-text">Coming Soon...</p>
      </div>
    </div>

    <img class="lock" src="@/assets/images/lockAsset.png" />
    <div class="privacy">
      We take your security and privacy very seriously. Your data is encrypted, and not being stored
      by Managr.
    </div>
    <p>
      <a href="https://managr.ai/terms-of-service" target="_blank">Term of Service</a>
      |
      <a href="https://managr.ai/documentation" target="_blank">Documentation</a>
      |
      <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
    </p>
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
      this.$router.push({ name: 'SlackFormSettings' })
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
  },
  async created() {
    // if there is a code assume an integration has begun
    if (this.$route.query.code) {
      this.generatingToken = true
      this.selectedIntegration = this.$route.query.state // state is the current integration name

      try {
        const modelClass = this.selectedIntegrationSwitcher
        if (this.selectedIntegration != 'SLACK') {
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
    slackButtonMessage() {
      if (!this.orgHasSlackIntegration && this.userCanIntegrateSlack) {
        return 'Connect Workspace'
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
  width: 10rem;
  margin-right: 1rem;
  margin-bottom: 2rem;
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
  font-size: 1.1rem;
  color: $light-gray-blue;
  min-height: 4rem;
}

.slack-button {
  @include primary-button();
  height: 2.5rem;
  width: 19rem;
  margin: 0rem 0 2rem 0;

  &--disabled {
    background-color: #{$gray} !important;
    height: 2.5rem;
    width: 19rem;
    margin: 6rem 0 5rem 0;
    @include secondary-button();
    cursor: default !important;
  }
}

.privacy {
  font-family: #{$bold-font-family};
  font-size: 14px;
  margin-bottom: 2rem;
}

.lock {
  height: 2rem;
  margin-bottom: 1rem;
}
</style>
