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
    <div class="route-to-detail" @click="routeToLeadDetail">See Lead Detail</div>
  </div>
</template>

<script>
import LeadActions from '@/components/shared/LeadActions'
import LeadInsights from '@/components/shared/LeadInsights'

export default {
  name: 'LeadDetails',
  props: ['lead'],
  components: {
    LeadActions,
    LeadInsights,
  },
  methods: {
    routeToLeadDetail() {
      this.$router.push({ name: 'LeadsDetail', params: { id: this.lead.id } })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.lead-details {
  padding: 2%;
}
.lead-details-content {
  display: flex;
  flex-flow: row;
}

.actions-pane {
  width: 72.5%;
  display: flex;
  justify-content: center;
}

.insights-pane {
  flex-grow: 1;
  display: flex;
  justify-content: center;
}

.route-to-detail {
  @include pointer-on-hover;
  @include disable-text-select;
  @include base-font-styles;
  text-transform: uppercase;
  font-size: 0.875rem;
  font-weight: bold;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: $dark-green;
  margin-top: 1rem;
}
</style>
