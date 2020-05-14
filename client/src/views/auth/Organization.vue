<template>
  <div class="organization">
    <div class="toolbar-pane">
      <ToolBar :tabs="organizationViewTabs" @selected-tab="setSelectedTab" />
    </div>
    <div class="lists-pane">
      <OrganizationContainer
        v-if="selectedTab"
        :tabs="organizationViewTabs"
        :data="organization"
        :activeTab="selectedTab"
      />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/organization/Toolbar'
import OrganizationContainer from '@/components/organization/OrganizationContainer'
import Organization from '@/services/organizations'
import CollectionManager from '@/services/collectionManager'
import { getSerializedAccounts } from '@/db.js'

const DETAILS_TAB = 'details'
const ACCOUNTS_TAB = 'accounts'
const TABS = [DETAILS_TAB, ACCOUNTS_TAB]
// import CollectionManager from '@/services/collectionManager'

export default {
  name: 'Organization',
  components: {
    ToolBar,
    OrganizationContainer,
  },
  data() {
    return {
      organizationViewTabs: TABS,
      accounts: null,
      selectedTab: '',
      organization: CollectionManager.create({
        ModelClass: Organization,
      }),
    }
  },
  methods: {
    async setSelectedTab(tab) {
      if (this.selectedTab != tab) {
        switch (tab.toLowerCase()) {
          case DETAILS_TAB:
            await this.organization.refresh()

            this.selectedTab = tab
        }
      }
    },
  },
  created() {
    this.accounts = getSerializedAccounts()
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.organization {
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
