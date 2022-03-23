<template>
  <div class="table-row">
    <div style="padding: 2vh" class="table-cell-checkbox-header">
      <div>
        <input @click="emitCheckAll" type="checkbox" id="checkAllprimary" v-model="allSelected" />
        <label for="checkAllprimary"></label>
      </div>
    </div>

    <div
      @click="
        $emit('sort-opps', 'String', 'Name', 'name'),
          (sortingForward = false),
          (nameSort = 1),
          (sortingIndex = null),
          (reverseIndex = null)
      "
      v-if="sortingForward"
      class="cell-name-header"
    >
      <div class="sort-img-visible">
        Name
        <img v-if="nameSort === 0" style="height: 0.75rem" src="@/assets/images/sort.png" alt="" />
        <span v-if="nameSort === 2">
          <img class="light-green" src="@/assets/images/ascend.png" style="height: 0.6rem" alt="" />
        </span>
      </div>
    </div>

    <div
      @click="
        $emit('sort-opps-reverse', 'String', 'Name', 'name'),
          (sortingForward = true),
          (nameSort = 2),
          (sortingIndex = null),
          (reverseIndex = null)
      "
      v-if="sortingForward === false"
      class="cell-name-header"
    >
      <div class="sort-img-visible">
        Name
        <img v-if="nameSort === 0" style="height: 0.75rem" src="@/assets/images/sort.png" alt="" />
        <span v-if="nameSort === 1">
          <img
            class="light-green"
            src="@/assets/images/descend.png"
            style="height: 0.6rem"
            alt=""
          />
        </span>
      </div>
    </div>

    <div class="table-cell-header" :key="i" v-for="(field, i) in oppFields" ref="fields">
      <p
        v-if="sortingIndex !== i"
        @click="
          $emit(
            'sort-opps',
            `${field.dataType}`,
            `${field.referenceDisplayLabel}`,
            `${field.apiName}`,
          ),
            (sortingIndex = i),
            (reverseIndex = null),
            (nameSort = 0)
        "
        class="sort-img-visible"
      >
        {{ field.referenceDisplayLabel }}
        <img
          v-if="reverseIndex !== i"
          style="height: 0.75rem"
          src="@/assets/images/sort.png"
          alt=""
        />
        <span v-if="reverseIndex === i">
          <img class="light-green" src="@/assets/images/ascend.png" style="height: 0.6rem" alt="" />
        </span>
      </p>

      <p
        v-if="sortingIndex === i"
        @click="
          $emit(
            'sort-opps-reverse',
            `${field.dataType}`,
            `${field.referenceDisplayLabel}`,
            `${field.apiName}`,
          ),
            (sortingIndex = null),
            (reverseIndex = i),
            (nameSort = 0)
        "
        class="sort-img-visible"
      >
        {{ field.referenceDisplayLabel }}
        <img
          v-if="sortingIndex !== i"
          style="height: 0.75rem"
          src="@/assets/images/sort.png"
          alt=""
        />
        <span v-if="sortingIndex === i">
          <img
            class="light-green"
            src="@/assets/images/descend.png"
            style="height: 0.6rem"
            alt=""
          />
        </span>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineHeader',
  data() {
    return {
      sortingIndex: null,
      reverseIndex: null,
      sortingForward: true,
      nameSort: 0,
    }
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

// .light-green {
//   filter: invert(36%) sepia(81%) saturate(5047%) hue-rotate(139deg) brightness(107%) contrast(80%);
// }
.sort-img-visible {
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: pointer;
}

.sort-img-visible > img {
  display: none;
}
.sort-img-visible:hover > img {
  display: block;
}
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
</style>