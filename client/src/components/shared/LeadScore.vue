<template>
  <v-popover trigger="hover" placement="right">
    <div class="display">
      {{ scoreDisplay }}
    </div>
    <template slot="popover">
      <div class="content" v-if="score">
        <div>
          How did we get this score?
        </div>
        <hr />
        <div v-if="score && score.incomingMessagesInsight">
          {{ score.incomingMessagesInsight }}
        </div>
        <div v-if="score && score.actionsInsight">
          {{ score.actionsInsight }}
        </div>
        <div v-if="score && score.daysInStageInsight">
          {{ score.daysInStageInsight }}
        </div>
        <div v-if="score && score.forecastTableInsight">
          {{ score.forecastTableInsight }}
        </div>
        <div v-if="score && score.expectedCloseDateInsight">
          {{ score.expectedCloseDateInsight }}
        </div>
        <div v-if="score && score.recentActionInsight">
          {{ score.recentActionInsight }}
        </div>
        <div class="footer">
          {{ footer }}
        </div>
      </div>
      <div class="content" v-else>
        Check back tomorrow!
      </div>
    </template>
  </v-popover>
</template>

<script>
export default {
  name: 'LeadScore',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  computed: {
    score() {
      return this.lead.score
    },
    scoreDisplay() {
      return this.score ? this.lead.score.current : 'N/A'
    },
    generalSummary() {
      // x >= 25            displays "Engagement is very high"
      // 25 > x >= 20       displays "Engagement is high"
      // 20 > x >= 15       displays "Engagement is moderate"
      // 15 > x >= 10       displays "Engagement is ok"
      // 10 > x >= 5        displays "Engagement is low"
      // x < 5              displays "No Engagement"

      if (!this.score) {
        return 'No Engagement.'
      }
      let { current } = this.score
      if (current >= 25) {
        return 'Engagement is very high.'
      }
      if (25 > current && current >= 20) {
        return 'Engagement is high.'
      }
      if (20 > current && current >= 15) {
        return 'Engagement is moderate.'
      }
      if (15 > current && current >= 10) {
        return 'Engagement is ok.'
      }
      if (10 > current && current >= 5) {
        return 'Engagement is low.'
      }
      return 'No Engagement.'
    },
    footer() {
      let previous = 'N/A'
      if (this.score && this.score.previousRef) {
        previous = this.score.previousRef.score
      }
      return 'Last Score: ' + previous
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.display {
  height: 2rem;
  width: 2rem;
  border-radius: 50%;
  border-color: $soft-gray;
  background-color: $white;
  color: $main-font-gray;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content {
  padding: 0.5rem;
}

.footer {
  margin-top: 1rem;
  color: $mid-gray;
}
</style>
