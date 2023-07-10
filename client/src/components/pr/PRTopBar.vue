<template>
  <div class="top-bar">
    <div class="">
      <!-- Searches -->
      <Multiselect
        placeholder="All Searches"
        v-model="selectedSearch"
        :options="searchList"
        openDirection="below"
        class="search-picklist"
        selectLabel="Enter"
        label="name"
      >
        <template slot="noResult">
          <p class="multi-slot custom-picklist-font">No results. Try loading more</p>
        </template>
        <template slot="placeholder">
          <p class="slot-icon custom-picklist-font">
            <img src="@/assets/images/search.svg" alt="" />
            All Searches
          </p>
        </template>
      </Multiselect>
    </div>
    <div class="display-flex">
      <div>
        Today
      </div>
      <div>
        Media Type
      </div>
      <div>
        Hamburger
      </div>
      <div>
        Refresh
      </div>
      <div>
        Edit Search
      </div>
      <div>
        New Search
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'PRTopBar',
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      searchList: [
        {
          name: 'Tesla'
        }
      ],
      selectedSearch: null,
    }
  },
  watch: {

  },
  created() {

  },
  methods: {

  },
  computed: {
    
  }
}
</script>
<style lang="scss" scoped>
  .top-bar {
    display: flex;
  }
  .display-flex {
    display: flex;
  }
  .slot-icon {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 0;
    margin: 0;
    img {
      height: 1rem;
      margin-right: 0.25rem;
      filter: invert(70%);
    }
  }

  .search-picklist {
    width: 20vw;
  }
</style>