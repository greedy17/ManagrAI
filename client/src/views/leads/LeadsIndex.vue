<template>
  <LoadingSVG v-if="loading" />
  <div v-else class="leads-index">
    <div class="toolbar-pane">
      <div class="view-toggle-container">
        <span class="left" :class="{ bold: !isCurrentRoute }">Forecast</span>
        <ToggleCheckBox
          class="checkbox"
          :checked="isCurrentRoute"
          @toggle-view="toggleView"
          :eventToEmit="'toggle-view'"
        />
        <span class="right" :class="{ bold: isCurrentRoute }">Lists</span>
      </div>
      <ToolBar class="toolbar" />
    </div>
    <div class="lists-container-pane">
      <ListsContainer :lists="lists" :leadsWithoutList="leadsWithoutList" />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/leads-index/ToolBar'
import ListsContainer from '@/components/shared/ListsContainer'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'

import Lead from '@/services/leads'
import CollectionManager from '@/services/collectionManager'
// import List from '@/services/lists'

export default {
  name: 'LeadsIndex',
  components: {
    ToolBar,
    ToggleCheckBox,
    ListsContainer,
  },
  data() {
    return {
      loading: true,
      lists: null,
      leadsWithoutList: null,
    }
  },
  created() {
    CollectionManager.create({
      ModelClass: Lead,
      filters: {
        onList: 'False',
      },
    })
      .refresh()
      .then(collection => {
        this.leadsWithoutList = collection.list
        this.loading = false
      })
  },
  methods: {
    toggleView() {
      this.$router.push({ name: 'Forecast' })
    },
  },
  computed: {
    isCurrentRoute() {
      return this.$route.name == 'LeadsIndex'
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.leads-index {
  display: flex;
  flex-flow: row;
  padding-top: 2%;
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

.view-toggle-container {
  @include base-font-styles();
  font-size: 0.825rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  width: 78%;
  margin: 0 0 1rem auto;

  .left,
  .right {
    width: 4rem;
    margin: 0 auto;
  }

  .left {
    text-align: right;
  }

  .checkbox {
    margin: 0 auto;
  }

  .bold {
    font-weight: bold;
  }
}

.lists-container-pane {
  width: 83%;
  padding: 0 2% 1% 1%;
  background-color: $off-white;
}
</style>
