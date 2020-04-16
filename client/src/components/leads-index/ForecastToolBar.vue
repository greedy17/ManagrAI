<template>
  <div class="toolbar">
    <div class="header section-shadow">
      KPIs
    </div>
    <div class="single-statistic section-shadow">
      <span class="title">Total Closed Value</span>
      <span class="statistic"> {{ totalClosedValue }}</span>
    </div>
    <div class="single-statistic section-shadow">
      <span class="title">Average Contract Value</span>
      <span class="statistic"> {{ averageContractValue }}</span>
    </div>
    <div class="statistics-container section-shadow">container</div>
    <div class="single-statistic section-shadow">
      <span class="title">Forecast</span>
      <span class="statistic"> {{ computedForecast }}</span>
    </div>
  </div>
</template>

<script>
import currencyFormatter from '@/services/currencyFormatter'
const statusEnums = ['Ready', 'Trial', 'Demo', 'Waiting']
const forecastEnums = ['50/50', 'NA', 'Strong', 'Future', 'Verbal']
const exampleReps = [
  { id: 1, name: 'Marcy Ewald' },
  { id: 2, name: 'Pari Baker' },
  { id: 3, name: 'Bruno Garcia Gonzalez' },
]

export default {
  name: 'ForecastToolBar',
  components: {},
  data() {
    return {
      statusEnums,
      forecastEnums,
      reps: exampleReps,
    }
  },
  computed: {
    totalClosedValue() {
      return currencyFormatter.format(33000)
    },
    averageContractValue() {
      return currencyFormatter.format(12000)
    },
    computedForecast() {
      return currencyFormatter.format(747000)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.toolbar {
  @include disable-text-select();
  background-color: $white;
  width: 78%;
  height: auto;
  display: flex;
  flex-flow: column;

  .section-shadow {
    box-shadow: 0 1px 0 0 $soft-gray;
  }
}

.toolbar,
.toolbar > * {
  font-family: $base-font-family, $backup-base-font-family;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 14px;
}

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
  height: 10rem;
}
</style>
