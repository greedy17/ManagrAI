<template>
  <div class="integrations">
    <h2>Integrations</h2>

    <div class="integrations__cards">
      <div class="card">
        <img class="card-img" src="@/assets/images/salesforce.svg" />
        <h3>Salesforce</h3>
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
        <PulseLoadingSpinnerButton
          text="Show Forms"
          :loading="generatingToken && selectedIntegration == 'SALESFORCE'"
          @click="$router.push({ name: 'SlackFormSettings' })"
          v-if="hasSalesforceIntegration"
          class="secondary-button"
        ></PulseLoadingSpinnerButton>
      </div>


      <div class="card">
        <img class="card-img" src="@/assets/images/slack.svg" />
        <h3>Slack</h3>
        <p class="card-text">Connect Slack to enable messaging between apps.</p>
        <PulseLoadingSpinnerButton
          v-if="
            (!orgHasSlackIntegration && userCanIntegrateSlack) ||
            (orgHasSlackIntegration && !hasSlackIntegration)
          "
          :disabled="(!orgHasSlackIntegration && !userCanIntegrateSlack) || hasSlackIntegration"
          @click="onIntegrateSlack"
          class="primary-button"
          text="Connect"
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
        <img class="card-img" src="@/assets/images/zoom_logo.svg" />
        <h3>Zoom</h3>
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
        <img class="card-img" src="@/assets/images/salesloft.svg" />
        <h3>Calendar</h3>
        <p class="card-text">Put Contacts right into Cadences</p>
        <PulseLoadingSpinnerButton
          v-if="!hasSalesloftIntegration"
          @click="onGetAuthLink('SALESLOFT')"
          class="primary-button"
          text="Connect"
          :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
        ></PulseLoadingSpinnerButton>
        <PulseLoadingSpinnerButton
          text="Revoke"
          :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
          v-else
          @click="onRevoke('SALESLOFT')"
          class="secondary-button"
        ></PulseLoadingSpinnerButton>
      </div>

      <div class="card">
        <img
          class="card-img"
          src="@/assets/images/google-calendar.svg"
          style="margin-right: 1rem"
        />
        <img class="card-img" src="@/assets/images/outlook-icon.svg" />
        <h3>Calendar</h3>
        <p class="card-text">Connect Calendar to access upcoming meetings & attendees.</p>
        <PulseLoadingSpinnerButton
          v-if="!hasNylasIntegration"
          @click="onGetAuthLink('NYLAS')"
          class="primary-button"
          text="Connect"
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
    </div>
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
import Salesloft from '@/services/salesloft'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

export default {
  name: 'Integrations',
  components: { PulseLoadingSpinnerButton },
  data() {
    return {
      generatingToken: false,
      authLink: null,
      selectedIntegration: null,
    }
  },
  methods: {
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
        this.generatingToken = false
        this.$store.dispatch('refreshCurrentUser')
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
          await SlackOAuth.api.testDM()
        }

        this.$router.replace({
          name: 'Integrations',
          params: {},
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.generatingToken = false
        this.selectedIntegration = null
      }
    }
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
    hasZoomIntegration() {
      return !!this.$store.state.user.zoomAccount && this.$store.state.user.hasZoomIntegration
    },
    hasNylasIntegration() {
      return !!this.$store.state.user.nylas
    },
    hasSalesloftIntegration() {
      return (
        !!this.$store.state.user.salesloftAccount && this.$store.state.user.hasSalesloftIntegration
      )
    },
    userCanIntegrateSlack() {
      return this.$store.state.user.isAdmin
    },

    selectedIntegrationSwitcher() {
      switch (this.selectedIntegration) {
        case 'SALESFORCE':
          return Salesforce
        case 'SLACK':
          return SlackOAuth
        case 'NYLAS':
          return Nylas
        case 'ZOOM':
          return ZoomAccount
        case 'SALESLOFT':
          return Salesloft
        default:
          return null
      }
    },
    user() {
      return this.$store.state.user
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.integrations {
  &__cards {
    display: flex;
    flex-wrap: wrap;
  }
}

.card {
  flex: 1;
  min-width: 28rem;
  max-width: 28rem;
  margin-right: 2rem;
  margin-bottom: 2rem;
}

.card-img {
  height: 4rem;
}

.card-text {
  font-size: 1.1rem;
  color: $light-gray-blue;
  min-height: 4rem;
}
</style>
