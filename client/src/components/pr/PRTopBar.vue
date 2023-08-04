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
      <div class="button">
        <img class="icon-img" src="@/assets/images/calendar.svg" />
        <span>Today</span>
      </div>
      <div class="button">
        <img class="icon-img" src="@/assets/images/comment.svg" />
        <span>Media Type</span>
      </div>

      <div class="button">
        <img class="icon-img" src="@/assets/images/edit-round.svg" />
        <span>Edit Search</span>
      </div>
      <div class="dark-button">
        <img class="icon-img" src="@/assets/images/sparkles-round.svg" />
        <span>New Search</span>
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
          name: 'Tesla',
        },
      ],
      selectedSearch: null,
    }
  },
  watch: {},
  created() {},
  methods: {},
  computed: {},
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

::v-deep .multiselect * {
  font-size: 13px;
  font-family: $base-font-family;
  border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}

::v-deep .multiselect__content-wrapper {
  border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  position: absolute !important;
}

::v-deep .multiselect__tags {
  border: 1px solid rgba(0, 0, 0, 0.15) !important;
}

::v-deep .multiselect__placeholder {
  color: $base-gray;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  width: 93vw;
  background-color: $white;
  border-radius: 8px;
  margin-top: 0.5rem;
  padding: 0.5rem;
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
.button {
  @include gray-text-button();
  margin-left: 1rem;
}
.dark-button {
  @include dark-blue-button();
  margin-left: 1rem;
  img {
    filter: invert(81%) sepia(38%) saturate(738%) hue-rotate(349deg) brightness(95%) contrast(88%);
  }
}
.icon-img {
  height: 12px;
  margin-right: 0.5rem;
}
.refresh-margin {
  margin-left: 4rem;
}
.no-img-margin {
  margin: 0;
}
</style>