<template>
  <div class="integrations">
    <h2>Integrations</h2>

    <div class="integrations__cards">
      <div class="card">
        <img class="card-img" src="@/assets/images/salesforce.svg" />
        <h3>Salesforce</h3>
        <p class="card-text">
          Connect Salesforce to sync Accounts, Opportunities & Contacts with managr.
        </p>
        <button
          v-if="!hasSalesforceIntegration"
          @click="onGetAuthLink('SALESFORCE')"
          class="primary-button"
        >
          Connect
        </button>
        <button v-else class="secondary-button">
          Revoke
        </button>
      </div>

      <div class="card">
        <img class="card-img" src="@/assets/images/zoom_logo.svg" />
        <h3>Zoom</h3>
        <p class="card-text">
          Connect Zoom to sync meeting data with managr.
        </p>
        <button
          v-if="!hasZoomIntegration"
          :disabled="hasZoomIntegration"
          @click="onGetAuthLink('ZOOM')"
          class="primary-button"
        >
          Connect
        </button>
        <button v-else class="secondary-button">
          Revoke
        </button>
      </div>

      <div class="card">
        <img class="card-img" src="@/assets/images/slack.svg" />
        <h3>Slack</h3>
        <p class="card-text">
          Connect Slack to enable messaging between apps.
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
        <button v-else-if="hasSlackIntegration && orgHasSlackIntegration" class="secondary-button">
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
          Connect Calendar to access upcoming meetings & attendees.
        </p>
        <button v-if="!hasNylasIntegration" @click="onGetAuthLink('NYLAS')" class="primary-button">
          Connect
        </button>
        <button v-else class="secondary-button">Revoke</button>
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
      this.selectedIntegration = integration
      const modelClass = this.selectedIntegrationSwitcher

      const res = await modelClass.api.getAuthLink()
      console.log(res)
      if (res.link) {
        window.location.href = res.link
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
          } catch (e) {
            console.log(e)
          } finally {
            this.generatingToken = false
          }
        }
      } else {
        if (!this.hasSlackIntegration) {
          try {
            let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.USER)
            console.log(res)
          } catch (e) {
            console.log(e)
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
