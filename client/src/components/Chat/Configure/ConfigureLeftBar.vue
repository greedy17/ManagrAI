<template>
  <div class="content-and-logout-container">
    <div class="content-container">
      <div class="img-container">
        <img src="@/assets/images/logo.png" height="35px" />
      </div>
        <!-- <div class="configure-text">Configure</div> -->
      <div style="margin-top: 1.6rem;">
        <div class="pointer" :class="configPage === 'integrations' ? 'left-active' : ''" @click="changeConfigPage('integrations')">
          <p><img src='@/assets/images/settings-sliders.svg' :class="configPage === 'integrations' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Integrations</p> <span class="config-number">{{ integrationsLength }}</span>
        </div>
        <div class="pointer" :class="configPage === 'forms' ? 'left-active' : ''" @click="changeConfigPage('forms')">
          <p><img src='@/assets/images/rectangle-list.svg' :class="configPage === 'forms' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />CRM Fields</p>
        </div>
        <div class="pointer" :class="configPage === 'workflows' ? 'left-active' : ''" @click="changeConfigPage('workflows')">
          <p><img src='@/assets/images/workflows-chat.svg' :class="configPage === 'workflows' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Workflows</p>
        </div>
        <div class="pointer" :class="configPage === 'notes' ? 'left-active' : ''" @click="changeConfigPage('notes')">
          <p><img src='@/assets/images/chat-notes.svg' :class="configPage === 'notes' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Note Templates</p>
        </div>
        <div class="pointer" :class="configPage === 'meetings' ? 'left-active' : ''" @click="changeConfigPage('meetings')">
          <p><img src='@/assets/images/calendar.svg' :class="configPage === 'meetings' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Meetings</p>
        </div>
        <div class="pointer" :class="configPage === 'profile' ? 'left-active' : ''" @click="changeConfigPage('profile')">
          <p><img src='@/assets/images/user.svg' :class="configPage === 'profile' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Profile</p>
        </div>
      </div>
    </div>
    <div>
      <div class="pointer" :class="configPage === 'demo' ? 'left-active' : ''" @click="changeConfigPage('demo')">
        <p><img src="@/assets/images/play-alt.svg" :class="configPage === 'demo' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Demo Center</p>
      </div>
      <div class="pointer" @click="logOut">
        <p><img src="@/assets/images/logout.svg" style="height: 12px; margin-right: 0.5rem;" />Log out</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfigureLeftBar',
  props: {
    changeConfigPage: {
      type: Function,
    },
    configPage: {
      type: String
    }
  },
  data() {
    return {

    }
  },
  methods: {
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
      localStorage.isLoggedOut = true
    },
  },
  computed: {
    integrationsLength() {
      let count = 0
      for (let key in this.$store.state.user) {
        const obj = this.$store.state.user[key]
        if (key === 'crm' && (obj === 'SALESFORCE' || obj === 'HUBSPOT')) {
          count++
        }
        if (key === 'hasZoomIntegration' && obj) {
          count++
        }
        if (key === 'nylas' && obj) {
          count++
        }
        if (key === 'slackRef' && Object.keys(obj).length) {
          count++
        }
      }
      return count
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
@import '@/styles/modals';

.content-and-logout-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 90vh;
}
.content-container {
  margin-top: 1rem;
}
.img-container {
  display: flex;
  // justify-content: center;
  // margin-left: 1rem;
}
.pointer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem;
  color: $light-gray-blue;
  font-size: 11px;
  p {
    margin: 0;
    display: flex;
    align-items: center;
  }
  img {
    filter: invert(45%);
  }
}
.configure-text {
  color: $light-gray-blue;
  font-size: 12px;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  margin-left: 0.5rem;
}
.flex-end {
  display: flex;
  justify-content: flex-end;
}
.left-active {
  background-color: $dark-green;
  color: $white;
  // margin: 14px 0px 4px 0px;
  border-radius: 4px;
  border-bottom: none;
  // img {
  //   filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
  //     brightness(93%) contrast(89%);
  // }
}
.config-number {
  background-color: $white-green;
  color: $dark-green;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 10px;
}

.left-active-icon {
  filter: invert(90%) !important;
  z-index: 4;
}
</style>