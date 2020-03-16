<template>
  <div class="list">
    <div class="list-header" @click="toggleDetails">
      <img class="icon" src="/list-header.svg" />
      <span class="list-title"> {{ list.title }} </span>
      <span class="list-length"> {{ list.leads.length }} Leads </span>
    </div>
    <div class="list-details" v-if="showDetails">
      Details!
    </div>
  </div>
</template>

<script>
export default {
  name: 'List',
  props: ['list'],
  data() {
    return {
      showDetails: false,
    }
  },
  methods: {
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
  },
}
</script>

<style lang="scss" scoped>
.list-header {
  display: flex;
  flex-flow: row;
  align-items: stretch;
  margin-left: 2%;

  &:hover {
    cursor: pointer;
  }
}

.icon {
  height: 40px;
  width: 40px;
  display: block;
}

.list-title {
  align-self: center;
  width: 25%;
}
.list-length {
  align-self: center;
  margin-left: auto;
  margin-right: 50%;
}
</style>
