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
  methods: {
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
</style>
