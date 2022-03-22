<template>
  <div class="table-row">
    <div v-if="opp" class="table-cell-checkbox">
      <div v-if="updateList.includes(opp.id)">
        <SkeletonBox width="10px" height="9px" />
      </div>
      <div v-else>
        <input
          @click="emitCheckedBox"
          type="checkbox"
          :id="index"
          v-model="primaryCheckList"
          :value="opp.id"
        />
        <label :for="index"></label>
      </div>
    </div>

    <div style="min-width: 26vw" class="table-cell cell-name">
      <div class="flex-row-spread">
        <div>
          <div class="flex-col" v-if="updateList.includes(opp.id)">
            <SkeletonBox width="125px" height="14px" style="margin-bottom: 0.2rem" />
            <SkeletonBox width="125px" height="9px" />
          </div>

          <PipelineNameSection
            v-else
            :name="opp['secondary_data']['Name']"
            :accountName="opp.account_ref ? opp.account_ref.name : ''"
            :owner="opp.owner_ref.first_name"
          />
        </div>
        <div v-if="updateList.includes(opp.id)" class="flex-row">
          <SkeletonBox width="15px" height="14px" />
          <SkeletonBox width="15px" height="14px" />
        </div>
        <div v-else class="flex-column">
          <button @click="emitCreateForm" class="name-cell-edit-note-button-1">
            Update
            <img class="invert" src="@/assets/images/edit-note.png" />
          </button>
          <button @click="emitGetNotes" class="name-cell-note-button-1">
            Notes
            <img class="gray" src="@/assets/images/white-note.png" />
          </button>
        </div>
      </div>
    </div>

    <div
      :key="i"
      v-for="(field, i) in oppFields"
      :class="
        field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
          ? 'table-cell-wide'
          : 'table-cell'
      "
    >
      <SkeletonBox v-if="updateList.includes(opp.id) && opp" width="100px" height="14px" />

      <div class="limit-cell-height" v-else-if="!updateList.includes(opp.id) && opp">
        <PipelineField
          style="direction: ltr"
          :apiName="field.apiName"
          :dataType="field.dataType"
          :fieldData="
            field.apiName.includes('__c')
              ? opp['secondary_data'][field.apiName]
              : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
          "
          :lastStageUpdate="opp['last_stage_update']"
        />
      </div>
    </div>
  </div>
</template>

<script>
import PipelineNameSection from '@/components/PipelineNameSection'
import PipelineField from '@/components/PipelineField'
import SkeletonBox from '@/components/SkeletonBox'

export default {
  name: 'PipelineTableRow',
  components: {
    PipelineNameSection,
    PipelineField,
    SkeletonBox,
  },
  data() {
    return {}
  },
  methods: {
    emitCreateForm() {
      this.$emit('create-form')
    },
    emitGetNotes() {
      this.$emit('get-notes')
    },
    emitCheckedBox() {
      this.$emit('checked-box')
    },
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1)
    },
    camelize(str) {
      return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function (match, index) {
        if (+match === 0) return ''
        return index === 0 ? match.toLowerCase() : match.toUpperCase()
      })
    },
  },
  props: {
    index: {},
    opp: {},
    oppFields: {},
    primaryCheckList: {},
    updateList: {},
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';

.table-row {
  display: table-row;
}
.table-cell {
  display: table-cell;
  position: sticky;
  min-width: 12vw;
  background-color: $off-white;
  padding: 2vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.cell-name {
  background-color: white;
  color: $base-gray;
  letter-spacing: 0.25px;
  position: sticky;
  left: 3.5vw;
  z-index: 2;
}
.table-cell-wide {
  display: table-cell;
  position: sticky;
  min-width: 26vw;
  background-color: $off-white;
  padding: 2vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
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
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.flex-column {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: flex-end;
}
.flex-row {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
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
.limit-cell-height {
  max-height: 4rem;
  width: 110%;
  overflow: auto;
  direction: rtl;
}
.name-cell-note-button-1 {
  cursor: pointer;
  border: none;
  border-radius: 0.2rem;
  padding: 0.25rem 0.3rem;
  background-color: white;
  box-shadow: 1px 1px 3px $very-light-gray;
  max-width: 4rem;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: space-around;
  font-size: 11px;
  font-weight: 700px;
  letter-spacing: 0.25px;
  img {
    height: 0.8rem;
  }
}
.name-cell-note-button-1:hover,
.name-cell-edit-note-button-1:hover {
  transform: scale(1.03);
  box-shadow: 1px 1px 1px 1px $very-light-gray;
}
.name-cell-edit-note-button-1 {
  cursor: pointer;
  border: none;
  border-radius: 0.2rem;
  padding: 0.25rem 0.3rem;
  background-color: $dark-green;
  color: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  box-shadow: 1px 1px 2px $very-light-gray;
  font-weight: 700px;
  letter-spacing: 0.25px;
  margin-top: 0.4rem;
  margin-bottom: 0.3rem;

  img {
    height: 0.8rem;
    margin-left: 0.25rem;
  }
}
// ::-webkit-scrollbar {
//   background-color: $off-white;
//   -webkit-appearance: none;
//   height: 100%;
//   width: 3px;
// }
// ::-webkit-scrollbar-thumb {
//   border-radius: 3px;
//   background-color: $very-light-gray;
// }
// ::-webkit-scrollbar-track {
//   margin-top: 1rem;
// }
</style>