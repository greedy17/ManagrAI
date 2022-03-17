<template>
  <div>
    <div v-if="dataType">
      <p v-if="apiName !== 'Amount' && dataType !== 'Date' && apiName !== 'StageName'">
        {{ fieldData ? fieldData : '---' }}
      </p>

      <p v-else-if="dataType === 'Date'">
        {{ fieldData ? formatDate(fieldData) : '---' }}
      </p>

      <p class="flex-columned" v-else-if="apiName === 'StageName'">
        {{ fieldData ? fieldData : '---' }}
        <span class="daysinstage">{{
          fieldData ? 'Days in Stage: ' + getDaysInStage(lastStageUpdate) : ''
        }}</span>
      </p>

      <p style="color: #199e54" v-else>
        {{ fieldData ? formatCash(fieldData) : '$ --- ---' }}
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
      console.log(this.currentDay.getTime())
      console.log(newDate.getTime())
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
  },
}
</script>
<style lang="scss" >
@import '@/styles/variables';
@import '@/styles/buttons';

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
</style>