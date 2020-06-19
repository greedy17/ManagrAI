<template>
  <div class="page">
    <div class="page__left-nav-bar">
      <div class="toolbar">
        <div class="toolbar__header">
          <span class="toolbar__title">Settings</span>
        </div>
        <div
          class="toolbar__row"
          @click="toggleActivePage('emailIntegration')"
          :class="{ toolbar__active: emailIntegrationActive }"
        >
          Email Integration
        </div>
        <div
          class="toolbar__row"
          @click="toggleActivePage('emailTemplates')"
          :class="{ toolbar__active: emailTemplatesActive }"
        >
          Email Templates
        </div>
        <div
          class="toolbar__row"
          @click="toggleActivePage('emailTest')"
          :class="{ toolbar__active: emailTestActive }"
        >
          Email Test
        </div>
        <div class="toolbar__row" @click="routeToInviteUser">
          Invite User
        </div>
        <div class="toolbar__row" @click="toggleActivePage('profile')">
          Profile
        </div>
        <!-- NOTE (Bruno 6-18-2020) once we get password-reset-flow incorporated, we can add the Password page -->
        <!-- <div class="toolbar__row" @click="toggleActivePage('password')">
          Password
        </div> -->
      </div>
    </div>
    <div class="page__main-content-area">
      <EmailIntegration v-if="emailIntegrationActive"></EmailIntegration>
      <EmailTemplates v-if="emailTemplatesActive"></EmailTemplates>
      <EmailTest v-if="emailTestActive"></EmailTest>
      <Profile v-if="profileActive"></Profile>
      <Password v-if="passwordActive"></Password>
    </div>
  </div>
</template>

<script>
import EmailTest from '@/components/settings/EmailTest'
import EmailIntegration from '@/components/settings/EmailIntegration'
import EmailTemplates from '@/components/settings/EmailTemplates'
import Profile from '@/components/settings/Profile'
import Password from '@/components/settings/Password'

export default {
  name: 'Settings',
  components: {
    EmailIntegration,
    EmailTemplates,
    EmailTest,
    Profile,
    Password,
  },
  data() {
    return {
      emailIntegrationActive: true,
      emailTemplatesActive: false,
      emailTestActive: false,
      profileActive: false,
      passwordActive: false,
    }
  },
  methods: {
    toggleActivePage(pageToActivate) {
      this.emailIntegrationActive = false
      this.emailTemplatesActive = false
      this.emailTestActive = false
      this.profileActive = false
      this.passwordActive = false
      if (pageToActivate === 'emailIntegration') this.emailIntegrationActive = true
      if (pageToActivate === 'emailTemplates') this.emailTemplatesActive = true
      if (pageToActivate === 'emailTest') this.emailTestActive = true
      if (pageToActivate === 'profile') this.profileActive = true
      if (pageToActivate === 'password') this.passwordActive = true
    },
    routeToInviteUser() {
      this.$router.push({ name: 'Invite' })
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
</style>
