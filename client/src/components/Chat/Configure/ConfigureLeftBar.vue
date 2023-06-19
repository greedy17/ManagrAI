<template>
  <div class="content-and-logout-container">
    <div class="content-container">
      <div class="img-container">
        <img src="@/assets/images/logo.png" height="35px" />
      </div>
        <!-- <div class="configure-text">Configure</div> -->
      <div style="margin-top: 1.6rem;">
        <div class="base-select" :class="configPage === 'integrations' ? 'left-active' : 'pointer'" @click="changeConfigPage('integrations')">
          <p><img src='@/assets/images/settings-sliders.svg' :class="configPage === 'integrations' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Integrations</p> <span class="config-number">{{ integrationsLength }}</span>
        </div>
        <div class="base-select" :class="configPage === 'forms' ? 'left-active' : 'pointer'" @click="changeConfigPage('forms')">
          <p><img src='@/assets/images/rectangle-list.svg' :class="configPage === 'forms' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />CRM Fields</p> <span class="config-number">{{ forms.length }}</span>
        </div>
        <div class="base-select" :class="configPage === 'workflows' ? 'left-active' : 'pointer'" @click="changeConfigPage('workflows')">
          <p><img src='@/assets/images/workflows-chat.svg' :class="configPage === 'workflows' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Lists</p> <span class="config-number">{{ activeTemplatesLength }}</span>
        </div>
        <div class="base-select" :class="configPage === 'notes' ? 'left-active' : 'pointer'" @click="changeConfigPage('notes')">
          <p><img src='@/assets/images/chat-notes.svg' :class="configPage === 'notes' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Templates</p> <span class="config-number">{{ noteTemplates.length }}</span>
        </div>
        <div class="base-select" :class="configPage === 'sync' ? 'left-active' : 'pointer'" @click="changeConfigPage('sync')">
          <p><img src='@/assets/images/cycle.svg' :class="configPage === 'sync' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Sync</p>
        </div>
        <!-- <div class="base-select" :class="configPage === 'profile' ? 'left-active' : 'pointer'" @click="changeConfigPage('profile')">
          <p><img src='@/assets/images/user.svg' :class="configPage === 'profile' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Profile</p>
        </div> -->
      </div>
    </div>
    <div>
      <!-- <div class="base-select" :class="configPage === 'demo' ? 'left-active' : 'pointer'" @click="changeConfigPage('demo')">
        <p><img src="@/assets/images/play-alt.svg" :class="configPage === 'demo' ? 'left-active-icon' : ''" style="height: 12px; margin-right: 0.5rem;" />Demo Center</p>
      </div> -->
      <div class="base-select pointer" @click="logOut">
        <p><img src="@/assets/images/logout.svg" style="height: 12px; margin-right: 0.5rem;" />Log out</p>
      </div>
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import AlertTemplate from '@/services/alerts/'

export default {
  name: 'ConfigureLeftBar',
  props: {
    changeConfigPage: {
      type: Function,
    },
    configPage: {
      type: String
    },
    forms: {
      type: Array
    }
  },
  data() {
    return {
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
    }
  },
  created() {
    this.templates.refresh();
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
    },
    activeTemplatesLength() {
      return this.templates.list.length
    },
    noteTemplates() {
      return this.$store.state.templates
    },
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
.base-select {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem;
  // font-size: 11px;
  font-size: 14px;
  border-radius: 4px;
  margin: 0.2rem 0;
  transition: all 0.3s;
  p {
    margin: 0;
    display: flex;
    align-items: center;
  }
}
.pointer {
  // color: $light-gray-blue;
  img {
    // filter: invert(45%);
  }
}
.pointer:hover {
  // background-color: $white-green;
  opacity: 60%;
}
.cursor-color {
  color: $light-gray-blue;
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