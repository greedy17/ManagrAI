<template>
  <div class="filter">
    <span class="title">Filter by Rep</span>
    <div class="reps-container">
      <span
        class="rep"
        v-for="rep in reps"
        @click="toggleRepInFilter(rep.id)"
        :key="rep.id"
        :class="{ active: activeReps[rep.id] }"
      >
        {{ rep.name }}</span
      >
    </div>
  </div>
</template>

<script>
const exampleReps = [
  { id: 1, name: 'Marcy Ewald' },
  { id: 2, name: 'Pari Baker' },
  { id: 3, name: 'Bruno Garcia Gonzalez' },
]

export default {
  name: 'FilterByRep',
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

.filter {
  height: auto;
  padding: 0 1rem;
  flex-grow: 1;
  margin-bottom: 1rem;
  display: flex;
  flex-flow: column;
}

.section-shadow {
  box-shadow: 0 1px 0 0 $soft-gray;
}

.reps-container {
  flex-grow: 1;
  display: flex;
  flex-flow: column;
  box-sizing: border-box;
  height: auto;
  border: 1px solid $soft-gray;
  margin-left: 1rem;
  margin-top: 0.5rem;
  padding-top: 0.2rem;

  .rep {
    @include pointer-on-hover();
    @include disable-text-select();
    display: flex;
    flex-flow: column;
    justify-content: center;
    margin: 0.1rem 0.5rem;
    padding-left: 0.5rem;

    height: 1.5rem;
    border-radius: 0.2rem;
  }

  .active {
    background-color: rgba($color: $dark-green, $alpha: 0.4);
  }
}
</style>
