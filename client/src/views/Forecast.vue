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
          <h3>Forecast Settings</h3>
          <img class="invert" @click="resetSettings" src="@/assets/images/close.svg" alt="" />
        </header>
        <div class="modal-container__body">
          <p>Add Opportunites to Forecast:</p>
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
          <h3>Remove from Forecast</h3>
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
      <div v-if="notes.length" class="modal-container">
        <div class="row-spread">
          <div class="align-center">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3>Notes</h3>
          </div>

          <img
            src="@/assets/images/close.svg"
            style="height: 1.5rem; margin-top: -0.5rem; margin-right: 0.5rem; cursor: pointer"
            @click="resetNotes"
            alt=""
          />
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{ note.saved_data__meeting_type ? note.saved_data__meeting_type + ':' : 'Untitled:' }}
          </p>
          <pre class="note-section__body">{{ note.saved_data__meeting_comments }}</pre>
          <p class="note-section__date">{{ formatDateTime(note.submission_date) }}</p>
        </section>
      </div>
      <div v-else class="modal-container">
        <div class="row-spread">
          <div class="align-center">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3>Notes</h3>
          </div>
          <img
            src="@/assets/images/close.svg"
            style="height: 1.5rem; margin-top: -0.5rem; margin-right: 0.5rem; cursor: pointer"
            @click="resetNotes"
            alt=""
          />
        </div>
        <section class="note-section">
          <p class="note-section__title">No notes for this opportunity</p>
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
    <header class="forecast-header">
      <section class="row">
        <div>
          <button @click.stop="showList = !showList" class="select-btn1">
            {{ currentForecast }}
            <img
              v-if="!showList"
              style="height: 1rem; margin-left: 0.5rem"
              src="@/assets/images/rightArrow.svg"
              class="invert"
              alt=""
            />
            <img
              v-else
              class="invert"
              style="height: 1rem; margin-left: 0.5rem"
              src="@/assets/images/downArrow.svg"
              alt=""
            />
          </button>
          <div v-outside-click="closeListSelect" v-show="showList" class="list-section">
            <div class="list-section__title row-spread">
              <p>Active Trackers</p>
            </div>
            <button class="list-button">
              My Tracker
              <span class="green-text" v-if="currentForecast === 'My Tracker'"> active</span>
            </button>
          </div>
          <p class="gray-text smaller-font margin-left-s" v-if="forecastOpps && !loading">
            Total Opps in Forecast: {{ forecastLength }}
          </p>
          <p v-else></p>
        </div>

        <!-- <section class="relative">
          <button @click.stop="addingFilter" class="add-filter-button margin-left-s">
            <img
              src="@/assets/images/plusOne.png"
              style="height: 0.8rem; margin-right: 0.25rem"
              alt=""
            />Add filter
          </button>
          <div v-outside-click="closeFilters" v-if="filtering" class="list-section">
            <div class="list-section__title flex-row-spread">
              <p>Select Filter</p>
            </div>
            <button
              :key="i"
              v-for="(filter, i) in filters"
              @click="addFilter(filter.apiName, filter.name, filter.type)"
              class="list-button-2"
            >
              {{ filter.name }}
            </button>
          </div>
        </section>

        <div
          v-for="(filter, i) in activeFilters"
          :key="i"
          @mouseenter="hoveredIndex = filter"
          @mouseleave="hoveredIndex = null"
          class="main"
        >
          <strong class="medium-font">{{ filter }}</strong>
          <small class="margin-left-s">{{ activeOperators[i] }}</small>
          <small class="margin-left-s">{{ filterValues[i] }}</small>
          <span v-if="hoveredIndex === filter" class="selected-filters__close"
            ><img src="@/assets/images/close.png" @click="removeFilter(filter, i)" alt=""
          /></span>
        </div>

        <section class="row relative" v-if="filterSelected">
          <main class="main__before">
            <small
              ><strong>{{ currentFilter }}</strong></small
            >
            <small style="margin-left: 0.2rem">{{ currentOperator }}</small>
            <small style="margin-left: 0.2rem">{{ currentVal }}</small>
          </main>

          <div>
            <FilterSelection
              @filter-added="applyFilter"
              @operator-selected="addOperator"
              @value-selected="valueSelected"
              @close-selection="closeFilterSelection"
              :type="filterType"
              :filterName="currentFilter"
              :dropdowns="picklistQueryOpts"
              :apiName="filterApiName"
            />
          </div>
        </section> -->
      </section>
      <div class="row">
        <!-- <button class="forecast-header__green-button">
          <p class="green-text">%</p>
        </button> -->
        <button class="margin-left-s forecast-header__button" @click="resetSettings">
          <img src="@/assets/images/settings.svg" alt="" />
        </button>
      </div>
    </header>
    <section v-if="!loading" class="table-section">
      <div class="table">
        <div class="table-row">
          <div class="cell-name-header">Opportunity Name</div>
          <div :key="index" v-for="(header, index) in forecastHeaders" class="table-cell-header">
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
        <div v-else-if="forecastOpps" v-for="(opp, i) in forecastOpps" :key="i" class="table-row">
          <p class="no-display">{{ setOriginalAmount(opp.data.Amount) }}</p>
          <div class="table-cell cell-name row">
            <div class="row-spread">
              <div>
                <p>{{ opp.data.Name }}</p>
                <p class="green-text">
                  {{
                    currentValues[opp.data.Name].account_ref
                      ? currentValues[opp.data.Name].account_ref.name
                      : ''
                  }}
                </p>
                <p class="gray-text">
                  Owned by: {{ currentValues[opp.data.Name].owner_ref.full_name }}
                </p>
              </div>

              <div class="row">
                <button
                  @click="getNotes(currentValues[opp.data.Name].id)"
                  class="name-cell-edit-note-button"
                >
                  <img
                    class="invert-less"
                    src="@/assets/images/white-note.svg"
                    height="12px"
                    alt=""
                  />
                </button>

                <button
                  @click="
                    deleteOpen = true
                    setDeleteId(opp.data.Id)
                  "
                  class="name-cell-edit-note-button"
                >
                  <img class="invertTrash" src="@/assets/images/trash.svg" height="14px" alt="" />
                </button>
              </div>
            </div>
          </div>
          <div class="table-cell">
            <p class="green-text align-center letter-spacing">
              {{ opp.data.Amount ? formatCash(currentValues[opp.data.Name].amount) : '' }}
              <span v-if="currentValues[opp.data.Name].amount < opp.data.Amount"
                ><img
                  class="filter-red margin-left-s"
                  src="@/assets/images/trendingDown.svg"
                  alt=""
              /></span>
              <span v-else-if="currentValues[opp.data.Name].amount > opp.data.Amount"
                ><img
                  class="filter-green margin-left-s"
                  src="@/assets/images/trendingUp.svg"
                  alt=""
              /></span>
            </p>
            <p class="gray-text letter-spacing">
              {{ opp.data.Amount ? formatCash(opp.data.Amount) : '' }}
            </p>
          </div>
          <div class="table-cell">
            <p>{{ formatDateTime(opp.dateAdded.split(' ')[0]) }}</p>
          </div>
          <div class="table-cell">
            <p class="align-center">
              {{ currentValues[opp.data.Name].stage }}
              <span
                v-if="
                  stages.indexOf(currentValues[opp.data.Name].stage) <
                  stages.indexOf(opp.data.StageName)
                "
                ><img
                  class="filter-red margin-left-s"
                  src="@/assets/images/trendingDown.svg"
                  alt=""
              /></span>
              <span
                v-else-if="
                  stages.indexOf(currentValues[opp.data.Name].stage) >
                  stages.indexOf(opp.data.StageName)
                "
                ><img
                  class="filter-green margin-left-s"
                  src="@/assets/images/trendingUp.svg"
                  alt=""
              /></span>
            </p>
            <p class="gray-text">{{ opp.data.StageName }}</p>
          </div>
          <div class="table-cell">
            <p class="align-center">
              {{ currentValues[opp.data.Name].forecast_category }}
              <span
                v-if="
                  forecasts.indexOf(currentValues[opp.data.Name].forecast_category) <
                  forecasts.indexOf(opp.data.ForecastCategoryName)
                "
                ><img
                  class="filter-red margin-left-s"
                  src="@/assets/images/trendingDown.svg"
                  alt=""
              /></span>
              <span
                v-else-if="
                  forecasts.indexOf(currentValues[opp.data.Name].forecast_category) >
                  forecasts.indexOf(opp.data.ForecastCategoryName)
                "
                ><img
                  class="filter-green margin-left-s"
                  src="@/assets/images/trendingUp.svg"
                  alt=""
              /></span>
            </p>
            <p class="gray-text">
              {{ opp.data.ForecastCategoryName ? opp.data.ForecastCategoryName : '' }}
            </p>
          </div>
          <div class="table-cell">
            <p class="align-center">
              {{
                currentValues[opp.data.Name]
                  ? formatDate(currentValues[opp.data.Name].close_date)
                  : ''
              }}
              <span v-if="currentValues[opp.data.Name].close_date > opp.data.CloseDate"
                ><img
                  class="filter-red margin-left-s"
                  src="@/assets/images/trendingDown.svg"
                  alt=""
              /></span>
              <span v-else-if="currentValues[opp.data.Name].close_date < opp.data.CloseDate"
                ><img
                  class="filter-green margin-left-s"
                  src="@/assets/images/trendingUp.svg"
                  alt=""
              /></span>
            </p>
            <p class="gray-text">
              {{ opp.data.CloseDate ? formatDate(opp.data.CloseDate) : '' }}
            </p>
          </div>
          <div class="table-cell">
            <p>
              {{
                opp.data.LastActivityDate
                  ? formatDateTime(currentValues[opp.data.Name].last_activity_date)
                  : ''
              }}
            </p>
          </div>
        </div>
        <div class="table-row-sticky" v-if="forecastOpps">
          <div class="table-cell-s">
            <p class="letter-spacing">Total:</p>
          </div>
          <div class="table-cell-s">
            <p class="green-text align-center letter-spacing">
              {{ formatCash(totalAmount) }}
              <span v-if="totalAmount < originalAmount"
                ><img
                  class="filter-red margin-left-s"
                  src="@/assets/images/trendingDown.svg"
                  alt=""
              /></span>
              <span v-else-if="totalAmount > originalAmount"
                ><img
                  class="filter-green margin-left-s"
                  src="@/assets/images/trendingUp.svg"
                  alt=""
              /></span>
            </p>
            <p class="gray-text letter-spacing">{{ formatCash(originalAmount) }}</p>
          </div>
          <div class="table-cell-s"><p class="letter-spacing">Avg Deal Size:</p></div>
          <div class="table-cell-s">
            <p class="letter-spacing">{{ formatCash(averageDeal) }}</p>
          </div>
          <div class="table-cell-s"></div>
          <div class="table-cell-s"></div>
          <div class="table-cell-s"></div>
        </div>
      </div>
    </section>
    <div v-if="loading">
      <PipelineLoader />
    </div>
  </div>
