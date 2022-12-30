<template>
  <div class="reports">
    <!-- <div class="alerts-header">
      <div class="results-title">
        <p v-if="!generating">
          <span>{{ user.organizationRef.name + ' ' + reportType + ' Reports' }}</span>
        </p>
        <p @click="generateReport" v-else style="color: #4d4e4c" class="left-margin-s centered">
          <img
            style="margin-right: 4px; filter: invert(30%)"
            src="@/assets/images/left.svg"
            height="13px"
            alt=""
          />
          Change Report
        </p>
      </div>

      <p v-if="generating" class="light-gray-text">{{ reportMode }}</p>

      <div class="flex-row">
        <span :class="!generating ? 'invert' : ''"
          ><img src="@/assets/images/shared.svg" height="12px" style="margin-right: 8px" alt="" />
          Share Report</span
        >
      </div>
    </div> -->

    <div v-if="!generating" class="container">
      <div class="space-between">
        <h2>Generate Report</h2>
      </div>

      <div style="margin-top: 32px; margin-bottom: 32px">
        <p>Select a Sales rep</p>
        <Multiselect
          id="user"
          placeholder="Reps"
          style="width: 94%"
          :options="reps.list"
          openDirection="below"
          :multiple="false"
          track-by="id"
          v-model="selectedUser"
          :custom-label="fullOrEmailLabel"
        >
          <template slot="noResult">
            <p class="multi-slot">No results.</p>
          </template>
        </Multiselect>
      </div>

      <div>
        <p>Select a Opportunity</p>

        <Multiselect
          id="opp"
          placeholder="Opportunities"
          style="width: 94%"
          :options="allOpps"
          openDirection="below"
          :multiple="false"
          v-model="selectedOpp"
          label="name"
        >
          <template slot="noResult">
            <p class="multi-slot">No results.</p>
          </template>
        </Multiselect>
      </div>

      <div class="bottom-right margin-right">
        <button
          :disabled="!(selectedOpp && selectedUser)"
          @click="generateReport"
          class="green_button"
        >
          Generate
        </button>
      </div>
    </div>

    <div v-else-if="generating && reportMode == 'Timeline'">
      <div class="container3">
        <div class="top space-between">
          <h2 style="margin-top: 0; font-size: 20px">{{ selectedOpp.name }}</h2>
          <!-- <button @click="reportMode = 'Visualize'" class="pink_button">Dashboard</button> -->
        </div>
        <TimeLine />
        <div style="margin-top: 1rem" class="bottom"></div>
      </div>

      <div class="container2">
        <div class="top">
          <sub class="gray-section">Insights</sub>
        </div>

        <p class="row light-gray-text">
          <img class="gold-filter" src="@/assets/images/star.svg" height="22px" alt="" />
          Deal closed <span class="inline-text"> faster than usual (92 days)</span>
          <img
            class="green-filter"
            src="@/assets/images/trendingUp.svg"
            style="margin-left: 4px"
            height="22px"
            alt=""
          />
        </p>
        <p class="row light-gray-text">
          <img class="gold-filter" src="@/assets/images/star.svg" height="22px" alt="" />
          For a <span class="inline-text"> higher amount </span> than usual (29k)
          <img
            class="green-filter"
            src="@/assets/images/trendingUp.svg"
            style="margin-left: 4px"
            height="22px"
            alt=""
          />
        </p>
        <p class="row light-gray-text">
          <img class="gold-filter" src="@/assets/images/star.svg" height="22px" alt="" />
          {{ selectedUser.firstName }} has a <span class="inline-text"> 83%</span> success rate when
          logging 5 or more meetings via Managr
        </p>
        <div style="margin-top: 1rem" class="bottom">
          <button @click="reportMode = 'Visualize'" class="pink_button">
            Overview
            <img
              style="filter: invert(100%); margin-left: 4px"
              src="@/assets/images/picture.svg"
              height="13px"
              alt=""
            />
          </button>
        </div>
      </div>
    </div>

    <div class="container4" v-else-if="generating && reportMode == 'Visualize'">
      <div class="space-between">
        <div class="row medText">
          <img src="@/assets/images/logo.png" height="24px" alt="" />
          Story Report
        </div>
        <sub class="gray-section">Sep 15, 2022 - Dec 17, 2022</sub>
      </div>

      <div class="space-between">
        <div style="margin-top: 2rem">
          <h2 style="margin-bottom: 0; font-size: 22px">{{ selectedOpp.name }}</h2>
          <p style="margin-top: 8px" class="light-gray-text">
            Closed by {{ selectedUser.fullName }}
          </p>
        </div>

        <div style="margin-top: 2rem" class="column">
          <small class="row">
            <img class="green-filter" src="@/assets/images/correct.svg" height="14px" alt="" />
            Dec 17, 2022 {{ selectedUser.firstName }} closed this deal for
            <span style="color: #41b883" class="inline-text">$29,000</span>
          </small>

          <small class="row">
            <img class="green-filter" src="@/assets/images/correct.svg" height="14px" alt="" />
            It took
            <span class="inline-text">92</span> days to close this deal
          </small>

          <small class="row">
            <img class="green-filter" src="@/assets/images/correct.svg" height="14px" alt="" />
            <span>
              This deal was updated
              <span class="inline-text">18</span> times. "Stage" was updated the most (6)
            </span>
          </small>
        </div>
      </div>

      <div class="even-row margin-top">
        <div class="card">
          <img src="@/assets/images/calendar.svg" height="24px" alt="" />
          <h1 class="green-text" style="margin: 12px 0">5</h1>
          <p>Meetings</p>
          <meter id="file" value="85" max="100"></meter>
          <p class="small-text">Avg: 7</p>
        </div>

        <div class="card">
          <img src="@/assets/images/check.svg" height="24px" alt="" />
          <h1 class="green-text" style="margin: 12px 0">25</h1>
          <p>Updates</p>
          <meter id="file" value="88" max="100"></meter>
          <p class="small-text">Avg: 30</p>
        </div>

        <div class="card">
          <img src="@/assets/images/doubleCheck.svg" height="24px" alt="" />
          <h1 class="green-text" style="margin: 12px 0">12</h1>
          <p>Fields Updated</p>
          <meter id="file" value="12" max="19"></meter>
          <p class="small-text">Avg: 19</p>
        </div>
      </div>

      <div class="even-row">
        <div class="card">
          <img src="@/assets/images/trendingUp.svg" height="28px" alt="" />
          <h1 class="green-text" style="margin: 12px 0">10</h1>
          <p>Days per Stage</p>
          <meter id="file" value="80" max="100"></meter>
          <p class="small-text">Avg: 12</p>
        </div>

        <div class="wide-card">
          <div style="margin-right: 4rem">
            <Chart />
          </div>

          <div>
            <img src="@/assets/images/cycle.svg" height="20px" alt="" />
            <h1 class="green-text" style="margin: 12px 0">60</h1>
            <p>Days in sales cycle</p>
            <small>Avg: 80</small>
          </div>
        </div>
      </div>

      <div style="margin-top: 1rem" class="bottom">
        <button @click="reportMode = 'Timeline'" class="pink_button">
          Timeline
          <img
            style="filter: invert(100%); margin-left: 4px"
            src="@/assets/images/route.svg"
            height="13px"
            alt=""
          />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import User from '@/services/users'
