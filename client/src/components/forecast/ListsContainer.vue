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
  </div>
</template>

<script>
import List from '@/components/forecast/List'
import Forecast from '@/services/forecasts'
import { capitalizeWord } from '@/services/utils'

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
      newCollectionList.sort(this.listSorter)
      this.lists[to].list = newCollectionList
      this.lists[to].pagination.totalCount += 1
    },
    listSorter(firstForecast, secondForecast) {
      if (firstForecast.leadRef.title.toLowerCase() > secondForecast.leadRef.title.toLowerCase()) {
        return 1
      }
      if (secondForecast.leadRef.title.toLowerCase() > firstForecast.leadRef.title.toLowerCase()) {
        return -1
      }
      return 0
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
