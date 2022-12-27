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
        $emit('sort-opps', 'String', userCRM === 'SALESFORCE' ? 'Name' : 'dealname', userCRM === 'SALESFORCE' ? 'name' : 'dealname'),
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
        <img v-if="nameSort === 0" style="height: 0.75rem" src="@/assets/images/sort.svg" alt="" />
        <span v-if="nameSort === 2">
          <img class="light-green" src="@/assets/images/ascend.svg" style="height: 0.6rem" alt="" />
        </span>
      </div>
    </div>

    <div
      @click="
        $emit('sort-opps-reverse', 'String', userCRM === 'SALESFORCE' ? 'Name' : 'dealname', userCRM === 'SALESFORCE' ? 'name' : 'dealname'),
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
        <img v-if="nameSort === 0" style="height: 0.75rem" src="@/assets/images/sort.svg" alt="" />
        <span v-if="nameSort === 1">
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
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="reverseIndex === i">
          <img class="light-green" src="@/assets/images/ascend.svg" style="height: 0.6rem" alt="" />
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
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="sortingIndex === i">
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
        v-if="sortingIndex !== oppFields.length + i"
        @click="
          $emit(
            'sort-opps',
            `${field.dataType}`,
            `${field.referenceDisplayLabel}`,
            `${field.apiName}`,
          ),
            (sortingIndex = oppFields.length + i),
            (reverseIndex = null),
            (nameSort = 0)
        "
        class="sort-img-visible"
      >
        {{ field.referenceDisplayLabel }}
        <img
          v-if="reverseIndex !== oppFields.length + i"
          style="height: 0.75rem"
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="reverseIndex === oppFields.length + i">
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
        v-if="sortingIndex === oppFields.length + i"
        @click="
          $emit(
            'sort-opps-reverse',
            `${field.dataType}`,
            `${field.referenceDisplayLabel}`,
            `${field.apiName}`,
          ),
            (sortingIndex = null),
            (reverseIndex = oppFields.length + i),
            (nameSort = 0)
        "
        class="sort-img-visible"
      >
        {{ field.referenceDisplayLabel }}
        <img
          v-if="sortingIndex !== oppFields.length + i"
          style="height: 0.75rem"
          src="@/assets/images/sort.svg"
          alt=""
        />
        <span v-if="sortingIndex === oppFields.length + i">
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

    <div class="table-cell-header-end">
      <div class="direction-row" @click="addField">
        <img src="@/assets/images/plusOne.svg" height="20px" style="filter: invert(30%)" alt="" />
      </div>

      <div v-if="addingField" class="add-field-section">
        <div class="add-field-section__title">
          <p>Add View Only Field</p>
          <img
            src="@/assets/images/close.svg"
            style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
            @click="closeAddField"
          />
        </div>

        <div class="add-field-section__body">
          <Multiselect
            style="width: 20vw"
            v-model="extraFieldObjs"
            placeholder="Select fields"
            selectLabel="Enter"
            label="referenceDisplayLabel"
            openDirection="below"
            track-by="id"
            :options="fieldOpts"
            :multiple="true"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
        </div>

        <div v-if="extraFieldObjs.length" @click="addExtraFields" class="add-field-section__footer">
          <p>Add</p>
        </div>
        <div v-else style="cursor: text" class="add-field-section__footer">
          <p style="color: gray; cursor: text">Add</p>
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
  name: 'PipelineHeader',
  data() {
    return {
      sortingIndex: null,
      reverseIndex: null,
      sortingForward: true,
      nameSort: 0,
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
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
  },
  methods: {
    async removeField(id) {
      try {
        const res = await SObjects.api.removeExtraField({
          field_ids: [id],
        })
        this.$toast('Field removed successfully', {
          timeout: 2000,
          position: 'bottom-right',
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
    removeExtraField(i) {
      this.removingField = true
      this.removingIndex = i
    },
    cancelRemoveField() {
      this.removingField = false
      this.removingIndex = null
    },
    addField() {
      this.addingField = true
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
    async addExtraFields() {
      for (let i = 0; i < this.extraFieldObjs.length; i++) {
        this.extraFields.push(this.extraFieldObjs[i].id)
      }
      try {
        const res = await SObjects.api.addExtraFields({
          field_ids: this.extraFields,
        })
        this.$toast('Field added successfully', {
          timeout: 2000,
          position: 'bottom-right',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.closeAddField()
        this.emitSetOpps()
      }
    },
  },
  props: {
    oppFields: {},
    allSelected: {},
    dataType: {},
    extraPipelineFields: {},
    fieldOpts: {},
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.red {
  filter: invert(46%) sepia(37%) saturate(832%) hue-rotate(308deg) brightness(104%) contrast(104%);
  height: 0.75rem;
}
.add-field-section {
  z-index: 5;
  position: absolute;
  right: 0.5rem;
  top: 9vh;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: white;
  min-width: 22vw;
  overflow: visible;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: $base-gray;
    // background-color: white;
    letter-spacing: 0.4px;
    padding-left: 1rem;
    font-size: 16px;
    width: 100%;
  }
  &__body {
    min-height: 3rem;
    padding-left: 1rem;
    margin-top: 1rem;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1rem;
    width: 100%;
    min-height: 6vh;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      color: $dark-green;
      font-weight: bolder;
    }
  }
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
  background-color: white;
  min-width: 16rem;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: $light-gray-blue;
    // background-color: white;
    letter-spacing: 0.4px;
    padding-left: 1rem;
    font-weight: bolder;
    font-size: 12px;
    width: 100%;
    height: 3rem;
  }
  &__body {
    height: 3rem;
    margin-left: 5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
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
      font-weight: bolder;
    }
  }
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
}
.table-cell-header-wide {
  border-bottom: 1px solid $soft-gray;
  display: table-cell;
  padding-left: 4px;
  min-width: 3rem;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: white;
  font-weight: bolder;
  font-size: 12px;
  letter-spacing: 0.75px;
  color: $light-gray-blue;
}
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

  border: none;
  z-index: 3;
  width: 4vw;
  top: 0;
  left: 0;
  position: sticky;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
}
.table-cell-header-end {
  display: table-cell;
  z-index: 3;
  right: 0;
  top: 0;
  position: sticky;
  font-weight: bolder;
  font-size: 12px;
  color: $base-gray;
  border-bottom: 1px solid $soft-gray;
  background-color: white;
  padding-left: 4px;
  // box-shadow: 1px 1px 2px 1px $very-light-gray;
}
.black {
  color: $base-gray;
}
.direction-row {
  width: 40px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}
.cell-name-header {
  display: table-cell;
  padding-left: 4px;
  border: none;
  border-bottom: 1px solid $soft-gray;
  z-index: 3;
  left: 3.5vw;
  top: 0;
  position: sticky;
  background-color: white;
  font-weight: bolder;
  font-size: 12px;
  letter-spacing: 0.75px;
  color: $light-gray-blue;
}
.table-cell-header {
  display: table-cell;
  padding-left: 4px;
  border: none;
  border-bottom: 1px solid $soft-gray;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: white;
  font-weight: bolder;
  font-size: 12px;
  letter-spacing: 0.75px;
  color: $light-gray-blue;
}
.invert {
  filter: invert(80%);
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