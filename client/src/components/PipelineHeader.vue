<template>
  <div class="table-row">
    <div style="padding: 2vh" class="table-cell-checkbox-header">
      <div>
        <input @click="emitCheckAll" type="checkbox" id="checkAllprimary" v-model="allSelected" />
        <label for="checkAllprimary"></label>
      </div>
    </div>
    <div class="cell-name-header">Name</div>
    <div class="table-cell-header" :key="i" v-for="(field, i) in oppFields" ref="fields">
      <p
        @click="$emit('sort-opps', `${field.dataType}`)"
        style="display: flex; flex-direction: row; align-items: center; margin-right: 0.2rem"
      >
        {{ field.referenceDisplayLabel }}
        <img style="height: 0.8rem" src="@/assets/images/sort.png" alt="" />
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineHeader',
  data() {
    return {}
  },
  methods: {
    emitCheckAll() {
      this.$emit('check-all')
    },
  },
  props: {
    oppFields: {},
    allSelected: {},
    dataType: {},
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';

.table-row {
  display: table-row;
}
.table-cell-checkbox-header {
  display: table-cell;
  padding: 2vh 1vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  z-index: 3;
  width: 4vw;
  top: 0;
  left: 0;
  position: sticky;
  background-color: $off-white;
}
.cell-name-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 3;
  left: 3.5vw;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
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
  letter-spacing: 0.5px;
  color: $base-gray;
}
// .rowed {
//   display: flex;
//   flex-direction: row;
//   justify-content: center;
//   // align-items: center;
//   outline: 1px solid red;
// }
