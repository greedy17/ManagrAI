<template>
  <div
    @mouseenter="showActions"
    @mouseleave="hideActions"
    class="table-row"
    :class="{ selected: primaryCheckList.includes(opp.id) }"
  >
    <div
      :class="showIcons ? 'hovered' : ''"
      class="cell-name limit-cell-height"
      :style="
        this.resourceName === 'Contact' || this.resourceName === 'Lead' ? 'max-width: none;' : ''
      "
    >
      <div class="flex-row-spread" :class="{ selected: primaryCheckList.includes(opp.id) }">
        <div v-if="showIcons" class="flex-row" style="margin-left: 8px">
          <div>
            <button @click="emitCreateForm(opp)" class="name-cell-edit-note-button-1">
              <img style="filter: invert(40%)" height="12px" src="@/assets/images/expand.svg" />
            </button>
          </div>

          <div>
            <button @click="emitGetNotes" class="name-cell-note-button-1">
              <img style="filter: invert(40%)" height="12px" src="@/assets/images/note.svg" />
            </button>
          </div>
        </div>
        <div
          v-else
          class="flex-row-spread"
          style="min-width: 4rem; margin-left: 16px; margin-right: -12px; color: #9596b4"
        >
          <div style="padding: 0; margin: 0">
            {{ index + 1 }}
          </div>
        </div>

        <div>
          <div
            class="flex-column"
            v-if="
              updateList.includes(opp.id) ||
              updatedList.includes(opp.id) ||
              (inlineLoader && currentInlineRow === index)
            "
          >
            <SkeletonBox width="125px" height="14px" style="margin: 6px 8px" />
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
          (field.dataType === 'String' &&
            (opp['secondary_data'][field.apiName] ||
              opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))])),
        'table-cell':
          opp['secondary_data'][field.apiName] ||
          opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))],
        empty: !(
          opp['secondary_data'][field.apiName] ||
          opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
        ),
        hovered: showIcons,
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

      <div :class="showIcons ? 'hovered' : ''" v-else-if="!updateList.includes(opp.id)">
        <div class="limit-cell-height">
          <PipelineField
            :index="i"
            style="direction: ltr"
            :apiName="field.apiName"
            :dataType="field.dataType"
            :fieldData="
              userCRM === 'SALESFORCE'
                ? field.apiName.includes('__c') || field.apiName.includes('__r')
                  ? opp['secondary_data'][field.apiName]
                  : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                : opp['secondary_data'][field.apiName]
            "
            :referenceOpts="referenceOpts"
            :field="field"
            :opp="opp"
            :lastStageUpdate="opp['last_stage_update']"
            :owner="opp.owner_ref.full_name"
          />
        </div>

        <!-- v-show="!(editing && editIndex === i && currentInlineRow === index)" -->
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

      <div v-else-if="!updateList.includes(opp.id)">
        <PipelineField
          style="direction: ltr"
          :apiName="field.apiName"
          :dataType="field.dataType"
          :fieldData="
            userCRM === 'SALESFORCE'
              ? field.apiName.includes('__c')
                ? opp['secondary_data'][field.apiName]
                : opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
              : opp['secondary_data'][field.apiName]
          "
          :lastStageUpdate="opp['last_stage_update']"
          :referenceOpts="referenceOpts"
        />
      </div>
    </div>
    <div :class="showIcons ? 'hovered' : ''" class="cell-end left-border light-gray"></div>
  </div>
</template>

<script>
import PipelineField from '@/components/PipelineField'
import User from '@/services/users'

