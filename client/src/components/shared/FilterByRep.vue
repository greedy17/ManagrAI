<template>
  <div class="filter">
    <span class="title">Filter by Rep</span>
    <div class="reps-container">
      <span
        class="rep"
        v-for="rep in users.list"
        @click="toggleActiveRep(rep.id)"
        :key="rep.id"
        :class="{ active: repFilterState[rep.id] }"
      >
        {{ rep.id == currentUser.id ? 'Me' : rep.fullName }}</span
      >
    </div>
  </div>
</template>

<script>
// understanding reactivity pb 05/15/20
//https://vuejs.org/v2/guide/list.html#Array-Change-Detection

import User from '@/services/users'
import CollectionManager from '@/services/collectionManager'
export default {
  name: 'FilterByRep',
  props: {
    repFilterState: {
      required: true,
      type: Object,
    },
  },
  data() {
    return {
      users: CollectionManager.create({
        ModelClass: User,
        filters: {
          active: true,
        },
      }),
    }
  },
  async created() {
    this.users.refresh()
  },
  methods: {
    toggleActiveRep(repID) {
      this.$emit('toggle-active-rep', repID)
    },
  },
  computed: {
    currentUser() {
      return this.$store.state.user
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
  @include standard-border();
  flex-grow: 1;
  display: flex;
  flex-flow: column;
  box-sizing: border-box;
  height: auto;
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
