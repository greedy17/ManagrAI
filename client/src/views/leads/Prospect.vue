<template>
  <div class="prospect">
    <NavBar />
    <div class="page-content">
      <div class="toolbar-pane">
        <ToolBar />
      </div>
      <div class="lists-pane">
        ListsContainer -- coming soon!
      </div>
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/prospect/ToolBar'

// import CollectionManager from '@/services/collectionManager'

export default {
  name: 'Prospect',
  components: {
    ToolBar,
  },
  data() {
    return {
      accounts: null,
      currentStep: 1,
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.prospect {
  min-height: 100vh;
  display: flex;
  flex-flow: column;
  background-color: $off-white;
}

.page-content {
  padding-top: 2%;
  flex-grow: 1;
  display: flex;
  flex-flow: row;
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
