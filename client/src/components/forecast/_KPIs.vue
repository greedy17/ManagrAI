<template>
  <div>
    <div class="header section-shadow">
      KPIs
    </div>

    <div v-if="KPIs === null" style="margin-top: 1.5rem; margin-bottom: 1rem;">
      <ComponentLoadingSVG />
    </div>
    <div v-else>
      <div class="daterange-container">
        <select class="daterange" v-model="dateRange" @change="getKPIs">
          <option v-for="(preset, i) in dateRangePresets" :value="preset.value" :key="i">
            {{ preset.label }}
          </option>
        </select>
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Sold</span>
        <span class="statistic">
          {{ KPIs.sold | currency }}
        </span>
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Quota</span>
        <span class="statistic">{{ KPIs.quota | currency }}</span>
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Percent of Quota</span>
        <span class="statistic">{{ percentOfQuotaKPI }}%</span>
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Shortage</span>
        <span class="statistic">{{ shortageKPI | currency }}</span>
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Average Contract Value</span>
        <span class="statistic"> {{ KPIs.averageContractValue | currency }}</span>
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Forecast</span>
        <span class="statistic">{{ KPIs.forecast | currency }}</span>
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Commit</span>
        <span class="statistic">{{ KPIs.commit | currency }}</span>
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Upside</span>
        <span class="statistic">{{ KPIs.upside | currency }}</span>
      </div>
    </div>

    <div
      class="single-statistic section-shadow"
      v-if="refreshedOnce && apiFailing"
      style="padding: 1rem;"
    >
      <p>We are unable to retrieve Activities at this time. Please try again later.</p>
    </div>
    <div v-if="refreshedOnce && !apiFailing">
      <div class="statistics-container section-shadow">
        <span class="title">Activities</span>
        <div class="graphic-statistic section-shadow">
          <div class="icon-container">
            <img class="icon" src="@/assets/images/telephone.svg" alt="icon" />
          </div>
          <div class="information">
            <span class="top">
              {{ insights && insights.calls.count }}
              {{ 'Call' | pluralize(insights ? insights.calls.count : 0) }}
            </span>
            <span class="bottom">
              {{ insights && insights.calls.latest | timeAgo }}
            </span>
          </div>
        </div>
        <div class="graphic-statistic section-shadow">
          <div class="icon-container">
            <img class="icon" src="@/assets/images/checkmark.svg" alt="icon" />
          </div>
          <div class="information">
            <span class="top">
              {{ insights && insights.actions.count }}
              {{ 'Action' | pluralize(insights ? insights.actions.count : 0) }}
            </span>
            <span class="bottom">
              {{ insights && insights.actions.latest | timeAgo }}
            </span>
          </div>
        </div>
        <div class="graphic-statistic section-shadow">
          <div class="icon-container">
            <img class="icon" src="@/assets/images/email.svg" alt="icon" />
          </div>
          <div class="information">
            <span class="top">
              {{ insights && insights.emails.count }}
              {{ 'Email' | pluralize(insights ? insights.emails.count : 0) }}
            </span>
            <span class="bottom">
              {{ insights && insights.emails.latest | timeAgo }}
            </span>
          </div>
        </div>
        <div class="graphic-statistic section-shadow">
          <div class="icon-container">
            <img class="icon" src="@/assets/images/check-box-filled-checked.svg" alt="icon" />
          </div>
          <div class="information">
            <span class="top"> {{ insights && insights.closedLeads.count }} Closed </span>
            <span class="bottom"> </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LeadActivityLog from '@/services/leadActivityLogs'
import Forecast from '@/services/forecasts'

const POLLING_INTERVAL = 10000

const dateRangePresets = [
  { value: Forecast.TODAY_ONWARD, label: 'Today Onward' },
  { value: Forecast.TODAY, label: 'Today' },
  { value: Forecast.YESTERDAY, label: 'Yesterday' },
  { value: Forecast.THIS_WEEK, label: 'This Week' },
  { value: Forecast.LAST_WEEK, label: 'Last Week' },
  { value: Forecast.THIS_MONTH, label: 'This Month' },
  { value: Forecast.LAST_MONTH, label: 'Last Month' },
  { value: Forecast.THIS_QUARTER, label: 'This Quarter' },
  { value: Forecast.LAST_QUARTER, label: 'Last Quarter' },
  { value: Forecast.THIS_YEAR, label: 'This Year' },
  { value: Forecast.LAST_YEAR, label: 'Last Year' },
  { value: Forecast.ALL_TIME, label: 'All Time' },
]

