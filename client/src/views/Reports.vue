<template>
  <div class="reports">
    <div class="alerts-header">
      <div v-if="isPaid" class="results-title">
        <p
          @click="selectPerformanceReport"
          :class="reportType == 'Story' ? '' : 'light-green-section'"
        >
          Performance Reports
        </p>

        <p
          style="margin-left: 16px"
          @click="selectStoryReport"
          :class="reportType == 'Performance' ? '' : 'light-green-section'"
        >
          Story Reports
        </p>
        <!-- <p
          style="margin-left: 16px; cursor: text"
          :class="reportType == 'Performance' ? '' : 'light-green-section'"
        >
          Story Reports <span class="purple-section">Coming Soon</span>
        </p> -->
      </div>

      <div class="results-title" v-else>
        <p class="light-gray-text row">
          Performance Reports
          <img
            class="shimmer"
            style="filter: invert(40%); margin-left: 4px"
            src="@/assets/images/lock.svg"
            height="14px"
            alt=""
          />
        </p>

        <p style="margin-left: 18px" class="light-gray-text row">
          Story Reports
          <img
            class="shimmer"
            style="filter: invert(40%); margin-left: 4px"
            src="@/assets/images/lock.svg"
            height="14px"
            alt=""
          />
        </p>
      </div>

      <!-- <div style="padding: 4px" class="flex-row">
        <span
          ><img src="@/assets/images/shared.svg" height="12px" style="margin-right: 8px" alt="" />
          Share Report</span
        >
      </div> -->
    </div>

    <div v-if="reportType == 'Story'">
      <div v-if="!generating" class="container">
        <div class="space-between">
          <h2>Generate Story Report</h2>
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
            {{ selectedUser.firstName }} has a <span class="inline-text"> 83%</span> success rate
            when logging 5 or more meetings via Managr
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

    <div v-else>
      <div v-if="!performanceReport && isPaid" class="container-small">
        <div class="space-between">
          <h2>Generate Performance Report</h2>
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
            :disabled="!isPaid"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
        </div>

        <div class="bottom-right margin-right">
          <button
            :disabled="!selectedUser"
            @click="getPerformanceReport(selectedUser.id)"
            class="green_button"
          >
            Generate
          </button>
        </div>
      </div>

      <div class="container4" v-else-if="performanceReport && isPaid">
        <div class="space-between">
          <div class="row medText">
            <img src="@/assets/images/logo.png" height="24px" alt="" />
            Performance Report
          </div>
          <sub class="gray-section">{{ allOpps.length }} Open Opportunities</sub>
        </div>

        <div class="space-between">
          <div style="margin-left: 0.5rem">
            <h2 style="margin-bottom: 0; font-size: 26px">January 2023</h2>
            <p style="margin-top: 8px" class="light-gray-text">
              {{ selectedUser.userLevel[0] + selectedUser.userLevel.toLowerCase().slice(1) }}:
              {{ selectedUser.fullName }}
            </p>
          </div>

          <div class="column margin-top-small">
            <small class="row">
              <img class="green-filter" src="@/assets/images/correct.svg" height="14px" alt="" />
              {{ workflows.list.length }} Active workflows
            </small>
            <small class="row">
              <img class="green-filter" src="@/assets/images/correct.svg" height="14px" alt="" />
              {{ notes.length }} Note templates
            </small>
          </div>
        </div>

        <div class="even-row">
          <div class="card">
            <img src="@/assets/images/session.svg" height="24px" alt="" />
            <h1 class="green-text" style="margin: 12px 0">
              {{ performanceReport['total sessions'] }}

              <img
                v-if="
                  performanceReport['total sessions'] >=
                  performanceReport['total sessions'] / totalMonths
                "
                src="@/assets/images/trendingUp.svg"
                class="green-filter"
                height="18"
                alt=""
              />
              <img
                v-else
                src="@/assets/images/trendingDown.svg"
                class="red-filter"
                height="18"
                alt=""
              />
            </h1>
            <p>Sessions</p>
            <div class="relative">
              <meter
                id="file"
                :value="performanceReport['total sessions']"
                :max="(performanceReport['total sessions'] / totalMonths) * 2"
              ></meter>
              <span class="center-line">|</span>
            </div>

            <p class="small-text">Avg: {{ performanceReport['total sessions'] / totalMonths }}</p>
          </div>

          <div class="card">
            <img src="@/assets/images/check.svg" height="24px" alt="" />
            <h1 class="green-text" style="margin: 12px 0">
              {{ performanceReport['updates'] }}
              <img
                v-if="performanceReport['updates'] >= performanceReport['updates'] / totalMonths"
                src="@/assets/images/trendingUp.svg"
                class="green-filter"
                height="18"
                alt=""
              />
              <img
                v-else
                src="@/assets/images/trendingDown.svg"
                class="red-filter"
                height="18"
                alt=""
              />
            </h1>
            <p>Total Updates</p>
            <div class="relative">
              <meter
                id="file"
                :value="performanceReport['updates']"
                :max="(performanceReport['updates'] / totalMonths) * 2"
              ></meter>
              <span class="center-line">|</span>
            </div>

            <p class="small-text">Avg: {{ performanceReport['updates'] / totalMonths }}</p>
          </div>

          <div class="card">
            <img src="@/assets/images/doubleCheck.svg" height="24px" alt="" />
            <h1 class="green-text" style="margin: 12px 0">
              {{ Object.keys(performanceReport['fields']).length }}
              <img
                v-if="
                  Object.keys(performanceReport['fields']).length >=
                  Object.keys(performanceReport['fields']).length / totalMonths
                "
                src="@/assets/images/trendingUp.svg"
                class="green-filter"
                height="18"
                alt=""
              />
              <img
                v-else
                src="@/assets/images/trendingDown.svg"
                class="red-filter"
                height="18"
                alt=""
              />
            </h1>
            <p>Fields Updated</p>
            <div class="relative">
              <meter
                id="file"
                :value="Object.keys(performanceReport['fields']).length"
                :max="(Object.keys(performanceReport['fields']).length / totalMonths) * 2"
              ></meter>
              <span class="center-line">|</span>
            </div>

            <p class="small-text">
              Avg: {{ Object.keys(performanceReport['fields']).length / totalMonths }}
            </p>
          </div>
        </div>

        <div class="even-row">
          <div class="card">
            <img src="@/assets/images/calendar.svg" height="22px" alt="" />
            <h1 class="green-text" style="margin: 12px 0">
              {{ performanceReport['meetings'] }}
              <img
                v-if="performanceReport['meetings'] >= performanceReport['meetings'] / totalMonths"
                src="@/assets/images/trendingUp.svg"
                class="green-filter"
                height="18"
                alt=""
              />
              <img
                v-else
                src="@/assets/images/trendingDown.svg"
                class="red-filter"
                height="18"
                alt=""
              />
            </h1>
            <p>Meetings Logged</p>

            <div class="relative">
              <meter
                id="file"
                :value="performanceReport['meetings']"
                :max="(performanceReport['meetings'] / totalMonths) * 2"
              ></meter>
              <span class="center-line">|</span>
            </div>

            <p class="small-text">Avg: {{ performanceReport['meetings'] / totalMonths }}</p>
          </div>

          <div class="card">
            <img src="@/assets/images/group.svg" height="24px" alt="" />
            <h1 class="green-text" style="margin: 12px 0">
              {{ performanceReport['contacts'] }}
              <img
                v-if="performanceReport['contacts'] >= performanceReport['contacts'] / totalMonths"
                src="@/assets/images/trendingUp.svg"
                class="green-filter"
                height="18"
                alt=""
              />
              <img
                v-else
                src="@/assets/images/trendingDown.svg"
                class="red-filter"
                height="18"
                alt=""
              />
            </h1>
            <p>Contacts Created</p>

            <div class="relative">
              <meter
                id="file"
                :value="performanceReport['contacts']"
                :max="(performanceReport['contacts'] / totalMonths) * 2"
              ></meter>
              <span class="center-line">|</span>
            </div>

            <p class="small-text">Avg: {{ performanceReport['contacts'] / totalMonths }}</p>
          </div>

          <div class="card">
            <img src="@/assets/images/note.svg" height="20px" alt="" />
            <h1 class="green-text" style="margin: 12px 0">
              {{
                performanceReport['fields']['meeting_comments']
                  ? performanceReport['fields']['meeting_comments']
                  : 0
              }}
              <img
                v-if="
                  (performanceReport['fields']['meeting_comments']
                    ? performanceReport['fields']['meeting_comments']
                    : 0) >=
                  (performanceReport['fields']['meeting_comments']
                    ? performanceReport['fields']['meeting_comments']
                    : 0 / totalMonths)
                "
                src="@/assets/images/trendingUp.svg"
                class="green-filter"
                height="18"
                alt=""
              />

              <img
                v-else
                src="@/assets/images/trendingDown.svg"
                class="red-filter"
                height="18"
                alt=""
              />
            </h1>
            <p>Notes Added</p>

            <div class="relative">
              <meter
                id="file"
                :value="
                  performanceReport['fields']['meeting_comments']
                    ? performanceReport['fields']['meeting_comments']
                    : 0
                "
                :max="
                  performanceReport['fields']['meeting_comments']
                    ? performanceReport['fields']['meeting_comments'] * 2
                    : 0 / totalMonths
                "
              ></meter>
              <span class="center-line">|</span>
            </div>

            <p class="small-text">
              Avg:
              {{
                performanceReport['fields']['meeting_comments']
                  ? performanceReport['fields']['meeting_comments']
                  : 0 / totalMonths
              }}
            </p>
          </div>
        </div>

        <div class="even-row">
          <div class="big-card">
            <p>Most Updated Fields</p>

            <div class="column">
              <div v-for="(field, i) in sortedUpdates" :key="i" class="space-between">
                <small v-if="i < 10">{{ fieldLabels[sortedUpdates[i][0]] }}</small>
                <section v-if="i < 10">
                  <meter id="file" :value="sortedUpdates[i][1]" :max="sortedUpdates[0][1]"></meter>
                  <small>{{ sortedUpdates[i][1] }}</small>
                </section>
              </div>

              <!-- <div class="space-between">
                <small>{{ sortedUpdates[0][0] }}</small>
                <section>
                  <meter id="file" value="50" max="50"></meter>
                  <small>{{ sortedUpdates[0][1] }}</small>
                </section>
              </div>

              <div class="space-between">
                <small>Next Step Date</small>
                <section>
                  <meter id="file" value="40" max="50"></meter>
                  <small>40</small>
                </section>
              </div>

              <div class="space-between">
                <small>Close Date</small>
                <section>
                  <meter id="file" value="35" max="50"></meter>
                  <small>35</small>
                </section>
              </div>

              <div class="space-between">
                <small>Amount</small>
                <section>
                  <meter id="file" value="10" max="50"></meter>
                  <small>10</small>
                </section>
              </div>

              <div class="space-between">
                <small>Metrics</small>
                <section>
                  <meter id="file" value="10" max="50"></meter>
                  <small>10</small>
                </section>
              </div> -->
            </div>
          </div>
        </div>

        <div style="margin-top: 1rem" class="bottom">
          <!-- <button @click="reportMode = 'Timeline'" class="pink_button">View Team Report</button> -->
        </div>
      </div>

      <div class="even-row" v-else>
        <div style="margin-right: 5vw" class="preview">
          <img src="@/assets/images/performance-prev.png" height="100%" width="100%" alt="" />
          <h3 style="margin-left: 8px">Performance Report</h3>
          <p class="preview-text">An automated report detailing how users work.</p>
          <p class="preview-text grape">*Requires Team Plan.</p>
        </div>
        <div class="preview">
          <img src="@/assets/images/story-prev.png" height="100%" width="100%" alt="" />
          <h3 style="margin-left: 8px; margin-top: 36px">Story Report</h3>
          <p class="preview-text">
            A contenxtualized "Story" report highlighting the deal journey.
          </p>
          <p class="preview-text grape">*Requires Team Plan.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import AlertTemplate from '@/services/alerts/'
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
      reportType: 'Performance',
      reportMode: 'Visualize',
      generating: false,
      performanceReport: null,
      sortedUpdates: [],
      totalMonths: null,
      fieldLabels: null,
      workflows: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
    }
  },
  watch: {
    performanceReport: 'getMostUpdated',
  },
  async created() {
    this.reps.refresh()
    this.workflows.refresh()
  },
  methods: {
    greaterVal(a, b) {
      if (a >= b) {
        return true
      } else {
        return false
      }
    },
    fullOrEmailLabel(props) {
      if (!props.fullName.trim()) {
        return props.email
      }
      return props.fullName
    },
    generateReport() {
      this.generating = !this.generating
    },
    async getPerformanceReport(id) {
      let today = new Date()
      let month = today.getMonth() + 1
      try {
        const res = await User.api.getPerformanceReport(id)
        console.log(res[month])
        this.fieldLabels = res[month].field_labels
        this.totalMonths = Object.keys(res).length
        this.performanceReport = res[month]
      } catch (e) {
        console.log(e)
      }
    },
    getMostUpdated() {
      if (this.performanceReport) {
        let uniqueFields = this.performanceReport['fields']
        let asArray = Object.entries(uniqueFields)
        let filterNotes = asArray.filter(
          ([key, value]) => key !== 'meeting_comments' && key !== 'meeting_type',
        )
        let filtered = Object.fromEntries(filterNotes)

        let sortable = []
        for (var field in filtered) {
          sortable.push([field, filtered[field]])
        }
        sortable.sort(function (a, b) {
          return b[1] - a[1]
        })
        this.sortedUpdates = sortable
      }
    },

    selectPerformanceReport() {
      this.reportType = 'Performance'
      this.generating = false
      this.selectedUser = null
      this.selectedOpp = null
      this.performanceReport = null
    },
    selectStoryReport() {
      this.reportType = 'Story'
      this.generating = false
      this.selectedUser = null
      this.selectedOpp = null
      this.performanceReport = null
    },
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
    allOpps() {
      return this.selectedUser
        ? this.$store.state.allOpps.filter((opp) => opp.owner == this.selectedUser.id)
        : this.$store.state.allOpps
      // return this.$store.state.allOpps
    },
    isAdmin() {
      return this.userIsLoggedIn && this.$store.state.user.isAdmin
    },
    user() {
      return this.$store.state.user
    },
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    notes() {
      return this.$store.state.templates
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

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

.center-line {
  position: absolute;
  right: 45%;
  font-weight: 900;
}
.relative {
  position: relative;
  width: fit-content;
}

.reports {
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-left: 80px;
  margin-top: 72px;
  letter-spacing: 0.75px;
}

.space-between {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
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
  padding: 4px 32px 0px 4px;
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
  flex-direction: row;
  align-items: flex-start;
  justify-content: center;
  margin-left: 4px;

  p {
    font-size: 15px;
    margin-left: 2px;
    color: $base-gray;
    padding: 6px 9px;
    cursor: pointer;
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
.margin-top-small {
  margin-top: 1.5rem;
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

.preview {
  min-height: 80vh;
  padding: 16px 32px 0 32px;
  width: 40vw;
  outline: 1px solid $soft-gray;
  border-radius: 8px;
  background-color: white;
  margin-top: 1rem;
  img {
    border: 1px solid transparent;
    border-radius: 6px;
  }
}

.preview-text {
  font-size: 13px;
  letter-spacing: 0.75px;
  margin-left: 8px;
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

.container-small {
  min-height: 48vh;
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
  color: $light-gray-blue !important;
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

.green-section {
  letter-spacing: 0.75px;
  color: white;
  background-color: $dark-green;
  padding: 6px 10px;
  border-radius: 6px;
}

.light-green-section {
  letter-spacing: 0.75px;
  color: $dark-green !important;
  background-color: $white-green;
  padding: 6px 9px;
  border-radius: 6px;
}

.purple-section {
  letter-spacing: 0.25px;
  color: white !important;
  font-size: 10px !important;
  background-color: $grape;
  padding: 2px 4px !important;
  border-radius: 4px !important;
}

.gray-text {
  color: $gray;
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

.grape {
  color: $grape;
  font-weight: bold;
}

.red-filter {
  margin-right: 8px !important;
  filter: invert(48%) sepia(76%) saturate(3436%) hue-rotate(326deg) brightness(113%) contrast(96%);
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
.big-card {
  border-radius: 5px;
  border: 1px solid $soft-gray;
  width: 51.5vw;
  padding: 16px;
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

  div {
    margin-top: 12px;

    meter {
      width: 32vw;
      height: 24px;
      border: 1px solid #ccc;
      border-radius: 12px;
    }

    meter::-webkit-meter-optimum-value {
      background: $dark-green; /* Green */
      border-radius: 8px;
    }

    section {
      small {
        margin-left: 32px;
      }
    }
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