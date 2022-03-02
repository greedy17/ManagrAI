<template>
  <div>
    <div style="max-width: 14vw">
      {{ name }}
      <span style="color: #199e54; margin-left: 0.2rem">{{
        accountName ? accountName : '---'
      }}</span>
      <div style="color: #9b9b9b">owned by {{ owner }}</div>
    </div>
    <!-- <div class="flex-row">
        <img
          @click="createFormInstance(id)"
          class="name-cell-note-button"
          src="@/assets/images/edit-note.png"
        />
        <img
          @click="getNotes(id)"
          class="name-cell-edit-note-button"
          src="@/assets/images/white-note.png"
        />
      </div> -->
  </div>
</template>

<script>
export default {
  name: 'PipelineRow',
  data() {
    return {}
  },
  methods: {},
  props: {
    name: {
      type: String,
    },
    accountName: {
      type: String,
    },
    owner: {
      type: String,
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.table {
  display: table;
  overflow: scroll;
  width: 99vw;
}
.empty-table {
  display: table;
  width: 98vw;
}
.table-row {
  display: table-row;
}
.table-cell {
  display: table-cell;
  position: sticky;
  min-width: 12vw;
  background-color: $off-white;
  padding: 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.table-cell-selected {
  display: table-cell;
  position: sticky;
  min-width: 12vw;
  background-color: white;
  color: $darker-green;
  padding: 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.table-cell:hover {
  cursor: text;
  background-color: white;
}
.table-cell-checkbox {
  display: table-cell;
  padding: 2vh;
  width: 4vw;
  border: none;
  left: 2px;
  position: sticky;
  z-index: 1;
  border-bottom: 1px solid $soft-gray;
  background-color: $off-white;
}
.table-cell-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.25px;
  color: $base-gray;
}
.cell-name-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 3;
  left: 4vw;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.25px;
  color: $base-gray;
}
.table-cell-checkbox-header {
  display: table-cell;
  padding: 2vh 1vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  z-index: 3;
  width: 4vw;
  top: 0;
  left: 2px;
  position: sticky;
  background-color: $off-white;
}
.table-row:nth-child(even) {
  background: $off-white;
}
.cell-name {
  background-color: white;
  color: $base-gray;
  letter-spacing: 0.25px;
  position: sticky;
  left: 4vw;
  z-index: 2;
}
