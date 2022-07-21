<template>
  <div class="table-row" :class="{ selected: primaryCheckList.includes(opp.id) }">
    <div v-if="opp" class="table-cell-checkbox">
      <div
        v-if="
          updateList.includes(opp.id) ||
          updatedList.includes(opp.id) ||
          (inlineLoader && currentInlineRow === index)
        "
      >
        <SkeletonBox width="10px" height="9px" />
      </div>
      <div v-else>
        <input
          @click="emitCheckedBox(index)"
          type="checkbox"
          :id="index"
          v-model="primaryCheckList"
          :value="opp.id"
        />
        <label :for="index"></label>
      </div>
    </div>

    <div style="min-width: 26vw" class="table-cell cell-name">
      <div class="flex-row-spread" :class="{ selected: primaryCheckList.includes(opp.id) }">
        <div>
          <div
            class="flex-column"
            v-if="
              updateList.includes(opp.id) ||
              updatedList.includes(opp.id) ||
              (inlineLoader && currentInlineRow === index)
            "
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
        <div
          v-if="
            updateList.includes(opp.id) ||
            updatedList.includes(opp.id) ||
            (inlineLoader && currentInlineRow === index)
          "
          class="flex-row"
        >
          <SkeletonBox width="15px" height="14px" />
          <SkeletonBox width="15px" height="14px" />
        </div>
        <div v-else class="flex-row">
          <div class="tooltip">
            <button @click="emitCreateForm" class="name-cell-edit-note-button-1">
              <img style="filter: invert(10%); height: 0.6rem" src="@/assets/images/edit.svg" />
            </button>
            <span class="tooltiptext">Update</span>
          </div>

          <div class="tooltip">
            <button @click="emitGetNotes" class="name-cell-note-button-1">
              <img class="gray" src="@/assets/images/white-note.svg" />
            </button>
            <span class="tooltiptext">View Notes</span>
          </div>
        </div>
      </div>
    </div>
    <div
      @click="editInline(i)"
      :key="i"
      v-for="(field, i) in oppFields"
      :class="{
        'active-edit': editing && editIndex === i && currentInlineRow === index,
        'table-cell-wide':
          field.dataType === 'TextArea' ||
          (field.length > 250 &&
            field.dataType === 'String' &&
            (opp['secondary_data'][field.apiName] ||
              opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))])),
        'table-cell':
          opp['secondary_data'][field.apiName] ||
          opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))],
        empty: !(
          opp['secondary_data'][field.apiName] ||
          opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
        ),
      }"
    >
      <SkeletonBox
        v-if="
          updateList.includes(opp.id) ||
          updatedList.includes(opp.id) ||
          (inlineLoader && currentInlineRow === index)
        "
        width="100px"
        height="14px"
      />

      <div class="limit-cell-height" v-else-if="!updateList.includes(opp.id)">
        <div class="inline-edit" v-if="editing && editIndex === i && currentInlineRow === index">
          <div
            v-if="
              field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
            "
            class="inline-row"
          >
            <input
              v-on:keyup.enter="setUpdateValues(field.apiName, $event.target.value, field.dataType)"
              id="user-input-wide"
              :value="
                field.apiName.includes('__c')
                  ? opp['secondary_data'][field.apiName]
                  : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />

            <div v-if="editing" class="save">
              <p>Press "Enter" to save</p>
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
              v-on:keyup.enter="setUpdateValues(field.apiName, $event.target.value, field.dataType)"
              id="user-input"
              type="text"
              :value="
                field.apiName.includes('__c')
                  ? opp['secondary_data'][field.apiName]
                  : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />
            <div v-if="editing" class="save">
              <p>Press "Enter" to save</p>
            </div>
          </div>

          <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
            <Multiselect
              v-if="field.apiName !== 'StageName'"
              :options="picklistOpts[field.id]"
              openDirection="below"
              selectLabel="Enter"
              style="width: 14vw; padding-bottom: 8rem; margin-left: 1vw"
              track-by="value"
              label="label"
              v-model="dropdownVal[field.apiName]"
              :multiple="field.dataType === 'MultiPicklist' ? true : false"
              @select="
                setUpdateValues(
                  field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                  $event.value,
                  field.dataType,
                  field.dataType === 'MultiPicklist' ? true : false,
                )
              "
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>

              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  {{
                    (
                      field.apiName.includes('__c')
                        ? opp['secondary_data'][field.apiName]
                        : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                    )
                      ? field.apiName.includes('__c')
                        ? opp['secondary_data'][field.apiName]
                        : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                      : field.referenceDisplayLabel
                  }}
                </p>
              </template>
            </Multiselect>
            <Multiselect
              v-else-if="field.apiName === 'StageName'"
              :options="picklistOpts[field.id]"
              openDirection="below"
              selectLabel="Enter"
              style="width: 14vw; padding-bottom: 8rem"
              track-by="value"
              label="label"
              @select="setDropdownValue($event)"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>

              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  {{ opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))] }}
                </p>
              </template>
            </Multiselect>
          </div>
          <div class="inline-row" v-else-if="field.dataType === 'Date'">
            <input
              v-on:keyup.enter="setUpdateValues(field.apiName, $event.target.value, field.dataType)"
              type="date"
              id="user-input"
              :value="
                field.apiName.includes('__c')
                  ? opp['secondary_data'][field.apiName]
                  : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />
            <div v-if="editing" class="save">
              <p>Press "Enter" to save</p>
            </div>
          </div>
          <div v-else-if="field.dataType === 'DateTime'">
            <input
              type="datetime-local"
              id="user-input"
              v-on:keyup.enter="setUpdateValues(field.apiName, $event.target.value, field.dataType)"
              :value="
                field.apiName.includes('__c')
                  ? opp['secondary_data'][field.apiName]
                  : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />
            <div v-if="editing" class="save">
              <p>Press "Enter" to save</p>
            </div>
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
              v-on:keyup.enter="setUpdateValues(field.apiName, $event.target.value, field.dataType)"
              id="user-input"
              type="number"
              :value="
                field.apiName.includes('__c')
                  ? opp['secondary_data'][field.apiName]
                  : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              "
            />
            <div v-if="editing" class="save">
              <p>Press "Enter" to save</p>
            </div>
          </div>
          <div v-else-if="field.dataType === 'Boolean'">
            <Multiselect
              v-model="dropdownVal[field.apiName]"
              :options="booleans"
              @select="setUpdateValues(field.apiName, $event)"
              openDirection="below"
              style="width: 14vw; padding-bottom: 8rem"
              selectLabel="Enter"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  {{ opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))] }}
                </p>
              </template>
            </Multiselect>
          </div>
        </div>
        <PipelineField
          :index="i"
          v-show="!(editing && editIndex === i && currentInlineRow === index)"
          style="direction: ltr; border: "
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
        v-if="
          updateList.includes(opp.id) ||
          updatedList.includes(opp.id) ||
          (inlineLoader && currentInlineRow === index)
        "
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
import { SObjects } from '@/services/salesforce'
import debounce from 'lodash.debounce'

