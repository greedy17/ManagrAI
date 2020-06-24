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

    <div v-if="state == editState" class="box__content">
      <CallAction :lead="lead" v-if="activeTab === 0" />
      <TextAction :lead="lead" v-if="activeTab === 1" />
      <EmailAction :lead="lead" v-if="activeTab === 2" />
      <ActionAction :lead="lead" v-if="activeTab === 3" />
      <ReminderAction :lead="lead" v-if="activeTab === 4" />
      <NoteAction :lead="lead" v-if="activeTab === 5" />
    </div>
    <div v-if="state == viewState" class="box__content">
      <div class="list-items" v-if="activeTab === 0">
        <div class="list-items__header">
          <span class="list-items__header__space">
            <!--space for header-->
          </span>
          <span class="list-items__header__title">Title</span>
          <span class="list-items__header__content">Content</span>
          <span class="list-items__header__call-date">Call Date</span>
          <span class="list-items__header__created-by">Creator</span>
          <span class="list-items__header__datetime-created">Created</span>
        </div>
        <template v-for="(item, i) in callNotes.list">
          <div class="list-items__item" :key="item.id + '-' + i">
            <span class="icon">
              <svg class="svg" viewBox="0 0 30 30" @click.stop="$emit('delete-list', list.id)">
                <use xlink:href="@/assets/images/svg-repo.svg#remove" />
              </svg>
            </span>
            <span class="list-items__item__title">{{ item.title }}</span>
            <span class="list-items__item__content">{{ item.content }}</span>
            <span class="list-items__item__call-date">
              {{ moment(item.callDate).format('MM/DD/YYYY') }}
            </span>
            <span class="list-items__item__created-by">{{ item.createdByRef.fullName }}</span>
            <span class="list-items__item__datetime-created">
              {{ moment(item.datetimeCreated).format('MM/DD/YYYY') }}
            </span>
          </div>
        </template>
      </div>
      <div class="list-items" v-if="activeTab === 4">
        <div class="list-items__header">
          <span class="list-items__header__space">
            <!--space for header-->
          </span>
          <span class="list-items__header__title">Title</span>
          <span class="list-items__header__content">Content</span>
          <span class="list-items__header__datetimeFor">Reminder On</span>
          <span class="list-items__header__created-by">Creator</span>
          <span class="list-items__header__datetime-created">Created</span>
        </div>
        <template v-for="(item, i) in reminders.list">
          <div class="list-items__item" :key="item.id + '-' + i">
            <span class="icon">
              <svg class="svg" viewBox="0 0 30 30" @click.stop="$emit('delete-list', list.id)">
                <use xlink:href="@/assets/images/svg-repo.svg#remove" />
              </svg>
            </span>
            <span class="list-items__item__title">{{ item.title }}</span>
            <span class="list-items__item__content">{{ item.content }}</span>
            <span class="list-items__item__datetime-for">
              {{ moment(item.datetimeFor).format('MM/DD/YYYY') }}
            </span>
            <span class="list-items__item__created-by">{{ item.createdByRef.fullName }}</span>
            <span class="list-items__item__datetime-created">
              {{ moment(item.datetimeCreated).format('MM/DD/YYYY') }}
            </span>
          </div>
        </template>
      </div>

      <div class="list-items" v-if="activeTab === 5">
        <div class="list-items__header">
          <span class="list-items__header__space">
            <!--space for header-->
          </span>
          <span class="list-items__header__title">Title</span>
          <span class="list-items__header__content">Content</span>
          <span class="list-items__header__created-by">Creator</span>
          <span class="list-items__header__datetime-created">Created</span>
        </div>
        <template v-for="(item, i) in notes.list">
          <div class="list-items__item" :key="item.id + '-' + i">
            <span class="icon">
              <svg class="svg" viewBox="0 0 30 30" @click.stop="$emit('delete-list', list.id)">
                <use xlink:href="@/assets/images/svg-repo.svg#remove" />
              </svg>
            </span>
            <span class="list-items__item__title">{{ item.title }}</span>
            <span class="list-items__item__content">{{ item.content }}</span>
            <span class="list-items__item__created-by">{{ item.createdByRef.fullName }}</span>
            <span class="list-items__item__datetime-created">
              {{ moment(item.datetimeCreated).format('MM/DD/YYYY') }}
            </span>
          </div>
        </template>
      </div>
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
import CollectionManager from '@/services/collectionManager'
import moment from 'moment'

const EDIT_STATE = 'create'
const VIEW_STATE = 'view'

export default {
  name: 'LeadActions',

  components: {
    ActionTabHeader,
    CallAction,
    TextAction,
    EmailAction,
    ReminderAction,
    ActionAction,
    NoteAction,
  },
  props: {
    lead: {
      type: Object,
      default: () => {},
    },
    state: {
      type: String,
      default: EDIT_STATE,
    },
  },
  data() {
    return {
      activeTab: 0,
      tabs: ['call', 'text', 'email', 'action', 'reminder', 'note'],
      loading: false,
      editState: EDIT_STATE,
      viewState: VIEW_STATE,
      moment: moment,
      notes: CollectionManager.create({
        ModelClass: Note,
        filters: {
          byLead: this.lead.id,
        },
      }),
      callNotes: CollectionManager.create({
        ModelClass: CallNote,
        filters: {
          byLead: this.lead.id,
        },
      }),
      reminders: CollectionManager.create({
        ModelClass: Reminder,
        filters: {
          byLead: this.lead.id,
        },
      }),
    }
  },
  async created() {
    await this.listItems(this.tabs[this.activeTab])
  },
  methods: {
    async listItems(tab) {
      if (this.state == this.viewState) {
        // only fetch lists if on view state
        switch (tab.toLowerCase()) {
          case 'note':
            await this.notes.refresh()
            break
          case 'call':
            await this.callNotes.refresh()
            break
          case 'reminder':
            await this.reminders.refresh()
            break
        }
      }
    },
    async updateActiveTab(index) {
      if (this.tabs[index] !== this.tabs[this.activeTab]) {
        await this.listItems(this.tabs[index])
        this.activeTab = index
      }
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
@import '@/styles/containers';

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
