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
          {{ focusRepDisplayNameLong }}
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
            {{ typicalData.activitiesCount | roundToOneDecimalPlace }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.actionsCount | roundToOneDecimalPlace }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.incomingMessagesCount | roundToOneDecimalPlace }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.forecastAmount | currencyNoCents }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ typicalData.dealsClosedCount | roundToOneDecimalPlace }}
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
            {{ organizationTypicalData.activitiesCount | roundToOneDecimalPlace }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.actionsCount | roundToOneDecimalPlace }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.incomingMessagesCount | roundToOneDecimalPlace }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.forecastAmount | currencyNoCents }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.dealsClosedCount | roundToOneDecimalPlace }}
          </td>
          <td class="report__summary-container__summary-table__statistic-cell">
            {{ organizationTypicalData.amountClosed | currencyNoCents }}
          </td>
        </tr>
      </table>
    </div>

    <div class="report__middle-row">
      <div class="report__middle-row__card">
        <div class="report__middle-row__card__title">
          Forecast
        </div>
        <div class="report__middle-row__card__summary">
          {{ focusRepDisplayNameShort }} added {{ focusData.forecastTableAdditions }} opportunities
          to the forecast.
          {{
            forecastAdditionsProportion !== localConstants.NA
              ? `That is ${forecastAdditionsProportion} the typical number.`
              : 'Since the typical number of additions is N/A, no trend can be determined.'
          }}
        </div>
        <div class="report__middle-row__card__content">
          <div class="report__middle-row__card__content__row">
            <div
              style="font-weight: 600; font-size: 3rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              {{ forecastAdditionsProportion }}
            </div>
            <img
              style="margin: 0 auto 0 1rem; height: 3rem; width: 3rem;"
              :src="require(`@/assets/images/${forecastAdditionsIcon}`)"
            />
          </div>
        </div>
      </div>
      <div class="report__middle-row__card">
        <div class="report__middle-row__card__title">
          Top Opportunities
        </div>
        <div class="report__middle-row__card__summary">
          {{ topOpportunitiesSummary }}
        </div>
        <div class="report__middle-row__card__content">
          <div
            v-for="(lead, idx) in focusTopOpportunities"
            :key="idx"
            class="report__middle-row__card__content__row"
            :class="{ 'soft-gray-background': idx % 2 !== 0 }"
          >
            <div style="font-weight: 600; width: 49%;">
              {{ lead.title }}
            </div>
            <div style="font-weight: 600; margin: 0 1rem 0 auto;" class="mid-gray-font">
              {{ lead.status | constantToCapitalized }},
              {{ lead.status === Lead.CLOSED ? lead.closingAmount : lead.amount | currencyNoCents }}
            </div>
          </div>
          <div
            v-for="n in 3 - focusTopOpportunities.length"
            :key="focusTopOpportunities.length - 1 + n"
            class="report__middle-row__card__content__row"
            :class="{ 'soft-gray-background': (focusTopOpportunities.length + n) % 2 == 0 }"
            style="justify-content: center;"
          >
            --
          </div>
        </div>
      </div>
      <div class="report__middle-row__card">
        <div class="report__middle-row__card__title">
          Sales Cycle
        </div>
        <div class="report__middle-row__card__summary" v-if="isNull(focusData.salesCycle)">
          {{ focusRepDisplayNameShort }}'s sales cycle trend could not be determined for
          {{ report.dateRangePreset | constantToCapitalized }}.
        </div>
        <div class="report__middle-row__card__summary" v-else>
          {{ focusRepDisplayNameShort }}'s sales cycle
          {{ focusData.salesCycle > Number(typicalData.salesCycle) ? 'extended' : 'contracted' }}
          this month to {{ focusData.salesCycle | roundToOneDecimalPlace }} days.
        </div>
        <div class="report__middle-row__card__content">
          <div>
            <div style="margin: 0 0 0.5rem 0;" class="report__middle-row__card__content__row">
              <div style="font-weight: 600;">
                {{ report.dateRangePreset | constantToCapitalized }}
              </div>
              <div
                class="mid-gray-font"
                style="font-weight: 600; margin-left: auto;"
                v-if="isNull(focusData.salesCycle)"
              >
                N/A
              </div>
              <div class="mid-gray-font" style="font-weight: 600; margin-left: auto;" v-else>
                {{ focusData.salesCycle | roundToOneDecimalPlace }} days
              </div>
            </div>
            <div style="padding: 0 1rem;">
              <ProgressBar
                :percentComplete="
                  generateProgressBarValue(focusData.salesCycle, typicalData.salesCycle)
                "
                :centerPiece="false"
                :widthValue="100"
                :widthUnit="'%'"
              />
            </div>
          </div>
          <div>
            <div style="margin: 2rem 0 0.5rem 0;" class="report__middle-row__card__content__row">
              <div style="font-weight: 600;">
                Typical {{ dateRangePresetFocus | constantToCapitalized }}
              </div>
              <div class="mid-gray-font" style="font-weight: 600; margin-left: auto;">
                {{ typicalData.salesCycle ? `${typicalData.salesCycle} days` : localConstants.NA }}
              </div>
            </div>
            <div style="padding: 0 1rem;">
              <ProgressBar
                :percentComplete="
                  generateProgressBarValue(typicalData.salesCycle, focusData.salesCycle)
                "
                :centerPiece="false"
                :widthValue="100"
                :widthUnit="'%'"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="report__middle-row">
      <div class="report__middle-row__card">
        <div class="report__middle-row__card__title">
          Actions to Close an Opportunity
        </div>
        <div
          class="report__middle-row__card__summary"
          v-if="isNull(focusData.actionsToCloseOpportunity.average)"
        >
          An insight could not be generated because no opportunities were closed
          {{ report.dateRangePreset | constantToCapitalized }}.
        </div>
        <div class="report__middle-row__card__summary" v-else>
          {{ focusRepDisplayNameShort }} took
          {{ focusData.actionsToCloseOpportunity.average | roundToOneDecimalPlace }} actions to
          close a deal.
          {{
            focusData.actionsToCloseOpportunity.average
              ? `${focusData.actionsToCloseOpportunity.mostPerformed} was the most frequently performed
          action.`
              : null
          }}
        </div>

        <div class="report__middle-row__card__content">
          <div class="report__middle-row__card__content__row soft-gray-background">
            <div style="font-weight: 600; width: 65%;">
              Average Actions on Closed<br />
              Opportunities {{ report.dateRangePreset | constantToCapitalized }}
            </div>
            <div
              v-if="isNull(focusData.actionsToCloseOpportunity.average)"
              style="font-weight: 600; font-size: 1.5rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              N/A
            </div>
            <div
              v-else
              style="font-weight: 600; font-size: 1.5rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              {{ focusData.actionsToCloseOpportunity.average | roundToOneDecimalPlace }}
            </div>
          </div>
          <div class="report__middle-row__card__content__row">
            <div style="font-weight: 600; width: 65%;">
              Typical Average Actions on<br />
              Closed Opportunities
            </div>
            <div
              v-if="isNull(typicalData.actionsToCloseOpportunity)"
              style="font-weight: 600; font-size: 1.5rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              N/A
            </div>
            <div
              v-else
              style="font-weight: 600; font-size: 1.5rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              {{ typicalData.actionsToCloseOpportunity | roundToOneDecimalPlace }}
            </div>
          </div>
        </div>
      </div>
      <div class="report__middle-row__card">
        <div class="report__middle-row__card__title">
          ACV
        </div>
        <div class="report__middle-row__card__summary" v-if="isNull(focusData.ACV)">
          An insight could not be generated because {{ focusRepDisplayNameShort }}'s ACV for
          {{ report.dateRangePreset | constantToCapitalized }} is N/A.
        </div>
        <div class="report__middle-row__card__summary" v-else>
          {{ focusRepDisplayNameShort }}'s ACV
          {{
            focusData.ACV > Number(typicalData.ACV)
              ? 'increased'
              : focusData.ACV < Number(typicalData.ACV)
              ? 'decreased'
              : 'steadied'
          }}
          {{ report.dateRangePreset | constantToCapitalized }} to
          {{ focusData.ACV | currencyNoCents }} from {{ typicalData.ACV || localConstants.NA }}.
        </div>
        <div class="report__middle-row__card__content">
          <div class="report__middle-row__card__content__row soft-gray-background">
            <div style="font-weight: 600; width: 40%;">
              ACV {{ report.dateRangePreset | constantToCapitalized }}
            </div>
            <div
              v-if="isNull(focusData.ACV)"
              style="font-weight: 600; font-size: 1.5rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              N/A
            </div>
            <div
              v-else
              style="font-weight: 600; font-size: 1.5rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              {{ focusData.ACV | currencyNoCents }}
            </div>
          </div>
          <div class="report__middle-row__card__content__row">
            <div style="font-weight: 600; width: 40%;">
              Typical ACV
            </div>
            <div
              v-if="isNull(typicalData.ACV)"
              style="font-weight: 600; font-size: 1.5rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              N/A
            </div>
            <div
              v-else
              style="font-weight: 600; font-size: 1.5rem; margin: 0 1rem 0 auto;"
              class="dark-green-font"
            >
              {{ typicalData.ACV | currencyNoCents }}
            </div>
          </div>
        </div>
      </div>
      <div class="report__middle-row__card">
        <div class="report__middle-row__card__title">
          Top Performers
        </div>
        <div class="report__middle-row__card__summary">
          {{ focusRepDisplayNameShort }} is #{{ focusRepPerformanceRank }} in overall performance.
        </div>
        <div class="report__middle-row__card__content">
          <div
            class="report__middle-row__card__content__row"
            style="align-items: unset; padding-top: 1rem;"
          >
            <div
              v-for="(rep, idx) in organizationFocusData.topPerformers"
              :key="idx"
              class="report__middle-row__card__content__column"
              style="justify-content: unset;"
            >
              <img
                class="report__middle-row__card__content__column__img"
                :src="rep.profilePhoto ? rep.profilePhoto : require('@/assets/images/camera.svg')"
              />
              <div class="report__middle-row__card__content__column__text">
                {{ rep.rank }}. {{ generateRepDisplayName(rep) }}
              </div>
              <div class="report__middle-row__card__content__column__text">
                {{ rep.ACV | currencyNoCents }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="report__deal-analysis">
      <div class="report__deal-analysis__title">
        Deal Analysis
      </div>
      <div class="report__deal-analysis__summary" v-if="focusData.dealsClosedCount">
        {{ dealAnalysisSummary }}
      </div>
      <div class="report__deal-analysis__breakdown" v-if="focusData.dealsClosedCount">
        <!-- Industry -->
        <div class="report__deal-analysis__breakdown__category">
          <div
            v-if="isNull(focusData.dealAnalysis.industry.value)"
            class="report__deal-analysis__breakdown__category__title"
          >
            Industry: N/A
          </div>
          <div v-else class="report__deal-analysis__breakdown__category__title">
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
            {{
              isNull(focusData.dealAnalysis.geography.value)
                ? 'Geography: N/A'
                : focusData.dealAnalysis.geography.value
            }}
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
            {{
              isNull(focusData.dealAnalysis.companySize.value)
                ? 'Company Size: N/A'
                : focusData.dealAnalysis.companySize.value
            }}
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
            {{
              isNull(focusData.dealAnalysis.type.value)
                ? 'Type: N/A'
                : focusData.dealAnalysis.type.value === localConstants.OTHER
                ? 'Type: Other'
                : focusData.dealAnalysis.type.value
            }}
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
            {{
              isNull(focusData.dealAnalysis.competitor.value)
                ? 'Competitor: N/A'
                : focusData.dealAnalysis.competitor.value === localConstants.YES
                ? 'Competitor Switch'
                : focusData.dealAnalysis.competitor.value === localConstants.NO
                ? 'Not using a competitor'
                : 'Other (Competitor)'
            }}
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
import pluralize from 'pluralize'
import Lead from '@/services/leads'
import PerformanceReport from '@/services/performanceReports'
import { constantToCapitalized, isNull } from '@/services/utils'
import { roundToOneDecimalPlace } from '@/services/filters'
import ProgressBar from '@/components/reports/ProgressBar'

const NA = 'N/A'
const OTHER = 'OTHER'
const YES = 'YES'
const NO = 'NO'

const localConstants = {
  NA,
  OTHER,
  YES,
  NO,
}

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
      localConstants,
      constantToCapitalized,
      isNull,
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
    topOpportunityMapper(status) {
      return lead => {
        return { ...lead, status }
      }
    },
    generateRepDisplayName(rep) {
      return rep.fullName.trim() ? rep.fullName : rep.email.slice(0, 10) + '...'
    },
    generateProgressBarValue(currentValue, comparativeValue) {
      // To be used with sales cycle statistics
      if (isNull(currentValue)) {
        return 0
      }
      if (isNull(comparativeValue) || currentValue > comparativeValue) {
        return 100
      }
      return (currentValue / comparativeValue) * 100
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
    focusRepDisplayNameLong() {
      return this.representative.fullName.trim()
        ? this.representative.fullName
        : this.representative.email
    },
    focusRepDisplayNameShort() {
      if (this.representative.firstName.trim()) {
        return this.representative.firstName
      }
      if (this.representative.lastName.trim()) {
        return this.representative.lastName
      }
      return this.representative.email
    },
    focusTopOpportunities() {
      const { CLOSED, VERBAL, STRONG, '50/50': FIFTY_FIFTY } = this.focusData.topOpportunities
      return [
        ...CLOSED.map(this.topOpportunityMapper('CLOSED')),
        ...VERBAL.map(this.topOpportunityMapper('VERBAL')),
        ...STRONG.map(this.topOpportunityMapper('STRONG')),
        ...FIFTY_FIFTY.map(this.topOpportunityMapper('50/50')),
      ]
    },
    topOpportunitiesSummary() {
      // this.focusRepDisplayNameShort
      const { CLOSED, VERBAL, STRONG, '50/50': FIFTY_FIFTY } = this.focusData.topOpportunities
      let str = `${this.focusRepDisplayNameShort} closed ${CLOSED.length} ${pluralize(
        'deal',
        CLOSED.length,
      )}`
      if (VERBAL.length) {
        str += `${STRONG.length || FIFTY_FIFTY.length ? ', ' : 'and'} moved ${
          VERBAL.length
        } ${pluralize('opportunity', VERBAL.length)} to verbal`
      }
      if (STRONG.length) {
        str += `${FIFTY_FIFTY.length ? ', ' : 'and'} moved ${STRONG.length} ${pluralize(
          'opportunity',
          STRONG.length,
        )} to strong`
      }
      if (FIFTY_FIFTY.length) {
        str += `${VERBAL.length || STRONG.length ? ',' : ''} and moved ${STRONG.length} ${pluralize(
          'opportunity',
          STRONG.length,
        )} to strong`
      }
      return str + '.'
    },
    canGenerateDealAnalysisSummary() {
      let { industry, geography, companySize, type, competitor } = this.focusData.dealAnalysis
      return !!(industry || geography || companySize || type || competitor)
    },
    dealAnalysisSummary() {
      if (!this.canGenerateDealAnalysisSummary) {
        return `Insights regarding ${this.focusRepDisplayNameShort}'s closed deals could not be generated because the needed data is N/A.`
      }
      let str = `${this.focusRepDisplayNameShort} closed mostly`
      if (this.focusData.dealAnalysis.industry.value) {
        str += ` ${constantToCapitalized(this.focusData.dealAnalysis.industry.value)}`
      }
      str += ' opportunities'
      if (this.focusData.dealAnalysis.geography.value) {
        str += ` in ${this.focusData.dealAnalysis.geography.value},`
      }
      if (this.focusData.dealAnalysis.companySize.value) {
        str += ` with ${this.focusData.dealAnalysis.companySize.value} employees`
      }
      str += '.'
      if (this.focusData.dealAnalysis.type.value) {
        let value =
          this.focusData.dealAnalysis.type.value === this.localConstants.OTHER
            ? constantToCapitalized(this.focusData.dealAnalysis.type.value)
            : this.focusData.dealAnalysis.type.value
        str += ` They were of type ${value}`
      }
      if (this.focusData.dealAnalysis.competitor.value) {
        if (this.focusData.dealAnalysis.competitor.value !== this.localConstants.OTHER) {
          let usingCompetitor =
            this.focusData.dealAnalysis.competitor.value === this.localConstants.YES
          str += usingCompetitor ? ', using a competitor' : ', not using a competitor'
        }
      }
      str += '.'
      return str
    },
    focusRepPerformanceRank() {
      for (let idx in this.organizationFocusData.topPerformers) {
        const rep = this.organizationFocusData.topPerformers[idx]
        if (rep.id === this.representative.id) {
          return rep.rank
        }
      }
      return 0
    },
    forecastAdditionsProportion() {
      const focus = this.focusData.forecastTableAdditions
      const typical = this.typicalData.forecastTableAdditions
      if (!typical) {
        return focus || this.localConstants.NA
      }
      return roundToOneDecimalPlace(focus / typical)
    },
    forecastAdditionsIcon() {
      if (this.forecastAdditionsProportion > 1) {
        return 'trending-up.svg'
      }
      if (this.forecastAdditionsProportion < 1) {
        return 'trending-down.svg'
      }
      return 'no-trend.svg'
    },
    focusData() {
      return this.report.data.representative.focus
    },
    typicalData() {
      return this.report.data.representative.typical
    },
    organizationFocusData() {
      return this.report.data.organization.focus
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
    min-width: 22rem;
    width: 30%;
    max-width: 35rem;
    display: flex;
    flex-flow: column;

    &__title {
      font-weight: 600;
      margin-bottom: 0.5rem;
      padding: 1rem 1rem 0 1rem;
    }

    &__summary {
      font-weight: 600;
      color: $mid-gray;
      padding: 0 1rem 0.5rem 1rem;
      height: 3.5rem;
      overflow-y: auto;
    }

    &__content {
      flex-grow: 1;
      display: flex;
      flex-flow: column;

      &__row {
        flex-grow: 1;
        display: flex;
        flex-flow: row;
        align-items: center;
        padding: 0 1rem;
      }

      &__column {
        flex-grow: 1;
        display: flex;
        flex-flow: column;
        align-items: center;
        // padding: 0 1rem;

        &__img {
          height: 3.5rem;
          width: 3.5rem;
          border-radius: 50%;
          border: 2px solid $yellow;
          object-fit: cover;
        }

        &__text {
          font-size: 0.8rem;
          color: $mid-gray;
          padding-top: 0.5rem;
        }
      }
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
    font-weight: 600;
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

.dark-green-font {
  color: $dark-green;
}

.mid-gray-font {
  color: $mid-gray;
}
</style>
