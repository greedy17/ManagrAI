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
        <select class="daterange" v-model="dateRange" @change="onDateRangeFilterChange">
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

      <div
        class="single-statistic section-shadow"
        :class="{ 'kpi-editable': editKPIs.editingQuota }"
      >
        <span class="title">Quota</span>
        <span class="statistic with-icon" v-if="oneRepSelected && !editKPIs.editingQuota">
          <div class="fifth-wide" />
          <span class="three-fifth-wide value">{{ KPIs.quota | currency }}</span>
          <div class="fifth-wide">
            <img src="@/assets/images/pencil.svg" class="edit-icon" @click="editQuota" />
          </div>
        </span>
        <div v-else-if="oneRepSelected && editKPIs.editingQuota" style="width: 100%;">
          <form class="kpi-form" @submit.prevent="updateQuota">
            <input type="number" v-model="editKPIs.tempQuota" />
            <img class="save" src="@/assets/images/checkmark.svg" @click="updateQuota" />
            <img class="reset" src="@/assets/images/remove.svg" @click="resetQuota" />
          </form>
        </div>
        <span class="statistic" v-else>{{ KPIs.quota | currency }}</span>
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

      <div
        class="single-statistic section-shadow"
        :class="{ 'kpi-editable': editKPIs.editingCommit }"
      >
        <span class="title">Commit</span>
        <span class="statistic with-icon" v-if="oneRepSelected && !editKPIs.editingCommit">
          <div class="fifth-wide" />
          <span class="three-fifth-wide value">{{ KPIs.commit | currency }}</span>
          <div class="fifth-wide">
            <img src="@/assets/images/pencil.svg" class="edit-icon" @click="editCommit" />
          </div>
        </span>
        <div v-else-if="oneRepSelected && editKPIs.editingCommit" style="width: 100%;">
          <form class="kpi-form" @submit.prevent="updateCommit">
            <input type="number" v-model="editKPIs.tempCommit" />
            <img class="save" src="@/assets/images/checkmark.svg" @click="updateCommit" />
            <img class="reset" src="@/assets/images/remove.svg" @click="resetCommit" />
          </form>
        </div>
        <span class="statistic" v-else>{{ KPIs.commit | currency }}</span>
      </div>

      <div
        class="single-statistic section-shadow"
        :class="{ 'kpi-editable': editKPIs.editingUpside }"
      >
        <span class="title">Upside</span>
        <span class="statistic with-icon" v-if="oneRepSelected && !editKPIs.editingUpside">
          <div class="fifth-wide" />
          <span class="three-fifth-wide value">{{ KPIs.upside | currency }}</span>
          <div class="fifth-wide">
            <img src="@/assets/images/pencil.svg" class="edit-icon" @click="editUpside" />
          </div>
        </span>
        <div v-else-if="oneRepSelected && editKPIs.editingUpside" style="width: 100%;">
          <form class="kpi-form" @submit.prevent="updateUpside">
            <input type="number" v-model="editKPIs.tempUpside" />
            <img class="save" src="@/assets/images/checkmark.svg" @click="updateUpside" />
            <img class="reset" src="@/assets/images/remove.svg" @click="resetUpside" />
          </form>
        </div>
        <span class="statistic" v-else>{{ KPIs.upside | currency }}</span>
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
import User from '@/services/users'

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
      editKPIs: {
        editingQuota: false,
        tempQuota: 0,
        editingCommit: false,
        tempCommit: 0,
        editingUpside: false,
        tempUpside: 0,
      },
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
    onDateRangeFilterChange() {
      this.$emit('date-range-filter-change', this.dateRange)
      this.getKPIs()
    },
    getKPIs() {
      this.KPIs = null
      this.editKPIs = {
        editingQuota: false,
        tempQuota: 0,
        editingCommit: false,
        tempCommit: 0,
        editingUpside: false,
        tempUpside: 0,
      }

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
    editQuota() {
      // This UX is only available if a single representative is selected.
      // Therefore this.KPIs.quota represents the single representative's quota.
      this.editKPIs.tempQuota = this.KPIs.quota
      this.editKPIs.editingQuota = true
    },
    updateQuota() {
      let data = {
        quota: this.editKPIs.tempQuota,
      }
      User.api
        .update(this.oneRepSelected, data)
        .then(response => {
          this.KPIs.quota = response.data.quota
          this.resetQuota()
        })
        .catch(() => {
          this.resetQuota()
        })
    },
    resetQuota() {
      this.editKPIs.editingQuota = false
      this.editKPIs.tempQuota = 0
    },
    editCommit() {
      // This UX is only available if a single representative is selected.
      // Therefore this.KPIs.commit represents the single representative's commit.
      this.editKPIs.tempCommit = this.KPIs.commit
      this.editKPIs.editingCommit = true
    },
    updateCommit() {
      let data = {
        commit: this.editKPIs.tempCommit,
      }
      User.api
        .update(this.oneRepSelected, data)
        .then(response => {
          this.KPIs.commit = response.data.commit
          this.resetCommit()
        })
        .catch(() => {
          this.resetCommit()
        })
    },
    resetCommit() {
      this.editKPIs.editingCommit = false
      this.editKPIs.tempCommit = 0
    },
    editUpside() {
      // This UX is only available if a single representative is selected.
      // Therefore this.KPIs.upside represents the single representative's upside.
      this.editKPIs.tempUpside = this.KPIs.upside
      this.editKPIs.editingUpside = true
    },
    updateUpside() {
      let data = {
        upside: this.editKPIs.tempUpside,
      }
      User.api
        .update(this.oneRepSelected, data)
        .then(response => {
          this.KPIs.upside = response.data.upside
          this.resetUpside()
        })
        .catch(() => {
          this.resetUpside()
        })
    },
    resetUpside() {
      this.editKPIs.editingUpside = false
      this.editKPIs.tempUpside = 0
    },
  },
  watch: {
    repFilterState() {
      this.refresh(POLLING_INTERVAL)
      this.getKPIs()
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
    oneRepSelected() {
      let reps = Object.entries(this.repFilterState)
        .map(([key, value]) => (value === true ? key : null))
        .filter(i => i !== null)
      if (reps.length === 1) {
        return reps[0]
      } else {
        return false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

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

.with-icon {
  width: 100%;
  display: flex;
  flex-flow: row;
  align-items: center;

  .fifth-wide {
    width: 20%;
  }

  .three-fifth-wide {
    width: 60%;
  }

  .value {
    text-align: center;
  }

  .edit-icon {
    @include pointer-on-hover;
    opacity: 0.4;
    height: 1.2rem;
    width: 1.2rem;

    &:hover {
      opacity: 1;
    }
  }
}

.kpi-editable {
  height: 6rem;
}

.kpi-form {
  display: flex;
  flex-flow: row;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
  padding-top: 1rem;

  input {
    @include input-field();
    margin-left: 1rem;
    width: 7rem;
  }

  .save {
    background-color: $dark-green;
    border-radius: 3px;
    margin-left: auto;
  }

  .reset {
    background-color: $silver;
    border-radius: 3px;
    margin-left: auto;
    margin-right: auto;
  }
}
</style>
