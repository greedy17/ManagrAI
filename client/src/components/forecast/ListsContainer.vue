<template>
  <div class="lists-container">
    <List
      v-for="(forecast, index) in FORECASTS"
      :key="index"
      :title="capitalizeWord(forecast)"
      :collection="lists[forecast]"
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
