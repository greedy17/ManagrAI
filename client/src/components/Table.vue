<template>
  <div class="table-section">
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
          <template v-slot:noResult>
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
    <table class="table">
      <thead>
        <tr>
          <th :class="{ highlight: nameSort === 1 || nameSort === 2 }" class="sort-img-visible">
            <span @mousedown.prevent="onMouseDown($event)" class="ui-column-resizer"></span>
            <span>#</span>
            Name
            <span @click="sortByName(sortingForward)">
              <img v-if="nameSort === 2" src="@/assets/images/arrowDrop.svg" height="16px" alt="" />
              <img
                v-else-if="nameSort === 1"
                src="@/assets/images/arrowDropUp.svg"
                height="16px"
                alt=""
              />
              <img
                id="not-sorting"
                v-else-if="nameSort === 0"
                src="@/assets/images/sort.svg"
                height="16px"
                alt=""
              />
            </span>
          </th>
          <th
            class="sort-img-visible"
            v-for="(field, i) in oppFields"
            :key="i * 7777 + 1"
            :class="{ highlight: reverseIndex === i || sortingIndex === i }"
            :title="field.referenceDisplayLabel"
          >
            <span @mousedown="onMouseDown($event)" class="ui-column-resizer"></span>
            {{ field.referenceDisplayLabel }}
            <span @click="fieldSort(field, i)">
              <img
                v-if="sortingIndex === i"
                src="@/assets/images/arrowDrop.svg"
                height="16px"
                alt=""
              />
              <img
                v-else-if="reverseIndex === i"
                src="@/assets/images/arrowDropUp.svg"
                height="16px"
                alt=""
              />
              <img
                v-if="reverseIndex !== i && sortingIndex !== i"
                id="not-sorting"
                src="@/assets/images/sort.svg"
                height="16px"
                alt=""
              />
            </span>
          </th>
          <th
            class="sort-img-visible"
            v-for="(field, i) in extraPipelineFields"
            :key="i * 333333 + 2"
            :class="{
              highlight:
                reverseIndex === oppFields.length + i || sortingIndex === oppFields.length + i,
            }"
          >
            <span class="ui-column-resizer" @mousedown="onMouseDown($event)"></span>
            {{ field.referenceDisplayLabel }}
            <span @click="viewOnlySort(field, i)">
              <img
                v-if="sortingIndex === oppFields.length + i"
                src="@/assets/images/arrowDrop.svg"
                height="16px"
                alt=""
              />
              <img
                v-else-if="reverseIndex === oppFields.length + i"
                src="@/assets/images/arrowDropUp.svg"
                height="16px"
                alt=""
              />
              <img
                v-if="
                  reverseIndex !== oppFields.length + i && sortingIndex !== oppFields.length + i
                "
                id="not-sorting"
                src="@/assets/images/sort.svg"
                height="16px"
                alt=""
              />
            </span>
          </th>
          <th v-show="userCRM === 'SALESFORCE'">
            <span @click="addField"> + </span>
          </th>
        </tr>
      </thead>
      <tbody id="tablebody">
        <tr
          @mouseenter="setIndex(j)"
          @mouseleave="currentRow = null"
          v-for="(opp, j) in allOpps"
          :key="j"
          :class="{ hovered: currentRow === j }"
        >
          <td :title="oppName(userCRM, opp)" :class="{ hovered: currentRow === j }">
            <span v-if="currentRow === j">
              <img @click="emitCreateForm(opp)" height="13px" src="@/assets/images/expand.svg" />
              <img @click="emitGetNotes(opp)" height="13px" src="@/assets/images/note.svg" />
            </span>
            <span v-else>{{ j + 1 }}</span>
            <label for="">{{ oppName(userCRM, opp) }}</label>
          </td>

          <td
            @mouseenter="editCell = i"
            @mouseleave="editCell = null"
            @click="editInline(i, j)"
            :class="{
              gray: !fieldConditions(userCRM, field, opp),
              'active-cell': editCell === i && currentRow === j,
            }"
            v-for="(field, i) in oppFields"
            :key="field.dataType + i * 4"
            :title="
              fieldData(
                field.dataType,
                userCRM,
                field,
                opp,
                opp.owner_ref ? opp.owner_ref.full_name : '',
                opp.account_ref ? opp.account_ref.name : '',
              )
            "
          >
            <span :class="{ shimmer: inlineLoader && editIndex === i && currentInlineRow === j }">
              {{
                fieldData(
                  field.dataType,
                  userCRM,
                  field,
                  opp,
                  opp.owner_ref ? opp.owner_ref.full_name : '',
                  opp.account_ref ? opp.account_ref.name : '',
                )
              }}
            </span>
            <!-- <span class="green-section" v-show="field.apiName === 'StageName'">{{
              (getDaysInStage(opp['last_stage_update']) > 19000
                ? 0
                : getDaysInStage(opp['last_stage_update'])) + ' days'
            }}</span> -->
          </td>

          <td
            class="text-cursor"
            :class="{
              gray: !fieldConditions(userCRM, field, opp),
            }"
            v-for="(field, i) in extraPipelineFields"
            :key="field.dataType + i * 3"
            :title="fieldData(field.dataType, userCRM, field, opp)"
          >
            {{ fieldData(field.dataType, userCRM, field, opp) }}
          </td>
          <td v-show="userCRM === 'SALESFORCE'" :class="{ hovered: currentRow === j }"></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { SObjects } from '@/services/salesforce'

