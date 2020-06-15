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
      </div>
    </div>
    <div class="page__main-content-area">
      <EmailIntegration v-if="emailIntegrationActive"></EmailIntegration>
      <EmailTemplates v-if="emailTemplatesActive"></EmailTemplates>
      <EmailTest v-if="emailTestActive"></EmailTest>
    </div>
  </div>
</template>

<script>
import EmailTest from '@/components/settings/EmailTest'
import EmailIntegration from '@/components/settings/EmailIntegration'
import EmailTemplates from '@/components/settings/EmailTemplates'

export default {
  name: 'Settings',
  components: {
    EmailIntegration,
    EmailTemplates,
    EmailTest,
  },
  data() {
    return {
      emailIntegrationActive: false,
      emailTemplatesActive: false,
      emailTestActive: true,
    }
  },
  methods: {
    toggleActivePage(pageToActivate) {
      this.emailIntegrationActive = false
      this.emailTemplatesActive = false
      this.emailTestActive = false
      if (pageToActivate === 'emailIntegration') this.emailIntegrationActive = true
      if (pageToActivate === 'emailTemplates') this.emailTemplatesActive = true
      if (pageToActivate === 'emailTest') this.emailTestActive = true
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
