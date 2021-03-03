<template>
  <div class="flexbox-container">
    <div class="flexbox-container__column">
      <h4>Contacts</h4>
      <ContactBox
        v-for="contact in lead.linkedContactsRef"
        :contact="contact"
        @toggle="toggleActive($event)"
        :isActive="contactIsActive(contact.id)"
        :key="contact.id"
      />
    </div>

    <div class="flexbox-container__column" style="flex: 2">
      <div class="form">
        <div class="form__element">
          <div class="form__element-header">Title</div>
          <input type="text" class="form__input" v-model="reminder.title" />
          <!-- <div class="form__element-error">Error Message Goes here</div> -->
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <textarea class="form__textarea" v-model="reminder.content" />
        </div>
      </div>
      <div class="form__element">
        <div class="form__element-header">Date</div>
        <input type="datetime-local" class="form__input" v-model="reminder.datetimeFor" />
      </div>
      <div
        class="form__element"
        style="display: flex; flex-direction: column; align-items: flex-end;"
      >
        <button @click="save" class="form__button" :disabled="loading">
          <span v-if="!loading">Save</span>
          <ComponentLoadingSVG v-if="loading" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import ContactBox from '@/components/shared/ContactBox'
import Reminder from '@/services/reminders/'
import moment from 'moment'

export default {
  name: 'ReminderAction',
  components: { ContactBox },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      activeContacts: [],
      reminder: Reminder.create({}),
      loading: false,
    }
  },
  methods: {
    async save() {
      try {
        this.loading = true
        await Reminder.api.create({
          reminder: {
            title: this.reminder.title,
            content: this.reminder.content,
            datetimeFor: moment(this.reminder.datetimeFor).format(),
            linkedContacts: this.activeContacts,
          },
          createdFor: [this.lead.id],
        })
        this.reminder = Reminder.create({})
        this.activeContacts = []
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: `
              <p>Reminder Has Been Set.</p>
            `,
        })
      } catch (e) {
        return e
      } finally {
        this.loading = false
      }
    },
    toggleActive(contactId) {
      if (this.activeContacts.includes(contactId)) {
        this.activeContacts = this.activeContacts.filter(id => id !== contactId)
      } else {
        this.activeContacts.push(contactId)
      }
    },
    contactIsActive(contactId) {
      return this.activeContacts.includes(contactId)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/forms';
@import '@/styles/mixins/inputs';
</style>
