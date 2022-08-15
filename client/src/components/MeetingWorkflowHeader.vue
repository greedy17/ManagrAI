<template>
  <div class="table-row">
    <div class="cell-name-header">Meeting Title</div>
    <div class="table-cell-header" v-for="(column, i) in columns" :key="i">
      {{ column }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'MeetingWorkflowHeader',
  data() {
    return {
      columns: ['# of Attendees', 'Attendees', 'Record Type', 'Actions'],
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.table-row {
  display: table-row;
}
.cell-name-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  border-radius: 1px;
  z-index: 3;
  left: 0;
  top: 0;
  position: sticky;
  background-color: white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
.table-cell-header {
  display: table-cell;
  padding: 1.25vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  border-radius: 1px;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
</style>