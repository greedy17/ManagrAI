<template>
  <div class="lead-details">
    <div class="lead-details-content">
      <div class="actions-pane">
        <LeadActions :lead="lead" />
      </div>
      <div class="insights-pane">
        <LeadInsights :lead="lead" />
      </div>
    </div>
  </div>
</template>

<script>
import LeadActions from '@/components/leads-index/LeadActions'
import LeadInsights from '@/components/leads-index/LeadInsights'

export default {
  name: 'LeadDetails',
  props: ['lead'],
  components: {
    LeadActions,
    LeadInsights,
  },
}
</script>

<style lang="scss" scoped>
.lead-details {
  padding: 2%;
}
.lead-details-content {
  display: flex;
  flex-flow: row;
}

.actions-pane {
  width: 72.5%;
}

.insights-pane {
  flex-grow: 1;
}
/* for development purposes */
div {
  border-style: dashed;
  border-width: 1px;
}
</style>
