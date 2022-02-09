<template>
  <div class="pipelines">
    <header v-if="!loading" class="flex-row-spread">
      <div>
        <h3 class="title">Hi, {{ user.fullName }}</h3>
        <h5 class="sub-heading">
          Update you pipeline faster. Changes auto sync to Salesforce instantly
        </h5>
      </div>

      <div>
        <!-- <button class="pipe-button">
          <img src="@/assets/images/refresh.png" style="height: 1rem" alt="" />
        </button> -->
      </div>
    </header>

    <section v-if="!loading" style="margin-top: -1rem" class="flex-row-spread">
      <div v-if="noSelection" class="flex-row">
        <!-- <DropDownSelect
          :items="opportunities"
          valueKey="key"
          displayKey="name"
          nullDisplay="Opportunities"
        /> -->

        <button class="pipe-button">
          <img
            class="invert"
            src="@/assets/images/list.png"
            style="height: 1rem; margin-right: 0.25rem"
            alt=""
          />All Opportunities
        </button>
        <button class="add-button">
          <img
            src="@/assets/images/plusOne.png"
            style="height: 1rem; margin-right: 0.25rem"
            alt=""
          />Filter
        </button>
        <h5 v-if="!loading">
          Results: <span class="resNum">{{ allOpps.length }}</span>
        </h5>
      </div>

      <div class="flex-row">
        <div class="search-bar">
          <input type="search" placeholder="search" />
          <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
        </div>

        <button class="add-button">
          <img src="@/assets/images/plusOne.png" style="height: 1rem" alt="" />
          Opportunity
        </button>
      </div>
    </section>

    <section v-if="!loading" class="table-section">
      <div class="table">
        <div class="table-row">
          <div class="table-cell-checkbox-header">
            <input style="padding-top: 0.5rem" type="checkbox" />
          </div>
          <div class="table-cell-header">Name</div>
          <div class="table-cell-header">Stage</div>
          <div class="table-cell-header">Forecast Category</div>
          <div class="table-cell-header">Amount</div>
          <div class="table-cell-header">Next Step</div>
          <div class="table-cell-header">Close Date</div>
          <div class="table-cell-header">Last Activity</div>
        </div>

        <tr class="table-row" :key="i" v-for="(opp, i) in allOpps">
          <div class="table-cell-checkbox">
            <input type="checkbox" />
          </div>
          <div class="table-cell cell-name">
            {{ opp.name }}
            <span style="color: #199e54; margin-left: 0.2rem">account name</span>
            <div style="color: #9b9b9b">owner: owner's name</div>
            <div style="margin-top: 0.5rem" class="flex-row">
              <img class="name-cell-edit-note-button" src="@/assets/images/white-note.png" />
              <img class="name-cell-note-button" src="@/assets/images/note.png" />
            </div>
          </div>

          <div class="table-cell">{{ opp.stage }}</div>
          <div class="table-cell">{{ opp.forecast_category }}</div>
          <div class="table-cell" style="color: #199e54">
            {{ formatCash(parseFloat(opp.amount)) }}
          </div>
          <div v-if="opp.secondary_data.NextStep" class="table-cell">
            {{ opp.secondary_data.NextStep }}
          </div>
          <div v-else>No next step found</div>
          <div class="table-cell">{{ formatDate(opp.close_date) }}</div>
          <div class="table-cell">{{ formatDateTime(opp.last_activity_date) }}</div>
        </tr>
      </div>
    </section>
    <div class="loader" v-if="loading">
      <img src="@/assets/images/loading-gif.gif" class="invert" style="height: 8rem" alt="" />
    </div>
  </div>
</template>

<script>
import DropDownSelect from '@thinknimble/dropdownselect'
import { SObjectField, SObjectValidation, SObjectPicklist, SObjects } from '@/services/salesforce'
import CollectionManager from '@/services/collectionManager'
import User from '@/services/users'

export default {
  name: 'Pipelines',
  components: {
    DropDownSelect,
  },
  data() {
    return {
      noSelection: true,
      opportunities: ['test'],
      allOpps: null,
      loading: false,
      team: CollectionManager.create({ ModelClass: User }),
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  created() {
    this.getObjects()
    this.team.refresh()
    console.log(this.team)
  },
  methods: {
    async getObjects() {
      this.loading = true
      try {
        const res = await SObjects.api.getObjects('Opportunity')
        this.allOpps = res.results
        console.log(this.allOpps)
      } catch {
        this.$Alert.alert({
          type: 'error',
          timeout: 2000,
          message: 'There was an error collecting objects',
        })
      }
      this.loading = false
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

      return cash.format(money)
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
}
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
  font-size: 14px;
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
  background-color: transparent;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
p {
  font-size: 13px;
}
header,
section {
  margin: 0;
  padding: 0px 10px;
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
  margin-top: 3rem;
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
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}
.pipe-button:hover {
  transform: scale(1.025);
  box-shadow: 1px 2px 2px $very-light-gray;
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
}
.add-button:hover {
  transform: scale(1.025);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.resNum {
  color: $dark-green;
  font-weight: bold;
}
.search-bar {
  height: 4.5vh;
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
.name-cell-note-button {
  height: 1.25rem;
  cursor: pointer;
  box-shadow: 1px 1px 1px 1px $very-light-gray;
  border: none;
  border-radius: 50%;
  padding: 0.2rem;
  margin-right: 0.25rem;
}
.name-cell-edit-note-button {
  height: 1.25rem;
  cursor: pointer;
  box-shadow: 1px 1px 1px 1px $very-light-gray;
  border: none;
  border-radius: 50%;
  padding: 0.2rem;
  margin-right: 0.25rem;
  background-color: $lighter-green;
}
.spacer {
  height: 5vh;
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