<template>
  <div class="lead-details">
    <div class="lead-details-content">
      <div class="actions-pane">
        <LeadActions class="lead-actions" :lead="lead" />
      </div>
    </div>
    <div class="route-to-detail" @click="openLeadDetail">See Opportunity Detail</div>
  </div>
</template>

<script>
// import LeadActions from '@/components/shared/LeadActions'
import LeadActions from '@/components/shared/TEMP_LeadActions'

export default {
  name: 'LeadDetails',
  props: ['lead'],
  components: {
    LeadActions,
  },
  methods: {
    openLeadDetail() {
      let routeData = this.$router.resolve({ name: 'LeadsDetail', params: { id: this.lead.id } })
      window.open(routeData.href, '_blank')
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
  display: flex;
  flex: 1;
  justify-content: center;
}

.lead-actions {
  flex: 1;
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
