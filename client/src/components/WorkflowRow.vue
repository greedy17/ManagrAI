<template>
  <div class="table-row">
    <div style="padding: 2vh" class="table-cell-checkbox">
      <div
        v-if="updateWorkflowList.includes(workflow.id) || updatedWorkflowList.includes(workflow.id)"
      >
        <SkeletonBox width="10px" height="9px" />
      </div>
      <div v-else>
        <input
          type="checkbox"
          :id="index"
          v-model="workflowCheckList"
          :value="workflow.id"
          @click="emitCheckedBox"
        />
        <label :for="index"></label>
      </div>
    </div>

    <div style="min-width: 26vw" class="table-cell cell-name">
      <div class="flex-row-spread">
        <div>
          <div
            class="flex-column"
            v-if="
              updateWorkflowList.includes(workflow.id) || updatedWorkflowList.includes(workflow.id)
            "
          >
            <SkeletonBox width="125px" height="14px" style="margin-bottom: 0.2rem" />
            <SkeletonBox width="125px" height="9px" />
          </div>

          <PipelineNameSection
            v-else
            :name="workflow['secondary_data']['Name']"
            :accountName="workflow.account_ref ? workflow.account_ref.name : ''"
            :owner="workflow.owner_ref.first_name"
          />
        </div>
        <div
          v-if="
            updateWorkflowList.includes(workflow.id) || updatedWorkflowList.includes(workflow.id)
          "
          class="flex-row"
        >
          <SkeletonBox width="15px" height="14px" />
          <SkeletonBox width="15px" height="14px" />
        </div>

        <div v-else class="flex-row">
          <button @click="emitCreateForm" class="name-cell-edit-note-button-2">
            <img style="filter: invert(90%); height: 0.6rem" src="@/assets/images/edit.png" />
          </button>
          <button @click="emitGetNotes" class="name-cell-note-button-2">
            <img class="gray" src="@/assets/images/white-note.png" />
          </button>
        </div>
      </div>
    </div>

    <div
      @click="editInline(i)"
      :key="i"
      v-for="(field, i) in oppFields"
      :class="{
        'active-edit': editing && editIndex === i && currentRow === index,
        'table-cell-wide':
          field.dataType === 'TextArea' ||
          (field.length > 250 &&
            field.dataType === 'String' &&
            (workflow['secondary_data'][field.apiName] ||
              workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))])),
        'table-cell':
          workflow['secondary_data'][field.apiName] ||
          workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))],
        empty: !(
          workflow['secondary_data'][field.apiName] ||
          workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
        ),
      }"
    >
      <SkeletonBox
        v-if="updateWorkflowList.includes(workflow.id) || updatedWorkflowList.includes(workflow.id)"
        width="125px"
        height="14px"
        style="margin-bottom: 0.2rem"
      />

      <div class="limit-cell-height" v-else>
        <div class="inline-edit" v-show="editing && editIndex === i && currentRow === index">
          <div
            v-if="
              field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
            "
            class="inline-row"
          >
            <textarea
              @input="executeUpdateValues(field.apiName, $event.target.value)"
              id="user-input-wide"
              :value="
                field.apiName.includes('__c')
                  ? workflow['secondary_data'][field.apiName]
                  : workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            >
            </textarea>

            <div v-if="inlineLoader">
              <PipelineLoader />
            </div>
          </div>
          <div
            v-else-if="
              (field.dataType === 'String' && field.apiName !== 'meeting_type') ||
              (field.dataType === 'String' && field.apiName !== 'meeting_comments') ||
              (field.dataType === 'String' && field.apiName !== 'NextStep') ||
              (field.dataType === 'Email' && field.apiName !== 'NextStep')
            "
            class="inline-row"
          >
            <input
              @input="executeUpdateValues(field.apiName, $event.target.value)"
              id="user-input"
              type="text"
              :value="
                field.apiName.includes('__c')
                  ? workflow['secondary_data'][field.apiName]
                  : workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />
            <div v-if="inlineLoader">
              <PipelineLoader />
            </div>
          </div>

          <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
            <div v-if="inlineLoader">
              <PipelineLoader />
            </div>
            <Multiselect
              v-else-if="field.apiName !== 'StageName'"
              :options="picklistOpts[field.apiName]"
              openDirection="below"
              selectLabel="Enter"
              style="width: 14vw; padding-bottom: 8rem"
              track-by="value"
              label="label"
              v-model="dropdownValue"
              @select="
                setUpdateValues(
                  field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                  $event.value,
                  field.dataType,
                )
              "
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>

              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.png" alt="" />
                  {{ `${field.referenceDisplayLabel}` }}
                </p>
              </template>
            </Multiselect>
            <Multiselect
              v-else-if="field.apiName === 'StageName'"
              :options="picklistOpts[field.apiName]"
              openDirection="below"
              selectLabel="Enter"
              style="width: 14vw; padding-bottom: 8rem"
              track-by="value"
              label="label"
              v-model="dropdownValue"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>

              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.png" alt="" />
                  {{ `${field.referenceDisplayLabel}` }}
                </p>
              </template>
            </Multiselect>
          </div>
          <div v-else-if="field.dataType === 'Date'">
            <div v-if="inlineLoader">
              <PipelineLoader />
            </div>
            <input
              v-else
              @input="setUpdateValues(field.apiName, $event.target.value)"
              type="date"
              id="user-input"
              :value="
                field.apiName.includes('__c')
                  ? workflow['secondary_data'][field.apiName]
                  : workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />
          </div>
          <div v-else-if="field.dataType === 'DateTime'">
            <div v-if="inlineLoader">
              <PipelineLoader />
            </div>
            <input
              v-else
              type="datetime-local"
              id="user-input"
              @input="setUpdateValues(field.apiName, $event.target.value)"
              :value="
                field.apiName.includes('__c')
                  ? workflow['secondary_data'][field.apiName]
                  : workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />
          </div>
          <div
            v-else-if="
              field.dataType === 'Phone' ||
              field.dataType === 'Double' ||
              field.dataType === 'Currency'
            "
            class="inline-row"
          >
            <input
              @input="executeUpdateValues(field.apiName, $event.target.value)"
              id="user-input"
              type="number"
              :value="
                field.apiName.includes('__c')
                  ? workflow['secondary_data'][field.apiName]
                  : workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />
            <div v-if="inlineLoader">
              <PipelineLoader />
            </div>
          </div>
        </div>
        <PipelineField
          style="direction: ltr"
          v-show="!editing || editIndex !== i"
          :apiName="field.apiName"
          :dataType="field.dataType"
          :fieldData="
            field.apiName.includes('__c') || field.apiName.includes('__r')
              ? workflow['secondary_data'][field.apiName]
              : workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
          "
          :lastStageUpdate="workflow['last_stage_update']"
        />
      </div>
    </div>
    <div
      :key="field.id"
      v-for="field in extraPipelineFields"
      :class="
        workflow['secondary_data'][field.apiName] ||
        workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
          ? 'table-cell'
          : 'empty'
      "
    >
      <SkeletonBox
        v-if="updateWorkflowList.includes(workflow.id) || updatedWorkflowList.includes(workflow.id)"
        width="100px"
        height="14px"
      />

      <div class="limit-cell-height" v-else-if="!updateWorkflowList.includes(workflow.id)">
        <PipelineField
          style="direction: ltr"
          :apiName="field.apiName"
          :dataType="field.dataType"
          :fieldData="
            field.apiName.includes('__c')
              ? workflow['secondary_data'][field.apiName]
              : workflow['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
          "
          :lastStageUpdate="workflow['last_stage_update']"
        />
      </div>
    </div>
  </div>
</template>

<script>
import PipelineNameSection from '@/components/PipelineNameSection'
import PipelineField from '@/components/PipelineField'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjects, SObjectField } from '@/services/salesforce'
import debounce from 'lodash.debounce'

