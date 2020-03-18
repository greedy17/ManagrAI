<template>
  <div class="actions">
    <div class="actions-tab-headers">
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
import ActionTabHeader from '@/components/leads-index/ActionTabHeader'
import CallAction from '@/components/leads-index/CallAction'
import EmailAction from '@/components/leads-index/EmailAction'
import ReminderAction from '@/components/leads-index/ReminderAction'
import ActionAction from '@/components/leads-index/ActionAction'
import NoteAction from '@/components/leads-index/EmailAction'

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
      tabs: ['call', 'email', 'reminder', 'action', 'notes'],
    }
  },
  methods: {
    updateActiveTab(index) {
      this.activeTab = index
    },
  },
}
</script>

<style lang="scss" scoped>
.actions {
  width: 765px;
  height: 325px;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px #f2f2f3;
  background-color: #ffffff;
  display: flex;
  flex-flow: column;
}

.actions-tab-headers {
  height: 48px;
  display: flex;
  flex-flow: row;
  box-shadow: 0 1px 0 0 #ececee;
}

.action-tab-content {
  flex-grow: 1;
  padding: 2vh;
  display: flex;
  flex-flow: row;
}

// div {
//   border: 1px dashed black;
// }
</style>
