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
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="nameSortWorkflows === 2">
          <img class="light-green" src="@/assets/images/ascend.svg" style="height: 0.6rem" alt="" />
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
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="nameSortWorkflows === 1">
          <img
            class="light-green"
            src="@/assets/images/descend.svg"
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
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="reverseIndexWorkflows === i">
          <img class="light-green" src="@/assets/images/ascend.svg" style="height: 0.6rem" alt="" />
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
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="sortingIndexWorkflows === i">
          <img
            class="light-green"
            src="@/assets/images/descend.svg"
            style="height: 0.6rem"
            alt=""
          />
        </span>
      </p>
    </div>

    <div :key="field.name" v-for="(field, i) in extraPipelineFields" class="table-cell-header-wide">
      <p
        v-if="sortingIndexWorkflows !== oppFields.length + i"
        @click="
          $emit(
            'sort-opps',
            `${field.dataType}`,
            `${field.referenceDisplayLabel}`,
            `${field.apiName}`,
          ),
            (sortingIndexWorkflows = oppFields.length + i),
            (reverseIndexWorkflows = null),
            (nameSortWorkflows = 0)
        "
        class="sort-img-visible"
      >
        {{ field.referenceDisplayLabel }}
        <img
          v-if="reverseIndexWorkflows !== oppFields.length + i"
          style="height: 0.75rem"
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="reverseIndexWorkflows === oppFields.length + i">
          <img class="light-green" src="@/assets/images/ascend.svg" style="height: 0.6rem" alt="" />
        </span>
        <img
          style="margin-left: 0.1rem"
          class="red"
          @click="removeExtraField(i)"
          src="@/assets/images/close.svg"
          alt=""
        />
      </p>

      <p
        v-if="sortingIndexWorkflows === oppFields.length + i"
        @click="
          $emit(
            'sort-opps-reverse',
            `${field.dataType}`,
            `${field.referenceDisplayLabel}`,
            `${field.apiName}`,
          ),
            (sortingIndexWorkflows = null),
            (reverseIndexWorkflows = oppFields.length + i),
            (nameSortWorkflows = 0)
        "
        class="sort-img-visible"
      >
        {{ field.referenceDisplayLabel }}
        <img
          v-if="sortingIndexWorkflows !== oppFields.length + i"
          style="height: 0.75rem"
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="sortingIndexWorkflows === oppFields.length + i">
          <img
            class="light-green"
            src="@/assets/images/descend.svg"
            style="height: 0.6rem"
            alt=""
          />
        </span>
        <img class="red" @click="removeExtraField(i)" src="@/assets/images/close.svg" alt="" />
      </p>

      <div v-if="removingField && removingIndex === i" class="remove-field-section">
        <div class="remove-field-section__title">Remove {{ field.referenceDisplayLabel }}</div>
        <div class="remove-field-section__body">Are you sure ?</div>
        <div class="remove-field-section__footer">
          <p style="color: #fa646a" @click="removeField(field.id)">Remove</p>
          <p style="color: #9b9b9b" @click="cancelRemoveField">Cancel</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { SObjects } from '@/services/salesforce'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjectField } from '@/services/salesforce'

export default {
  name: 'WorkflowHeader',
  computed: {
    extraPipelineFields() {
      let extras = []
      extras = this.objectFields.list.filter((field) => this.hasExtraFields.includes(field.id))
      return extras
    },
    hasExtraFields() {
      return this.$store.state.user.salesforceAccountRef.extraPipelineFields
    },
  },
  data() {
    return {
      sortingIndexWorkflows: null,
      reverseIndexWorkflows: null,
      sortingForwardWorkflows: true,
      nameSortWorkflows: 0,
      extraFields: [],
      extraFieldObjs: [],
      addingField: false,
      removingField: false,
      removingIndex: null,
      objectFields: CollectionManager.create({
        ModelClass: SObjectField,
        pagination: { size: 200 },
        filters: {
          salesforceObject: 'Opportunity',
        },
      }),
    }
  },
  async created() {
    await this.objectFields.refresh()
  },
  methods: {
    async removeField(id) {
      try {
        const res = await SObjects.api.removeExtraField({
          field_ids: [id],
        })
        this.$toast('Field removed successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.cancelRemoveField()
        this.emitSetOpps()
      }
    },
    cancelRemoveField() {
      this.removingField = false
      this.removingIndex = null
    },
    removeExtraField(i) {
      this.removingField = true
      this.removingIndex = i
    },
    closeAddField() {
      this.addingField = false
      this.extraFields = []
      this.extraFieldObjs = []
    },
    emitCheckAll() {
      this.$emit('check-all')
    },
    emitSetOpps() {
      this.$emit('set-opps')
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
.red {
  filter: invert(46%) sepia(37%) saturate(832%) hue-rotate(308deg) brightness(104%) contrast(104%);
  height: 0.75rem;
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
  border-bottom: 1px solid $light-orange-gray;
  z-index: 3;
  width: 4vw;
  top: 0;
  left: 0;
  position: sticky;
  background-color: $off-white;
}
.remove-field-section {
  z-index: 5;
  position: absolute;
  right: 0;
  top: 9vh;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 16rem;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.4px;
    padding-left: 1rem;
    font-weight: bold;
    font-size: 14px;
    width: 100%;
    height: 3rem;
  }
  &__body {
    height: 3rem;
    margin-left: 5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-evenly;
    width: 100%;
    height: 3rem;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      // color: $dark-green;
      font-weight: bold;
    }
  }
}
.table-cell-header-wide {
  display: table-cell;
  padding: 0.25rem;
  padding: 1.25vh 2.5vh;
  min-width: 3rem;
  border: none;
  border-bottom: 1px solid $light-orange-gray;
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
.cell-name-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 1px solid $light-orange-gray;
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
  padding: 1.25vh 3vh;
  border: none;
  border-bottom: 1px solid $light-orange-gray;
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
input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 0.9ex;
  left: 0.4ex;
  border: 2px solid $dark-green;
  border-top: none;
  border-right: none;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}
input[type='checkbox'] {
  line-height: 2.1ex;
}
input[type='checkbox'] {
  position: absolute;
  left: -999em;
}
input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}
input[type='checkbox'] + label::before {
  content: '';
  display: inline-block;
  vertical-align: -22%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}
</style>