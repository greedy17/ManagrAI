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

    <div :key="field.name" v-for="(field, i) in extraPipelineFields" class="table-cell-header">
      <p @click="removeExtraField(i)" class="sort-img-visible">
        {{ field.referenceDisplayLabel }}
        <img
          style="height: 0.75rem; margin-top: 0.25rem"
          src="@/assets/images/remove.png"
          class="invert"
          alt=""
        />
      </p>
      <div v-if="removingField && removingIndex === i" class="remove-field-section">
        <div class="remove-field-section__title">Remove {{ field.referenceDisplayLabel }}</div>
        <div class="remove-field-section__body">Are you sure ?</div>
        <div class="remove-field-section__footer">
          <p style="color: #199e54" @click="removeField(field.id)">Remove</p>
          <p style="color: #fa646a" @click="cancelRemoveField">Cancel</p>
        </div>
      </div>
    </div>

    <div class="table-cell-header">
      <div v-outside-click="closeAddField" class="direction-row" @click="addField">
        <p style="color: white">.</p>
        <img src="@/assets/images/plusOne.png" class="add-row" alt="" />
      </div>

      <div v-if="addingField" class="add-field-section">
        <div class="add-field-section__title">
          <p>Add View Only Field</p>
          <!-- <img
            src="@/assets/images/closer.png"
            style="height: 1rem; cursor: pointer; margin-right: 0.75rem; margin-top: -0.5rem"
            @click="closeAddField"
          /> -->
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
            :options="objectFields.list"
            :multiple="true"
          >
            <template slot="noResult">
              <div class="row">
                <p>No results</p>
                <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
              </div>
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
import Modal from '@/components/InviteModal'
import Multiselect from 'vue-multiselect'

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
        pagination: { size: 500 },
      }),
    }
  },
  components: {
    Modal,
    Multiselect,
  },
  async created() {
    await this.objectFields.refresh()
  },
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
  methods: {
    test() {
      console.log(this.extraFields)
    },
    async removeField(id) {
      try {
        const res = await SObjects.api.removeExtraField({
          field_ids: [id],
        })
        this.$Alert.alert({
          type: 'success',
          timeout: 1000,
          message: 'Field removed successfully',
        })
        console.log(res)
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
    nextPage() {
      this.objectFields.nextPage()
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
      console.log(this.extraFields)
      try {
        const res = await SObjects.api.addExtraFields({
          field_ids: this.extraFields,
        })
        this.$Alert.alert({
          type: 'success',
          timeout: 1000,
          message: 'Field added successfully',
        })
        console.log(res)
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
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';

::v-deep .multiselect {
  min-width: 7rem;
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
  background-color: $white;
  min-width: 22vw;
  overflow: visible;
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
      font-weight: bold;
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
.add-row {
  height: 1rem;
  margin-left: 0.25rem;
  padding-right: 0.25rem;
  filter: invert(36%) sepia(81%) saturate(5047%) hue-rotate(139deg) brightness(77%) contrast(80%);
}
.direction-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: pointer;
  color: $dark-green;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;

  img {
    margin-left: 0.5rem;
  }
}
</style>