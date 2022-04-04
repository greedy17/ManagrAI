<template>
  <div class="table-row">
    <div style="padding: 2vh" class="table-cell-checkbox-header">
      <div>
        <input
          @click="emitCheckAll"
          type="checkbox"
          id="checkAllWorkflows"
          v-model="allWorkflowsSelected"
        />
        <label for="checkAllWorkflows"></label>
      </div>
    </div>

    <div
      @click="
        $emit('sort-opps-workflows', 'String', 'Name', 'name'),
          (sortingForwardWorkflows = false),
          (nameSortWorkflows = 1),
          (sortingIndexWorkflows = null),
          (reverseIndexWorkflows = null)
      "
      v-if="sortingForwardWorkflows"
      class="cell-name-header"
    >
      <div class="sort-img-visible">
        Name
        <img
          v-if="nameSortWorkflows === 0"
          style="height: 0.75rem"
          src="@/assets/images/sort.png"
          alt=""
        />
        <span v-if="nameSortWorkflows === 2">
          <img class="light-green" src="@/assets/images/ascend.png" style="height: 0.6rem" alt="" />
        </span>
      </div>
    </div>

    <div
      @click="
        $emit('sort-opps-reverse-workflows', 'String', 'Name', 'name'),
          (sortingForwardWorkflows = true),
          (nameSortWorkflows = 2),
          (sortingIndexWorkflows = null),
          (reverseIndexWorkflows = null)
      "
      v-if="sortingForwardWorkflows === false"
      class="cell-name-header"
    >
      <div class="sort-img-visible">
        Name
        <img
          v-if="nameSortWorkflows === 0"
          style="height: 0.75rem"
          src="@/assets/images/sort.png"
          alt=""
        />
        <span v-if="nameSortWorkflows === 1">
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
        v-if="sortingIndexWorkflows !== i"
        @click="
          $emit(
            'sort-opps-workflows',
            `${field.dataType}`,
            `${field.referenceDisplayLabel}`,
            `${field.apiName}`,
          ),
            (sortingIndexWorkflows = i),
            (reverseIndexWorkflows = null),
            (nameSortWorkflows = 0)
        "
        class="sort-img-visible"
      >
        {{ field.referenceDisplayLabel }}
        <img
          v-if="reverseIndexWorkflows !== i"
          style="height: 0.75rem"
          src="@/assets/images/sort.png"
          alt=""
        />
        <span v-if="reverseIndexWorkflows === i">
          <img class="light-green" src="@/assets/images/ascend.png" style="height: 0.6rem" alt="" />
        </span>
      </p>

      <p
        v-if="sortingIndexWorkflows === i"
        @click="
          $emit(
            'sort-opps-reverse-workflows',
            `${field.dataType}`,
            `${field.referenceDisplayLabel}`,
            `${field.apiName}`,
          ),
            (sortingIndexWorkflows = null),
            (reverseIndexWorkflows = i),
            (nameSortWorkflows = 0)
        "
        class="sort-img-visible"
      >
        {{ field.referenceDisplayLabel }}
        <img
          v-if="sortingIndexWorkflows !== i"
          style="height: 0.75rem"
          src="@/assets/images/sort.png"
          alt=""
        />
        <span v-if="sortingIndexWorkflows === i">
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
  name: 'WorkflowHeader',
  data() {
    return {
      sortingIndexWorkflows: null,
      reverseIndexWorkflows: null,
      sortingForwardWorkflows: true,
      nameSortWorkflows: 0,
    }
  },
  methods: {
    emitCheckAll() {
      this.$emit('check-all')
    },
  },
  props: {
    oppFields: {},
    allWorkflowsSelected: {},
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

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
</style>