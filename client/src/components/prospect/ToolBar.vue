<template>
  <div class="toolbar">
    <button class="new-lead" @click="routeToLeadsNew">
      New Lead
    </button>
    <div class="kpi-container">
      <div class="header section-shadow">
        Filter
      </div>
      <form @submit.prevent="onSearchFilter">
        <label>Filter by Lead Title</label>
        <input v-model="searchTerm" />
        <div v-if="activeSearchTerm">
          <span class="help-text">Currently active: "{{ activeSearchTerm }}"</span>
          <span class="clear" @click.stop="clearSearchTerm">CLEAR</span>
        </div>
      </form>
      <div class="filter-container">
        <FilterByRep
          :repFilterState="repFilterState"
          :filterByUnclaimed="true"
          :unclaimedFilterState="unclaimedFilterState"
          @toggle-active-rep="emitToggleActiveRep"
          @toggle-unclaimed="$emit('toggle-unclaimed')"
        />
      </div>
    </div>
  </div>
</template>

<script>
import FilterByRep from '@/components/shared/FilterByRep'

export default {
  name: 'ToolBar',
  components: {
    FilterByRep,
  },
  data() {
    return {
      searchTerm: '',
    }
  },
  props: {
    repFilterState: {
      required: true,
      type: Object,
    },
    unclaimedFilterState: {
      required: true,
      type: Boolean,
    },
    activeSearchTerm: {
      type: String,
      required: true,
    },
  },
  methods: {
    routeToLeadsNew() {
      this.$router.push({ name: 'LeadsNew' })
    },
    emitToggleActiveRep(repID) {
      this.$emit('toggle-active-rep', repID)
    },
    onSearchFilter() {
      this.$emit('search-filter', this.searchTerm)
    },
    clearSearchTerm() {
      this.searchTerm = ''
      this.$emit('clear-search-filter')
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

.toolbar {
  width: 78%;
  height: auto;
  display: flex;
  flex-flow: column;
}

.toolbar,
.toolbar > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.875rem;
}

.header {
  @include base-font-styles();
  color: $main-font-gray;
  line-height: 1.14;
  font-size: 1rem;
  font-weight: bold;
  height: 3rem;
  display: flex;
  flex-flow: column;
  justify-content: center;
  margin-bottom: 1rem;
  padding-left: 1rem;
}

button.new-lead {
  @include primary-button();
  height: 2.5rem;
  width: 100%;
  font-size: 1rem;
}

.kpi-container {
  @include standard-border;
  margin-top: 1rem;
  background-color: $white;
}

.filter-container {
  height: auto;
  margin: 1.5rem 0;
}

form {
  width: 100%;
  display: flex;
  flex-flow: column;
  margin-top: 1rem;
  padding: 0 1rem;
  box-sizing: border-box;

  input {
    @include input-field;
    margin-top: 0.5rem;
    margin-left: 1rem;
  }

  div {
    display: flex;
    flex-flow: row;
    align-items: center;
    margin-top: 0.25rem;
    font-size: 0.8rem;

    .help-text {
      font-weight: 500rem;
      margin-left: 1rem;
      color: $dark-green;
    }

    .clear {
      @include pointer-on-hover;
      margin-left: auto;

      &:hover {
        font-weight: bold;
      }
    }
  }
}
</style>
