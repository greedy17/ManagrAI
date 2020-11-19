<template>
  <div class="box">
    <div class="box__tab-header">
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

    <div class="box__content">
      <div v-if="activeTab === 0">
        <img id="image" src="@/assets/images/timeline-temp.png" />
      </div>
      <div v-if="activeTab === 1">
        <img id="image" src="@/assets/images/message-rep-temp.png" />
      </div>
    </div>
  </div>
</template>

<script>
import ActionTabHeader from '@/components/shared/ActionTabHeader'

export default {
  name: 'TEMP_LeadActions',
  components: {
    ActionTabHeader,
  },
  props: {
    lead: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      activeTab: 0,
      tabs: ['timeline', 'message rep', 'schedule reminders', 'insights'],
    }
  },
  methods: {
    async updateActiveTab(index) {
      if (index > 1) {
        return
      }
      this.activeTab = index
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/containers';

#image {
  object-fit: cover;
  width: 100%;
}
.list-items {
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow-y: scroll;
}
.icon {
  height: 1.625rem;
  width: 1.625rem;
  display: block;
}
.svg {
  fill: red;
  width: 30px;
  height: 30px;
}
.list-items__header {
  font-weight: bold;
}
.list-items__item,
.list-items__header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  border-bottom: solid rgba($color: $main-font-gray, $alpha: 0.1) 1px;
  > * {
    align-self: center;
    margin-left: 0.75rem;
    color: rgba($color: $main-font-gray, $alpha: 0.4);
    flex: 1;
  }
  &__content {
    color: rgba($color: $main-font-gray, $alpha: 1);
    flex: 2;
  }
}
</style>
