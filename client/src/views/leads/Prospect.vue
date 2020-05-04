<template>
  <div class="prospect">
    <div class="toolbar-pane">
      <ToolBar />
    </div>
    <div class="lists-pane">
      <AccountsContainer :accounts="accounts" />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/prospect/ToolBar'
import AccountsContainer from '@/components/prospect/AccountsContainer'
import { getSerializedAccounts } from '@/db.js'

// import CollectionManager from '@/services/collectionManager'

export default {
  name: 'Prospect',
  components: {
    ToolBar,
    AccountsContainer,
  },
  data() {
    return {
      accounts: null,
    }
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
