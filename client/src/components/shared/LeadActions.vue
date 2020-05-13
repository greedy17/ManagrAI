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
      <CallAction ref="call-note-action" @save-call-note="createCallNote" v-if="activeTab === 0" />
      <TextAction v-if="activeTab === 1" />
      <EmailAction v-if="activeTab === 2" />
      <ActionAction v-if="activeTab === 3" />
      <ReminderAction
        ref="reminder-action"
        @save-reminder="createReminder"
        v-if="activeTab === 4"
      />
      <NoteAction ref="note-action" @save-note="createNote" v-if="activeTab === 5" />
    </div>
  </div>
</template>

<script>
import ActionTabHeader from '@/components/shared/ActionTabHeader'
import CallAction from '@/components/shared/CallAction'
import TextAction from '@/components/shared/TextAction'
import EmailAction from '@/components/shared/EmailAction'
import ReminderAction from '@/components/shared/ReminderAction'
import ActionAction from '@/components/shared/ActionAction'
import NoteAction from '@/components/shared/NoteAction'
import Note from '@/services/notes'
import Reminder from '@/services/reminders'
import CallNote from '@/services/call-notes'

export default {
  name: 'LeadActions',
  props: ['lead'],
  components: {
    ActionTabHeader,
    CallAction,
    TextAction,
    EmailAction,
    ReminderAction,
    ActionAction,
    NoteAction,
  },
  data() {
    return {
      activeTab: 0,
      tabs: ['call', 'text', 'email', 'action', 'reminder', 'note'],
      loading: false,
    }
  },

  methods: {
    updateActiveTab(index) {
      this.activeTab = index
    },
    async createNote(note) {
      let d = { note }
      d.created_for = [this.lead.id]
      this.loading = true

      try {
        await Note.api.create(d)
        this.$Alert.alert({
          type: 'success',
          timeout: 4000,
          message: 'note created!',
        })
        this.$refs['note-action'].notesForm.resetForm()
      } finally {
        this.loading = false
      }
    },
    async createReminder(reminder) {
      let d = { reminder }
      this.loading = true
      d.created_for = [this.lead.id]
      try {
        await Reminder.api.create(d)
        this.$Alert.alert({
          type: 'success',
          timeout: 4000,
          message: 'reminder created!',
        })
        this.$refs['reminder-action'].remindersForm.resetForm()
      } finally {
        this.loading = false
      }
    },
    async createCallNote(callNote) {
      let d = { ...callNote }
      d.created_for = this.lead.id
      this.loading = true
      try {
        await CallNote.api.create(d)
        this.$Alert.alert({
          type: 'success',
          timeout: 4000,
          message: 'call note created!',
        })
        this.$refs['call-note-action'].callNotesForm.resetForm()
      } finally {
        this.loading = false
      }
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