export default {
  name: 'PipelineTableRow',
  components: {
    PipelineField,
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
  },
  data() {
    return {
      showIcons: false,
      // booleans: ['true', 'false'],
      isSelected: false,
      task: false,
      checker: null,
      verboseName: null,
      currentRow: null,
      formData: {},
      dropdownVal: {},
      editing: false,
      editIndex: null,
      currentOpp: null,
      updatedList: [],
      newCloseDate: null,
    }
  },
  watch: {
    closeDateData: 'futureDate',
    closeEdit: 'closeInline',
    primaryCheckList: 'checkSelect',
    task: 'checkAndClearInterval',
  },
  props: {
    index: {},
    opp: {},
    oppFields: {},
    primaryCheckList: {},
    stageData: {},
    closeDateData: {},
    ForecastCategoryNameData: {},
    BulkUpdateName: {},
    BulkUpdateValue: {},
    updateList: {},
    picklistOpts: {},
    referenceOpts: {},
    inlineLoader: {},
    closeEdit: {},
    stages: {},
    currentInlineRow: {},
    extraPipelineFields: {},
    dropdownLoading: {},
    resourceName: {},
    baseResourceType: {},
  },
  methods: {
    showActions() {
      this.showIcons = true
    },
    hideActions() {
      this.showicons = true ? (this.showIcons = false) : (this.showIcons = true)
    },
    checkAndClearInterval() {
      if (this.task.completed == true) {
        this.stopChecker()
        this.updatedList = []
        this.$emit('updated-values')
      } else {
        return
      }
    },
    test(log) {
      console.log('log', log)
    },
    checkSelect() {
      this.primaryCheckList.includes(this.opp.id)
        ? (this.isSelected = true)
        : (this.isSelected = false)
    },
    closeInline() {
      this.editing = false
      this.$emit('close-inline-editor')
    },
    emitDropdown(val, opp) {
      const item = { val: val.value, oppId: opp.id, oppIntegrationId: opp.integration_id }
      this.$emit('set-dropdown-value', item)
    },
    editInline(index) {
      this.editing = true
      this.$emit('current-inline-row', this.index, index)
      this.currentRow = this.index
      this.editIndex = index
    },
    setUpdateValues(key, val, dataType, multi) {
      this.formData = {}
      if (multi) {
        this.formData[key] = this.formData[key] ? this.formData[key] + ';' + val : val
      }

      if (val && !multi) {
        this.formData[key] = val
      }
      setTimeout(() => {
        this.dropdownVal = {}
        this.$emit('inline-edit', this.formData, this.opp.id, this.opp.integration_id, dataType)
      }, 500)
    },
    emitCreateForm(opp) {
      this.$emit('create-form', opp)
    },
    emitGetNotes() {
      this.$emit('get-notes')
    },
    // emitCheckedBox(i) {
    //   this.$emit('checked-box', this.opp.id, i)
    // },
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
            resource_type: this.baseResourceType,
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
            resource_type: this.baseResourceType,
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
            resource_type: this.baseResourceType,
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
    async checkTask() {
      try {
        this.task = await User.api.checkTasks(this.verboseName)
      } catch (e) {
        console.log(e)
      }
    },
    stopChecker() {
      clearInterval(this.checker)
    },
    async onBulkUpdate() {
      this.updatedList.push(this.opp.id)
      try {
        const formData = {}
        formData[this.BulkUpdateName] = this.BulkUpdateValue
        const res = await SObjects.api
          .bulkUpdate({
            form_data: formData,
            resource_type: this.baseResourceType,
            form_type: 'UPDATE',
            resource_id: this.opp.id,
            integration_ids: [this.opp.integration_id],
          })
          .then((res) => {
            this.verboseName = res.verbose_name
            this.checker = setInterval(() => {
              this.checkTask()
            }, 1000)
          })
      } catch (e) {
        console.log(e)
      }
    },
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
// .light-gray {
//   background-color: $off-white !important;
// }

.img-border {
  border: none;
  box-shadow: 1px 1px 2px 1px $very-light-gray !important;
  padding: 4px 6px 3px 6px;
  border-radius: 6px;
  box-shadow: 1px 1px 6px 1px $off-white;
  background-color: white;
}

.action-buttons {
  background-color: white;
  padding: 8px 8px 8px 24px;
  border-radius: 6px;
  box-shadow: 1px 1px 2px 1px $off-white;
  display: flex;
  flex-direction: row;
  align-items: space-evenly;
  // box-shadow: 1px 1px 1px $very-light-gray;
}

.tooltip {
  position: relative;
  display: inline-block;
}

/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  opacity: 0.7;

  /* Position the tooltip text - see examples below! */
  position: absolute;
  z-index: 1;
  top: 100%;
  left: 40%;
  margin-left: -60px; /* half of width */
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
}
.tooltip .tooltiptext::after {
  content: ' ';
  position: absolute;
  bottom: 100%; /* At the top of the tooltip */
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: transparent transparent black transparent;
}
.save {
  background-color: transparent;
  color: $base-gray;
  letter-spacing: 0.75px;
  font-size: 10px;
  z-index: 2;
  // opacity: 0.5;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  p {
    span {
      background-color: $white-green;
      padding: 2px 6px;
      border-radius: 6px;
      color: $dark-green;
    }
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
  color: $base-gray !important;
  font-family: $base-font-family;
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
  // z-index: 2000;
  // position: sticky;
  // top: 10vh;
  // left: -2px;
  // min-height: 200px;
  // width: 150%;
  // background-color: white !important;
  // box-shadow: 1px 1px 2px 1px $very-light-gray;
  // padding: 8px 12px;
  // border-radius: 4px;
}
.inline-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
}
.active-edit {
  // border: 1.5px solid $dark-green !important;
  border-radius: 3px;
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
  height: 4vh;
}
.empty {
  display: table-cell;
  position: sticky;
  width: fit-content;
  border-bottom: 1px solid $soft-gray;
  padding: 0px 24px 0px 12px;
}
.selected {
  color: $dark-green !important;
}
.table-cell {
  display: table-cell;
  width: fit-content;
  white-space: nowrap;
  text-overflow: ellipsis;
  border-bottom: 1px solid $soft-gray;
  line-height: 1;
  font-size: 12px;
  padding: 0px 32px 0px 12px;
}
.cell-name {
  display: table-cell;
  white-space: nowrap;
  text-overflow: ellipsis;
  background-color: white;
  color: $base-gray;
  letter-spacing: 0.75px;
  position: sticky;
  left: 0vw;
  z-index: 2;
  padding: 0px 4px;
  line-height: 1;
  font-size: 12px;
  border-bottom: 1px solid $soft-gray;
  cursor: text !important;
}
.cell-end {
  display: table-cell;
  position: sticky;
  border: none;
  font-size: 13px;
  background-color: white;
  color: $base-gray;
  letter-spacing: 0.75px;
  border-bottom: 1px solid $soft-gray;
  border-left: 1px solid $soft-gray;
  position: sticky;
  right: 0;
  z-index: 2;
}

.table-cell-wide {
  display: table-cell;
  text-overflow: ellipsis;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
  padding-left: 4px;
  white-space: nowrap;
  padding: 0px 28px 0px 12px;
}
.table-cell-checkbox {
  display: table-cell;
  padding: 0 2vh;
  width: 3.75vw;
  border: none;
  left: 0;
  position: sticky;
  z-index: 1;
  // border-bottom: 1px solid $soft-gray;
  background-color: $white;
}

.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  // justify-content: space-between;
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
  padding-left: 4px;
  // justify-content: flex-end;
  // align-items: flex-end;
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
  width: fit-content;
  padding: 0;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.name-cell-note-button-1 {
  margin-right: 10px;
  padding: 0.25rem;
  border-radius: 4px;
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
}

.name-cell-edit-note-button-1 {
  margin-right: 6px;
  padding: 0.25rem;
  border-radius: 4px;
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
}
.hovered {
  // background-color: rgba(220, 248, 233, 0.2);
  background-color: $off-white;
}
// .mar-right {
//   margin-right: 8px;
// }
// .mar-left {
//   margin-left: 8px;
// }
</style>