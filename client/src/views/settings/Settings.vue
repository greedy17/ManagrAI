<template>
  <div class="page">
    <div class="page__left-nav-bar" style="padding: 1rem;">
      <div class="toolbar">
        <div class="toolbar__header">
          <span class="toolbar__title">Settings</span>
          <h5 class="org-statement" v-if="organization">
            You're viewing settings for {{ organization }}
          </h5>
        </div>
        <div
          v-for="option in options"
          :key="option.value"
          class="toolbar__row"
          @click="toggleActivePage(option.value)"
          :class="{ toolbar__active: isActivePage(option.value) }"
        >
          {{ option.label }}
        </div>
      </div>
    </div>
    <div class="page__main-content-area" style="padding: 1rem;">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import SlackOAuthModel from '@/services/slack'

const standardOptions = [
  {
    value: 'EmailIntegration',
    label: 'Email Integration',
  },
  {
    value: 'EmailTemplates',
    label: 'Email Templates',
  },
  {
    value: 'TextIntegration',
    label: 'Text Integration',
  },
  {
    value: 'SlackIntegration',
    label: 'Slack Integration',
  },
  {
    value: 'NotificationSettings',
    label: 'Notification Settings',
  },
  {
    value: 'Profile',
    label: 'Profile',
  },
  // NOTE (Bruno 6-18-2020) once we get password-reset-flow incorporated, we can add the Password page
  // {
  //   value: 'Password',
  //   label: 'Password'
  // },
]

const adminOptions = [
  {
    value: 'Invite',
    label: 'Invite User',
  },
]

export default {
  name: 'Settings',
  created() {
    // check to see if this page is loaded as result of Slack OAuth redirect
    this.handleSlackOAuth()
  },
  methods: {
    handleSlackOAuth() {
      /*
        If the OAuth request was accepted, the URL will contain a temporary code in a GET code parameter.
        If the OAuth request was denied, the URL will contain a GET error parameter.
        In either case, the URL will also contain the state provided in the initial redirect step in a state parameter.
      */
      let slackOAuth = new SlackOAuthModel()
      if (!slackOAuth.isSlackOAuthRedirect) {
        return
      }
      // If the states don't match, the request has been created by a third party and the process should be aborted.
      if (!slackOAuth.stateParamIsValid) {
        return
      }
      if (slackOAuth.params.error) {
        this.$Alert.alert({
          type: 'error',
          timeout: 3000,
          message: 'Slack Integration declined.',
        })
        return
      }
      // Now will need to exchange the params.code for an access token using the oauth.access method.
      // https://api.slack.com/methods/oauth.v2.access
      slackOAuth.getAccessToken().then(data => {
        debugger
      })
    },
    toggleActivePage(name) {
      this.$router.push({ name })
    },
    isActivePage(pageName) {
      return pageName === this.$route.name
    },
  },
  computed: {
    options() {
      if (this.isStaff || this.isManager) {
        return [...standardOptions, ...adminOptions]
      }
      return standardOptions
    },
    isStaff() {
      // used to check superuser if is staff then they currently do not have an org
      return this.$store.state.user.isStaff
    },
    isManager() {
      // used to check superuser if is staff then they currently do not have an org
      return this.$store.state.user.isStaff
    },
    organization() {
      return this.$store.state.user.organizationRef && this.$store.state.user.organizationRef.name
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/sidebars';
@import '@/styles/mixins/utils';

.toolbar__row {
  @include pointer-on-hover;
}

.org-statement {
  color: $mid-gray;
  margin-top: 1rem;
  margin-bottom: 0;
}
</style>
