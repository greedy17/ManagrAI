<template>
  <div class="page">
    <div class="page__left-nav-bar" style="padding: 1rem;">
      <div class="toolbar">
        <div class="toolbar__header">
          <span class="toolbar__title">Slack Forms</span>
        </div>
        <router-link :to="{ name: 'OpportunityFormSettings', params: { resource: 'Opportunity' } }">
          <div class="toolbar__row">
            Opportunities
          </div>
        </router-link>
        <router-link :to="{ name: 'AccountFormSettings', params: { resource: 'Account' } }">
          <div class="toolbar__row">
            Accounts
          </div>
        </router-link>
      </div>
    </div>
    <div class="page__main-content-area" style="padding: 1rem;">
      <router-view name="slack-form-settings" :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

import SlackOAuth, { salesforceFields } from '@/services/slack'

export default {
  name: 'SlackFormSettings',
  components: { PulseLoadingSpinnerButton },
  data() {
    return {
      forms: [],
    }
  },
  async created() {},
  computed: {},
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
a {
  text-decoration: none;
}
::v-deep .router-link-exact-active.router-link-active {
  .toolbar__row {
    background-color: #e5f2ea;
    border-bottom: 4px #199e54 solid;
  }
}
</style>
