<template>
  <div class="leads-index">
    <NavBar />
    <div class="page-content">
      <div class="toolbar-pane">
        <ToolBar class="toolbar" />
      </div>
      <div class="lists-container-pane">
        <ListsContainer :lists="lists" />
      </div>
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/leads-index/ToolBar'
import ListsContainer from '@/components/leads-index/ListsContainer'
import { getSerializedLists } from '@/db.js'

export default {
  name: 'LeadsIndex',
  components: {
    ToolBar,
    ListsContainer,
  },
  data() {
    return {
      lists: [],
    }
  },
  created() {
    this.lists = getSerializedLists()
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.leads-index {
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
  width: 17%;
  padding: 0% 1% 1% 1%;
  display: flex;
  flex-flow: column;
  background-color: $off-white;

  .toolbar {
    margin-left: auto;
  }
}

.lists-container-pane {
  width: 83%;
  padding: 0 2% 1% 1%;
  background-color: $off-white;
}
</style>
