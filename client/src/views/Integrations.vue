<template>
  <div class="integrations">
    <h2>Integrations</h2>

    <div class="integrations__cards">
      <div class="card">
        <img class="card-img" src="@/assets/images/salesforce.svg" />
        <h3>Salesforce</h3>
        <p class="card-text">Connect Salesforce to sync your Salesforce data with Managr.</p>
        <button
          v-if="!hasSalesforceIntegration"
          @click="onGetAuthLink('SALESFORCE')"
          class="primary-button"
        >
          Connect
        </button>
        <button @click="onRevoke('SALESFORCE')" v-else class="secondary-button">
          Revoke
        </button>
      </div>

      <div class="card">
        <img class="card-img" src="@/assets/images/zoom_logo.svg" />
        <h3>Zoom</h3>
        <p class="card-text">
          Connect Zoom so Managr can help you track how your meetings went and send that info
          straight to Salesforce.
        </p>
        <button
          v-if="!hasZoomIntegration"
          :disabled="hasZoomIntegration"
          @click="onGetAuthLink('ZOOM')"
          class="primary-button"
        >
          Connect
        </button>
        <button v-else @click="onRevoke('ZOOM')" class="secondary-button">
          Revoke
        </button>
      </div>

      <div class="card">
        <img class="card-img" src="@/assets/images/slack.svg" />
        <h3>Slack</h3>
        <p class="card-text">
          Connect Slack to easily make updates to your Salesforce opportunities from within the
          Slack interface.
        </p>
        <button
          v-if="
            (!orgHasSlackIntegration && userCanIntegrateSlack) ||
              (orgHasSlackIntegration && !hasSlackIntegration)
          "
          :disabled="(!orgHasSlackIntegration && !userCanIntegrateSlack) || hasSlackIntegration"
          @click="onIntegrateSlack"
          class="primary-button"
        >
          Connect
        </button>
        <button
          v-else-if="hasSlackIntegration && orgHasSlackIntegration"
          @click="onRevoke('SLACK')"
          class="secondary-button"
        >
          Revoke
        </button>
      </div>

      <div class="card">
        <img
          class="card-img"
          src="@/assets/images/google-calendar.svg"
          style="margin-right: 1rem"
        />
        <img class="card-img" src="@/assets/images/outlook-icon.svg" />
        <h3>Calendar</h3>
        <p class="card-text">
          Connect you calendar and Managr will make sure that you capture all the contacts who
          attended your meetings.
        </p>
        <button v-if="!hasNylasIntegration" @click="onGetAuthLink('NYLAS')" class="primary-button">
          Connect
        </button>
        <button v-else @click="onRevoke('NYLAS')" class="secondary-button">Revoke</button>
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

export default {
  name: 'Integrations',
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
    hasZoomIntegration() {
      return !!this.$store.state.user.zoomAccount
    },
    orgHasSlackIntegration() {
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    hasNylasIntegration() {
      return !!this.$store.state.user.emailAuthAccount
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
  margin-right: 1rem;
  margin-bottom: 1rem;
}

.card-img {
  height: 4rem;
}

.card-text {
  font-size: 1.1rem;
  color: $light-gray-blue;
  min-height: 6rem;
}
</style>
