<template>
  <div class="page">
    <PageLoadingSVG v-if="loading" />
    <div class="not-available" v-else-if="show404">
      <h1>404</h1>
      <p>Report Not Found</p>
    </div>
    <div class="not-available" v-else-if="!report.datetimeGenerated">
      <p>This report is still being generated.</p>
    </div>
    <div class="report shadow" v-else>
      Page 1!!
      <div class="divider" />
      <div class="profile-photo-and-list">
        <div class="profile-photo">
          photo here
        </div>
        <div class="list">
          list here
        </div>
      </div>
      <div class="status-metrics">
        <StageDaysGraphic
          :count="leadMetrics.daysReadyToBooked"
          :title="'Days from Ready to Booked'"
          :average="repMetrics.averageDaysReadyToBooked"
        />
        <StageDaysGraphic
          :count="leadMetrics.daysBookedToDemo"
          :title="'Days from Booked to Demo'"
          :average="repMetrics.averageDaysBookedToDemo"
        />
        <StageDaysGraphic
          :count="leadMetrics.actionCount"
          :title="'Actions to Close this deal'"
          :average="repMetrics.averageActionCount"
        />
        <StageDaysGraphic
          :count="leadMetrics.daysDemoToClosed"
          :title="'Days from Demo to Closed'"
          :average="repMetrics.averageDaysDemoToClosed"
        />
        <StageDaysGraphic
          :count="leadMetrics.daysToClosed"
          :title="'Days in Entire Sales Cycle'"
          :average="repMetrics.averageDaysToClosed"
        />
        <CircularProgressBar :percentComplete="daysToClosedGraphicValue" />
      </div>
      <div class="managr-logo">
        managr
      </div>
      <div class="divider" />
      <div class="actions">
        <h2>Actions</h2>
        <ActionsGraphic :actions="sortedActionMetrics" />
      </div>
      <div class="contract-hero">
        <div>
          <div class="amount">{{ leadMetrics.contractValue | currencyNoCents }}</div>
          <div class="description">Deal Size</div>
        </div>
        <div>
          <div class="amount">{{ repMetrics.averageContractValue | currencyNoCents }}</div>
          <div class="description">Average contract value</div>
        </div>
      </div>
      <div class="table">
        <table style="width:100%">
          <tr>
            <th></th>
            <th>Calls</th>
            <th>Texts</th>
            <th>Emails</th>
            <th>Actions</th>
          </tr>
          <tr>
            <td>
              <div>{{ rep.fullName }}</div>
              <div>On this Deal</div>
            </td>
            <td>{{ leadMetrics.callCount || 0 }}</td>
            <td>{{ leadMetrics.textCount || 0 }}</td>
            <td>{{ leadMetrics.emailCount || 0 }}</td>
            <td>{{ leadMetrics.actionCount || 0 }}</td>
          </tr>

          <tr>
            <td>{{ rep.firstName }}'s average on all closed deals</td>
            <td>{{ repMetrics.averageCallCount || 0 }}</td>
            <td>{{ repMetrics.averageTextCount || 0 }}</td>
            <td>{{ repMetrics.averageEmailCount || 0 }}</td>
            <td>{{ repMetrics.averageActionCount || 0 }}</td>
          </tr>

          <tr>
            <td>Company average on all closed deals</td>
            <td>{{ orgMetrics.averageCallCount || 0 }}</td>
            <td>{{ orgMetrics.averageTextCount || 0 }}</td>
            <td>{{ orgMetrics.averageEmailCount || 0 }}</td>
            <td>{{ orgMetrics.averageActionCount || 0 }}</td>
          </tr>
        </table>
      </div>
      <div class="managr-logo">
        managr
      </div>
    </div>
  </div>
</template>

<script>
import StoryReport from '@/services/storyReports'
import StageDaysGraphic from '@/components/reports/StageDaysGraphic'
import CircularProgressBar from '@/components/reports/CircularProgressBar'
import ActionsGraphic from '@/components/reports/ActionsGraphic'

function customActionSorter(firstAction, secondAction) {
  if (firstAction.count > secondAction.count) {
    return -1
  }
  if (secondAction.count > firstAction.count) {
    return 1
  }
  if (firstAction.title.toLowerCase() > secondAction.title.toLowerCase()) {
    return 1
  }
  if (secondAction.title.toLowerCase() > firstAction.title.toLowerCase()) {
    return -1
  }
  return 0
}

export default {
  name: 'StoryReportDetail',
  components: { StageDaysGraphic, CircularProgressBar, ActionsGraphic },
  props: ['id'],
  data() {
    return {
      loading: true,
      show404: false,
      report: null,
    }
  },
  created() {
    StoryReport.api
      .retrieve(this.id)
      .then(report => {
        this.report = report
      })
      .catch(({ response }) => {
        if (response.status === 404) {
          this.show404 = true
        }
      })
      .finally(() => {
        this.loading = false
      })
  },
  methods: {},
  computed: {
    missingReport() {
      return this.report === null
    },
    leadMetrics() {
      return this.missingReport ? null : this.report.data.lead
    },
    repMetrics() {
      return this.missingReport ? null : this.report.data.representative
    },
    orgMetrics() {
      return this.missingReport ? null : this.report.data.organization
    },
    rep() {
      return this.missingReport ? null : this.report.leadRef.claimedByRef
    },
    sortedActionMetrics() {
      if (this.missingReport) {
        return null
      }
      let unsortedArray = Object.keys(this.leadMetrics.customActionCounts).map(key => ({
        title: key,
        count: this.leadMetrics.customActionCounts[key],
      }))
      return unsortedArray.sort(customActionSorter)
    },
    daysToClosedGraphicValue() {
      if (this.missingReport) {
        return 0
      }
      return (this.leadMetrics.daysToClosed / this.repMetrics.averageDaysToClosed) * 100
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
// @import '@/styles/layout';
// @import '@/styles/containers';
// @import '@/styles/sidebars';
// @import '@/styles/mixins/utils';

.page {
  padding: 0 10vw;
}

.shadow {
  box-shadow: 0 0 5px 1px $soft-gray;
}

.report {
  background-color: $white;
}

.divider {
  background-color: $dark-green;
  height: 0.5em;
  width: 100%;
}

.not-available {
  padding-top: 10rem;
  color: $mid-gray;
  display: flex;
  flex-flow: column;
  align-items: center;
  h1 {
    font-size: 2rem;
  }
  p {
    font-size: 1.5rem;
    margin-top: 0;
  }
}

.managr-logo {
  text-align: center;
  font-family: $logo-font-family;
  font-size: 2.25rem;
  font-weight: 500;
  font-stretch: normal;
  font-style: normal;
  line-height: normal;
  color: $dark-green;
  padding: 2rem 0;
}

.contract-hero {
  background-color: rgba($color: $dark-green, $alpha: 0.15);
  padding: 6rem 0;
  display: flex;
  flex-flow: row;
  align-items: center;

  div {
    flex-grow: 1;
    display: flex;
    flex-flow: column;
    align-items: center;

    .amount {
      color: $dark-green;
      font-size: 5rem;
    }

    .description {
      font-size: 1.5rem;
      font-weight: 600;
    }
  }
}

tr {
  height: 3rem;
}

.actions {
  margin: 3rem 0;

  h2 {
    color: $dark-green;
    padding-left: 4rem;
  }
}
</style>