import TimeLine from '@/components/Timeline'
import Chart from '@/components/Chart'

export default {
  name: 'Reports',
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    ToggleCheckBox,
    TimeLine,
    Chart,
  },
  data() {
    return {
      reps: CollectionManager.create({ ModelClass: User }),
      selectedOpp: null,
      selectedUser: null,
      reportType: 'Story',
      reportMode: 'Visualize',
      generating: false,
    }
  },
  async created() {
    this.reps.refresh()
  },
  methods: {
    fullOrEmailLabel(props) {
      if (!props.fullName.trim()) {
        return props.email
      }
      return props.fullName
    },
    generateReport() {
      this.generating = !this.generating
    },
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
    allOpps() {
      return this.$store.state.allOpps
    },
    isAdmin() {
      return this.userIsLoggedIn && this.$store.state.user.isAdmin
    },
    user() {
      return this.$store.state.user
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.reports {
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-left: 80px;

  letter-spacing: 0.75px;
}

.space-between {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
}

.alerts-header {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 72px;
  background-color: white;
  width: 96vw;
  border-bottom: 1px solid $soft-gray;
  padding: 8px 32px 0px 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $light-gray-blue;
  }
}

.results-title {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  margin-left: 4px;

  p {
    font-size: 16px;
    margin-left: 2px;
    color: $base-gray;
    span {
      // background-color: $white-green;
      color: $light-gray-blue;
      border-radius: 6px;
      padding: 2px;
      margin-left: 4px;
      font-size: 14px;
    }
  }
}

.even-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 16px;
  justify-content: space-between;
}

