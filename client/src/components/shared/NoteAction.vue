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
          <div class="form__element-header">Title</div>
          <input type="text" class="form__input" v-model="note.title" />
          <!-- <div class="form__element-error">Error Message Goes here</div> -->
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <textarea class="form__textarea" v-model="note.content" />
        </div>
      </div>
      <div class="form__element">
        <button class="form__button">Save</button>
      </div>
    </div>
  </form>
</template>

<script>
import ContactBox from '@/components/shared/ContactBox'

import Note from '@/services/notes'

export default {
  name: 'NoteAction',
  components: { ContactBox },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      note: Note.create({
        createdFor: this.lead.id,
      }),
    }
  },
  methods: {
    reset() {
      this.note = Note.create({
        createdFor: this.lead.id,
      })
    },
    toggleActive(contactId) {
      if (this.note.linkedContacts.includes(contactId)) {
        this.note.linkedContacts = this.note.linkedContacts.filter(id => id !== contactId)
      } else {
        this.note.linkedContacts.push(contactId)
      }
    },
    contactIsActive(contactId) {
      return this.note.linkedContacts.includes(contactId)
    },
    onSubmit() {
      Note.api
        .create(this.note)
        .then(() => {
          this.reset()
          this.$Alert.alert({
            type: 'success',
            message: `
              <p>Note saved.</p>
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
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/forms';
@import '@/styles/mixins/inputs';
</style>
