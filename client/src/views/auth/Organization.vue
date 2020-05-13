<template>
  <div class="prospect">
    <div class="toolbar-pane">
      <ToolBar @selected-tab="setSelectedTab" />
    </div>
    <div class="lists-pane">
      <OrganizationContainer :activeTab="selectedTab" />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/organization/Toolbar'
import OrganizationContainer from '@/components/organization/OrganizationContainer'
import { getSerializedAccounts } from '@/db.js'

// import CollectionManager from '@/services/collectionManager'

export default {
  name: 'Prospect',
  components: {
    ToolBar,
    OrganizationContainer,
  },
  data() {
    return {
      accounts: null,
      selectedTab: '',
    }
  },
  methods: {
    setSelectedTab(tab) {
      this.selectedTab = tab
    },
  },
  created() {
    this.accounts = getSerializedAccounts()
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.prospect {
  display: flex;
  flex-flow: row;
  padding-top: 2%;
  padding-bottom: 2%;
}

.toolbar-pane {
  width: 18vw;
  display: flex;
  flex-flow: column;
  align-items: center;
}

.lists-pane {
  width: 82vw;
}
</style>
