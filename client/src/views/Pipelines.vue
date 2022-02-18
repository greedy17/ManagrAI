<template>
  <div class="pipelines">
    <Modal
      v-if="modalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetNotes()
        }
      "
    >
      <div v-if="notes.length" class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 2rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Notes</h2>
          </div>
          <img
            src="@/assets/images/clear.png"
            style="height: 1.3rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetNotes"
            class="invert"
            alt=""
          />
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{
              note.saved_data__meeting_type
                ? 'Notes for ' + note.saved_data__meeting_type
                : 'Untitled note'
            }}
          </p>
          <p class="note-section__body">{{ note.saved_data__meeting_comments }}</p>
        </section>
      </div>

      <div v-else class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 2rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Notes</h2>
          </div>
          <img
            src="@/assets/images/clear.png"
            style="height: 1.3rem; margin-right: 0.75rem; cursor: pointer"
            @click="resetNotes"
            class="invert"
            alt=""
          />
        </div>
        <section class="note-section">
          <p class="note-section__title">No notes for this opportunity</p>
        </section>
      </div>
    </Modal>
    <div v-if="!loading">
      <header class="flex-row-spread">
        <!-- <div @click="test">
          <h3 class="title">Hi, {{ user.fullName }}</h3>
          <h5 class="sub-heading">
            Update you pipeline faster. Changes instantly auto sync to Salesforce
          </h5>
        </div>
        <div>
        </div> -->
      </header>

      <section class="flex-row-spread">
        <div v-if="noSelection" class="flex-row">
          <button @click="showList = !showList" class="pipe-button">
            <!-- <img
              src="@/assets/images/list.png"
              style="height: 1rem; margin-right: 0.3rem"
              alt=""
            /> -->
            {{ currentList }}
            <img
              v-if="showPopularList"
              class="invert filter"
              style="height: 0.75rem"
              src="@/assets/images/downArrow.png"
              alt=""
            />
          </button>
          <div v-show="showList" class="list-section">
            <p @click="showPopularList = !showPopularList" class="list-section__title">
              Popular Lists
              <img v-if="showPopularList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <button v-if="showPopularList" @click="allOpportunities" class="list-button">
              All Opportunities
              <span class="filter" v-if="currentList === 'All Opportunities'"> active</span>
            </button>
            <button v-if="showPopularList" @click="closeDatesThisMonth" class="list-button">
              Closing this month
              <span class="filter" v-if="currentList === 'Closing this month'"> active</span>
            </button>
            <button v-if="showPopularList" @click="closeDatesNextMonth" class="list-button">
              Closing next month
              <span class="filter" v-if="currentList === 'Closing next month'"> active</span>
            </button>
            <p @click="showWorkflowList = !showWorkflowList" class="list-section__title">
              Workflows
              <img v-if="showWorkflowList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <div v-if="showWorkflowList">
              <button
                :key="i"
                v-for="(template, i) in templates.list"
                @click="selectList(template.configs[0], template.title, template.id)"
                class="list-button"
              >
                {{ template.title }}
                <span class="filter" v-if="currentList === template.title"> active</span>
              </button>
            </div>
          </div>
          <button @click="filtering = !filtering" class="add-button">
            <img
              src="@/assets/images/plusOne.png"
              style="height: 1rem; margin-right: 0.25rem"
              alt=""
            />Filter
          </button>
          <h5>
            Results:
            <span>{{ selectedWorkflow ? currentWorkflow.list.length : allOpps.length }}</span>
          </h5>

          <div v-if="filtering" class="filter-section">
            <div class="flex-row-spread wide">
              <p class="filter-section__title">All Filters</p>
              <img @click="closeFilters" class="exit" src="@/assets/images/close.png" alt="" />
            </div>
            <div class="wide" style="display: flex; justify-content: center">
              <div style="margin-left: 0.5rem" class="search-bar wide">
                <input
                  class="wide"
                  type="search"
                  v-model="searchFilterText"
                  placeholder="Search filters"
                />
                <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
              </div>
            </div>

            <small v-if="filterTitle" class="filter-title"
              >{{ filterTitle + ' ' + (filterOption ? filterOption : '') }}:</small
            >
            <div v-if="filterType && !enteringAmount" class="filter-option-section">
              <button
                @click="selectFilterOption(option)"
                class="filter-option-button"
                :key="option"
                v-for="option in monetaryOptions"
              >
                {{ option }}
              </button>
            </div>
            <div v-if="filterType && enteringAmount" class="filter-option-section">
              <input class="search-bar" v-model="amountValue" type="text" />
              <button
                @click="applyAmountFilter"
                :disabled="!amountValue"
                :class="!amountValue ? 'disabled-button' : 'add-button'"
              >
                add
              </button>
            </div>

            <div :key="i" v-for="(filter, i) in filteredFilters" class="filter-section__filters">
              <button
                @click="selectFilter(filter.type, filter.title)"
                style="margin-top: -0.5rem"
                class="list-button"
              >
                <img
                  v-if="filter.type === 'monetary'"
                  src="@/assets/images/monetary.png"
                  class="img"
                  alt=""
                />
                <img
                  v-if="filter.type === 'date'"
                  src="@/assets/images/date.png"
                  class="img"
                  alt=""
                />
                <img
                  v-if="filter.type === 'time'"
                  src="@/assets/images/time.png"
                  class="img"
                  alt=""
                />
                <img
                  v-if="filter.type === 'person'"
                  src="@/assets/images/person.png"
                  class="img"
                  alt=""
                />
                {{ filter.title }}
              </button>
            </div>
          </div>
        </div>

        <div class="flex-row">
          <div v-if="!selectedWorkflow" class="search-bar">
            <input type="search" v-model="filterText" placeholder="search" />
            <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
          </div>
          <div v-else class="search-bar">
            <input type="search" v-model="workflowFilterText" placeholder="search" />
            <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
          </div>
          <button class="add-button">
            <img src="@/assets/images/plusOne.png" style="height: 1rem" alt="" />
            Opportunity
          </button>
          <button @click="refresh(refreshId)" class="pipe-button">
            <img src="@/assets/images/refresh.png" class="invert" style="height: 1rem" alt="" />
          </button>
        </div>
      </section>

      <section v-if="!selectedWorkflow" class="table-section">
        <div class="table">
          <div class="table-row">
            <div class="table-cell-checkbox-header">
              <input style="padding-top: 0.5rem" type="checkbox" />
            </div>
            <div class="table-cell-header">Name</div>
            <div class="table-cell-header">Stage</div>
            <div class="table-cell-header">Forecast Category</div>
            <div class="table-cell-header">Amount</div>
            <!-- <div class="table-cell-header">Next Step</div> -->
            <div class="table-cell-header">Close Date</div>
            <div class="table-cell-header">Last Activity</div>
            <div class="table-cell-header cell-name">
              <img src="@/assets/images/plusOne.png" class="invert" style="height: 1rem" alt="" />
            </div>
          </div>

          <tr class="table-row" :key="i" v-for="(opp, i) in allOppsFiltered">
            <div class="table-cell-checkbox">
              <input type="checkbox" />
            </div>
            <div class="table-cell cell-name">
              <div class="flex-row-spread">
                <div>
                  {{ opp.name }}
                  <span style="color: #199e54; margin-left: 0.2rem">account name</span>
                  <div style="color: #9b9b9b">owner: owner's name</div>
                </div>
                <div style="margin-top: 0.5rem" class="flex-row">
                  <img class="name-cell-note-button" src="@/assets/images/edit-note.png" />
                  <img
                    @click="getNotes(opp.id)"
                    class="name-cell-edit-note-button"
                    src="@/assets/images/white-note.png"
                    :id="opp.id"
                  />
                </div>
              </div>
            </div>

            <div class="table-cell">{{ opp.stage }}</div>
            <div class="table-cell">{{ opp.forecast_category }}</div>
            <div class="table-cell" style="color: #199e54">
              {{ formatCash(parseFloat(opp.amount)) }}
            </div>
            <!-- <div v-if="opp.secondary_data.NextStep" class="table-cell">
              {{ opp.secondary_data.NextStep }}
            </div>
            <div class="table-cell" v-else>-</div> -->
            <div class="table-cell">{{ formatDate(opp.close_date) }}</div>
            <div class="table-cell" v-if="opp.last_activity_date">
              {{ formatDateTime(opp.last_activity_date) }}
            </div>
            <div class="table-cell" v-else>-</div>
            <div class="table-cell">
              <p>---</p>
            </div>
          </tr>
        </div>
      </section>

      <section v-if="selectedWorkflow && currentWorkflow.list.length > 0" class="table-section">
        <div class="table">
          <div class="table-row">
            <div class="table-cell-checkbox-header">
              <input style="padding-top: 0.5rem" type="checkbox" />
            </div>
            <div class="table-cell-header">Name</div>
            <div class="table-cell-header" :key="i" v-for="(field, i) in oppFields" ref="fields">
              {{ getFields(field.referenceDisplayLabel) }}
            </div>
            <div class="table-cell-header cell-name">
              <img src="@/assets/images/plusOne.png" class="invert" style="height: 1rem" alt="" />
            </div>
          </div>

          <tr class="table-row" :key="i" v-for="(workflow, i) in filteredWorkflows">
            <div class="table-cell-checkbox">
              <input type="checkbox" />
            </div>
            <div class="table-cell cell-name">
              <div class="flex-row-spread">
                <div>
                  {{ workflow.resourceRef.name }}
                  <span style="color: #199e54; margin-left: 0.2rem">account name</span>
                  <div style="color: #9b9b9b">owner: owner's name</div>
                </div>
                <div style="margin-top: 0.5rem" class="flex-row">
                  <img class="name-cell-note-button" src="@/assets/images/edit-note.png" />
                  <img
                    @click="getNotes(workflow.resourceRef.id)"
                    class="name-cell-edit-note-button"
                    src="@/assets/images/white-note.png"
                  />
                </div>
              </div>
            </div>

            <!-- <div :key="field" v-for="field in currentWorkflowFields" class="table-cell">
              {{ workflow.resourceRef[camelize(field)] }}
            </div> -->

            <div :key="field.name" v-for="field in currentWorkflowFields" class="table-cell">
              {{
                field === 'Stage'
                  ? workflow.resourceRef.secondaryData[
                      capitalizeFirstLetter(camelize(field + 'Name'))
                    ]
                  : workflow.resourceRef.secondaryData[capitalizeFirstLetter(camelize(field))]
              }}
            </div>
            <div class="table-cell">
              <p>---</p>
            </div>
          </tr>
        </div>
      </section>

      <section v-if="currentWorkflow && currentWorkflow.list.length < 1" class="table-section">
        <div class="table">
          <div class="table-row">
            <div class="table-cell-header">Name</div>
            <div class="table-cell-header">Stage</div>
            <div class="table-cell-header">Forecast Category</div>
            <div class="table-cell-header">Amount</div>
            <div class="table-cell-header">Close Date</div>
            <div class="table-cell-header">Last Activity</div>
          </div>

          <div class="table-row flex-row">
            <h5 style="margin-left: 1rem">
              No results for the {{ currentList }} workflow. Try refreshing
            </h5>
            <button @click="refresh(refreshId)" class="centered__button">
              <img src="@/assets/images/refresh.png" style="height: 0.75rem" alt="" />
            </button>
          </div>
        </div>
      </section>
    </div>
    <div class="loader" v-if="loading">
      <img src="@/assets/images/loading-gif.gif" class="invert" style="height: 8rem" alt="" />
    </div>
  </div>
