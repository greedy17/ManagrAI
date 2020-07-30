<template>
  <div class="lists-container">
    <List
      v-if="lists[Forecast.FIFTY_FIFTY].list.length"
      :title="capitalizeWord(Forecast.FIFTY_FIFTY)"
      :collection="lists[Forecast.FIFTY_FIFTY]"
      @move-lead-in-forecast-list="moveLeadInForecastList"
    />
    <List
      v-if="lists[Forecast.STRONG].list.length"
      :title="capitalizeWord(Forecast.STRONG)"
      :collection="lists[Forecast.STRONG]"
      @move-lead-in-forecast-list="moveLeadInForecastList"
    />
    <List
      v-if="lists[Forecast.VERBAL].list.length"
      :title="capitalizeWord(Forecast.VERBAL)"
      :collection="lists[Forecast.VERBAL]"
      @move-lead-in-forecast-list="moveLeadInForecastList"
    />
    <List
      v-if="lists[Forecast.FUTURE].list.length"
      :title="capitalizeWord(Forecast.FUTURE)"
      :collection="lists[Forecast.FUTURE]"
      @move-lead-in-forecast-list="moveLeadInForecastList"
    />
    <List
      v-if="lists[Forecast.UNFORECASTED].list.length"
      :title="capitalizeWord(Forecast.UNFORECASTED)"
      :collection="lists[Forecast.UNFORECASTED]"
      @move-lead-in-forecast-list="moveLeadInForecastList"
    />
    <List
      v-if="lists[Forecast.CLOSED].list.length"
      :title="'Deals'"
      :collection="lists[Forecast.CLOSED]"
      @move-lead-in-forecast-list="moveLeadInForecastList"
    />
  </div>
</template>

<script>
import moment from 'moment'
import List from '@/components/forecast/List'
import Forecast from '@/services/forecasts'
import { capitalizeWord } from '@/services/utils'

function listSorter(firstForecast, secondForecast) {
  // Sorting must be by Lead.expectedCloseDate
  // tie break on alphabetical Lead.title
  // nulls last
  let firstMoment = moment(firstForecast.leadRef.expectedCloseDate)
  let secondMoment = moment(secondForecast.leadRef.expectedCloseDate)
  let bothValid = firstMoment.isValid() && secondMoment.isValid()
  let oneValid = firstMoment.isValid() || secondMoment.isValid()

  if (bothValid) {
    if (firstMoment > secondMoment) {
      return 1
    }
    if (secondMoment > firstMoment) {
      return -1
    }
    // check by alphabetical beyond this point
    if (firstForecast.leadRef.title.toLowerCase() > secondForecast.leadRef.title.toLowerCase()) {
      return 1
    }
    if (secondForecast.leadRef.title.toLowerCase() > firstForecast.leadRef.title.toLowerCase()) {
      return -1
    }
    return 0
  }

  if (oneValid) {
    if (firstMoment.isValid()) {
      return -1
    } else {
      return 1
    }
  }

  // beyond this point neither is valid, so sort alphabetically
  if (firstForecast.leadRef.title.toLowerCase() > secondForecast.leadRef.title.toLowerCase()) {
    return 1
  }
  if (secondForecast.leadRef.title.toLowerCase() > firstForecast.leadRef.title.toLowerCase()) {
    return -1
  }
  return 0
}

export default {
  name: 'ListsContainer',
  props: {
    lists: {
      type: Object,
      required: true,
    },
  },
  components: {
    List,
  },
  data() {
    return {
      Forecast,
    }
  },
  methods: {
    capitalizeWord,
    moveLeadInForecastList(payload) {
      this.$emit('trigger-refresh-kpis')
      let { forecast, from, to } = payload
      // clean up 'Unforecasted'/'NA' client/server inconsistency
      to = to == Forecast.NA ? Forecast.UNFORECASTED : to
      from = from == Forecast.NA ? Forecast.UNFORECASTED : from
      let { leadRef } = forecast
      // remove from proper collection
      this.lists[from].list = this.lists[from].list.filter(f => f.leadRef.id != leadRef.id)
      this.lists[from].pagination.totalCount -= 1
      // add to proper collection, sort
      let newCollectionList = [...this.lists[to].list, forecast]
      newCollectionList.sort(listSorter)
      this.lists[to].list = newCollectionList
      this.lists[to].pagination.totalCount += 1
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.lists-container {
  @include standard-border();
  background-color: $white;
  padding-top: 1vh;
  padding-bottom: 1vh;
}
</style>