</template>

<script>
import { SObjects, SObjectPicklist } from '@/services/salesforce'
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
      currentValues: {},
      addedOpportunities: [],
      activeOperators: [],
      addedFilters: [],
      filterValues: [],
      deleteIds: [],
      notes: [],
      activeFilters: [],
      filterNames: [],
    }
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    FilterSelection: () => import(/* webpackPrefetch: true */ '@/components/FilterSelection'),
  },
  watch: {
    allOpps: ['setCurrentValues', 'getStagesAndForecast'],
  },
  async created() {
    this.getOpportunites()
  },
  beforeMount() {
    this.setPicklist()
  },
  mounted() {
    console.log(this.forecastOpps)
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
          }
        }
      } catch (e) {
        console.log(e)
      }
    },
    setDeleteId(id) {
      this.deleteIds = []
      this.deleteIds.push(id)
      console.log(this.deleteIds)
    },
    async removeForecast() {
      try {
        await User.api.modifyForecast('remove', this.deleteIds)
        this.$Alert.alert({
          type: 'success',
          timeout: 1500,
          message: 'Opportunity removed. Refresh to see changes.',
        })
      } catch (e) {
        this.$Alert.alert({
          type: 'error',
          timeout: 1500,
          message: 'Error Removing Opportunity',
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
        this.$Alert.alert({
          type: 'success',
          timeout: 1500,
          message: 'Opportunity added to forecast.',
        })
      } catch (e) {
        this.$Alert.alert({
          type: 'error',
          timeout: 1500,
          message: 'Error adding Opportunities',
        })
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.resetSettings()
      }
    },
    async getOpportunites() {
      try {
        let res = await SObjects.api.getObjects('Opportunity')
        this.allOpps = res.results
        // console.log(this.allOpps)
      } catch (e) {
        this.$Alert.alert({
          type: 'error',
          timeout: 1500,
          message: 'Error gathering your Opportunities',
        })
      }
    },
    setCurrentValues() {
      this.loading = true
      if (this.forecastOpps) {
        let forecast = []
        for (let i in this.forecastOpps) {
          forecast.push(i)
        }
        let newOpps = this.allOpps.filter((opp) => forecast.includes(opp.integration_id))
        for (let i = 0; i < newOpps.length; i++) {
          this.currentValues[newOpps[i].name] = newOpps[i]
          this.totalAmount += parseInt(newOpps[i].amount) ? parseInt(newOpps[i].amount) : 0
        }
        this.forecastLength = forecast.length
        this.averageDeal = this.totalAmount / this.forecastLength
        this.loading = false
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
        let res = await SObjectPicklist.api.listPicklists({
          picklistFor: 'StageName',
          salesforceObject: 'Opportunity',
        })
        let res2 = await SObjectPicklist.api.listPicklists({
          picklistFor: 'ForecastCategoryName',
          salesforceObject: 'Opportunity',
        })
        this.stages = res.length ? res[0]['values'] : []
        this.stages ? (this.stages = this.stages.map((stage) => stage.value)) : []
        this.forecasts = res2.length ? res2[0]['values'] : []
        this.forecasts ? (this.forecasts = this.forecasts.map((forecast) => forecast.value)) : []
      } catch (e) {
        this.$Alert.alert({
          type: 'error',
          timeout: 1500,
          message: 'Error gathering your stages',
        })
      } finally {
        this.loading = false
      }
    },
    async listPicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.picklistQueryOpts[type] = res.length ? res[0]['values'] : []
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
      console.log(this.activeFilters)
    },
    valueSelected(value) {
      this.currentVal = value
    },
    addOperator(val) {
      this.currentOperator = val
    },
    removeFilter(name, index) {
      console.log(index)
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

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
.align-center {
  display: flex;
  align-items: center;
}
.forecast {
  margin-top: 3.5rem;
}
.letter-spacing {
  letter-spacing: 1px;
}
.relative {
  position: relative;
}
.filter-green {
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.filter-red {
  filter: invert(48%) sepia(76%) saturate(3436%) hue-rotate(326deg) brightness(113%) contrast(96%);
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
  min-height: 50vh;
  height: 78vh;
  overflow: scroll;
  margin-top: -0.5rem;
  border-radius: 5px;
  border: 1.25px solid $soft-gray;
  border-bottom: 3px solid $soft-gray;
  background-color: white;
}
.table {
  display: table;
  overflow: scroll;
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
  outline: 2px solid #e8e8e8;
  //   background-color: white;
}
.table-cell {
  display: table-cell;
  position: sticky;
  min-width: 12vw;
  background-color: $off-white;
  padding: 1vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
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
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
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
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
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
  padding: 0.5rem 0.25rem;
  margin-bottom: -0.5rem;
  position: relative;
  z-index: 4;

  &__button {
    background-color: white;
    border: 1.25px solid $soft-gray;
    height: 2rem;
    width: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 3px;
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
    // filter: invert(70%);
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
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
}
.modal-container {
  background-color: $white;
  overflow: auto;
  width: 34vw;
  min-height: 48vh;
  align-items: center;
  border-radius: 0.3rem;
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
  border: 1px solid #e8e8e8;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between !important;
  border-radius: 0.25rem;
  background-color: white;
  cursor: pointer;
  color: $dark-green;
  letter-spacing: 0.2px;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%) !important;
  }
}
.list-section {
  z-index: 4;
  position: absolute;
  top: 3rem;
  left: 0.5rem;
  border-radius: 0.25rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 20vw;
  max-height: 70vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 2px 2px $very-light-gray;
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
  border-radius: 0.25rem;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
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
  padding: 0.5rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 16px;
    font-weight: bolder;
    color: $dark-green;
    letter-spacing: 1.2px;
  }
  &__body {
    color: $base-gray;
    font-family: $base-font-family;
    word-wrap: break-word;
    white-space: pre-wrap;
  }
  &__date {
    color: $mid-gray;
    font-size: 11px;
  }
}
</style>