</template>

<script>
import DropDownSelect from '@thinknimble/dropdownselect'
import { SObjects } from '@/services/salesforce'
import AlertTemplate, { AlertConfig, AlertInstance } from '@/services/alerts/'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth, { salesforceFields } from '@/services/slack'
import Modal from '@/components/InviteModal'
import User from '@/services/users'

export default {
  name: 'Pipelines',
  components: {
    DropDownSelect,
    Modal,
  },
  data() {
    return {
      noSelection: true,
      originalList: null,
      allOpps: null,
      loading: false,
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      team: CollectionManager.create({ ModelClass: User }),
      currentWorkflow: null,
      currentWorkflowFields: null,
      selectedWorkflow: false,
      modalOpen: false,
      refreshId: null,
      filterText: '',
      workflowFilterText: '',
      searchFilterText: '',
      currentList: 'All Opportunities',
      showList: false,
      showWorkflowList: true,
      showPopularList: true,
      filtering: false,
      filterType: null,
      filterTitle: null,
      filterOption: null,
      enteringAmount: false,
      amountValue: null,
      todaysAlerts: null,
      todaysList: null,
      todaysTemplate: null,
      showNotes: false,
      notes: [],
      updateOppForm: null,
      oppFields: [],
      instances: [],
      testingUpdate: null,
      monetaryOptions: ['less than', 'greater than', 'equals'],
      oppFilters: [
        {
          title: 'Amount',
          type: 'monetary',
        },
        {
          title: 'Close date',
          type: 'date',
        },
        {
          title: 'Next step date',
          type: 'date',
        },
        {
          title: 'Last activity',
          type: 'time',
        },
        {
          title: 'Last modified',
          type: 'time',
        },
        {
          title: 'Owner',
          type: 'person',
        },
      ],
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    allOppsFiltered() {
      return this.allOpps.filter((opp) =>
        opp.name.toLowerCase().includes(this.filterText.toLowerCase()),
      )
    },
    filteredWorkflows() {
      return this.currentWorkflow.list.filter((opp) =>
        opp.resourceRef.name.toLowerCase().includes(this.workflowFilterText.toLowerCase()),
      )
    },
    filteredFilters() {
      return this.oppFilters.filter((opp) =>
        opp.title.toLowerCase().includes(this.searchFilterText.toLowerCase()),
      )
    },
    currentMonth() {
      let date = new Date()
      return date.getMonth()
    },
  },
  created() {
    this.getObjects()
    this.getAllForms()
    this.createFormInstance()
    this.team.refresh()
    this.templates.refresh()
  },
  methods: {
    test() {
      console.log(this.updateResource())
    },
    async refresh(id) {
      if (id) {
        try {
          await AlertTemplate.api.runAlertTemplateNow(id)
          this.$Alert.alert({
            message: `workflow initiated successfully`,
            type: 'success',
            timeout: 2000,
          })
        } catch {
          this.$Alert.alert({
            message: 'Something went wrong (o^^)o.... Try again',
            type: 'error',
            timeout: 2000,
          })
        }
      }
      this.$Alert.alert({
        message: `workflows sucessfully refreshed`,
        type: 'success',
        timeout: 2000,
      })
    },
    resetNotes() {
      this.notes = []
      this.noteTitles = []
      this.modalOpen = !this.modalOpen
    },
    camelize(str) {
      return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function (match, index) {
        if (+match === 0) return ''
        return index === 0 ? match.toLowerCase() : match.toUpperCase()
      })
    },
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1)
    },
    getFields(field) {
      while (!this.currentWorkflowFields.includes(field)) {
        this.currentWorkflowFields.push(field)
        console.log(this.currentWorkflowFields)
      }
      return field
    },
    // defaultList(){
    //   this.defaultList = CollectionManager.create({
    //     ModelClass: AlertInstance,
    //     filters: {
    //       byConfig: configId,
    //     },
    //   })
    //   this.currentWorkflow.refresh()
    // },

    async createFormInstance() {
      try {
        const res = await SObjects.api.createFormInstance({
          formData: {
            resourceType: 'Opportunity',
            formType: 'Update',
          },
        })
        console.log(res)
        this.testingUpdate = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    async updateResource() {
      try {
        const res = await SObjects.api.updateResource({
          form_id: this.testingUpdate,
          form_data: {
            meeting_type: 'Update pending......',
          },
        })
        console.log(res)
      } catch (e) {
        console.log(e)
      }
    },
    selectList(configId, title, id) {
      this.currentWorkflowFields = []
      this.refreshId = id
      this.currentWorkflow = CollectionManager.create({
        ModelClass: AlertInstance,
        filters: {
          byConfig: configId,
        },
      })
      this.currentWorkflow.refresh()
      this.currentList = title
      this.selectedWorkflow = true
      this.showList = false
    },
    showAlertList() {
      this.allOpps = this.alertList
    },
    async getConfigs(configId) {
      try {
        const res = await AlertConfig.api.getCurrentInstances({
          configId: configId,
        })
        this.todaysAlerts = res.data.instances
        this.todaysTemplate = res.data.template
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    async getAllForms() {
      this.loading = true
      try {
        this.updateOppForm = await SlackOAuth.api.getOrgCustomForm()
        this.updateOppForm = this.updateOppForm.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Opportunity',
        )
        this.oppFields = this.updateOppForm[0].fieldsRef.filter(
          (field) =>
            field.apiName !== 'meeting_type' &&
            field.apiName !== 'meeting_comments' &&
            field.apiName !== 'Name',
        )
      } catch (error) {
        console.log(error)
      }
      this.loading = false
    },
    async getObjects() {
      this.loading = true
      try {
        const res = await SObjects.api.getObjects('Opportunity')
        this.allOpps = res.results
        this.originalList = res.results
        this.todaysList = res.results
      } catch {
        this.$Alert.alert({
          type: 'error',
          timeout: 2000,
          message: 'There was an error collecting objects',
        })
      }
      this.loading = false
    },
    async getNotes(id) {
      console.log(id)
      try {
        const res = await SObjects.api.getNotes({
          resourceId: id,
        })
        this.modalOpen = true
        console.log(res)
        if (res.length) {
          for (let i = 0; i < res.length; i++) {
            this.notes.push(res[i])
          }
        }
      } catch (e) {
        console.log(e)
      }
    },

    async handleCancel() {
      await this.refresh()
      this.resetNotes()
      this.$emit('cancel')
    },
    applyAmountFilter() {
      // this.allOpps = this.allOpps.filter((opp) => opp.amount > this.amountValue)
    },
    showAmount() {
      console.log(this.amountValue)
    },
    selectFilter(type, title) {
      switch (type) {
        case 'monetary':
          this.monetaryFilter(type, title)
          break
        case 'date':
          this.dateFilter(type, title)
          break
        case 'time':
          this.timeFilter(type, title)
          break
        case 'person':
          this.personFilter(type, title)
          break
      }
    },
    selectFilterOption(option) {
      if (option === 'less than' || option === 'greater than' || option === 'equals') {
        this.amountInput(option)
      }
    },
    amountInput(option) {
      this.enteringAmount = !this.enteringAmount
      this.filterOption = option
    },
    monetaryFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
      console.log(type, title)
    },
    dateFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
      console.log(type, title)
    },
    timeFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
      console.log(type, title)
    },
    personFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
      console.log(type, title)
    },
    closeFilters() {
      this.filtering = !this.filtering
    },
    closeDatesThisMonth() {
      this.selectedWorkflow = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.close_date).getMonth() == this.currentMonth,
      )
      this.currentList = 'Closing this month'
      this.showList = !this.showList
    },
    closeDatesNextMonth() {
      this.selectedWorkflow = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.close_date).getMonth() == this.currentMonth + 1,
      )
      this.currentList = 'Closing next month'
      this.showList = !this.showList
    },
    allOpportunities() {
      this.selectedWorkflow = false
      this.allOpps = this.originalList
      this.currentList = 'All Opportunities'
      this.showList = !this.showList
    },
    closeList() {
      if (this.showList === false) {
        this.showList = this.showList
      } else {
        this.showList = !this.showList
      }
    },
    formatDate(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      return input.replace(pattern, '$2/$3/$1')
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    formatCash(money) {
      let cash = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        //maximumFractionDigits: 0, // (2500.99 would be printed as $2,501)
      })
      if (money) {
        return cash.format(money)
      }
      return '-'
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

