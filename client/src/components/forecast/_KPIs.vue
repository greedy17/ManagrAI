<template>
  <div>
    <div class="header section-shadow">
      KPIs
    </div>

    <div
      class="single-statistic section-shadow"
      v-if="refreshedOnce && apiFailing"
      style="padding: 1rem;"
    >
      <p>We are unable to retrieve KPIs at this time. Please try again later.</p>
    </div>

    <div v-if="refreshedOnce && !apiFailing">
      <div class="single-statistic section-shadow">
        <span class="title">Total Closed Value</span>
        <span class="statistic">
          {{ insights ? insights.closedLeads.totalValue : 0 | currency }}</span
        >
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Average Contract Value</span>
        <span class="statistic">
          {{ insights ? insights.averageContractValue : 0 | currency }}</span
        >
      </div>
      <div class="single-statistic section-shadow">
        <span class="title">Forecast</span>
        <span class="statistic"> {{ insights ? insights.forecast : 0 | currency }}</span>
      </div>
      <div class="statistics-container section-shadow">
        <span class="title">Statistics</span>
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

const POLLING_INTERVAL = 10000

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
      insights: null,
      apiFailing: false,
      refreshedOnce: false,
    }
  },
  created() {
    this.refresh(POLLING_INTERVAL)
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
  },
  watch: {
    repFilterState() {
      this.refresh(POLLING_INTERVAL)
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
