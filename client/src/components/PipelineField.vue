<template>
  <div class="red">
    <div v-if="dataType">
      <p
        v-if="
          apiName !== 'Amount' &&
          dataType !== 'Date' &&
          dataType !== 'DateTime' &&
          apiName !== 'StageName'
        "
        :class="fieldData ? '' : 'blank'"
      >
        {{ fieldData ? fieldData : '' }}
      </p>

      <p :class="fieldData ? '' : 'blank'" v-else-if="dataType === 'Date'">
        {{ fieldData ? formatDate(fieldData) : '' }}
      </p>

      <p :class="fieldData ? '' : 'blank'" v-else-if="dataType === 'DateTime'">
        {{ fieldData ? formatDateTime(fieldData) : '' }}
      </p>

      <p :class="fieldData ? 'flex-columned' : 'blank'" v-else-if="apiName === 'StageName'">
        {{ fieldData ? fieldData : '' }}
        <span class="daysinstage">{{
          fieldData
            ? 'Days in Stage: ' +
              (getDaysInStage(lastStageUpdate) > 19000 ? 0 : getDaysInStage(lastStageUpdate))
            : ''
        }}</span>
      </p>

      <p :class="fieldData ? 'cash' : 'blank'" v-else>
        {{ fieldData ? formatCash(fieldData) : '' }}
      </p>
    </div>
    <div v-else>
      <p>{{ fieldData }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineField',
  data() {
    return {}
  },
  methods: {
    formatDate(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      return input.replace(pattern, '$2/$3/$1')
    },
    formatCash(money) {
      let cash = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
      })
      if (money) {
        return cash.format(money)
      }
      return '-'
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    getDaysInStage(date) {
      let newDate = new Date(date)
      return Math.floor((this.currentDay.getTime() - newDate.getTime()) / (24 * 3600 * 1000))
    },
  },
  computed: {
    currentDay() {
      let date = new Date()
      return date
    },
  },
  props: {
    apiName: {
      type: String,
    },
    dataType: {
      type: String,
    },
    fieldData: {},
    lastStageUpdate: {},
    index: {},
  },
}
</script>
<style lang="scss" >
@import '@/styles/variables';
@import '@/styles/buttons';
.red {
  width: fit-content;
}
.flex-columned {
  display: flex;
  flex-direction: column;
}

.daysinstage {
  font-size: 11px;
  font-weight: bold;
  margin-top: 0.5rem;
  color: $gray;
}
.cash {
  color: $dark-green;
  background-color: $white-green;
  border-radius: 6px;
  padding: 5px;
}
.yellow {
  color: $yellow !important;
  background-color: #fdf7e6;
  border-radius: 6px;
  padding: 5px 1px;
}
</style>