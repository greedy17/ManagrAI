<template>
  <form @submit.prevent="onSubmit" class="flexbox-container">
    <div class="flexbox-container__column">
      <h4>Contacts</h4>
      <div
        class="form__element-error"
        v-if="showErrors && !linkedContactsValid"
        style="margin-bottom: 0.5rem;"
      >
        Select one or more contacts
      </div>
      <ContactBox
        v-for="contact in lead.linkedContactsRef"
        :contact="contact"
        @toggle="toggleActive($event)"
        :isActive="contactIsActive(contact.id)"
        :key="contact.id"
      />
    </div>

    <div class="flexbox-container__column" style="flex: 2;">
      <div class="form">
        <div class="form__element">
          <div class="form__element-header">Title</div>
          <input type="text" class="form__input" v-model="note.title" />
          <div class="form__element-error" v-if="showErrors && !titleValid">
            Enter a title for this note
          </div>
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <textarea class="form__textarea" v-model="note.content" />
        </div>
      </div>
      <div
        class="form__element"
        style="display: flex; flex-direction: column; align-items: flex-end;"
      >
        <button class="form__button" :disabled="saving">
          <span v-if="!saving">Save</span>
          <ComponentLoadingSVG v-if="saving" />
        </button>
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
      saving: false,
      showErrors: false,
    }
  },
  computed: {
    formValid() {
      return this.titleValid
    },
    linkedContactsValid() {
      return this.note.linkedContacts.length > 0
    },
    titleValid() {
      return this.note.title !== ''
    },
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
      if (!this.formValid) {
        this.showErrors = true
        return
      } else {
        this.showErrors = false
      }

      this.saving = true
      Note.api
        .create(this.note)
        .then(() => {
          this.reset()
          this.$Alert.alert({
            type: 'success',
            timeout: 3000,
            message: `
              <p>Note saved.</p>
            `,
          })
        })
        .catch(error => {
          this.$Alert.alert({
            type: 'error',
            timeout: 3000,
            message: `
              <h3>Error</h3>
              <p>There was an error saving this note.</p>
            `,
          })
          // eslint-disable-next-line no-console
          console.error(error)
        })
        .finally(() => {
          this.saving = false
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
