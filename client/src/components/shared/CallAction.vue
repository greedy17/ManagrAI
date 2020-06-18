<template>
  <form @submit.prevent="onSubmit" class="flexbox-container">
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
          <input type="text" class="form__input" v-model="callNote.title" />
          <!-- <div class="form__element-error">Error Message Goes here</div> -->
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <div class="form__element-help">What notes do you have?</div>
          <textarea class="form__textarea" v-model="callNote.content" />
          <!-- <div class="form__element-error">Error Message Goes here</div> -->
        </div>
      </div>
      <div class="form__element">
        <div class="form__element-header">Date</div>
        <input type="date" class="form__input" v-model="callNote.callDate" />
      </div>
      <div class="form__element">
        <button class="form__button">Save</button>
      </div>
    </div>
  </form>
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
      callNote: CallNote.create({ createdFor: this.lead.id }),
    }
  },
  methods: {
    reset() {
      this.callNote = CallNote.create({
        createdFor: this.lead.id,
      })
    },
    toggleActive(contactId) {
      if (this.callNote.linkedContacts.includes(contactId)) {
        this.callNote.linkedContacts = this.callNote.linkedContacts.filter(id => id !== contactId)
      } else {
        this.callNote.linkedContacts.push(contactId)
      }
    },
    contactIsActive(contactId) {
      return this.callNote.linkedContacts.includes(contactId)
    },
    onSubmit() {
      CallNote.api
        .create(this.callNote)
        .then(() => {
          this.reset()

          this.$Alert.alert({
            type: 'success',
            message: `
              <p>Call saved.</p>
            `,
          })
        })
        .catch(error => {
          this.$Alert.alert({
            type: 'error',
            message: `
              <h3>Error</h3>
              <p>There was an error saving this note.</p>
            `,
          })
          // eslint-disable-next-line no-console
          console.error(error)
        })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/forms';
@import '@/styles/layout';
@import '@/styles/containers';
</style>
