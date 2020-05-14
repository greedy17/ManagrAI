<template>
  <div class="toolbar">
    <div class="actions-tab-headers section-shadow">
      <ActionTabHeader
        v-for="(tab, index) in tabs"
        :key="tab"
        :active="index === activeTab"
        :index="index"
        @update-active-tab="updateActiveTab"
      >
        {{ tab }}
      </ActionTabHeader>
    </div>
  </div>
</template>

<script>
import ActionTabHeader from '@/components/shared/ActionTabHeader'

export default {
  name: 'ToolBar',
  components: {
    ActionTabHeader,
  },
  props: {
    tabs: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      optionTabs: ['Details', 'Accounts', 'Reps', 'ActionTypes'],
      activeTab: 0,
    }
  },
  watch: {
    activeTab: {
      immediate: true,
      handler(curr, prev) {
        if (curr != prev) {
          console.log(curr)
          this.$emit('selected-tab', this.tabs[this.activeTab])
        }
      },
    },
  },
  methods: {
    routeToLeadsNew() {
      this.$router.push({ name: 'LeadsNew' })
    },
    updateActiveTab(index) {
      this.activeTab = index
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.toolbar {
  height: auto;
  width: 15rem;
}

.toolbar,
.toolbar > * {
  @include base-font-styles();
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
.actions-tab-headers {
  height: 3rem;
  display: flex;
  flex-flow: column;
  width: 100%;
}
.actions {
  min-width: 48rem;
  width: 100%;
  min-height: 21rem;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px $soft-gray;
  background-color: $white;
  display: flex;
  flex-flow: column;
}
</style>
