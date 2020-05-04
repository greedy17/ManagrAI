<template>
  <div class="actions" :style="height">
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
    <div class="action-tab-content">
      <CallAction v-if="activeTab === 0" />
      <EmailAction v-if="activeTab === 1" />
      <ReminderAction v-if="activeTab === 2" />
      <ActionAction v-if="activeTab === 3" />
      <NoteAction v-if="activeTab === 4" />
    </div>
  </div>
</template>

<script>
import ActionTabHeader from '@/components/shared/ActionTabHeader'
import CallAction from '@/components/shared/CallAction'
import EmailAction from '@/components/shared/EmailAction'
import ReminderAction from '@/components/shared/ReminderAction'
import ActionAction from '@/components/shared/ActionAction'
import NoteAction from '@/components/shared/NoteAction'

export default {
  name: 'LeadActions',
  props: ['lead'],
  components: {
    ActionTabHeader,
    CallAction,
    EmailAction,
    ReminderAction,
    ActionAction,
    NoteAction,
  },
  data() {
    return {
      activeTab: 0,
      tabs: ['call', 'email', 'reminder', 'action', 'note'],
    }
  },
  methods: {
    updateActiveTab(index) {
      this.activeTab = index
    },
  },
  computed: {
    height() {
      if (this.tabs[this.activeTab] === 'email') {
        return { height: '28rem' }
      } else {
        return { height: '21rem' }
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

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

.actions-tab-headers {
  height: 3rem;
  display: flex;
  flex-flow: row;
}

.action-tab-content {
  flex-grow: 1;
  padding: 2vh;
  display: flex;
  flex-flow: row;
}
</style>
