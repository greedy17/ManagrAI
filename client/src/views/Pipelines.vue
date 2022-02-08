<template>
  <div class="pipelines">
    <header class="flex-row-spread">
      <div>
        <h2>Hey, {{ user.fullName }}</h2>
        <h5 class="sub-heading">
          This is where you can manage your pipeline. All updates will auto sync back to Salesforce
        </h5>
      </div>

      <div>
        <button class="pipe-button">
          <img src="@/assets/images/refresh.png" class="invert" style="height: 1rem" alt="" />
        </button>
      </div>
    </header>

    <section style="margin-top: -0.5rem" class="flex-row-spread">
      <div v-if="noSelection" class="flex-row">
        <DropDownSelect
          :items="opportunities"
          valueKey="key"
          displayKey="name"
          nullDisplay="Opportunities"
        />

        <button class="pipe-button">
          <img
            src="@/assets/images/list.png"
            style="height: 1rem; margin-right: 0.25rem"
            alt=""
          />select a list
        </button>
        <button class="add-button">
          <img
            src="@/assets/images/plusOne.png"
            style="height: 1rem; margin-right: 0.25rem"
            alt=""
          />filter
        </button>
        <h6>Results: <span class="resNum">5</span></h6>
      </div>

      <div class="flex-row">
        <div class="search-bar">
          <input type="search" placeholder="search" />
          <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
        </div>

        <button class="add-button">
          <img src="@/assets/images/plusOne.png" style="height: 1rem" alt="" />
        </button>
      </div>
    </section>

    <section>
      <table>
        <tr>
          <td>Name</td>
          <td>Stage</td>
          <td>Forecast Category</td>
          <td>Amount</td>
          <td>Close Date</td>
          <td>Last Activity</td>
        </tr>

        <tr :key="i" v-for="(opp, i) in allOpps">
          <td>{{ opp.name }}</td>
          <td>{{ opp.stage }}</td>
          <td>{{ opp.forecast_category }}</td>
          <td>{{ opp.amount }}</td>
          <td>{{ opp.close_date }}</td>
          <td>{{ opp.last_activity_date }}</td>
        </tr>
      </table>
    </section>
  </div>
</template>

<script>
import DropDownSelect from '@thinknimble/dropdownselect'
import { SObjectField, SObjectValidation, SObjectPicklist, SObjects } from '@/services/salesforce'
import axios from 'axios'

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
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  created() {
    this.getObjects()
  },
  mounted() {
    //   axios
    //     .get('http://d5w00000525speaa.my.salesforce.com/services/data/v54.0/sobjects/Opportunity')
    //     .then((response) => console.log(response))
  },
  methods: {
    async getObjects() {
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
  top: 12px;
  right: 1em;
  width: 0;
  height: 0;
  border: 5px solid transparent;
  border-color: $base-gray transparent transparent transparent;
}
::v-deep .tn-dropdown__selection-container {
  width: 12vw;
  height: 4vh;
  border: none;
  box-shadow: 1px 2px 3px $very-light-gray;
  padding: 0.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
::v-deep .tn-dropdown--medium {
  display: flex;
  justify-content: center;
  width: 12vw;
  height: 4vh;
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
  color: $mid-gray;
  margin-top: -2vh;
}
.pipe-button {
  display: flex;
  align-items: center;
  box-shadow: 1px 2px 3px $very-light-gray;
  border: none;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.5rem;
  border-radius: 0.2rem;
  background-color: transparent;
  color: $base-gray;
  cursor: pointer;
}
.add-button {
  display: flex;
  align-items: center;
  border: none;
  box-shadow: 1px 2px 3px $very-light-gray;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.5rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
}
.resNum {
  color: black;
  font-weight: bold;
}
.search-bar {
  height: 4vh;
  box-shadow: 1px 2px 3px $very-light-gray;
  border: none;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 5px;
  margin-right: 0.5rem;
}
</style>