export default {
  name: 'PipelineTableRow',
  components: {
    PipelineNameSection,
    PipelineField,
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
  },
  data() {
    return {
      booleans: ['true', 'false'],
      isSelected: false,
      currentRow: null,
      formData: {},
      dropdownValue: {},
      dropdownVal: {},
      executeUpdateValues: debounce(this.setUpdateValues, 2000),
      editing: false,
      editIndex: null,
      currentOpp: null,
      // objectFields: CollectionManager.create({
      //   ModelClass: SObjectField,
      //   pagination: { size: 300 },
      //   filters: {
      //     salesforceObject: 'Opportunity',
      //   },
      // }),
      updatedList: [],
      newCloseDate: null,
    }
  },
  watch: {
    closeDateData: 'futureDate',
    closeEdit: 'closeInline',
    primaryCheckList: 'checkSelect',
    dropdownValue: {
      handler(val) {
        if (this.stages.includes(val)) {
          this.$emit('open-stage-form', val, this.opp.id, this.opp.integration_id)
        } else {
          this.setUpdateValues('StageName', val)
        }
      },
    },
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
    picklistOpts: {},
    inlineLoader: {},
    closeEdit: {},
    stages: {},
    currentInlineRow: {},
    extraPipelineFields: {},
  },
  methods: {
    // async setForm() {
    //   try {
    //     const res = await SObjects.api.createFormInstance({
    //       resourceType: 'Opportunity',
    //       formType: 'UPDATE',
    //       resourceId: this.opp.id,
    //     })
    //     this.formId = res.form_id
    //   } catch (e) {
    //     console.log(e)
    //   }
    // },
    checkSelect() {
      this.primaryCheckList.includes(this.opp.id)
        ? (this.isSelected = true)
        : (this.isSelected = false)
    },
    closeInline() {
      this.editing = false
    },
    setDropdownValue(val) {
      this.dropdownValue = val.value
    },
    editInline(index) {
      this.editing = true
      this.$emit('current-inline-row', this.index)
      this.currentRow = this.index
      this.editIndex = index
    },
    setUpdateValues(key, val, dataType, multi) {
      if (multi) {
        this.formData[key] = this.formData[key] ? this.formData[key] + ';' + val : val
      }

      if (val && !multi) {
        this.formData[key] = val
      }
      setTimeout(() => {
        this.$emit('inline-edit', this.formData, this.opp.id, this.opp.integration_id, dataType)
      }, 500)
    },
    emitCreateForm() {
      this.$emit('create-form')
    },
    emitGetNotes() {
      this.$emit('get-notes')
    },
    emitCheckedBox(i) {
      this.$emit('checked-box', this.opp.id, i)
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
      this.updatedList.push(this.opp.id)
      try {
        const res = await SObjects.api
        SObjects.api
          .updateResource({
            form_data: { StageName: this.stageData },
            resource_type: 'Opportunity',
            form_type: 'UPDATE',
            resource_id: this.opp.id,
            integration_ids: [this.opp.integration_id],
          })
          .then(
            this.$toast('Salesforce Update Successful', {
              timeout: 1000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            }),
          )
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.updatedList = []
        }, 1000)
      }
    },
    async onPushCloseDate() {
      this.updatedList.push(this.opp.id)
      try {
        const res = await SObjects.api
          .updateResource({
            form_data: { CloseDate: this.newCloseDate },
            resource_type: 'Opportunity',
            form_type: 'UPDATE',
            resource_id: this.opp.id,
            integration_ids: [this.opp.integration_id],
          })
          .then(
            this.$toast('Salesforce Update Successful', {
              timeout: 1000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            }),
          )
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.updatedList = []
        }, 1000)
      }
    },
    async onChangeForecast() {
      this.updatedList.push(this.opp.id)
      try {
        const res = await SObjects.api
          .updateResource({
            form_data: { ForecastCategoryName: this.ForecastCategoryNameData },
            resource_type: 'Opportunity',
            form_type: 'UPDATE',
            resource_id: this.opp.id,
            integration_ids: [this.opp.integration_id],
          })
          .then(
            this.$toast('Salesforce Update Successful', {
              timeout: 1000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            }),
          )
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.updatedList = []
        }, 2000)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

