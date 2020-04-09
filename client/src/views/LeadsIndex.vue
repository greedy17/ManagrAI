<template>
  <div class="leads-index">
    <NavBar />
    <div class="page-content">
      <div class="toolbar-pane">
        <ToolBar />
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
  height: inherit;
  display: flex;
  flex-flow: column;
  background-color: $off-white;
}

.page-content {
  overflow-x: scroll;
  flex-grow: 1;
  display: flex;
  flex-flow: row;
}

.toolbar-pane {
  width: 17%;
  padding: 1%;
  background-color: $off-white;
  /* screenshot -related */
  display: flex;
  flex-flow: row;
  justify-content: center;
  .left-pane-screenshot {
    width: 217px;
    height: 781px;
    display: block;
    margin-left: auto;
  }
}

.lists-container-pane {
  width: 83%;
  padding: 1% 2% 1% 1%;
  background-color: $off-white;
}
</style>
