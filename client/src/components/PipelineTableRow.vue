<template>
  <div class="table-row">
    <div v-if="opp" class="table-cell-checkbox">
      <div v-if="updateList.includes(opp.id) || updatedList.includes(opp.id)">
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
          <div
            class="flex-column"
            v-if="updateList.includes(opp.id) || updatedList.includes(opp.id)"
          >
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
        <div v-if="updateList.includes(opp.id) || updatedList.includes(opp.id)" class="flex-row">
          <SkeletonBox width="15px" height="14px" />
          <SkeletonBox width="15px" height="14px" />
        </div>
        <div v-else class="flex-row">
          <button @click="emitCreateForm" class="name-cell-edit-note-button-1">
            <img style="filter: invert(90%); height: 0.6rem" src="@/assets/images/edit.png" />
          </button>
          <button @click="emitGetNotes" class="name-cell-note-button-1">
            <img class="gray" src="@/assets/images/white-note.png" />
          </button>
        </div>
      </div>
    </div>

    <div
      :key="i"
      v-for="(field, i) in oppFields"
      :class="
        field.dataType === 'TextArea' ||
        (field.length > 250 &&
          field.dataType === 'String' &&
          (opp['secondary_data'][field.apiName] ||
            opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]))
          ? 'table-cell-wide'
          : opp['secondary_data'][field.apiName] ||
            opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
          ? 'table-cell'
          : 'empty'
      "
    >
      <SkeletonBox
        v-if="updateList.includes(opp.id) || updatedList.includes(opp.id)"
        width="100px"
        height="14px"
      />

      <div class="limit-cell-height" v-else-if="!updateList.includes(opp.id)">
        <PipelineField
          style="direction: ltr"
          :apiName="field.apiName"
          :dataType="field.dataType"
          :fieldData="
            field.apiName.includes('__c') || field.apiName.includes('__r')
              ? opp['secondary_data'][field.apiName]
              : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
          "
          :lastStageUpdate="opp['last_stage_update']"
        />
      </div>
    </div>
    <div
      :key="field.id"
      v-for="field in extraPipelineFields"
      :class="
        opp['secondary_data'][field.apiName] ||
        opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
          ? 'table-cell'
          : 'empty'
      "
    >
      <SkeletonBox
        v-if="updateList.includes(opp.id) || updatedList.includes(opp.id)"
        width="100px"
        height="14px"
      />

      <div class="limit-cell-height" v-else-if="!updateList.includes(opp.id)">
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
    <div class="table-cell-checkbox"></div>
  </div>
</template>

<script>
import PipelineNameSection from '@/components/PipelineNameSection'
import PipelineField from '@/components/PipelineField'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjectField } from '@/services/salesforce'

export default {
  name: 'PipelineTableRow',
  components: {
    PipelineNameSection,
    PipelineField,
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
  },
  async created() {
    await this.objectFields.refresh()
  },
  data() {
    return {
      objectFields: CollectionManager.create({
        ModelClass: SObjectField,
        pagination: { size: 300 },
        filters: {
          salesforceObject: 'Opportunity',
        },
      }),
      updatedList: [],
      newCloseDate: null,
    }
  },
  watch: {
    closeDateData: 'futureDate',
  },
  props: {
    index: {},
    opp: {},
    oppFields: {},
    primaryCheckList: {},
    stageData: {},
    closeDateData: {},
    ForecastCategoryNameData: {},
    updateList: {},
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
    futureDate() {
      let currentDate = new Date()
      currentDate.setDate(currentDate.getDate() + Number(this.closeDateData))
      let currentDayOfMonth = currentDate.getDate()
      let currentMonth = currentDate.getMonth()
      let currentYear = currentDate.getFullYear()
      let dateString = currentYear + '-' + (currentMonth + 1) + '-' + currentDayOfMonth
      this.newCloseDate = dateString
      console.log(this.newCloseDate)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.table-row {
  display: table-row;
}
.empty {
  display: table-cell;
  background: white;
  min-width: 12vw;
  border-left: 1px solid $soft-gray;
  border-right: 1px solid $soft-gray;
  border-bottom: 1px solid $soft-gray;
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
.table-cell-checkbox {
  display: table-cell;
  padding: 2vh;
  width: 3.75vw;
  border: none;
  left: 0;
  position: sticky;
  z-index: 1;
  border-bottom: 1px solid $soft-gray;
  background-color: $off-white;
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
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: flex-end;
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
  height: 1.5rem;
  width: 1.5rem;
  margin-right: 0.2rem;
  padding: 0.25rem;
  border-radius: 0.25rem;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
  img {
    height: 0.8rem;
    padding: 1px;
  }
}
.name-cell-note-button-1:hover,
.name-cell-edit-note-button-1:hover {
  transform: scale(1.03);
  box-shadow: 1px 1px 1px $soft-gray;
  cursor: pointer;
}
.name-cell-edit-note-button-1 {
  height: 1.5rem;
  width: 1.5rem;
  margin-right: 0.2rem;
  padding: 0.25rem;
  border-radius: 0.25rem;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
  img {
    height: 1.2rem;
  }
}
</style>