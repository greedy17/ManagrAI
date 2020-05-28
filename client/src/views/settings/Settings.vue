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
          @click="toggleActivePage('profile')"
          :class="{ toolbar__active: profileActive }"
        >
          Profile
        </div>
      </div>
    </div>
    <div class="page__main-content-area">
      <EmailIntegration v-if="emailIntegrationActive"></EmailIntegration>
      <EmailTemplates v-if="emailTemplatesActive"></EmailTemplates>
      <Profile v-if="profileActive"></Profile>
    </div>
  </div>
</template>

<script>
import Profile from '@/components/settings/Profile'
import EmailIntegration from '@/components/settings/EmailIntegration'
import EmailTemplates from '@/components/settings/EmailTemplates'

export default {
  name: 'Settings',
  components: {
    EmailIntegration,
    EmailTemplates,
    Profile,
  },
  data() {
    return {
      emailIntegrationActive: true,
      emailTemplatesActive: false,
      profileActive: false,
    }
  },
  methods: {
    toggleActivePage(pageToActivate) {
      this.emailIntegrationActive = false
      this.emailTemplatesActive = false
      this.profileActive = false
      if (pageToActivate === 'emailIntegration') this.emailIntegrationActive = true
      if (pageToActivate === 'emailTemplates') this.emailTemplatesActive = true
      if (pageToActivate === 'profile') this.profileActive = true
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
</style>
