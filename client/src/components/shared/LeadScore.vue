<template>
  <Tooltip>
    <template v-slot:tooltip-target>
      <div class="display">
        {{ display }}
      </div>
    </template>
    <template v-slot:tooltip-content>
      <div class="content">
        {{ content }}
        <br />
        <br />
        Last Score: {{ lead.lastScore ? lead.lastScore.score : 'N/A' }}
      </div>
    </template>
  </Tooltip>
</template>

<script>
import Tooltip from '@/components/shared/Tooltip'

// Help Hover Copy
// x = engagement score ( 0 - 100 )
// x >= 25            displays "Engagement is very high"
// 25 > x >= 20       displays "Engagement is high"
// 20 > x >= 15       displays "Engagement is moderate"
// 15 > x >= 10       displays "Engagement is ok"
// 10 > x >= 5        displays "Engagement is low"
// x < 5              displays "No Engagement"

export default {
  name: 'LeadScore',
  components: { Tooltip },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  computed: {
    display() {
      let { latestScore } = this.lead
      return latestScore ? latestScore.score : 'N/A'
    },
    content() {
      let { latestScore } = this.lead
      if (!latestScore) {
        return 'No Engagement'
      }
      let { score } = latestScore
      if (score >= 25) {
        return 'Engagement is very high'
      }
      if (25 > score && score >= 20) {
        return 'Engagement is high'
      }
      if (20 > score && score >= 15) {
        return 'Engagement is moderate'
      }
      if (15 > score && score >= 10) {
        return 'Engagement is ok'
      }
      if (10 > score && score >= 5) {
        return 'Engagement is low'
      }
      return 'No Engagement'
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
  display: unset !important;
  text-align: left !important;
}
</style>