export default {
  name: 'KPIs',
  props: {
    repFilterState: {
      required: true,
      type: Object,
    },
  },
  data() {
    return {
      dateRangePresets,
      dateRange: Forecast.TODAY_ONWARD,
      insights: null,
      apiFailing: false,
      refreshedOnce: false,
      KPIs: null,
    }
  },
  created() {
    this.refresh(POLLING_INTERVAL)
    this.getKPIs()
  },
  destroyed() {
    clearTimeout(this.pollingTimeout)
  },
  methods: {
    refresh(repeat) {
      clearTimeout(this.pollingTimeout)

      const filters = {}
      const claimedBy = Object.entries(this.repFilterState)
        .map(([key, value]) => (value === true ? key : null))
        .filter(i => i !== null)

      if (claimedBy.length > 0) {
        filters['claimedBy'] = claimedBy
      } else {
        filters['empty'] = true
      }

      LeadActivityLog.api
        .getInsights({ filters, enable400Alert: false, enable500Alert: false })
        .then(result => {
          this.insights = result
          this.apiFailing = false
          if (repeat) {
            this.pollingTimeout = setTimeout(() => this.refresh(POLLING_INTERVAL), repeat)
          }
        })
        .catch(() => {
          this.apiFailing = true
          if (repeat) {
            // Repeat with exponential back-off as long as calls are failing
            this.pollingTimeout = setTimeout(() => this.refresh(repeat * 2), repeat * 2)
          }
        })
        .finally(() => {
          this.refreshedOnce = true
        })
    },
    getKPIs() {
      let reps = Object.entries(this.repFilterState)
        .map(([key, value]) => (value === true ? key : null))
        .filter(i => i !== null)

      let data = {
        dateRangePreset: this.dateRange,
        representatives: reps,
      }

      Forecast.api.KPIs(data).then(data => {
        this.KPIs = data
      })
    },
  },
  watch: {
    repFilterState() {
      this.refresh(POLLING_INTERVAL)
    },
  },
  computed: {
    shortageKPI() {
      let shortage = this.KPIs.quota - this.KPIs.sold
      if (shortage < 0) {
        return 0
      } else {
        return shortage
      }
    },
    percentOfQuotaKPI() {
      if (this.KPIs.quota == 0) {
        return 100
      }
      let percent = (this.KPIs.sold / this.KPIs.quota) * 100
      let roundedPercentage = Math.round(percent * 10) / 10
      if (roundedPercentage > 100) {
        return 100
      } else {
        return percent
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.header {
  display: flex;
  flex-flow: column;
  justify-content: center;
  height: 3rem;
  padding-left: 7%;
  font-weight: bold;
}

.daterange-container {
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
  padding: 1.2rem 0;

  select {
    background-color: rgba($color: $dark-gray-blue, $alpha: 0);
    border: 0;
    color: $main-font-gray;
    border-radius: 0.5rem;
    padding: 0.5rem;
    font-size: 1rem;
    font-weight: 600;

    option {
      padding-top: 1rem;
    }
  }
}

.single-statistic {
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
  height: 4rem;
  .statistic {
    color: rgba($color: $main-font-gray, $alpha: 0.5);
    margin-top: 0.5rem;
  }
}

.statistics-container {
  height: auto;
  .title {
    display: flex;
    flex-flow: column;
    justify-content: center;
    height: 3rem;
    padding-left: 7%;
  }
}

.graphic-statistic {
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 3rem;

  .icon-container {
    width: 30%;
    display: flex;
    align-items: center;
    justify-content: center;

    .icon {
      height: 1.25rem;
      width: 1.25rem;
    }
  }

  .information {
    display: flex;
    flex-flow: column;
    flex-grow: 1;

    .top {
      @include base-font-styles();
      font-size: 0.875rem;
      line-height: 1.14;
      color: $main-font-gray;
    }

    .bottom {
      @include base-font-styles();
      font-size: 0.875rem;
      line-height: 1.14;
      color: rgba($color: $main-font-gray, $alpha: 0.4);
    }
  }
}
</style>
