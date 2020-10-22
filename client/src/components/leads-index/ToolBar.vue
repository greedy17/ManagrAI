<template>
  <div class="toolbar">
    <div class="header section-shadow">
      Filter
    </div>
    <div class="filter section-shadow">
      <div class="filter-header">Rating</div>
      <div class="filter-options">
        <LeadRating
          v-for="(n, i) in 5"
          :key="'rating' + '-' + (5 - i)"
          class="option"
          :selected="currentFilters.byRating ? currentFilters.byRating : null"
          :rating="6 - n"
          @update-rating-filter="emitUpdateFilter({ key: 'byRating', value: $event })"
        />
      </div>
    </div>
    <div class="filter section-shadow">
      <div class="filter-header">Stage</div>
      <div class="filter-options">
        <div
          class="option"
          @click="emitUpdateFilter({ key: 'byStatus', value: status.obj.id })"
          v-for="status in statuses"
          :key="status.obj.id"
          :class="{
            active: currentFilters.byStatus ? currentFilters.byStatus == status.obj.id : false,
          }"
        >
          {{ status.obj.title.toLowerCase() }} ({{ status.count }})
        </div>
      </div>
    </div>
    <div class="filter section-shadow">
      <div class="filter-header">Score</div>
      <div class="filter-options">
        <div
          class="option"
          v-for="option in scoreOptions"
          @click="emitUpdateFilter({ key: 'byScore', value: option.value })"
          :key="option.value"
          :class="{
            active: currentFilters.byScore ? currentFilters.byScore == option.value : false,
          }"
        >
          {{ option.value }} ({{ option.count }})
        </div>
      </div>
    </div>
    <div
      class="filter section-shadow"
      v-if="$store.state.user.isManager || $store.state.user.isStaff"
    >
      <FilterByRep
        :repFilterState="formattedRepFilters"
        @toggle-active-rep="toggleRep"
        @select-all-reps="toggleAllReps"
        @deselect-all-reps="toggleAllReps"
      />
    </div>
  </div>
</template>

<script>
import { forecastEnums } from '@/services/leads/enumerables'
import LeadRating from '@/components/leads-index/LeadRating'
import FilterByRep from '@/components/shared/FilterByRep'
import Lead from '@/services/leads'

const LEAD_SCORE_RANGES = ['0-25', '26-50', '51-75', '76-100']

export default {
  name: 'ListsToolBar',
  components: {
    LeadRating,
    FilterByRep,
  },
  props: {
    currentFilters: {
      type: Object,
    },
  },
  data() {
    return {
      forecastEnums,
      statuses: this.$store.state.stages.map(s => ({ obj: s, count: null })),
      scoreOptions: LEAD_SCORE_RANGES.map(r => ({ value: r, count: null })),
    }
  },
  created() {
    this.getAllCounts()
  },
  methods: {
    getAllCounts() {
      this.statuses.forEach(this.fetchStatusCount)
      this.scoreOptions.forEach(this.fetchScoreOptionCount)
    },
    fetchStatusCount(status) {
      let params = {
        stage: status.obj.id,
        representatives: this.currentFilters.byReps.join(','),
        scoreRange: this.currentFilters.byScore,
        rating: this.currentFilters.byRating,
      }
      Lead.api.count(params).then(data => {
        status.count = data.count
      })
    },
    fetchScoreOptionCount(scoreOption) {
      let params = {
        stage: this.currentFilters.byStatus,
        representatives: this.currentFilters.byReps.join(','),
        scoreRange: scoreOption.value,
        rating: this.currentFilters.byRating,
      }
      Lead.api.count(params).then(data => {
        scoreOption.count = data.count
      })
    },
    toggleAllReps(repArray) {
      if (!repArray) {
        // deselect all is a default from the component
        // for this view we want it to deselect everyone but self
        repArray = [this.$store.state.user.id]
      }
      this.$emit('update-filter', { key: 'byReps', value: repArray })
    },
    toggleRep(repId) {
      if (this.formattedRepFilters[repId]) {
        let reps = this.currentFilters.byReps.filter(rep => rep !== repId)

        // if the list is empty set it to the current user (aka disable no select)
        if (!reps.length) {
          reps = [this.$store.state.user.id]
        }
        this.$emit('update-filter', {
          key: 'byReps',
          value: reps,
        })
      } else {
        this.$emit('update-filter', {
          key: 'byReps',
          value: [...this.currentFilters.byReps, repId],
        })
      }
    },
    emitUpdateFilter(item) {
      this.$emit('update-filter', item)
    },
  },
  computed: {
    formattedRepFilters() {
      let repFilters = {}
      if (this.currentFilters.byReps) {
        this.currentFilters.byReps.forEach(rep => (repFilters[rep] = true))
      }
      return repFilters
    },
  },
  watch: {
    currentFilters: {
      deep: true,
      handler() {
        this.getAllCounts()
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.toolbar {
  @include disable-text-select();
  @include standard-border();
  background-color: $white;

  height: auto;
  display: flex;
  flex-flow: column;
}

.toolbar,
.toolbar > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 14px;
}

.header,
.sort {
  display: flex;
  flex-flow: column;
  justify-content: center;
  height: 3rem;
}

.header {
  padding-left: 7%;
  font-weight: bold;
}

.sort {
  padding-left: 10%;
  font-weight: normal;
}

.sort-header {
  display: flex;
  flex-flow: row;
  align-items: center;

  .icon {
    margin: 0 10% 0 auto;
  }
}

.filter {
  .filter-header {
    height: 3rem;
    display: flex;
    flex-flow: column;
    justify-content: center;
    padding-left: 10%;
    font-weight: normal;
  }

  .filter-options {
    padding-left: 14%;
    margin-bottom: 1.25rem;
    color: rgba($color: $main-font-gray, $alpha: 0.4);

    .option {
      height: 1.75rem;
      margin: 0.5rem;
      cursor: pointer;
      max-width: 6rem;
      text-transform: capitalize;
    }
  }
}

.list {
  margin-bottom: 0.875rem;
}
.active {
  color: rgba($color: $dark-green, $alpha: 1);
}
</style>
