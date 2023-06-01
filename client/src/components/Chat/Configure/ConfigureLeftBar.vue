<template>
  <div class="content-and-logout-container">
    <div class="content-container">
      <div class="img-container">
        <img src="@/assets/images/logo.png" height="40px" />
      </div>
      <h4>Configure</h4>
      <div>
        <div class="pointer" :class="configPage === 'integrations' ? 'left-active' : ''" @click="changeConfigPage('integrations')">
          <p>Integrations</p> <span class="config-number">{{ integrationsLength }}</span>
        </div>
        <div class="pointer" :class="configPage === 'forms' ? 'left-active' : ''" @click="changeConfigPage('forms')">
          <p>Forms</p>
        </div>
        <div class="pointer" :class="configPage === 'workflows' ? 'left-active' : ''" @click="changeConfigPage('workflows')">
          <p>Workflow</p>
        </div>
        <div class="pointer" :class="configPage === 'notes' ? 'left-active' : ''" @click="changeConfigPage('notes')">
          <p>Note Templates</p>
        </div>
        <div class="pointer" :class="configPage === 'meetings' ? 'left-active' : ''" @click="changeConfigPage('meetings')">
          <p>Meetings</p>
        </div>
        <div class="pointer" :class="configPage === 'profile' ? 'left-active' : ''" @click="changeConfigPage('profile')">
          <p>Profile</p>
        </div>
      </div>
    </div>
    <div>
      <div>
        <p>Demo Center</p>
      </div>
      <div>
        <p><img src="@/assets/images/logout.svg" height="14px" style="margin-right: 0.5rem;" />Log out</p>
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
  justify-content: center;
}
.pointer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem;
  color: $light-gray-blue;
  p {
    margin: 0;
  }
}
.left-active {
  background-color: $dark-green;
  color: $white;
  // margin: 14px 0px 4px 0px;
  border-radius: 4px;
  border-bottom: none;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
.config-number {
  background-color: $white-green;
  color: $dark-green;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 12px;
}
</style>