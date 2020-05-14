<template>
  <div class="filter">
    <span class="title">Filter by Rep</span>
    <div class="reps-container">
      <span
        class="rep"
        v-for="rep in users.list"
        @click="toggleRepInFilter(rep.id)"
        :key="rep.id"
        :class="{ active: activeReps[rep.id] }"
      >
        {{ rep.fullName }}</span
      >
    </div>
  </div>
</template>

<script>
// NOTE FOR BRUNO 05/15/20 PB
/*

Using components is great because you do such a great job breaking down the code, 
One caveat with Vue is that deeply nested components dont always react to changes from their parents
so always passing data down through a prop does not mean that it will necessarily react when a change is made
for example:
ListIndex contains the data from the server, we pass that list to the ListContainer component
and that list passes it down to the List component
If I want to delete a list I can click the delete button from the List component and send back an event
through the ListContainer and then to the LeadIndex view. 
When my ListIndex successfully deletes the item from the backend I decide to slice it from the array (rather than another db hit)
This will not re-render the List component. 
Vue uses the keys to decide on rerendering (remember we usually use the id of a record)
Therefore although the list is updated the ID's are still the same and no re-rendering occures, therefore either the parent can reach into the child and call this.$foreceUpdate
or you have to make the api call to re-render
This is why I prefer to usually call apis directly from my child component if it is too deep

*/
import User from '@/services/users'
import CollectionManager from '@/services/collectionManager'
export default {
  name: 'FilterByRep',
  props: {
    activeReps: {
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
