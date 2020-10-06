<template>
  <div class="report">
    <div class="report__summary-container">
      <div class="report__summary-container__report-focus soft-gray-background">
        <img
          :src="
            representative.profilePhoto
              ? representative.profilePhoto
              : require('@/assets/images/camera.svg')
          "
        />
        <div class="report__summary-container__report-focus__date-range-preset">
          {{ report.dateRangePreset | constantToCapitalized }}
        </div>
        <div class="report__summary-container__report-focus__representative-info">
          {{ representative.fullName.trim() ? representative.fullName : representative.email }}
        </div>
      </div>
      <table class="report__summary-container__summary-table">
        <!-- header row -->
        <tr class="report__summary-container__summary-table__header-row soft-gray-background">
          <th></th>
          <th class="report__summary-container__summary-table__title-cell">Activities</th>
          <th class="report__summary-container__summary-table__title-cell">Actions</th>
          <th class="report__summary-container__summary-table__title-cell">
            Incoming<br />Messages
          </th>
          <th class="report__summary-container__summary-table__title-cell">Forecast<br />Amount</th>
          <th class="report__summary-container__summary-table__title-cell">Deals<br />Closed</th>
          <th class="report__summary-container__summary-table__title-cell">Amount<br />Closed</th>
        </tr>

        <!-- content row #1 -->
        <tr
          class="report__summary-container__summary-table__content-row report__summary-container__summary-table__focus-row"
        >
          <td class="report__summary-container__summary-table__label-cell">
            {{ report.dateRangePreset | constantToCapitalized }}
          </td>

          <!-- focusData.activitiesCount -->
          <td class="report__summary-container__summary-table__statistic-cell">
            <div class="report__summary-container__summary-table__statistic-cell__container">
              <div
                class="report__summary-container__summary-table__statistic-cell__container__value"
              >
                {{ focusData.activitiesCount }}
              </div>
              <div
                class="report__summary-container__summary-table__statistic-cell__container__trend"
              >
                <img
                  class="report__summary-container__summary-table__statistic-cell__container__trend__icon"
                  :src="require(`@/assets/images/${getTrendIcon('activitiesCount')}`)"
                />
                <span
                  class="report__summary-container__summary-table__statistic-cell__container__trend__stat"
                >
                  {{ getTrendStat('activitiesCount') }}%
                </span>
              </div>
            </div>
          </td>

          <!-- focusData.actionsCount -->
          <td class="report__summary-container__summary-table__statistic-cell">
            <div class="report__summary-container__summary-table__statistic-cell__container">
              <div
                class="report__summary-container__summary-table__statistic-cell__container__value"
              >
                {{ focusData.actionsCount }}
              </div>
              <div
                class="report__summary-container__summary-table__statistic-cell__container__trend"
              >
                <img
                  class="report__summary-container__summary-table__statistic-cell__container__trend__icon"
                  :src="require(`@/assets/images/${getTrendIcon('actionsCount')}`)"
                />
                <span
                  class="report__summary-container__summary-table__statistic-cell__container__trend__stat"
                >
                  {{ getTrendStat('actionsCount') }}%
                </span>
              </div>
            </div>
          </td>

          <!-- focusData.incomingMessagesCount -->
          <td class="report__summary-container__summary-table__statistic-cell">
            <div class="report__summary-container__summary-table__statistic-cell__container">
              <div
                class="report__summary-container__summary-table__statistic-cell__container__value"
              >
                {{ focusData.incomingMessagesCount }}
              </div>
              <div
                class="report__summary-container__summary-table__statistic-cell__container__trend"
              >
                <img
                  class="report__summary-container__summary-table__statistic-cell__container__trend__icon"
                  :src="require(`@/assets/images/${getTrendIcon('incomingMessagesCount')}`)"
                />
                <span
                  class="report__summary-container__summary-table__statistic-cell__container__trend__stat"
                >
                  {{ getTrendStat('incomingMessagesCount') }}%
                </span>
              </div>
            </div>
          </td>

          <!-- focusData.forecastAmount -->
          <td class="report__summary-container__summary-table__statistic-cell">
            <div class="report__summary-container__summary-table__statistic-cell__container">
              <div
                class="report__summary-container__summary-table__statistic-cell__container__value"
              >
                {{ focusData.forecastAmount | currencyNoCents }}
              </div>
              <div
                class="report__summary-container__summary-table__statistic-cell__container__trend"
              >
                <img
                  class="report__summary-container__summary-table__statistic-cell__container__trend__icon"
                  :src="require(`@/assets/images/${getTrendIcon('forecastAmount')}`)"
                />
                <span
                  class="report__summary-container__summary-table__statistic-cell__container__trend__stat"
                >
                  {{ getTrendStat('forecastAmount') }}%
                </span>
              </div>
            </div>
          </td>

          <!-- focusData.dealsClosedCount -->
          <td class="report__summary-container__summary-table__statistic-cell">
            <div class="report__summary-container__summary-table__statistic-cell__container">
              <div
                class="report__summary-container__summary-table__statistic-cell__container__value"
              >
                {{ focusData.dealsClosedCount }}
              </div>
              <div
                class="report__summary-container__summary-table__statistic-cell__container__trend"
              >
                <img
                  class="report__summary-container__summary-table__statistic-cell__container__trend__icon"
                  :src="require(`@/assets/images/${getTrendIcon('dealsClosedCount')}`)"
                />
                <span
                  class="report__summary-container__summary-table__statistic-cell__container__trend__stat"
                >
                  {{ getTrendStat('dealsClosedCount') }}%
                </span>
              </div>
            </div>
          </td>

          <!-- focusData.amountClosed -->
          <td class="report__summary-container__summary-table__statistic-cell">
            <div class="report__summary-container__summary-table__statistic-cell__container">
              <div
                class="report__summary-container__summary-table__statistic-cell__container__value"
              >
                {{ focusData.amountClosed | currencyNoCents }}
              </div>
              <div
                class="report__summary-container__summary-table__statistic-cell__container__trend"
              >
                <img
                  class="report__summary-container__summary-table__statistic-cell__container__trend__icon"
                  :src="require(`@/assets/images/${getTrendIcon('amountClosed')}`)"
                />
                <span
                  class="report__summary-container__summary-table__statistic-cell__container__trend__stat"
                >
                  {{ getTrendStat('amountClosed') }}%
                </span>
              </div>
            </div>
          </td>
        </tr>

        <!-- content row #2 -->
        <tr class="report__summary-container__summary-table__content-row soft-gray-background">
          <td class="report__summary-container__summary-table__label-cell">
            Typical {{ dateRangePresetFocus | constantToCapitalized }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.activitiesCount }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.actionsCount }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.incomingMessagesCount }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.forecastAmount | currencyNoCents }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.dealsClosedCount }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.amountClosed | currencyNoCents }}
          </td>
        </tr>

        <!-- content row #3 -->
        <tr class="report__summary-container__summary-table__content-row">
          <td class="report__summary-container__summary-table__label-cell">
            Typical Team {{ dateRangePresetFocus | constantToCapitalized }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.activitiesCount }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.actionsCount }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.incomingMessagesCount }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.forecastAmount | currencyNoCents }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.dealsClosedCount }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.amountClosed | currencyNoCents }}
          </td>
        </tr>
      </table>
    </div>

    <div class="report__middle-row">
      <div class="report__middle-row__card">
        row__card
      </div>
      <div class="report__middle-row__card">
        row__card
      </div>
      <div class="report__middle-row__card">
        row__card
      </div>
    </div>

    <div class="report__middle-row">
      <div class="report__middle-row__card">
        row__card
      </div>
      <div class="report__middle-row__card">
        row__card
      </div>
      <div class="report__middle-row__card">
        row__card
      </div>
    </div>

    <div class="report__deal-analysis">
      <div class="report__deal-analysis__title">
        Deal Analysis
      </div>
      <div class="report__deal-analysis__summary" v-if="focusData.dealsClosedCount">
        {{ dealAnalysisDisplayName }} closed mostly
        {{ focusData.dealAnalysis.industry.value | constantToCapitalized }} opportunities in
        {{ focusData.dealAnalysis.geography.value | constantToCapitalized }}, with
        {{ focusData.dealAnalysis.companySize.value }} employees. They were of type
        {{
          focusData.dealAnalysis.type.value === 'OTHER'
            ? constantToCapitalized(focusData.dealAnalysis.type.value)
            : focusData.dealAnalysis.type.value
        }}
        {{
          focusData.dealAnalysis.competitor.value === 'OTHER'
            ? null
            : focusData.dealAnalysis.competitor.value === 'YES'
            ? ', using a competitor'
            : ', not using a competitor'
        }}.
      </div>
      <div class="report__deal-analysis__breakdown" v-if="focusData.dealsClosedCount">
        <!-- Industry -->
        <div class="report__deal-analysis__breakdown__category">
          <div class="report__deal-analysis__breakdown__category__title">
            {{ focusData.dealAnalysis.industry.value | constantToCapitalized }}
          </div>
          <div class="report__deal-analysis__breakdown__category__graphic">
            <ProgressBar
              :percentComplete="focusData.dealAnalysis.industry.percentage"
              :centerPiece="false"
              :widthValue="50"
              :widthUnit="'rem'"
            />
          </div>
          <div class="report__deal-analysis__breakdown__category__percentage">
            {{ focusData.dealAnalysis.industry.percentage }}%
          </div>
        </div>

        <!-- Geography -->
        <div class="report__deal-analysis__breakdown__category">
          <div class="report__deal-analysis__breakdown__category__title">
            {{ focusData.dealAnalysis.geography.value }}
          </div>
          <div class="report__deal-analysis__breakdown__category__graphic">
            <ProgressBar
              :percentComplete="focusData.dealAnalysis.geography.percentage"
              :centerPiece="false"
              :widthValue="50"
              :widthUnit="'rem'"
            />
          </div>
          <div class="report__deal-analysis__breakdown__category__percentage">
            {{ focusData.dealAnalysis.geography.percentage }}%
          </div>
        </div>

        <!-- companySize -->
        <div class="report__deal-analysis__breakdown__category">
          <div class="report__deal-analysis__breakdown__category__title">
            {{ focusData.dealAnalysis.companySize.value }}
          </div>
          <div class="report__deal-analysis__breakdown__category__graphic">
            <ProgressBar
              :percentComplete="focusData.dealAnalysis.companySize.percentage"
              :centerPiece="false"
              :widthValue="50"
              :widthUnit="'rem'"
            />
          </div>
          <div class="report__deal-analysis__breakdown__category__percentage">
            {{ focusData.dealAnalysis.companySize.percentage }}%
          </div>
        </div>

        <!-- type -->
        <div class="report__deal-analysis__breakdown__category">
          <div class="report__deal-analysis__breakdown__category__title">
            {{ focusData.dealAnalysis.type.value }}
          </div>
          <div class="report__deal-analysis__breakdown__category__graphic">
            <ProgressBar
              :percentComplete="focusData.dealAnalysis.type.percentage"
              :centerPiece="false"
              :widthValue="50"
              :widthUnit="'rem'"
            />
          </div>
          <div class="report__deal-analysis__breakdown__category__percentage">
            {{ focusData.dealAnalysis.type.percentage }}%
          </div>
        </div>

        <!-- competitor -->
        <div class="report__deal-analysis__breakdown__category">
          <div class="report__deal-analysis__breakdown__category__title">
            {{ focusData.dealAnalysis.competitor.value | constantToCapitalized }} competitor
          </div>
          <div class="report__deal-analysis__breakdown__category__graphic">
            <ProgressBar
              :percentComplete="focusData.dealAnalysis.competitor.percentage"
              :centerPiece="false"
              :widthValue="50"
              :widthUnit="'rem'"
            />
          </div>
          <div class="report__deal-analysis__breakdown__category__percentage">
            {{ focusData.dealAnalysis.competitor.percentage }}%
          </div>
        </div>
      </div>
      <div class="report__deal-analysis__none-closed" v-else>
        No deals closed.
      </div>
    </div>
  </div>
