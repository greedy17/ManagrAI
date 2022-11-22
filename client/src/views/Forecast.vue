<template>
  <div class="forecast">
    <Modal
      v-if="modalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetSettings()
        }
      "
    >
      <div class="modal-container">
        <header class="modal-container__header">
          <h3>Tracker Settings</h3>
          <img
            @click="resetSettings"
            src="@/assets/images/close.svg"
            class="invert-less"
            style="filter: invert(30%)"
            alt=""
          />
        </header>
        <div class="modal-container__body">
          <p>Add Opportunites to Tracker:</p>
          <Multiselect
            v-model="forecastVmodel"
            style="width: 60%"
            openDirection="below"
            selectLabel="Enter"
            track-by="id"
            label="name"
            :maxHeight="150"
            :options="allOpps"
            :multiple="true"
            :closeOnSelect="false"
            @select="addOppToList($event.integration_id)"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.svg" alt="" />
                Select Opportunities
              </p>
            </template>
          </Multiselect>
        </div>
        <footer class="modal-container__footer">
          <button @click="modifyForecast('add')" class="add-button">Save</button>
        </footer>
      </div>
    </Modal>
    <Modal
      v-if="deleteOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetDelete()
        }
      "
    >
      <div class="modal-container-small">
        <header class="modal-container__header">
          <h3>Remove from Tracker</h3>
          <img class="invert" @click="resetDelete" src="@/assets/images/close.svg" alt="" />
        </header>
        <div class="modal-container__body center">
          <p>Are you sure ?</p>

          <div class="row">
            <button @click="resetDelete" class="no__button">No</button>
            <button @click="removeForecast('remove')" class="yes__button">Yes</button>
          </div>
        </div>
      </div>
    </Modal>
    <Modal
      v-if="notesOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetNotes()
        }
      "
    >
      <div v-if="notes.length" class="modal-container-notes rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h4>Notes</h4>
          </div>

          <div class="flex-row">
            <small class="note-border">Total: {{ notesLength }}</small>
            <small class="note-border light-green-bg"
              >Most recent: {{ formatMostRecent(notes[0].submission_date) }} days</small
            >
            <small class="note-border"
              >Oldest: {{ formatMostRecent(notes[notes.length - 1].submission_date) }} days</small
            >
          </div>
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{ note.saved_data__meeting_type ? note.saved_data__meeting_type : 'Untitled' }}
          </p>
          <p class="note-section__date">{{ formatDateTime(note.submission_date) }}</p>
          <pre class="note-section__body">{{ note.saved_data__meeting_comments }}</pre>
        </section>
      </div>
      <div v-else class="modal-container">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h4>Notes</h4>
          </div>

          <div class="flex-row">
            <small class="note-border">Total: {{ notesLength }}</small>
            <small class="note-border light-green-bg">Most recent: 0 days</small>
            <small class="note-border">Oldest: 0 days</small>
          </div>
        </div>
        <section class="note-section">
          <p class="note-section__body">No notes for this opportunity</p>
        </section>
      </div>
    </Modal>
    <!-- <Modal
      v-if="calculatorOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetCalculator()
        }
      "
    >
      <div class="modal-container"></div>
    </Modal> -->

    <div class="forecast-header title">
      <p>Tracker</p>
      <div class="row margin-top-s">
        <div class="header-settings">
          <p>%</p>
          <img
            style="cursor: pointer"
            @click="resetSettings"
            src="@/assets/images/settings.svg"
            alt=""
          />
        </div>
      </div>
    </div>

    <section class="row">
      <div class="col">
        <section class="forecast-overview">
          <div class="forecast-overview__section" v-if="forecastOpps && !loading">
            <!-- <h3>{{ forecastLength }}</h3> -->
            <div>
              <img src="@/assets/images/coins.svg" height="16px" style="margin-right: 8px" alt="" />
              <h3>5</h3>
            </div>
            <p>Opportunites Tracked</p>
          </div>
          <div class="forecast-overview__section">
            <div>
              <span class="filter-red"
                ><img src="@/assets/images/caret-down.svg" height="18px" alt=""
              /></span>

              <h3>$1,000,000</h3>
              <!-- <h3>{{ formatCash(averageDeal) }}</h3> -->
            </div>
            <p>Avg Deal Size <span class="red">4.25%</span></p>
          </div>
          <div class="forecast-overview__section">
            <div>
              <span class="filter-green">
                <img src="@/assets/images/caret-up.svg" height="18px" alt="" />
              </span>

              <h3>$5,000,000</h3>
              <!-- <h3>{{formatCash(originalAmount) }}</h3> -->
            </div>
            <p>Total <span class="green">8.73%</span></p>
          </div>
        </section>

        <section v-if="!loading && stages" class="table-section">
          <div class="table">
            <div class="table-row">
              <div class="cell-name-header">Opportunity Name</div>
              <div
                :key="index"
                v-for="(header, index) in forecastHeaders"
                class="table-cell-header"
              >
                {{ header }}
              </div>
            </div>
            <div v-if="!forecastOpps" class="margin-left margin-top small-font gray-text">
              <p>
                No opps in forecast. Add them via
                <span @click="resetSettings" class="settings"
                  >settings <img src="@/assets/images/settings.svg" class="invert" alt="" />
                </span>
              </p>
            </div>
            <div
              v-else-if="forecastOpps"
              v-for="(opp, i, index) in forecastOpps"
              :key="i"
              class="table-row"
            >
              <p class="no-display">{{ setOriginalAmount(opp.data.Amount) }}</p>
              <div class="table-cell cell-name row">
                <div class="row-spread">
                  <div>
                    <p class="letter-spacing">{{ opp.data.Name }}</p>
                    <p class="blue-text">
                      {{
                        currentValues[index].account_ref
                          ? currentValues[index].account_ref.name
                          : ''
                      }}
                    </p>
                    <p class="gray-text">
                      Owned by:
                      {{
                        currentValues[index].owner_ref
                          ? currentValues[index].owner_ref.full_name
                          : ''
                      }}
                    </p>
                  </div>
                </div>
              </div>
              <div class="table-cell">
                <p
                  class="letter-spacing"
                  :class="{
                    'green-background': currentValues[index].amount > opp.data.Amount,
                    'red-background': currentValues[index].amount < opp.data.Amount,
                  }"
                >
                  {{ currentValues[index].amount ? formatCash(currentValues[index].amount) : '' }}
                </p>
                <p class="gray-text letter-spacing">
                  {{ opp.data.Amount ? formatCash(opp.data.Amount) : '' }}
                </p>
              </div>
              <div class="table-cell">
                <p>{{ formatDateTime(opp.dateAdded.split(' ')[0]) }}</p>
              </div>
              <div class="table-cell">
                <p
                  class="align-center"
                  :class="{
                    'green-background':
                      stages.indexOf(currentValues[index].stage) >
                      stages.indexOf(opp.data.StageName),
                    'red-background':
                      stages.indexOf(currentValues[index].stage) <
                      stages.indexOf(opp.data.StageName),
                  }"
                >
                  {{ currentValues[index].stage }}
                </p>
                <p class="gray-text">{{ opp.data.StageName }}</p>
              </div>

              <div class="table-cell">
                <p
                  class="align-center"
                  :class="{
                    'green-background':
                      forecasts.indexOf(currentValues[index].forecast_category) >
                      forecasts.indexOf(opp.data.ForecastCategoryName),
                    'red-background':
                      forecasts.indexOf(currentValues[index].forecast_category) <
                      forecasts.indexOf(opp.data.ForecastCategoryName),
                  }"
                >
                  {{ currentValues[index].forecast_category }}
                </p>
                <p class="gray-text">
                  {{ opp.data.ForecastCategoryName ? opp.data.ForecastCategoryName : '' }}
                </p>
              </div>

              <div class="table-cell">
                <p
                  class="align-center"
                  :class="{
                    'green-background': currentValues[index].close_date < opp.data.CloseDate,
                    'red-background': currentValues[index].close_date > opp.data.CloseDate,
                  }"
                >
                  {{ currentValues[index] ? formatDate(currentValues[index].close_date) : '' }}
                </p>
                <p class="gray-text">
                  {{ opp.data.CloseDate ? formatDate(opp.data.CloseDate) : '' }}
                </p>
              </div>
              <div class="table-cell">
                <p>
                  {{
                    opp.data.LastActivityDate
                      ? formatDateTime(currentValues[index].last_activity_date)
                      : ''
                  }}
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
      <div style="position: relative" class="statistics">
        <h3 class="letter-spacing">{{ selectedOpp.name }}</h3>
        <div>
          <small class="yellow">fair</small>
          <Chart />
          <div class="margin-top-neg">
            <Tabs />
          </div>
        </div>
        <div style="position: sticky; bottom: 0">test</div>

        <!-- <div class="row">
          <button
            @click="getNotes(allOpps.filter((opp) => opp.integration_id === i)[0].id)"
            class="name-cell-edit-note-button"
          >
            <img class="invert-less" src="@/assets/images/note.svg" height="12px" alt="" />
          </button>

          <button
            @click="
              deleteOpen = true
              setDeleteId(opp.data.Id)
            "
            class="name-cell-edit-note-button"
          >
            <img class="invertTrash" src="@/assets/images/trash.svg" height="12px" alt="" />
          </button>
        </div> -->
      </div>
    </section>
    <div v-if="loading">
      <PipelineLoader />
    </div>
  </div>
