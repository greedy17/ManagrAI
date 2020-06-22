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
          <div class="form__element-header">Topic</div>
          <div class="form__element-help">What was the meeting topic?</div>
          <select class="form__select" v-model="callNote.title">
            <option v-for="(option, index) in TOPIC_OPTIONS" :value="option" :key="index">
              {{ option }}
            </option>
          </select>
          <div class="form__element-error" v-if="showErrors && !titleValid">
            Select a meeting topic
          </div>
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <div class="form__element-help">What notes do you have?</div>
          <textarea class="form__textarea" v-model="callNote.content" />
        </div>
      </div>
      <div class="form__element">
        <div class="form__element-header">Date</div>
        <input type="date" class="form__input" v-model="callNote.callDate" />
        <div class="form__element-error" v-if="showErrors && !dateValid">Please enter a date.</div>
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
import CallNote from '@/services/call-notes'

import ContactBox from '@/components/shared/ContactBox'

const TOPIC_OPTIONS = ['Pick Up', 'Voicemail', 'No Answer', 'Success', 'Other']

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
      callNote: CallNote.create({ title: TOPIC_OPTIONS[0], createdFor: this.lead.id }),
      TOPIC_OPTIONS,
      saving: false,
      showErrors: false,
    }
  },
  computed: {
    formValid() {
      return this.titleValid && this.dateValid
    },
    linkedContactsValid() {
      return this.callNote.linkedContacts.length > 0
    },
    titleValid() {
      return this.callNote.title !== '' && TOPIC_OPTIONS.includes(this.callNote.title)
    },
    dateValid() {
      return !!this.callNote.callDate
    },
  },
  methods: {
    reset() {
      this.callNote = CallNote.create({
        title: TOPIC_OPTIONS[0],
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
      if (!this.formValid) {
        this.showErrors = true
        return
      } else {
        this.showErrors = false
      }

      this.saving = true
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
        .finally(() => {
          this.saving = false
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
