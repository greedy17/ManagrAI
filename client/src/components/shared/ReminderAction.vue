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
          <input type="text" class="form__input" />
          <!-- <div class="form__element-error">Error Message Goes here</div> -->
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <textarea class="form__textarea" />
        </div>
      </div>
      <div class="form__element">
        <div class="form__element-header">Date</div>
        <input type="datetime-local" class="form__input" />
      </div>
      <div
        class="form__element"
        style="display: flex; flex-direction: column; align-items: flex-end;"
      >
        <button class="form__button">Save</button>
      </div>
    </div>
  </div>
</template>

<script>
import ContactBox from '@/components/shared/ContactBox'
import Reminder from '@/services/reminders/'

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
      reminder: {},
    }
  },
  methods: {
    save() {
      Reminder.api.create(this.reminder)
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
