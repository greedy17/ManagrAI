<template>
  <div class="integrations">
    <h2>Integrate your apps</h2>
    <div
      class="integrations__subtitle"
    >Connect with the apps below to sync your sales data for managr to use.</div>

    <div class="integrations__cards">
      <div class="card">
        <div class="card__header">
          <img class="card-img" src="@/assets/images/salesforce.png" />
          <h3 class="card__title">Salesforce</h3>
        </div>
        <p
          class="card-text"
        >Connect Salesforce to sync Accounts, Opportunities & Contacts with managr.</p>
        <PulseLoadingSpinnerButton
          v-if="!hasSalesforceIntegration"
          @click="onGetAuthLink('SALESFORCE')"
          class="primary-button"
          text="Connect"
          :loading="generatingToken && selectedIntegration == 'SALESFORCE'"
        >Connect</PulseLoadingSpinnerButton>
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

        <p class="card-text">Connect Zoom to sync meeting data with managr.</p>
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
        <div class="card__header">
          <img class="card-img" src="@/assets/images/gmail.png" style="margin-right: 1rem" />
          <img class="card-img" src="@/assets/images/outlook.png" />
          <h3 class="card__title">Calendar</h3>
        </div>

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

    <div v-if="user.isAdmin">
      <PulseLoadingSpinnerButton
        v-if="hasSalesforceIntegration"
        @click="goToSlackFormBuilder"
        class="slack-button"
        text="Slack Form Builder"
      ></PulseLoadingSpinnerButton>
      <div
        v-if="!hasSalesforceIntegration"
        class="slack-button--disabled"
        text="Slack Form Builder"
      >Slack Form Builder</div>
    </div>
    <div
      class="privacy"
    >We take your security and privacy very seriously. Your data is encrypted, and not being stored by Managr.</div>
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
  flex: 1;
  min-width: 28rem;
  max-width: 28rem;
  margin-right: 2rem;
  margin-bottom: 2rem;

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
  margin: 6rem 0 5rem 0;

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
</style>