.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-top: 8px;
  padding-bottom: 0;
}

.small-text {
  font-size: 10px;
}

.flex-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
}

.margin-top {
  margin-top: 3rem;
}

.margin-right {
  margin-right: 6%;
}

.green_button {
  color: white;
  background-color: $dark-green;
  max-height: 2rem;
  border-radius: 0.25rem;
  padding: 0.5rem 1.25rem;
  font-size: 13px;
  letter-spacing: 0.75px;
  border: none;
  cursor: pointer;
}

.pink_button {
  color: white;
  background-color: $grape;
  max-height: 2rem;
  border-radius: 0.25rem;
  padding: 6px 10px;
  font-size: 13px;
  letter-spacing: 0.75px;
  border: none;
  cursor: pointer;
  box-shadow: 1px 3px 3px;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.container {
  min-height: 64vh;
  padding: 16px 32px 0 32px;
  width: 40vw;
  outline: 1px solid $soft-gray;
  border-radius: 8px;
  background-color: white;
  margin-top: 1rem;
}

.container2 {
  height: 32vh;
  overflow-y: scroll;
  padding: 0px 32px 0px 32px;
  width: 54vw;
  outline: 1px solid $soft-gray;
  border-radius: 8px;
  background-color: white;
  margin-top: 0.5rem;
}

.container3 {
  height: 62vh;
  overflow-y: scroll;
  padding: 0px 32px 0px 32px;
  width: 54vw;
  outline: 1px solid $soft-gray;
  border-radius: 8px;
  background-color: white;
  margin-top: 0.5rem;
  //   border-top: 2px solid $dark-green;
}

.container4 {
  height: 98vh;
  overflow-y: scroll;
  padding: 24px 32px 0px 32px;
  width: 56vw;
  margin-top: 0.5rem;
  outline: 1px solid $soft-gray;
  border-radius: 8px;
  background-color: white;
  //   border-top: 3px solid $dark-green;
}

.invert {
  color: $light-gray-blue;

  img {
    filter: invert(50%);
  }
}

.medText {
  font-size: 18px;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;

  img {
    margin-right: 4px;
  }
}

.row_ {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

.light-gray-text {
  color: $light-gray-blue;
  letter-spacing: 0.75px;
}

:disabled {
  background-color: $soft-gray;
  color: $light-gray-blue;
}

#canClick {
  cursor: pointer;
}

.gray-section {
  letter-spacing: 0.75px;
  color: $light-gray-blue;
  background-color: $soft-gray;
  padding: 6px 8px;
  border-radius: 4px;
}

.shimmer {
  display: inline-block;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  max-width: 200px;
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.green-filter {
  margin-right: 8px !important;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}

.filter-green {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background-color: $white-green;
  padding: 2px 3px;
  font-weight: bold;
  margin-left: 8px;
  small {
    color: $dark-green;
    margin-right: 4px;
  }
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

.green-text {
  color: $dark-green;
}

.yellow-text {
  color: $yellow;
}

.blue-text {
  color: $panther-blue;
}

.card {
  border-radius: 5px;
  border: 1px solid $soft-gray;
  width: 16vw;
}
.wide-card {
  border-radius: 5px;
  border: 1px solid $soft-gray;
  width: 34vw;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 26px 0;
}

.section {
  border-bottom: 1px solid $soft-gray;
}

.bottom {
  display: flex;
  flex-direction: row;
  justify-content: center;
  position: sticky;
  bottom: 0;
  background-color: white;
  padding: 6px 2px;
  letter-spacing: 0.75px;
}

.top {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 3;
  padding: 12px 0;
}

.bottom-right {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: flex-end;
  height: 100px;
  bottom: 0;
  background-color: white;
  padding: 6px 2px;
  letter-spacing: 0.75px;
}

.column {
  display: flex;
  flex-direction: column;
  align-items: space-between;

  small {
    margin-top: 8px;
  }
}

.inline-text {
  font-weight: 900;
  font-size: 15px;
  margin: 0 2px;
  color: $base-gray;
}

p {
  font-size: 14px;
}

.gold-filter {
  filter: invert(81%) sepia(35%) saturate(920%) hue-rotate(343deg) brightness(91%) contrast(90%);
}
</style>