::placeholder {
  color: $mid-gray;
}
h3 {
  font-size: 22px;
}
::v-deep .tn-dropdown__selection-container:after {
  position: absolute;
  content: '';
  top: 13px;
  right: 1em;
  width: 0;
  height: 0;
  border: 5px solid transparent;
  border-color: $base-gray transparent transparent transparent;
}
::v-deep .tn-dropdown__selection-container {
  width: 12vw;
  height: 4.5vh;
  border: 1px solid $soft-gray;
  box-shadow: 1px 2px 1px $very-light-gray;
  padding: 0.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
::v-deep .tn-dropdown--medium {
  display: flex;
  justify-content: center;
  width: 12vw;
  height: 4.5vh;
  margin-right: 1rem;
}
::v-deep .tn-dropdown__selected-items__item-selection--muted {
  color: $base-gray;
}
::v-deep .tn-dropdown__options__option--selected {
  color: $base-gray;
  background-color: white;
  border-radius: 0.25rem;
}
.table-section {
  height: 67vh;
  overflow: scroll;
  margin-top: 0.5rem;
  border-radius: 5px;
  box-shadow: 1px 1px 20px 1px $soft-gray;
  background-color: $off-white;
}
.table {
  display: table;
  width: 98vw;
  height: 10vh !important;
}
.table-row {
  display: table-row;
}
.table-cell {
  display: table-cell;
  background-color: $off-white;
  padding: 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
  overflow: scroll;
}
.table-cell:hover {
  cursor: text;
  background-color: white;
}
.modal-container {
  background-color: $off-white;
  min-height: 60vh;
  align-items: center;
  border-radius: 0.5rem;
  padding: 0.5rem;
}
.note-section {
  padding: 0.5rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-radius: 0.3rem;
  &__title {
    font-size: 16px;
    font-weight: bold;
    color: $base-gray;
  }
  &__body {
    color: $gray;
  }
}
// .table-row > .table-cell:hover {
//   background-color: $off-white;
// }
.table-cell-checkbox {
  display: table-cell;
  padding: 2vh 1vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
}
.table-cell-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 1;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 15px;
  color: $base-gray;
}
.table-cell-checkbox-header {
  display: table-cell;
  padding: 2vh 1vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  z-index: 1;
  top: 0;
  position: sticky;
  background-color: $off-white;
}
.table-row:nth-child(even) {
  background: $off-white;
}
.cell-name {
  background-color: white;
  border-radius: 6px;
}
input[type='search'] {
  border: none;
  background-color: $off-white;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
input[type='text']:focus {
  outline: none;
}
input[type='checkbox'] {
  cursor: pointer;
}
p {
  font-size: 13px;
}
.img {
  margin-right: 0.25rem;
  height: 0.75rem;
  filter: invert(50%);
}

header,
section {
  margin: 0;
  padding: 0px 2px;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.flex-col {
  display: flex;
  flex-direction: column;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.pipelines {
  margin-top: 5rem;
  color: $base-gray;
}
.invert {
  filter: invert(80%);
}
.sub-heading {
  color: $gray;
  margin-top: -1vh;
}
.title {
  color: $base-gray;
}
.pipe-button {
  display: flex;
  align-items: center;
  height: 4.5vh;
  // box-shadow: 1px 2px 3px $very-light-gray;
  background-color: $lighter-green;
  border: none;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.5rem;
  border-radius: 0.2rem;
  color: $darker-green;
  cursor: pointer;
  transition: all 0.3s;
}
.pipe-button:hover {
  transform: scale(1.03);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.disabled-button {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $gray;
  cursor: not-allowed;
  color: white;
}
.add-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  // box-shadow: 1px 2px 3px 1px $very-light-gray;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}
.add-button:hover {
  transform: scale(1.03);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.resNum {
  color: $dark-green;
  font-weight: bold;
}
.search-bar {
  height: 4.5vh;
  background-color: $off-white;
  box-shadow: 1px 1px 1px $very-light-gray;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 5px;
  margin-right: 0.5rem;
}
.loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  filter: invert(99%);
}
.invert {
  filter: invert(99%);
}
.wide {
  width: 100%;
}
.name-cell-note-button {
  height: 1.5rem;
  cursor: pointer;
  // box-shadow: 1px 1px 1px 1px $very-light-gray;
  border: none;
  border-radius: 50%;
  padding: 0.2rem;
  margin-right: 0.5rem;
  background-color: $lighter-green;
  transition: all 0.3s;
}
.name-cell-note-button:hover,
.name-cell-edit-note-button:hover {
  transform: scale(1.03);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.name-cell-edit-note-button {
  height: 1.5rem;
  cursor: pointer;
  border: none;
  border-radius: 50%;
  padding: 0.2rem;
  margin-right: 0.25rem;
  background-color: $dark-green;
  transition: all 0.3s;
}
.list-section {
  z-index: 2;
  position: absolute;
  top: 28vh;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $off-white;
  width: 16vw;
  max-height: 40vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 1px 1px $very-light-gray;

  &__title {
    font-size: 13px;
    font-weight: bold;
    display: flex;
    align-items: center;
    margin-left: 0.75rem;
    color: $base-gray;
    cursor: pointer;

    img {
      margin: 2px 0px 0px 3px;
      height: 0.75rem;
      filter: invert(70%);
    }
  }
}
.filter-section {
  position: absolute;
  top: 21vh;
  left: 22vw;
  z-index: 2;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $off-white;
  width: 20vw;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 1px 2px $light-orange-gray;

  &__title {
    color: $dark-green;
    margin-left: 0.75rem;
    font-weight: bold;
    border-bottom: 2px solid $dark-green;
    padding-bottom: 2px;
  }

  &__filters {
    // background-color: $white-green;
    border-radius: 5px;
    width: 100%;
    margin-top: 1rem;
  }
}
.list-button {
  display: flex;
  align-items: center;
  height: 4.5vh;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75rem;
  border-radius: 0.2rem;
  color: $mid-gray;
  cursor: pointer;
  font-size: 11px;
  font-weight: bold;
}
.list-button:hover {
  color: $dark-green;
  background-color: white;
}
.filter {
  color: #199e54;
  margin-left: 0.2rem;
}
.exit {
  padding-right: 0.5rem;
  height: 1rem;
  cursor: pointer;
}
.filter-option-button {
  padding: 0.25rem 0.5rem;
  border: none;
  background-color: $dark-green;
  color: white;
  border-radius: 3px;
  margin: 0.1rem;
  font-size: 10px;
  cursor: pointer;
}
.filter-option-section {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  max-height: 10vh;
  padding: 0.5rem;
  border-radius: 1px;
  width: 100%;
  background-color: $white-green;
}
.filter-title {
  padding-left: 0.7rem;
  padding-top: 0.5rem;
  margin-top: 0.5rem;
  width: 100%;
  border-radius: 2px;
  color: $base-gray;
  background-color: $white-green;
}
.centered {
  display: flex;
  align-items: center;
  justify-content: center;

  &__button {
    display: flex;
    align-items: center;
    background-color: $dark-green;
    border: none;
    margin-left: 0.5rem;
    padding: 0.25rem;
    border-radius: 0.2rem;
    cursor: pointer;
  }
}
::-webkit-scrollbar {
  background-color: $light-orange-gray;
  -webkit-appearance: none;
  width: 1px;
  height: 100%;
}
::-webkit-scrollbar-thumb {
  border-radius: 2px;
  background-color: $very-light-gray;
}
</style>