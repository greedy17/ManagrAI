<template>
  <div class="filter">
    <span class="title">Filter by Rep</span>
    <div v-if="!users.refreshing" class="reps-container">
      <span
        class="rep"
        @click="toggleActiveRep(currentUser.id)"
        :key="currentUser.id"
        :class="{ active: repFilterState[currentUser.id] }"
      >
        You
      </span>
      <span
        v-if="filterByUnclaimed"
        class="rep"
        @click="$emit('toggle-unclaimed')"
        :key="'unclaimed'"
        :class="{ active: unclaimedFilterState }"
      >
        Unclaimed
      </span>
      <div class="divider" />
      <span
        class="rep"
        v-for="rep in otherReps"
        @click="toggleActiveRep(rep.id)"
        :key="rep.id"
        :class="{ active: repFilterState[rep.id] }"
      >
        {{ rep.fullName.trim() ? rep.fullName : rep.email }}
      </span>
    </div>
    <div v-else class="reps-container">
      <ComponentLoadingSVG />
    </div>
  </div>
</template>

<script>
import User from '@/services/users'
import CollectionManager from '@/services/collectionManager'

export default {
  name: 'FilterByRep',
  props: {
    repFilterState: {
      required: true,
      type: Object,
    },
    filterByUnclaimed: {
      type: Boolean,
      default: false,
    },
    unclaimedFilterState: {
      type: Boolean,
      default: false,
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
    otherReps() {
      return this.users.list.filter(u => u.id != this.currentUser.id)
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

.divider {
  border-top: 1px solid $soft-gray;
  margin: 0.3rem 0.5rem;
}
</style>
