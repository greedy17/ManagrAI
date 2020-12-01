<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">
          SLACK INTEGRATION
          <div
            class="test-message"
            v-if="organizationHasIntegration && userHasIntegration"
            @click="handleTest"
          >
            Send Test Message
          </div>
        </div>
      </div>
      <div class="box__content">
        <template v-if="organizationHasIntegration && userHasIntegration">
          Activated on
          {{ userIntegrationDate | dateShort }}.
        </template>
        <template v-else-if="organizationHasIntegration">
          <img
            src="https://api.slack.com/img/sign_in_with_slack.png"
            @click.prevent="oAuthAttempt(SlackOAuth.options.USER)"
          />
        </template>
        <template v-else-if="userCanAddIntegrationToOrganization">
          Your organization has not enabled this feature, but you can do so: <br />
          <img
            @click.prevent="oAuthAttempt(SlackOAuth.options.WORKSPACE)"
            style="margin-top: 1rem;"
            alt="Add to Slack"
            height="40"
            width="139"
            src="https://platform.slack-edge.com/img/add_to_slack.png"
            srcset="
              https://platform.slack-edge.com/img/add_to_slack.png    1x,
              https://platform.slack-edge.com/img/add_to_slack@2x.png 2x
            "
          />
        </template>
        <template v-else>
          Your organization has not enabled this feature.
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'

export default {
  name: 'SlackIntegration',
  data() {
    return {
      SlackOAuth,
      fetching: false,
    }
  },
  methods: {
    oAuthAttempt(linkType) {
      if (this.fetching) {
        return
      }
      this.fetching = true
      SlackOAuth.api
        .getOAuthLink(linkType)
        .then(({ link }) => (window.location.href = link))
        .finally(() => {
          this.fetching = false
        })
    },
    handleTest() {
      // todo: disable the button in the meantime and $Alert success
      const { testChannel, testDM } = SlackOAuth.api
      let isChannelTest = this.userCanAddIntegrationToOrganization
      let apiCall = isChannelTest ? testChannel : testDM
      apiCall().then(() => {
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Test sent.',
        })
      })
    },
  },
  computed: {
    organizationHasIntegration() {
      let { organizationRef } = this.$store.state.user
      return !!(organizationRef && organizationRef.slackRef)
    },
    userHasIntegration() {
      return !!this.$store.state.user.slackRef
    },
    userCanAddIntegrationToOrganization() {
      return this.$store.state.user.type === 'INTEGRATION'
    },
    userIntegrationDate() {
      if (this.userHasIntegration) {
        return this.$store.state.user.slackRef.datetimeCreated
      }
      return null
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/mixins/utils';

img {
  cursor: pointer;
}

.box__title {
  display: flex;
  flex-flow: row;
  align-items: center;
  width: 100%;
}

.test-message {
  @include primary-button;
  margin-left: auto;
  margin-right: 1rem;
  padding: 0.5rem 1rem;
}
</style>