</template>

<script>
import { SObjects, SObjectPicklist } from '@/services/salesforce'
import Chart from '@/components/Chart'
import Tabs from '@/components/Tabs'
import User from '@/services/users'

export default {
  name: 'Forecast',
  data() {
    return {
      filters: [
        { name: 'Amount', apiName: 'Amount', type: 'Currency' },
        { name: 'Stage', apiName: 'StageName', type: 'Picklist' },
        { name: 'Forecast', apiName: 'ForecastCategoryName', type: 'Picklist' },
        { name: 'Close Date', apiName: 'CloseDate', type: 'Date' },
        { name: 'Last Activity', apiName: 'LastActivityDate', type: 'Date' },
      ],
      filterTypes: [
        { name: 'equals', value: '=' },
        { name: 'greater than', value: '>' },
        { name: 'greater or equal', value: '>=' },
        { name: 'less than', value: '<' },
        { name: 'less or equal', value: '<=' },
      ],
      forecastHeaders: ['Amount', 'Date Added', 'Stage', 'Forecast', 'Close Date', 'Last Activity'],
      forecastOptions: ['My forecast', 'Team Forecast'],
      currentForecast: 'My Tracker',
      forecastOppsCopy: this.$store.state.user.forecast.state,
      forecastOpps: this.$store.state.user.forecast.state,
      calculatorOpen: false,
      filterSelected: false,
      addingOperator: false,
      deleteOpen: false,
      filtering: false,
      modalOpen: false,
      notesOpen: false,
      showList: false,
      loading: true,
      forecastVmodel: null,
      forecastLength: null,
      currentOperator: null,
      currentFilter: null,
      filterApiName: null,
      hoveredIndex: null,
      averageDeal: null,
      filterType: null,
      currentVal: null,
      forecasts: null,
      allOpps: null,
      stages: null,
      originalAmount: 0,
      totalAmount: 0,
      limit: 0,
      picklistQueryOpts: { StageName: null, ForecastCategoryName: null },
      currentValues: null,
      addedOpportunities: [],
      activeOperators: [],
      addedFilters: [],
      filterValues: [],
      deleteIds: [],
      notes: [],
      activeFilters: [],
      filterNames: [],
      notesLength: 0,
      selectedOpp: null,
    }
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    FilterSelection: () => import(/* webpackPrefetch: true */ '@/components/FilterSelection'),
    Chart,
    Tabs,
  },
  // watch: {
  //   allOpps: ['getStagesAndForecast'],
  // },
  async created() {
    this.getStagesAndForecast()
    this.getForecastValues()
    this.getOpportunites()
  },

  mounted() {
    this.setPicklist()
    setTimeout(() => {
      console.log(this.forecastOpps)
    }, 3000)
  },
  methods: {
    resetNotes() {
      this.notesOpen = !this.notesOpen
      this.notes = []
    },
    async getNotes(id) {
      try {
        const res = await SObjects.api.getNotes({
          resourceId: id,
        })
        this.notesOpen = true
        if (res.length) {
          for (let i = 0; i < res.length; i++) {
            this.notes.push(res[i])
            this.notes = this.notes.filter((note) => note.saved_data__meeting_comments !== null)
            this.notesLength = this.notes.length
          }
        }
      } catch (e) {
        console.log(e)
      }
    },
    setDeleteId(id) {
      this.deleteIds = []
      this.deleteIds.push(id)
    },
    async removeForecast() {
      try {
        await User.api.modifyForecast('remove', this.deleteIds)
        this.$toast('Opportunity Removed. Refresh to see changes', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error removing opportunity!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.deleteOpen = false
        this.deleteIds = []
      }
    },
    async modifyForecast(action) {
      try {
        await User.api.modifyForecast(action, this.addedOpportunities)
        this.$toast('Opportunity Added to Tracker', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error adding opportunities', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.resetSettings()
      }
    },
    async getForecastValues() {
      this.loading = true
      try {
        const res = await User.api.getForecastValues()
        console.log(res)
        this.currentValues = res
        this.selectedOpp = res[0]
        for (let i = 0; i < res.length; i++) {
          this.totalAmount += parseInt(res[i].amount) ? parseInt(res[i].amount) : 0
        }
        this.forecastLength = res.length
        this.averageDeal = this.totalAmount / this.forecastLength
      } catch (e) {
        this.$toast('No tracked opportunities', {
          timeout: 2000,
          position: 'top-left',
          type: 'default',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getOpportunites() {
      try {
        let res = await SObjects.api.getObjectsForWorkflows('Opportunity')
        this.allOpps = res.results
      } catch (e) {
        this.$toast('Error gathering opportunities', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    setOriginalAmount(i) {
      if (this.limit < this.forecastLength) {
        this.originalAmount += i
        this.limit += 1
      }
    },
    async getStagesAndForecast() {
      this.loading = true
      try {
        let res
        if (this.userCRM === 'HUBSPOT') {
          res = await ObjectField.api.listFields({
            crmObject: this.DEAL,
            search: 'Deal Stage',
          })
          let dealStage
          for (let i = 0; i < res.length; i++) {
            if (res[i].apiName === 'dealstage') {
              dealStage = res[i]
              break
            }
          }
          this.stages = dealStage ? dealStage.options : []
        } else if (this.userCRM === 'SALESFORCE') {
          res = await SObjectPicklist.api.listPicklists({
            picklistFor: 'StageName',
            salesforceObject: 'Opportunity',
          })
          this.stages = res.length ? res[0]['values'] : []
        }
        let res2 = await SObjectPicklist.api.listPicklists({
          picklistFor: 'ForecastCategoryName',
          salesforceObject: 'Opportunity',
        })
        this.stages ? (this.stages = this.stages.map((stage) => stage.value)) : []
        this.forecasts = res2.length ? res2[0]['values'] : []
        this.forecasts ? (this.forecasts = this.forecasts.map((forecast) => forecast.value)) : []
      } catch (e) {
        this.$toast('Error gathering your stages', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loading = false
      }
    },
    async listPicklists(type, query_params) {
      try {
        let res
        if (this.userCRM === 'HUBSPOT') {
          res = await ObjectField.api.listFields({
            crmObject: this.DEAL,
            search: 'Deal Stage',
          })
          let dealStage
          for (let i = 0; i < res.length; i++) {
            if (res[i].apiName === 'dealstage') {
              dealStage = res[i]
              break
            }
          }
          this.picklistQueryOpts[type] = dealStage ? dealStage.options : []
        } else if (this.userCRM === 'SALESFORCE') {
          res = await SObjectPicklist.api.listPicklists(query_params)
          this.picklistQueryOpts[type] = res.length ? res[0]['values'] : []
        }
      } catch (e) {
        console.log(e)
      }
    },
    setPicklist() {
      for (let i in this.picklistQueryOpts) {
        this.picklistQueryOpts[i] = this.listPicklists(i, {
          picklistFor: i,
          salesforceObject: 'Opportunity',
        })
      }
    },
    applyFilter() {
      this.forecastOpps = Object.values(this.forecastOpps)
      this.activeFilters.push(this.currentFilter)
      this.activeOperators.push(this.currentOperator)
      this.filterValues.push(this.currentVal)

      if (this.currentOperator === 'EQUALS') {
        this.forecastOpps = this.forecastOpps.filter(
          (opp) => opp.data[this.filterApiName] == this.currentVal,
        )
      } else if (this.currentOperator === 'NOT_EQUALS') {
        this.forecastOpps = this.forecastOpps.filter(
          (opp) => opp.data[this.filterApiName] != this.currentVal,
        )
      } else if (this.currentOperator === 'GREATER_THAN') {
        this.forecastOpps = this.forecastOpps.filter(
          (opp) => opp.data[this.filterApiName] > this.currentVal,
        )
      } else if (this.currentOperator === 'GREATER_THAN_EQUALS') {
        this.forecastOpps = this.forecastOpps.filter(
          (opp) => opp.data[this.filterApiName] >= this.currentVal,
        )
      } else if (this.currentOperator === 'LESS_THAN') {
        this.forecastOpps = this.forecastOpps.filter(
          (opp) => opp.data[this.filterApiName] < this.currentVal,
        )
      } else if (this.currentOperator === 'LESS_THAN_EQUALS') {
        this.forecastOpps = this.forecastOpps.filter(
          (opp) => opp.data[this.filterApiName] <= this.currentVal,
        )
      } else if (this.currentOperator === 'CONTAINS') {
        this.forecastOpps = this.forecastOpps.filter((opp) =>
          opp.data[this.filterApiName].includes(this.currentVal),
        )
      }
      this.closeFilterSelection()
    },
    valueSelected(value) {
      this.currentVal = value
    },
    addOperator(val) {
      this.currentOperator = val
    },
    removeFilter(name, index) {
      this.activeFilters.splice(index, 1)
      this.filterValues.splice(index, 1)
      this.activeOperators.splice(index, 1)
      this.filterSelected = false
    },
    addFilter(filter, name, type) {
      this.filterApiName = filter
      this.currentFilter = name
      this.filterType = type
      this.filtering = false
      this.filterSelected = true
    },
    closeFilterSelection() {
      this.filterSelected = false
      this.currentFilter = null
      this.currentOperator = null
    },
    gotToPipeline() {
      this.$router.push({ name: 'Pipelines' })
    },
    closeListSelect() {
      this.showList = false
    },
    addOppToList(val) {
      this.addedOpportunities.push(val)
    },
    resetSettings() {
      this.modalOpen = !this.modalOpen
    },
    resetDelete() {
      this.deleteOpen = !this.deleteOpen
    },
    resetAddOpp() {
      this.addOppOpen = !this.addOppOpen
    },
    weekDay(input) {
      let newer = new Date(input)
      return this.days[newer.getDay()]
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    formatMostRecent(date2) {
      let today = new Date()
      let d = new Date(date2)
      let diff = today.getTime() - d.getTime()
      let days = diff / (1000 * 3600 * 24)
      return Math.floor(days)
    },
    formatDate(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      return input.replace(pattern, '$2/$3/$1')
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
    closeFilters() {
      this.filtering = false
    },
    addingFilter() {
      if (this.filtering === true) {
        this.filtering = false
      } else {
        this.filtering = true
        this.filterSelected = false
      }
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    userCRM() {
      return this.$store.state.user.crm
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.statistics {
  border: 1px solid $soft-gray;
  background-color: white;
  height: 83vh;
  width: 32vw;
  border-radius: 8px;
  padding: 12px;
  h3 {
    color: $base-gray;
  }
}
.col {
  display: flex;
  flex-direction: column;
  margin-right: 16px;
}
.green-background {
  // background-color: $off-white;
  color: $dark-green;
  padding: 4px 6px;
  border-radius: 6px;
  margin-left: -6px;
}
.red-background {
  // background-color: $off-white;
  color: $coral;
  padding: 4px 6px;
  border-radius: 6px;
  margin-left: -6px;
}
.blue-text {
  color: $light-gray-blue !important;
}
.margin-top-neg {
  margin-top: -32px;
}
.modal-container-notes {
  background-color: $white;
  overflow: auto;
  min-width: 36vw;
  max-width: 36vw;
  min-height: 44vh;
  max-height: 80vh;
  align-items: center;
  border-radius: 0.5rem;
  border: 1px solid #e8e8e8;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.light-green-bg {
  background-color: $white-green;
  color: $dark-green !important;
  border: 1px solid $dark-green !important;
}
.note-border {
  border: 1px solid $very-light-gray;
  border-radius: 6px;
  padding: 4px;
  margin: 0px 6px;
  font-size: 12px;
}
.border-bottom {
  border-bottom: 1.25px solid $soft-gray;
}
.sticky {
  position: sticky;
  background-color: white;
  width: 100%;
  left: 0;
  top: 0;
  padding: 0px 6px 8px -2px;
}
.rel {
  position: relative;
}
.margin-left {
  margin-left: 1.25rem;
}
.margin-left-s {
  margin-left: 0.25rem;
}
.margin-top {
  margin-top: 1rem;
}
.margin-top-2 {
  margin-top: 2rem;
}
.small-font {
  font-size: 12px;
  font-weight: 300 !important;
}
.smaller-font {
  font-size: 11px;
  font-weight: 300 !important;
}
.gray-text {
  color: $gray;
}
.green-text {
  color: $dark-green;
}
.green-text-amount {
  color: $dark-green;
  background-color: $white-green;
  padding: 4px;
  border-radius: 6px;
}
.align-center {
  display: flex;
  align-items: center;
}
.forecast {
  margin: 8px 0px 0px 64px;
  padding: 0 1rem 0rem 0.75rem;
}
.letter-spacing {
  letter-spacing: 1px;
}
.relative {
  position: relative;
}
.filter-green {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: $white-green;
  margin-right: 8px;
  padding: 2px;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
    padding: 0px;
  }
}
.filter-red {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: $light-red;
  margin-right: 8px;
  padding: 2px;
  img {
    filter: invert(48%) sepia(76%) saturate(3436%) hue-rotate(326deg) brightness(113%) contrast(96%);
    padding: 0px;
  }
}
.red {
  color: $coral;
  margin-left: 8px;
}
.green {
  color: $dark-green;
  margin-left: 8px;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}
.center {
  display: flex;
  align-items: center;
  justify-content: center;
}
.row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.invert {
  filter: invert(70%);
}
.invertTrash {
  filter: invert(30%);
}
.invert-less {
  filter: invert(40%);
}
.table-section {
  margin: 0;
  padding: 0;
  height: 66vh;
  width: 60vw;
  margin-top: 16px;
  overflow: scroll;
  border-radius: 12px;
  border: 1.25px solid $soft-gray;
  border-bottom: 1px solid $soft-gray;
  background-color: white;
}
.table {
  display: table;
  overflow: scroll;
  border-collapse: separate;
  border-spacing: 3px;
  width: 100vw;
  padding-bottom: -0.5rem !important;
}
.table-row {
  display: table-row;
  left: 0;
}
.table-row-sticky {
  display: table-row;
  position: sticky;
  z-index: 2;
  bottom: 0;
  outline: none;
  border-top: 1px solid #e8e8e8;
  padding: 0.5rem;
}
.table-cell {
  display: table-cell;
  position: sticky;
  min-width: 12vw;
  background-color: white;
  padding: 1vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 12px;
}
.table-cell-s {
  display: table-cell;
  position: sticky;
  left: 0;
  min-width: 12vw;
  padding: 0 3vh;
  border: none;
  font-size: 12px;
  background-color: white;

  p {
    height: 0.4rem !important;
  }
}
.table-cell-header {
  display: table-cell;
  padding: 2vh 3vh;
  border: none;
  border-bottom: 1px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: white;
  font-weight: bold;
  font-size: 12px;
  letter-spacing: 0.5px;
  color: $light-gray-blue;
}
.cell-name-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 1px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 3;
  left: 0;
  top: 0;
  position: sticky;
  background-color: white;
  font-weight: bold;
  font-size: 12px;
  letter-spacing: 0.5px;
  color: $light-gray-blue;
}
.cell-name {
  background-color: white;
  color: $base-gray;
  letter-spacing: 0.25px;
  position: sticky;
  left: 0;
  z-index: 2;
  p {
    margin-top: -0.4rem;
    font-size: 12px;
  }
}
.forecast-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 4px 0px;
  position: relative;
  z-index: 4;

  &__button {
    margin-top: 4px;
    background-color: white;
    box-shadow: 1px 2px 2px $very-light-gray;
    border: none;
    height: 2rem;
    width: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    cursor: pointer;
  }
  &__green-button {
    background-color: white;
    border: 0.5px solid $dark-green;
    height: 2rem;
    width: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 3px;
    cursor: pointer;
  }
  button > img {
    height: 1rem;
  }
}
.forecast-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0.25rem 1rem;
}
.no-display {
  display: none;
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
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.modal-container-small {
  background-color: $white;
  overflow: auto;
  width: 26vw;
  height: 28vh;
  align-items: center;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}
.modal-container {
  background-color: $white;
  overflow: auto;
  width: 34vw;
  min-height: 48vh;
  align-items: center;
  border-radius: 8px;
  border: 1px solid #e8e8e8;

  &__header {
    display: flex;
    justify-content: space-between;
    padding-left: 0.75rem;
    border-bottom: 1px solid #e8e8e8;
    img {
      filter: invert(80%);
      height: 1.25rem;
      margin-top: 0.75rem;
      margin-right: 0.5rem;
      cursor: pointer;
    }
  }
  &__body {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    margin-top: 1vh;
    padding: 0 1rem;
    min-height: 28vh;
  }
  &__footer {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    position: sticky;
    height: 8vh;
    padding: 0.5rem;
  }
}
.add-button {
  display: flex;
  align-items: center;
  border: none;
  margin: 0 0.5rem 0 0;
  padding: 0.5rem 1.25rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
}
.add-filter-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: transparent;
  cursor: pointer;
  color: $dark-green;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
.settings {
  display: flex;
  align-items: center;
  color: $dark-green;
  text-decoration: underline;
  padding-bottom: 0.2rem;
  cursor: pointer;
  img {
    height: 0.75rem;
    filter: invert(80%);
    margin-left: 0.25rem;
  }
}
.select-btn1 {
  width: 9rem !important;
  border: 0.25px solid $very-light-gray;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between !important;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  color: $base-gray;
  letter-spacing: 0.2px;

  img {
    filter: invert(40%);
  }
}
.list-section {
  z-index: 4;
  position: absolute;
  top: 3rem;
  left: 0.5rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 20vw;
  max-height: 70vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  &__title {
    position: sticky;
    top: 0;
    z-index: 5;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.25px;
    padding-left: 0.75rem;
    font-weight: bold;
    font-size: 16px;
    width: 100%;
  }
  &__sub-title {
    font-size: 12px;
    letter-spacing: 0.3px;
    font-weight: bold;
    display: flex;
    align-items: center;
    margin-left: 0.75rem;
    margin-top: 1rem;
    color: $base-gray;
    cursor: pointer;
    width: 100%;
    img {
      margin: 2px 0px 0px 3px;
      height: 0.75rem;
      filter: invert(70%);
    }
  }
}
.list-button {
  display: flex;
  align-items: center;
  justify-content: space-between !important;
  height: 3rem !important;
  width: 100% !important;
  background-color: transparent;
  border: none;
  padding: 0.75rem;
  margin-top: 0.2rem;
  border-radius: 0.2rem;
  color: $mid-gray;
  cursor: pointer;
  font-size: 11px;
  font-weight: bolder;
}
.list-button-2 {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 2rem;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75rem;
  margin-top: 0.2rem;
  border-radius: 0.2rem;
  color: $mid-gray;
  cursor: pointer;
  font-size: 11px;
  font-weight: bolder;
}
.list-button:hover,
.list-button-2:hover {
  color: $dark-green;
  background-color: $off-white;
}
.selected-filters {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  max-width: 50vw;
  margin-top: 1rem;
  overflow: scroll;
  padding: 0;

  &__close {
    background-color: $white-green;
    backdrop-filter: blur(0.5px);
    opacity: 4;
    border: none;
    margin-left: -1rem;
    padding: 0rem 0.1rem 0rem 0.1rem;
    min-height: 3vh;

    img {
      height: 0.9rem;
      filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
    }
  }
}
.main {
  border: none;
  height: 5vh;
  max-width: 12vw;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $white-green;
  cursor: pointer;
  color: $dark-green;
  white-space: nowrap;
  overflow: hidden;
  //   text-overflow: ellipsis;
}
.main__before {
  display: flex;
  align-items: center;
  flex-direction: row;
  border: none;
  min-height: 5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  font-weight: bold;
}

.name-cell-edit-note-button {
  height: 1.5rem;
  width: 1.5rem;
  margin-right: 0.2rem;
  padding: 0.25rem;
  border-radius: 5px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0.8px solid $gray;
  cursor: pointer;
}
.no__button {
  background-color: $soft-gray;
  outline: 1px solid $soft-gray;
  border: none;
  font-size: 14px;
  border-radius: 0.3rem;
  cursor: pointer;
  padding: 0.4rem 2rem;
  margin-right: 0.5rem;
  color: $base-gray;
}
.yellow {
  background-color: $light-yellow;
  color: $yellow;
  padding: 4px 6px;
  border-radius: 6px;
}
.yes__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 2rem;
  border-radius: 0.3rem;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.25px;
  color: white;
  background-color: $dark-green;
  outline: 1px solid $dark-green;
  cursor: pointer;
  font-size: 14px;
}
.logo {
  height: 1.75rem;
  margin-left: 0.5rem;
  margin-right: 0.25rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.note-section {
  padding: 0.25rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 19px;
    font-weight: bolder;
    letter-spacing: 0.6px;
    color: $base-gray;
    padding: 0;
  }
  &__body {
    color: $base-gray;
    font-family: $base-font-family;
    word-wrap: break-word;
    white-space: pre-wrap;
    border-left: 2px solid $dark-green;
    padding-left: 8px;
    font-size: 14px;
  }
  &__date {
    color: $mid-gray;
    font-size: 12px;
    margin-top: -14px;
    margin-bottom: 8px;
    letter-spacing: 0.6px;
  }
}
.title {
  padding: 0;
  margin: 0;
  margin-left: 8px;
  margin-bottom: 9px;
  font-size: 18px;
  color: $light-gray-blue;
  letter-spacing: 1px;
}
.margin-top-s {
  margin-top: 12px;
}
.header-settings {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  background-color: white;
  outline: 1px solid $soft-gray;
  border-radius: 6px;
  padding: 4px 6px;
  width: 80px;
  p {
    margin: 0;
    color: $base-gray;
    cursor: pointer;
  }
}
.forecast-overview {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 0px 12px;
  border: 1px solid $soft-gray;
  border-radius: 12px;
  width: 60vw;
  background-color: white;

  &__section {
    display: flex;
    flex-direction: column;
    margin-right: 32px;
    padding: 12px;

    div {
      display: flex;
      flex-direction: row;
      align-items: center;
    }

    p {
      font-size: 11px;
      color: $light-gray-blue;
      margin-top: -8px;
    }
    h3 {
      color: $base-gray;
    }
  }
}
</style>