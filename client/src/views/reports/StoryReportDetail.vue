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
      <div class="divider" />
      <div class="profile-photo-and-list">
        <div class="profile-photo">
          <img
            :class="{ photo: !!rep.profilePhoto, icon: !rep.profilePhoto }"
            :src="rep.profilePhoto ? rep.profilePhoto : require('@/assets/images/camera.svg')"
          />
          <div v-if="!rep.profilePhoto">
            No profile photo
          </div>
        </div>
        <div class="list">
          <div class="list-item">
            <div class="icon">
              <img src="@/assets/images/checkmark.svg" />
            </div>
            <div class="content">
              <div class="desc">
                {{ rep.firstName }} closed {{ lead.title }} for
                {{ leadMetrics.contractValue | currency }}
              </div>
              <div class="sub-desc">
                Primarily worked with (based on calls, texts, and emails) <br />
                <template v-if="leadMetrics.primaryContact">
                  {{ leadMetrics.primaryContact.fullName }},
                  {{
                    (
                      leadMetrics.primaryContact.firstName +
                      '' +
                      leadMetrics.primaryContact.lastName
                    ).trim()
                      ? leadMetrics.primaryContact.firstName +
                        '' +
                        leadMetrics.primaryContact.lastName
                      : leadMetrics.primaryContact.email
                  }}
                  {{
                    leadMetrics.primaryContact.title
                      ? leadMetrics.primaryContact.title
                      : 'title not known'
                  }}.
                </template>
                <template v-else>
                  no primary contact.
                </template>
              </div>
            </div>
          </div>
          <div class="list-item">
            <div class="icon">
              <img src="@/assets/images/checkmark.svg" />
            </div>
            <div class="content">
              <div class="desc">
                It took a total of {{ leadMetrics.daysToClosed }} days to close the deal
              </div>
              <div class="sub-desc">
                <template v-if="leadMetrics.daysToDemo">
                  {{ leadMetrics.daysToDemo }} to first demo
                </template>
                <template v-if="leadMetrics.daysDemoToClosed">
                  {{ leadMetrics.daysDemo ? ', c' : 'C' }}losed
                  {{ leadMetrics.daysDemoToClosed }} days post demo
                </template>
                <template v-if="!leadMetrics.daysToDemo && !leadMetrics.daysDemoToClosed">
                  Did not have to leverage a demo.
                </template>
              </div>
            </div>
          </div>
          <div class="list-item" v-if="leadMetrics.daysToClosed && repMetrics.averageDaysToClosed">
            <div class="icon">
              <img src="@/assets/images/checkmark.svg" />
            </div>
            <div class="content">
              <div class="desc">
                Closed this deal
                <template v-if="leadMetrics.daysToClosed < repMetrics.averageDaysToClosed">
                  faster than usual ({{ repMetrics.averageDaysToClosed }}
                  {{ 'day' | pluralize(repMetrics.averageDaysToClosed) }})
                </template>
                <template v-else-if="leadMetrics.daysToClosed > repMetrics.averageDaysToClosed">
                  slower than usual ({{ repMetrics.averageDaysToClosed }}
                  {{ 'day' | pluralize(repMetrics.averageDaysToClosed) }})
                </template>
                <template v-else>
                  on par with her/his average ({{ repMetrics.averageDaysToClosed }}
                  {{ 'day' | pluralize(repMetrics.averageDaysToClosed) }})
                </template>
                <div>
                  and for
                  <template v-if="leadMetrics.contractValue > repMetrics.averageContractValue">
                    a higher ACV ({{ repMetrics.averageContractValue | currencyNoCents }})
                  </template>
                  <template v-else-if="leadMetrics.contractValue < repMetrics.averageContractValue">
                    a lower ACV ({{ repMetrics.averageContractValue | currencyNoCents }})
                  </template>
                  <template v-else>
                    her/his ACV ({{ repMetrics.averageContractValue | currencyNoCents }})
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="status-metrics">
        <div class="group">
          <StageDaysGraphic
            :icon="'calendar'"
            :count="leadMetrics.daysReadyToBooked"
            :titleTop="'Days from'"
            :titleBottom="'Ready to Booked'"
            :average="repMetrics.averageDaysReadyToBooked"
          />
          <StageDaysGraphic
            :icon="'event-available'"
            :count="leadMetrics.daysBookedToDemo"
            :titleTop="'Days from'"
            :titleBottom="'Booked to Demo'"
            :average="repMetrics.averageDaysBookedToDemo"
          />
          <StageDaysGraphic
            :icon="'claimed'"
            :count="leadMetrics.actionCount"
            :titleTop="'Actions'"
            :titleBottom="'to Close this deal'"
            :average="repMetrics.averageActionCount"
          />
        </div>
        <div class="group">
          <StageDaysGraphic
            :icon="'forecast'"
            :count="leadMetrics.daysDemoToClosed"
            :titleTop="'Days from'"
            :titleBottom="'Demo to Closed'"
            :average="repMetrics.averageDaysDemoToClosed"
          />
          <div class="days-to-closed">
            <CircularProgressBar :percentComplete="daysToClosedGraphicValue" />
            <div>
              <StageDaysGraphic
                :icon="'loop'"
                :count="leadMetrics.daysToClosed"
                :titleTop="'Days in'"
                :titleBottom="'Entire Sales Cycle'"
                :average="repMetrics.averageDaysToClosed"
                :asCard="false"
                :progressBar="false"
              />
            </div>
          </div>
        </div>
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
          <tr class="rep-row">
            <td class="left-column">
              <div class="rep-cell">
                <img
                  :class="{ photo: !!rep.profilePhoto, icon: !rep.profilePhoto }"
                  :src="rep.profilePhoto ? rep.profilePhoto : require('@/assets/images/camera.svg')"
                />
                <div style="display: inline-block;">
                  <div>{{ rep.fullName }}</div>
                  <div><span>On this Deal</span></div>
                </div>
              </div>
            </td>
            <td>{{ leadMetrics.callCount || 0 }}</td>
            <td>{{ leadMetrics.textCount || 0 }}</td>
            <td>{{ leadMetrics.emailCount || 0 }}</td>
            <td>{{ leadMetrics.actionCount || 0 }}</td>
          </tr>

          <tr>
            <td class="left-column">{{ rep.firstName }}'s average on all closed deals</td>
            <td>{{ repMetrics.averageCallCount || 0 }}</td>
            <td>{{ repMetrics.averageTextCount || 0 }}</td>
            <td>{{ repMetrics.averageEmailCount || 0 }}</td>
            <td>{{ repMetrics.averageActionCount || 0 }}</td>
          </tr>

          <tr>
            <td class="left-column">Company average on all closed deals</td>
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
  components: {
    StageDaysGraphic,
    CircularProgressBar,
    ActionsGraphic,
  },
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
    lead() {
      return this.missingReport ? null : this.report.leadRef
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
  padding: 3rem 0;
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

.actions {
  margin: 3rem 0;

  h2 {
    color: $dark-green;
    padding-left: 4rem;
  }
}

.status-metrics {
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding-bottom: 2rem;
  margin-top: -11rem;

  .group {
    margin-top: 2rem;
    display: flex;
    flex-flow: row;
    justify-content: center;
    width: 100%;
  }
}

.days-to-closed {
  background-color: $white;
  border-radius: 0.5rem;
  box-shadow: 0 0 5px 1px $soft-gray;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  margin: 0 2rem;
}

.profile-photo-and-list {
  padding-top: 1rem;
  display: flex;
  flex-flow: row;
  height: 31rem;
  background-color: $off-white;
  .profile-photo {
    flex-grow: 1;
    display: flex;
    flex-flow: column;
    align-items: center;

    .icon {
      height: 5rem;
      width: 5rem;
      border-radius: 50%;
      margin-top: 5rem;
    }
    .photo {
      border-radius: 50%;
      margin-top: 5rem;
      height: 10rem;
      width: 10rem;
      border: 2px solid $yellow;
      object-fit: cover;
    }
    div {
      font-style: italic;
    }
  }
  .list {
    flex-grow: 1;

    .list-item {
      display: flex;
      flex-flow: row;
      padding: 0 2rem;
      margin-top: 2rem;

      .icon img {
        height: 2.5rem;
      }

      .content {
        margin-left: 2rem;
        padding-top: 0.5rem;
        .desc {
          line-height: 1.3rem;
          font-weight: 600;
        }
        .sub-desc {
          font-style: italic;
        }
      }
    }
  }
}

.table {
  margin-top: 3rem;
  margin-bottom: 1rem;
  padding: 0 3rem;
  font-size: 1.2rem;

  .icon {
    height: 1rem;
    width: 1rem;
    border-radius: 50%;
  }
  .photo {
    border-radius: 50%;
    height: 3rem;
    width: 3rem;
    border: 2px solid $yellow;
    object-fit: cover;
  }
}
table {
  border: 1px solid $soft-gray;
}
tr {
  height: 4rem;
}
.rep-row {
  background-color: rgba($color: $yellow, $alpha: 0.1);
}
.rep-cell {
  display: flex;
  flex-flow: row;
  align-items: center;

  img {
    margin-right: 1rem;
  }
}
th {
  font-weight: 600;
}
td {
  text-align: center;
}
.left-column {
  text-align: left;
  font-weight: 600;
  padding-left: 2rem;

  span {
    font-weight: 300;
    font-style: italic;
  }
}
</style>
