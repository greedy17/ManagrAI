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
export default {
  name: 'FilterByRep',
  props: {
    reps: {
      required: true,
      type: Array,
    },
    activeReps: {
      required: true,
      type: Object,
    },
  },
  methods: {
    toggleRepInFilter(repID) {
      this.$emit('toggle-rep-in-filter', repID)
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
