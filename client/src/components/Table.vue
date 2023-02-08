<template>
  <div>
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
          <th class="sort-img-visible" @click="sortByName(sortingForward)">
            <span>#</span>
            Name
            <span>
              <img v-if="nameSort === 2" src="@/assets/images/arrowDrop.svg" height="12px" alt="" />
              <img
                v-else-if="nameSort === 1"
                src="@/assets/images/arrowDropUp.svg"
                height="12px"
                alt=""
              />
              <img v-else-if="nameSort === 0" src="@/assets/images/sort.svg" height="12px" alt="" />
            </span>
          </th>
          <th
            class="sort-img-visible"
            @click="fieldSort(field, i)"
            v-for="(field, i) in oppFields"
            :key="i * 7777 + 1"
            :title="field.referenceDisplayLabel"
          >
            {{ field.referenceDisplayLabel }}
            <span>
              <img
                v-if="sortingIndex === i"
                src="@/assets/images/arrowDrop.svg"
                height="12px"
                alt=""
              />
              <img
                v-else-if="reverseIndex === i"
                src="@/assets/images/arrowDropUp.svg"
                height="12px"
                alt=""
              />
              <img
                v-if="reverseIndex !== i && sortingIndex !== i"
                src="@/assets/images/sort.svg"
                height="12px"
                alt=""
              />
            </span>
          </th>
          <th
            class="sort-img-visible"
            @click="viewOnlySort(field, i)"
            v-for="(field, i) in extraPipelineFields"
            :key="i * 333333 + 2"
            :title="field.referenceDisplayLabel"
          >
            {{ field.referenceDisplayLabel }}
            <span>
              <img
                v-if="sortingIndex === oppFields.length + i"
                src="@/assets/images/arrowDrop.svg"
                height="12px"
                alt=""
              />
              <img
                v-else-if="reverseIndex === oppFields.length + i"
                src="@/assets/images/arrowDropUp.svg"
                height="12px"
                alt=""
              />
              <img
                v-if="
                  reverseIndex !== oppFields.length + i && sortingIndex !== oppFields.length + i
                "
                src="@/assets/images/sort.svg"
                height="12px"
                alt=""
              />
            </span>
          </th>
          <th>
            <span @click="addField"> + </span>
          </th>
        </tr>
      </thead>
      <tbody>
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
            :title="fieldData(field.dataType, userCRM, field, opp)"
            @click="editInline(i)"
            :class="{
              gray: !fieldConditions(userCRM, field, opp),
              'edit-active': editing && editIndex === i && currentRow === j,
            }"
            v-for="(field, i) in oppFields"
            :key="field.dataType + i * 4"
          >
            {{ fieldData(field.dataType, userCRM, field, opp) }}
          </td>

          <td
            :title="fieldData(field.dataType, userCRM, field, opp)"
            class="text-cursor"
            :class="{
              gray: !fieldConditions(userCRM, field, opp),
            }"
            v-for="(field, i) in extraPipelineFields"
            :key="field.dataType + i * 3"
          >
            {{ fieldData(field.dataType, userCRM, field, opp) }}
          </td>
          <td></td>
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
  },
  watch: {
    closeEdit: 'closeInline',
  },
  methods: {
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
      return crm === 'SALESFORCE'
        ? opp['secondary_data']['Name']
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
    fieldData(type, crm, field, opp) {
      if (type === 'Date') {
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
      console.log('here', this.addingField)
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
    emitSetOpps() {
      this.$emit('set-opps')
    },
    editInline(index) {
      this.editing = true
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
  },
  mounted() {},
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

table {
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 13px;
}
thead {
  position: sticky;
  top: 0;
  z-index: 3;
}
th {
  background-color: $light-gray;
  text-align: left;
  max-width: 11vw;
  //   color: $light-gray-blue;
}
td {
  max-width: 18vw;
}
th,
td {
  padding: 13px 16px 13px 8px;
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
  //   background-color: white;
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
.sort-img-visible > span > img {
  display: none;
}
.sort-img-visible:hover > span > img {
  display: block;
}
label {
  background-color: $light-gray;
  padding: 4px 8px 4px 6px;
  border-radius: 4px;
}

[title]:hover:after {
  opacity: 1;
  transition: all 0.1s ease 0.5s;
  visibility: visible;
}
</style>