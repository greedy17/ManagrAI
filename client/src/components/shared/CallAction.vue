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
    <div class="flexbox-container__column">
      <div class="form">
        <div class="form__element">
          <div class="form__element-header">Topic</div>
          <div class="form__element-help">What was the meeting topic?</div>
          <input type="text" class="form__input" />
          <!-- <div class="form__element-error">Error Message Goes here</div> -->
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <div class="form__element-help">What notes do you have?</div>
          <textarea class="form__textarea" />
          <!-- <div class="form__element-error">Error Message Goes here</div> -->
        </div>
      </div>
      <div class="form__element">
        <div class="form__element-header">Date</div>
        <input type="datetime-local" class="form__input" />
      </div>
      <div class="form__element">
        <button class="form__button">Save</button>
      </div>
    </div>
  </div>
</template>

<script>
import CallNote from '@/services/call-notes'

import ContactBox from '@/components/shared/ContactBox'

export default {
  name: 'CallAction',
  components: { ContactBox },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      callNote: new CallNote(),
      activeContacts: [],
    }
  },
  methods: {
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
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/forms';
@import '@/styles/layout';
@import '@/styles/containers';
</style>
