<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">SLACK INTEGRATION</div>
      </div>
      <div class="box__content">
        <!-- in user.orgRef add user.orgRef.slackRef -->
        <div>
          (For Organization Workspace, signs you in too)
          <a :href="slackOAuth.addToWorkspaceLink">
            <img
              alt="Add to Slack"
              height="40"
              width="139"
              src="https://platform.slack-edge.com/img/add_to_slack.png"
              srcset="
                https://platform.slack-edge.com/img/add_to_slack.png    1x,
                https://platform.slack-edge.com/img/add_to_slack@2x.png 2x
              "
            />
          </a>
        </div>
        <div>
          (Sign in only)
          <a :href="slackOAuth.userSignInLink">
            <img src="https://api.slack.com/img/sign_in_with_slack.png" />
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SlackOAuthModel from '@/services/slack'

export default {
  name: 'SlackIntegration',
  data() {
    return {
      slackOAuth: new SlackOAuthModel(),
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/mixins/utils';

a {
  cursor: pointer;
}
</style>
