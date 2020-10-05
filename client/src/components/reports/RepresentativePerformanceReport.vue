<template>
  <div class="report">
    <div class="report__summary-container">
      <div class="report-focus">
        <img
          :src="
            representative.profilePhoto
              ? representative.profilePhoto
              : require('@/assets/images/camera.svg')
          "
        />
        <div class="report-focus__date-range-preset">
          {{ report.dateRangePreset | constantToCapitalized }}
        </div>
        <div class="report-focus__representative-info">
          {{ representative.fullName.trim() ? representative.fullName : representative.email }}
        </div>
      </div>
      <table class="summary-table">
        <!-- header row -->
        <tr class="summary-table__header-row">
          <th></th>
          <th class="summary-table__title-cell">Activities</th>
          <th class="summary-table__title-cell">Actions</th>
          <th class="summary-table__title-cell">Incoming<br />Messages</th>
          <th class="summary-table__title-cell">Forecast<br />Amount</th>
          <th class="summary-table__title-cell">Deals<br />Closed</th>
          <th class="summary-table__title-cell">Amount<br />Closed</th>
        </tr>

        <!-- content row #1 -->
        <tr class="summary-table__content-row summary-table__focus-row">
          <td class="summary-table__label-cell">
            {{ report.dateRangePreset | constantToCapitalized }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ focusData.activitiesCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ focusData.actionsCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ focusData.incomingMessagesCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ focusData.forecastAmount | currencyNoCents }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ focusData.dealsClosedCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ focusData.amountClosed | currencyNoCents }}
          </td>
        </tr>

        <!-- content row #2 -->
        <tr class="summary-table__content-row">
          <td class="summary-table__label-cell">
            Typical {{ dateRangePresetFocus | constantToCapitalized }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ typicalData.activitiesCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ typicalData.actionsCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ typicalData.incomingMessagesCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ typicalData.forecastAmount | currencyNoCents }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ typicalData.dealsClosedCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ typicalData.amountClosed | currencyNoCents }}
          </td>
        </tr>

        <!-- content row #3 -->
        <tr class="summary-table__content-row">
          <td class="summary-table__label-cell">
            Typical Team {{ dateRangePresetFocus | constantToCapitalized }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ organizationTypicalData.activitiesCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ organizationTypicalData.actionsCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ organizationTypicalData.incomingMessagesCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ organizationTypicalData.forecastAmount | currencyNoCents }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ organizationTypicalData.dealsClosedCount }}
          </td>
          <td class="summary-table__statistic-cell">
            {{ organizationTypicalData.amountClosed | currencyNoCents }}
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import PerformanceReport from '@/services/performanceReports'

export default {
  name: 'RepresentativePerformanceReport',
  props: {
    report: {
      required: true,
      type: PerformanceReport,
    },
  },
  created() {},
  methods: {},
  computed: {
    dateRangePresetFocus() {
      // Remove 'THE' from the dateRangePreset constant (e.g. THIS_MONTH)
      return this.report.dateRangePreset.split('_')[1]
    },
    representative() {
      return this.report.representativeRef
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

.report-focus {
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

.summary-table {
  width: 100%;

  &__focus-row {
    color: $dark-green;
    font-weight: 600;
  }

  &__title-cell {
    padding: 0.6rem 0;
  }

  &__label-cell {
    padding: 0.6rem;
  }

  &__statistic-cell {
    text-align: center;
    padding: 0.6rem 0;
  }
}
</style>
