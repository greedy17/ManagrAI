<template>
  <div class="report">
    <div>Representative Performance Report</div>
    <div class="report__summary-container">
      <table class="summary-table" style="width:100%">
        <!-- header row -->
        <tr class="summary-table__header-row">
          <th></th>
          <th>Activities</th>
          <th>Actions</th>
          <th>Incoming<br />Messages</th>
          <th>Forecast<br />Amount</th>
          <th>Deals<br />Closed</th>
          <th>Amount<br />Closed</th>
        </tr>

        <!-- content row #1 -->
        <tr class="summary-table__content-row">
          <td class="summary-table__label-column-cell">
            {{ report.dateRangePreset | constantToCapitalized }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ focusData.activitiesCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ focusData.actionsCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ focusData.incomingMessagesCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ focusData.forecastAmount | currencyNoCents }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ focusData.dealsClosedCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ focusData.amountClosed | currencyNoCents }}
          </td>
        </tr>

        <!-- content row #2 -->
        <tr class="summary-table__content-row">
          <td class="summary-table__label-column-cell">
            Typical {{ dateRangePresetFocus | constantToCapitalized }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ typicalData.activitiesCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ typicalData.actionsCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ typicalData.incomingMessagesCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ typicalData.forecastAmount | currencyNoCents }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ typicalData.dealsClosedCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ typicalData.amountClosed | currencyNoCents }}
          </td>
        </tr>

        <!-- content row #3 -->
        <tr class="summary-table__content-row">
          <td class="summary-table__label-column-cell">
            Typical Team {{ dateRangePresetFocus | constantToCapitalized }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ organizationTypicalData.activitiesCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ organizationTypicalData.actionsCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ organizationTypicalData.incomingMessagesCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ organizationTypicalData.forecastAmount | currencyNoCents }}
          </td>
          <td class="summary-table__statistic-column-cell">
            {{ organizationTypicalData.dealsClosedCount }}
          </td>
          <td class="summary-table__statistic-column-cell">
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
</style>
