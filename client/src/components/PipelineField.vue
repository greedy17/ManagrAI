<template>
  <div>
    <div v-if="dataType">
      <p v-if="apiName !== 'Amount' && dataType !== 'Date'">
        {{ fieldData ? fieldData : '---' }}
      </p>

      <p v-else-if="dataType === 'Date'">
        {{ fieldData ? formatDate(fieldData) : '---' }}
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
  },
  props: {
    apiName: {
      type: String,
    },
    dataType: {
      type: String,
    },
    fieldData: {},
  },
}
</script>
<style scoped>
</style>