<template>
  <div class="red">
    <div v-if="dataType">
      <p
        v-if="
          apiName !== 'Amount' &&
          dataType !== 'Date' &&
          dataType !== 'DateTime' &&
          dataType !== 'Reference' &&
          apiName !== 'StageName' &&
          apiName !== 'dealstage'
        "
        v-html="fieldData ? fieldData : 'Empty'"
        class="blank"
        :class="!fieldData ? 'gray' : ''"
      >
        <!-- {{ fieldData ? fieldData : '' }} -->
      </p>

      <p class="blank" :class="!fieldData ? 'gray' : ''" v-else-if="dataType === 'Date'">
        {{ fieldData ? formatDate(fieldData) : 'Empty' }}
      </p>

      <p class="blank" :class="!fieldData ? 'gray' : ''" v-else-if="dataType === 'DateTime'">
        {{ fieldData ? formatDateTime(fieldData) : 'Empty' }}
      </p>

      <p class="blank" :class="!fieldData ? 'gray' : ''" v-else-if="dataType === 'Reference'">
        {{ fieldData && apiName ? referenceName : 'Empty' }}
      </p>

      <p
        class="flex-columned blank"
        :class="!fieldData ? 'gray' : ''"
        v-else-if="apiName === 'StageName'"
      >
        {{ fieldData ? fieldData : 'Empty' }}
        <!-- <span class="daysinstage">{{
          fieldData
            ? 'Days in Stage: ' +
              (getDaysInStage(lastStageUpdate) > 19000 ? 0 : getDaysInStage(lastStageUpdate))
            : ''
        }}</span> -->
      </p>
      <p
        class="flex-columned blank"
        :class="!fieldData ? 'gray' : ''"
        v-else-if="apiName === 'dealstage'"
      >
        {{field && opp && field.options[0][opp['secondary_data'].pipeline] ? 
          field.options[0][opp['secondary_data'].pipeline].stages.filter(stage => stage.id === opp['secondary_data'][field.apiName])[0].label
          :
          fieldData ? fieldData : 'Empty'
        }}
      </p>
      <p class="blank" :class="!fieldData ? 'gray' : ''" v-else>
        {{ fieldData ? formatCash(fieldData) : 'Empty' }}
      </p>
    </div>
    <div v-else class="blank" :class="!fieldData ? 'gray' : ''">
      <p>{{ fieldData }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineField',
  data() {
    return {
      referenceName: null,
    }
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    getReferenceName() {
      setTimeout(() => {
        const list = this.referenceOpts[this.apiName]
        for (let i = 0; i < list.length; i++) {
          if (list[i].id === this.fieldData) {
            this.referenceName = list[i].name
            return
          }
        }
      }, 1000)
    },
    formatDate(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      const replace = input.replace(pattern, '$2/$3/$1')
      return this.userCRM === 'HUBSPOT' ? replace.split('T')[0] : replace
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
    userCRM() {
      return this.$store.state.user.crm
    }
  },
  mounted() {
    if (this.referenceOpts && this.dataType === 'Reference') {
      this.getReferenceName()
    }
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
    referenceOpts: {},
    field: {},
    opp: {},
  },
}
</script>
<style lang="scss" >
@import '@/styles/variables';
@import '@/styles/buttons';
.red {
  // width: fit-content;
}
.flex-columned {
  display: flex;
  flex-direction: column;
}

.daysinstage {
  font-size: 11px;
  font-weight: bold;
  margin-top: 0.25rem;
  color: $gray;
}
.cash {
  color: $dark-green;
  background-color: $white-green;
  border-radius: 6px;
  padding: 8px 14px;
  letter-spacing: 0.75px;
}
.bg {
  color: $base-gray;
  background-color: $off-white;
  border-radius: 6px;
  padding: 8px 14px;
  letter-spacing: 0.75px;
  border: 1px solid $soft-gray;
}
.yellow {
  color: $yellow !important;
  background-color: #fdf7e6;
  border-radius: 6px;
  padding: 5px 1px;
}
.gray {
  color: $very-light-gray;
  font-style: italic;
  font-weight: 400;
  font-size: 12px;
}
.yellow {
  color: $yellow !important;
  background-color: #fdf7e6;
  border-radius: 6px;
  padding: 5px 1px;
}
.blank {
  // margin: 3px 0;
}
</style>