@keyframes tooltips-horz {
  to {
    opacity: 0.95;
    transform: translate(0%, 50%);
  }
}

.tooltip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2px 0px;
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 12px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 100px;
  top: 100%;
  left: 50%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
.save {
  background-color: transparent;
  color: $dark-green;
  letter-spacing: 0.75px;
  font-weight: bold;
  font-size: 10px;
  z-index: 2;
  // opacity: 0.5;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  p {
    background-color: $white-green;
    padding: 2px 6px;
    border-radius: 6px;
  }
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2rem;
  padding: 7px;
  width: 12vw;
}
#user-input-wide {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2rem;
  width: 20vw;
  font-family: $base-font-family;
  // margin: 1.5rem 1rem;
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.active-edit {
  border-bottom: 2px solid $dark-green !important;
  border-left: 1px solid $soft-gray !important;
  border-right: 1px solid $soft-gray !important;
  border-top: 1px solid $soft-gray !important;
  background-color: white !important;
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
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
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
  position: sticky;
  background: $off-white;
  min-width: 12vw;
  border-left: 1px solid $soft-gray;
  border-right: 1px solid $soft-gray;
  border-bottom: 1px solid $soft-gray;
}
.selected {
  color: $dark-green !important;
}
.table-cell {
  display: table-cell;
  position: sticky;
  min-width: 16vw;
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
  background-color: white;
  border-radius: 4px;
}
.cell-name:hover {
  border: none;
  border-bottom: 1px solid #e8e8e8;
}
.table-cell-wide {
  display: table-cell;
  position: sticky;
  min-width: 26vw;
  background-color: $off-white;
  padding: 2vh 3.5vh;
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
  background-color: $white;
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
  background-color: $white;
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
  background-color: $white;
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
.name-cell-note-button-1 {
  height: 1.5rem;
  width: 1.5rem;
  margin-right: 0.2rem;
  padding: 0.25rem;
  border-radius: 4px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0.7px solid $gray;
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
  border-radius: 4px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0.7px solid $gray;
  img {
    height: 1.2rem;
  }
}
</style>