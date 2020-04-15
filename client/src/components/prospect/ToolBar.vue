<template>
  <div class="toolbar">
    <button class="new-lead" @click="routeToLeadsNew">
      New Lead
    </button>
    <div class="kpi-container">
      <KPIs />
    </div>
  </div>
</template>

<script>
import KPIs from '@/components/prospect/KPIs'

export default {
  name: 'ToolBar',
  components: {
    KPIs,
  },
  methods: {
    routeToLeadsNew() {
      this.$router.push({ name: 'LeadsNew' })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';

.toolbar {
  height: auto;
  width: 15rem;
}

.toolbar,
.toolbar > * {
  font-family: $base-font-family, $backup-base-font-family;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.9rem;
}

button.new-lead {
  @include primary-button();
  height: 2.5rem;
  width: 100%;
  font-size: 1rem;
}

.kpi-container {
  margin-top: 1rem;
}
</style>