export default {
  name: 'WorkflowRow',
  components: {
    PipelineNameSection,
    PipelineField,
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
  },
  data() {
    return {
      currentRow: null,
      formData: {},
      dropdownValue: null,
      executeUpdateValues: debounce(this.setUpdateValues, 800),
      editing: false,
      editIndex: null,
      currentOpp: null,
      updatedWorkflowList: [],
      newCloseDate: null,
      objectFields: CollectionManager.create({
        ModelClass: SObjectField,
        pagination: { size: 300 },
        filters: {
          salesforceObject: 'Opportunity',
        },
      }),
    }
  },
  props: {
    index: {},
    oppFields: {},
    workflowCheckList: {},
    workflow: {},
    updateWorkflowList: {},
    stageData: {},
    closeDateData: {},
    ForecastCategoryNameData: {},

    picklistOpts: {},
    inlineLoader: {},
    closeEdit: {},
    stages: {},
  },
  watch: {
    closeDateData: 'futureDate',
    closeEdit: 'closeInline',
    dropdownValue: {
      handler(val) {
        if (this.stages.includes(val.value)) {
          this.$emit('open-stage-form', val.value, this.workflow.id)
        } else {
          this.setUpdateValues('StageName', val.value)
        }
      },
    },
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
    closeInline() {
      this.editing = false
    },
    editInline(index) {
      this.currentRow = this.index
      this.editIndex = index
      this.editing = true
    },
    setUpdateValues(key, val, dataType) {
      if (val) {
        this.formData[key] = val
      }
      setTimeout(() => {
        this.$emit('inline-edit', this.formData, this.workflow.id, dataType)
      }, 200)
    },
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
    },
    async onAdvanceStage() {
      if (this.workflowCheckList.includes(this.workflow.id)) {
        this.updatedWorkflowList.push(this.workflow.id)
        try {
          const res = await SObjects.api
            .createFormInstance({
              resourceType: 'Opportunity',
              formType: 'UPDATE',
              resourceId: this.workflow.id,
            })
            .then(async (res) => {
              await SObjects.api.updateResource({
                form_id: [res.form_id],
                form_data: { StageName: this.stageData },
              })
            })
        } catch (e) {
          console.log(e)
        } finally {
          this.updatedWorkflowList = []
          this.$Alert.alert({
            type: 'success',
            timeout: 750,
            message: 'Salesforce update successful!',
          })
        }
      }
    },
    async onPushCloseDate() {
      if (this.workflowCheckList.includes(this.workflow.id)) {
        this.updatedWorkflowList.push(this.workflow.id)
        try {
          const res = await SObjects.api
            .createFormInstance({
              resourceType: 'Opportunity',
              formType: 'UPDATE',
              resourceId: this.workflow.id,
            })
            .then(async (res) => {
              await SObjects.api.updateResource({
                form_id: [res.form_id],
                form_data: { CloseDate: this.newCloseDate },
              })
            })
        } catch (e) {
          console.log(e)
        } finally {
          this.updatedWorkflowList = []
          this.$Alert.alert({
            type: 'success',
            timeout: 750,
            message: 'Salesforce update successful!',
          })
        }
      }
    },
    async onChangeForecast() {
      if (this.workflowCheckList.includes(this.workflow.id)) {
        this.updatedWorkflowList.push(this.workflow.id)
        try {
          const res = await SObjects.api
            .createFormInstance({
              resourceType: 'Opportunity',
              formType: 'UPDATE',
              resourceId: this.workflow.id,
            })
            .then(async (res) => {
              await SObjects.api.updateResource({
                form_id: [res.form_id],
                form_data: { ForecastCategoryName: this.ForecastCategoryNameData },
              })
            })
        } catch (e) {
          console.log(e)
        } finally {
          this.updatedWorkflowList = []
          this.$Alert.alert({
            type: 'success',
            timeout: 750,
            message: 'Salesforce update successful!',
          })
        }
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2rem;
  width: 12vw;
}
#user-input-wide {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2rem;
  width: 20vw;
  font-family: $base-font-family;
  margin: 1.5rem 1rem;
  padding: 7px;
}
#user-input:focus,
#user-input-wide:focus {
  outline: none;
}
input[type='text']:focus {
  outline: none;
  cursor: text;
}
textarea {
  resize: none;
  position: absolute;
  margin-top: -1rem;
}
input[type='date'] {
  background-color: $soft-gray !important;
  color: $base-gray !important;
}
input[type='date']::-webkit-calendar-picker-indicator {
  background-color: white;
  border-radius: 3px;
  padding: 5px;
}
input[type='date']::-webkit-datetime-edit-text,
input[type='date']::-webkit-datetime-edit-month-field,
input[type='date']::-webkit-datetime-edit-day-field,
input[type='date']::-webkit-datetime-edit-year-field {
  // color: #888;
  cursor: pointer;
  padding: 0.25rem;
}
input {
  padding: 7px;
}
.inline-edit {
  cursor: text;
}
.inline-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.active-edit {
  border-bottom: 2px solid $dark-green !important;
  border-left: 1px solid $soft-gray !important;
  border-right: 1px solid $soft-gray !important;
  border-top: 1px solid $soft-gray !important;
  background-color: white !important;
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem !important;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.table-row {
  display: table-row;
}
.empty {
  display: table-cell;
  background: white !important;
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
.table-cell:hover,
.empty:hover {
  border: 1px solid $dark-green;
}
.cell-name:hover {
  border: none;
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
  max-height: 8rem;
  // width: 110%;
  padding: 0;
  overflow: auto;
  img {
    height: 0.25rem;
  }
  // cursor: url('../assets/images/edit-cursor.svg'), auto;
  cursor: pointer;
}
.name-cell-note-button-2 {
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
.name-cell-note-button-2:hover,
.name-cell-edit-note-button-2:hover {
  transform: scale(1.03);
  box-shadow: 1px 1px 1px $soft-gray;
  cursor: pointer;
}
.name-cell-edit-note-button-2 {
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