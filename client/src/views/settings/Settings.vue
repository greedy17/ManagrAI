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
        <router-link :to="{ name: 'ZoomIntegration' }">
          <div class="toolbar__row">
            Zoom Integration
          </div>
        </router-link>
        <router-link :to="{ name: 'SlackIntegration' }">
          <div class="toolbar__row">
            Slack Integration
          </div>
        </router-link>
        <router-link :to="{ name: 'EmailIntegration' }">
          <div class="toolbar__row">
            Email Integration
          </div>
        </router-link>
        <router-link :to="{ name: 'EmailTemplates' }">
          <div class="toolbar__row">
            Email Templates
          </div>
        </router-link>
        <router-link :to="{ name: 'TextIntegration' }">
          <div class="toolbar__row">
            Text Integration
          </div>
        </router-link>
        <router-link :to="{ name: 'NotificationSettings' }">
          <div class="toolbar__row">
            Notification Settings
          </div>
        </router-link>
        <router-link
          v-if="$store.state.user.isManager || $store.state.user.isStaff"
          :to="{ name: 'Invite' }"
        >
          <div class="toolbar__row">
            Invite User
          </div>
        </router-link>

        <router-link :to="{ name: 'Profile' }">
          <div class="toolbar__row">
            Profile
          </div>
        </router-link>
        <!-- NOTE (Bruno 6-18-2020) once we get password-reset-flow incorporated, we can add the Password page -->
        <!-- <router-link :to="{ name: 'Profile' }">
          <div class="toolbar__row">
            Profile
          </div>
        </router-link> -->
      </div>
    </div>
    <div class="page__main-content-area" style="padding: 1rem;">
      <router-view name="user-settings" :key="$route.fullPath"></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  computed: {
    isStaff() {
      // used to check superuser if is staff then they currently do not have an org
      return this.$store.state.user.isStaff
    },
    isManager() {
      return this.$store.state.user.type === 'MANAGER'
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
