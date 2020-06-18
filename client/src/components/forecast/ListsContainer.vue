<template>
  <div class="lists-container">
    <List
      v-for="(forecast, index) in FORECASTS"
      :key="index"
      :title="capitalizeWord(forecast)"
      :collection="lists[forecast]"
      @move-lead-in-forecast-list="moveLeadInForecastList"
    />
  </div>
</template>

<script>
import List from '@/components/forecast/List'
import { capitalizeWord } from '@/services/utils'

const FIFTY_FIFTY = '50/50'
const STRONG = 'STRONG'
const VERBAL = 'VERBAL'
const FUTURE = 'FUTURE'
const UNFORECASTED = 'UNFORECASTED'

const FORECASTS = [FIFTY_FIFTY, STRONG, VERBAL, FUTURE, UNFORECASTED]

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
      FORECASTS,
    }
  },
  methods: {
    capitalizeWord,
    moveLeadInForecastList(payload) {
      let { forecast, from, to } = payload
      // clean up 'Unforecasted'/'NA' client/server inconsistency
      to = to == 'NA' ? 'UNFORECASTED' : to
      from = from == 'NA' ? 'UNFORECASTED' : from
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
      // a must be equal to b
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
