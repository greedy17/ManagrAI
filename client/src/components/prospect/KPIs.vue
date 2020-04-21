<template>
  <div class="kpis">
    <div class="header section-shadow">
      KPIs
    </div>
    <FilterByRep :reps="reps" :activeReps="activeReps" @toggle-rep-in-filter="toggleRepInFilter" />
  </div>
</template>

<script>
import FilterByRep from '@/components/shared/FilterByRep'

const exampleReps = [
  { id: 1, name: 'Marcy Ewald' },
  { id: 2, name: 'Pari Baker' },
  { id: 3, name: 'Bruno Garcia Gonzalez' },
]

export default {
  name: 'KPIs',
  components: { FilterByRep },
  data() {
    return {
      reps: exampleReps,
      activeReps: {}, // for the filter
    }
  },
  methods: {
    toggleRepInFilter(repID) {
      // depending on state of this.activeReps --> add or make false at that key
      // plainObject is used instead of an array because of O(1) lookup for <div class="rep" v-for.. />
      if (!this.activeReps[repID]) {
        this.activeReps = Object.assign({}, this.activeReps, { [repID]: true })
      } else {
        this.activeReps = Object.assign({}, this.activeReps, { [repID]: false })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.kpis {
  background-color: $white;
  height: 15rem;
  width: 15rem;
  border: 1px solid $soft-gray;
  display: flex;
  flex-flow: column;
}

.header {
  font-family: $base-font-family, $backup-base-font-family;
  color: $main-font-gray;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
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

.section-shadow {
  box-shadow: 0 1px 0 0 $soft-gray;
}
</style>
