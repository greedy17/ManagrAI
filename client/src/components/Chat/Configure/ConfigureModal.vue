<template>
  <div class="display-flex-container">
    <div class="left-bar">
      <ConfigureLeftBar :configPage="configPage" :changeConfigPage="changeConfigPage" />
    </div>
    <div class="main-content">
      <div v-if="configPage === 'integrations'">
        <ConfigureIntegrations />
      </div>
      <div v-else>
        <div>
          <h2>Error loading page. Please try again later.</h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ConfigureLeftBar from './ConfigureLeftBar.vue'
import ConfigureIntegrations from './ConfigureIntegrations.vue'

export default {
  name: 'ConfigureModal',
  props: {

  },
  components: {
    ConfigureLeftBar,
    ConfigureIntegrations,
  },
  data() {
    return {
      configPage: 'integrations',
    }
  },
  methods: {
    changeConfigPage(page) {
      this.configPage = page
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

.display-flex-container {
  display: flex;
  flex-direction: row;
  height: 90vh;
}

.test {
  border: 1px solid red;
}

.left-bar {
  width: 15%;
}
.main-content {
  width: 85%;
}
</style>