export default {
  name: 'Table',
  data() {
    return {
      currentRow: null,
      addingField: false,
      extraFields: [],
      extraFieldObjs: [],
      editing: false,
      editIndex: null,
      sortingForward: true,
      nameSort: 0,
      sortingIndex: null,
      reverseIndex: null,
      currentInlineRow: null,
      editCell: null,
      start: null,
      pressed: null,
      startX: null,
      startWidth: null,
    }
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    allOpps: {},
    oppFields: {},
    extraPipelineFields: {},
    fieldOpts: {},
    inlineLoader: {},
    closeEdit: {},
    resourceName: {},
  },
  watch: {
    closeEdit: 'closeInline',
  },
  methods: {
    // getDaysInStage(date) {
    //   let newDate = new Date(date)
    //   return Math.floor((this.currentDay.getTime() - newDate.getTime()) / (24 * 3600 * 1000))
    // },
    setIndex(n) {
      this.currentRow = n
    },
    fieldConditions(crm, field, opp) {
      return crm === 'SALESFORCE'
        ? field.apiName.includes('__c') || field.apiName.includes('__r')
          ? opp['secondary_data'][field.apiName]
          : opp['secondary_data'][this.capitalizeFirstLetter(this.camelize(field.apiName))]
        : opp['secondary_data'][field.apiName]
    },
    oppName(crm, opp) {
      return this.resourceName === 'Opportunity' || this.resourceName === 'Account'
        ? opp['secondary_data']['Name']
        : this.resourceName === 'Company'
        ? opp['secondary_data']['name']
        : this.resourceName === 'Contact' || this.resourceName === 'Lead'
        ? crm === 'SALESFORCE'
          ? opp['secondary_data']['Email']
          : opp['secondary_data']['email']
        : opp['secondary_data']['dealname']
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
    fieldData(type, crm, field, opp, owner = null, account = null) {
      if (field.apiName === 'OwnerId' || field.apiName === 'hubspot_owner_id') {
        return owner || 'empty'
      } else if (field.apiName === 'AccountId') {
        return account || 'empty'
      } else if (field.apiName === 'dealstage') {
        return field.options[0][opp['secondary_data'].pipeline]
          ? field.options[0][opp['secondary_data'].pipeline].stages.filter(
              (stage) => stage.id === opp['secondary_data'][field.apiName],
            )[0].label
          : 'empty'
      } else if (type === 'Date') {
        return this.fieldConditions(crm, field, opp)
          ? this.formatDate(this.fieldConditions(crm, field, opp))
          : 'empty'
      } else if (type === 'DateTime') {
        return this.fieldConditions(crm, field, opp)
          ? this.formatDateTime(this.fieldConditions(crm, field, opp))
          : 'empty'
      } else if (type === 'Currency') {
        return this.fieldConditions(crm, field, opp)
          ? this.formatCash(this.fieldConditions(crm, field, opp))
          : 'empty'
      } else {
        return this.fieldConditions(crm, field, opp)
          ? this.fieldConditions(crm, field, opp)
          : 'empty'
      }
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    formatDate(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      const replace = input.replace(pattern, '$2/$3/$1')
      return this.userCRM === 'HUBSPOT' ? replace.split('T')[0] : replace
    },
    formatCash(money) {
      let cash = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
      })
      if (money) {
        return cash.format(money)
      }
      return '-'
    },
    emitCreateForm(opp) {
      this.$emit('create-form', opp, opp.id, opp.integration_id, opp.secondary_data.Pricebook2Id)
    },
    emitGetNotes(opp) {
      this.$emit('get-notes', opp)
    },
    addField() {
      this.addingField = true
    },
    closeAddField() {
      this.addingField = false
      this.extraFields = []
      this.extraFieldObjs = []
    },
    async addExtraFields() {
      for (let i = 0; i < this.extraFieldObjs.length; i++) {
        this.extraFields.push(this.extraFieldObjs[i].id)
      }
      try {
        const res = await SObjects.api.addExtraFields({
          resource_type: this.resourceName,
          field_ids: this.extraFields,
        })
        this.$toast('Field added successfully', {
          timeout: 2000,
          position: 'top-left',
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
    emitSetOpps() {
      this.$emit('set-opps')
    },
    editInline(index, j) {
      this.editing = true
      this.currentInlineRow = j
      this.$emit('current-inline-row', this.currentRow, index)
      this.editIndex = index
    },
    closeInline() {
      this.editing = false
      this.$emit('close-inline-editor')
    },
    sortByName(forward) {
      if (forward) {
        this.$emit(
          'sort-opps',
          'String',
          this.userCRM === 'SALESFORCE' ? 'Name' : 'dealname',
          this.userCRM === 'SALESFORCE' ? 'name' : 'dealname',
        )
        this.sortingForward = false
        this.nameSort = 1
        this.sortingIndex = null
        this.reverseIndex = null
      } else {
        this.$emit(
          'sort-opps-reverse',
          'String',
          this.userCRM === 'SALESFORCE' ? 'Name' : 'dealname',
          this.userCRM === 'SALESFORCE' ? 'name' : 'dealname',
        )
        this.sortingForward = true
        this.nameSort = 2
        this.sortingIndex = null
        this.reverseIndex = null
      }
    },
    fieldSort(field, i) {
      if (this.sortingIndex === null) {
        this.$emit(
          'sort-opps',
          `${field.dataType}`,
          `${field.referenceDisplayLabel}`,
          `${field.apiName}`,
        )
        this.sortingIndex = i
        this.reverseIndex = null
        this.nameSort = 0
      } else {
        this.$emit(
          'sort-opps-reverse',
          `${field.dataType}`,
          `${field.referenceDisplayLabel}`,
          `${field.apiName}`,
        )
        this.reverseIndex = i
        this.sortingIndex = null
        this.nameSort = 0
      }
    },
    viewOnlySort(field, i) {
      if (this.sortingIndex === null) {
        this.$emit(
          'sort-opps',
          `${field.dataType}`,
          `${field.referenceDisplayLabel}`,
          `${field.apiName}`,
        )
        this.sortingIndex = this.oppFields.length + i
        this.reverseIndex = null
        this.nameSort = 0
      } else {
        this.$emit(
          'sort-opps-reverse',
          `${field.dataType}`,
          `${field.referenceDisplayLabel}`,
          `${field.apiName}`,
        )
        this.reverseIndex = this.oppFields.length + i
        this.sortingIndex = null
        this.nameSort = 0
      }
    },
    onMouseDown(e) {
      this.start = e.target
      this.pressed = true
      this.startX = e.clientX
      this.startWidth = this.start.parentElement.clientWidth
    },
    resize() {
      window.addEventListener('mousemove', (event) => {
        if (this.pressed) {
          let width = this.startWidth + (event.clientX - this.startX)
          this.start.parentElement.style.minWidth = `${width}px`
          this.start.parentElement.style.maxWidth = `${width}px`
        }
      })
    },
  },
  mounted() {
    this.resize()

    window.addEventListener('mouseup', () => {
      window.removeEventListener('mousemove', this.resize())
      if (this.pressed) {
        this.pressed = false
      }
    })
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
    currentDay() {
      let date = new Date()
      return date
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.shimmer {
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2s infinite;
  background-color: $soft-gray;
  display: inline-block;
  width: 90%;
  color: $soft-gray;
  opacity: 1.75;
  border-radius: 4px;
}
.table-section {
  margin: 0;
  min-height: 50vh;
  max-height: 89.5vh;
  width: 93vw;
  overflow: scroll;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  background-color: white;
}

table {
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 100%;
}
thead {
  position: sticky;
  top: 0;
  z-index: 3;
}

thead tr th {
  position: relative;
}
th {
  background-color: $light-gray;
  text-align: left;
  max-width: 11vw;
  font-weight: 900;
  letter-spacing: 2px;
  color: rgba($color: #000000, $alpha: 0.8);
  -webkit-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
th:hover {
  background-color: $soft-gray;
  color: $darker-green;
}
td {
  max-width: 18vw;
}
th,
td {
  padding: 14px 16px 14px 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: normal;
  letter-spacing: 1.15px;
  border-bottom: 1px solid $soft-gray;
  cursor: pointer;
}
td:first-of-type {
  position: sticky;
  left: 0;
  z-index: 2;
  background-color: white;
  cursor: text;
  span {
    display: inline-block;
    width: 40px;
    color: $light-gray-blue;
    margin: 0 8px;
  }
}
th:first-of-type {
  left: 0;
  position: sticky;
  z-index: 4;
}
th > span {
  display: inline-block;
  width: 40px;
  color: $light-gray-blue;
  margin: 0 8px;
}
th:last-of-type > span {
  width: auto;
}
th:last-of-type,
td:last-of-type {
  right: 0;
  position: sticky;
  cursor: pointer;
  font-size: 16px;
}
td:last-of-type {
  background-color: white;
}
.gray {
  color: $light-gray-blue;
}
.hovered {
  background-color: $off-white !important;
}
img:first-of-type {
  margin-right: 8px;
}
img {
  filter: invert(45%);
  margin: 0;
  padding: 0;
  cursor: pointer;
}
.add-field-section {
  z-index: 5;
  position: absolute;
  right: 2vw;
  top: 9vh;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: white;
  min-width: 22vw;
  overflow: visible;
  box-shadow: 1px 1px 20px 1px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: $base-gray;
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
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    width: 100%;
    height: 40px;
    padding: 4px 0px 6px 0px;
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
.text-cursor {
  cursor: text;
}
.sort-img-visible > span > #not-sorting {
  display: none;
}
.sort-img-visible:hover > span > #not-sorting {
  display: block;
  margin-left: auto;
}
.sort-img-visible > span > img {
  position: absolute;
  top: 38%;
  right: 12px;
  margin: 0;
  padding: 0;
}

label {
  background-color: $light-gray;
  padding: 5px 6px;
  border-radius: 4px;
}
.highlight {
  background-color: $soft-gray;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
.active-cell {
}

span.ui-column-resizer {
  display: block;
  position: absolute;
  // background-color: red;
  top: 0;
  right: 0;
  margin: 0;
  width: 12px;
  height: 100%;
  padding: 0;
  cursor: col-resize;
  border: 1px solid transparent;
}

span.ui-column-resizer:hover {
  border-right: 2px solid $dark-green;
}
// .green-section {
//   background-color: $white-green;
//   color: $dark-green;
//   padding: 4px 8px 4px 4px;
//   border-radius: 4px;
// }
</style>