</template>

<script>
import Lead from '@/services/leads'
import PerformanceReport from '@/services/performanceReports'
import { constantToCapitalized } from '@/services/utils'

import ProgressBar from '@/components/reports/ProgressBar'

export default {
  name: 'RepresentativePerformanceReport',
  props: {
    report: {
      required: true,
      type: PerformanceReport,
    },
  },
  components: {
    ProgressBar,
  },
  data() {
    return {
      Lead,
      constantToCapitalized,
    }
  },
  methods: {
    getTrendStat(field) {
      const focus = this.focusData[field]
      const typical = this.typicalData[field]
      if (!typical) {
        return 0
      }
      // | a - b | / b
      const proportion = Math.abs(focus - typical) / typical
      // Return as rounded percentage
      return Math.round(proportion * 100)
    },
    getTrendIcon(field) {
      const focus = this.focusData[field]
      const typical = this.typicalData[field]
      if (!typical) {
        return 'no-trend.svg'
      }
      if (typical === focus) {
        return 'no-trend.svg'
      }
      if (focus > typical) {
        return 'trending-up.svg'
      } else {
        return 'trending-down.svg'
      }
    },
  },
  computed: {
    dateRangePresetFocus() {
      // Remove 'THE' from the dateRangePreset constant (e.g. THIS_MONTH)
      return this.report.dateRangePreset.split('_')[1]
    },
    representative() {
      return this.report.representativeRef
    },
    dealAnalysisDisplayName() {
      // Name to display in the 'Deal Analysis' portion of report
      if (this.representative.firstName.trim()) {
        return this.representative.firstName
      }
      if (this.representative.lastName.trim()) {
        return this.representative.lastName
      }
      return this.representative.email
    },
    focusData() {
      return this.report.data.representative.focus
    },
    typicalData() {
      return this.report.data.representative.typical
    },
    organizationTypicalData() {
      return this.report.data.organization.typical
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
.report {
  padding: 2rem 3rem;

  &__summary-container {
    border: 1px solid $soft-gray;
    border-radius: 7px;
    margin-bottom: 2rem;
  }

  &__middle-row {
    display: flex;
    flex-flow: row;
    margin-bottom: 2rem;
  }

  &__deal-analysis {
    border: 1px solid $soft-gray;
    border-radius: 7px;
    padding: 1rem;
  }
}

.report__summary-container {
  &__report-focus {
    flex-grow: 1;
    display: flex;
    flex-flow: row;
    max-height: 1rem;
    overflow: visible;
    padding: 0.5rem;

    img {
      height: 4rem;
      width: 4rem;
      border-radius: 50%;
      border: 2px solid $yellow;
      object-fit: cover;
    }

    &__date-range-preset {
      font-weight: 600;
      padding: 0 0.5rem;
    }

    &__representative-info {
      font-weight: 600;
      color: $mid-gray;
      padding: 0 0.5rem;
    }
  }

  &__summary-table {
    width: 100%;
    border-spacing: 0;
    table-layout: fixed;

    &__focus-row {
      color: $dark-green;
      font-weight: 600;
    }

    &__title-cell {
      padding: 0.6rem 0;
      text-align: left;
    }

    &__label-cell {
      padding: 0.6rem;
    }

    &__statistic-cell {
      padding: 0.6rem 0;

      &__container {
        display: flex;
        flex-flow: row;

        &__trend {
          margin-left: 1rem;
          &__icon {
            height: 0.7rem;
          }
          &__stat {
            color: $mid-gray;
            font-size: 0.8rem;
          }
        }
      }
    }
  }
}

.report__middle-row {
  &__card {
    border: 1px solid $soft-gray;
    border-radius: 7px;
    height: 15rem;
    width: 22rem;

    &__title {
    }

    &__summary {
    }
  }

  & > &__card:first-of-type {
    margin-right: auto;
  }

  & > &__card:last-of-type {
    margin-left: auto;
  }
}

.report__deal-analysis {
  &__title {
    font-weight: 600;
    padding-bottom: 0.4rem;
  }

  &__summary {
    color: $mid-gray;
    margin-bottom: 0.5rem;
  }

  &__none-closed {
    color: $mid-gray;
    text-align: center;
    padding: 0.5rem;
  }

  &__breakdown {
    &__category {
      display: flex;
      flex-flow: row;
      align-items: center;
      padding: 0.5rem 0;

      &__title {
        font-weight: 600;
        width: 15%;
      }

      &__percentage {
        font-weight: 600;
        color: $mid-gray;
        padding-left: 1rem;
      }
    }
  }
}

.soft-gray-background {
  background-color: $soft-gray;

  & > .report__summary-container__summary-table__statistic-cell:last-of-type {
    box-shadow: 2px 0 0 -1px $soft-gray;
  }

  & > .report__summary-container__summary-table__title-cell:last-of-type {
    box-shadow: 2px 0 0 -1px $soft-gray;
  }
}
</style>
