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
          <div class="form__element-header">Type</div>
          <select class="form__select" v-model="selectedContact">
            <option value="Testing">A list of action types will go here</option>
            <option value="Testing">A list of action types will go here</option>
            <option value="Testing">A list of action types will go here</option>
            <option value="Testing">A list of action types will go here</option>
          </select>
        </div>
        <div class="form__element">
          <div class="form__element-header">Title</div>
          <input type="text" class="form__input" />
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
      <div class="form__element">
        <button class="form__button">Save</button>
      </div>
    </div>
  </div>
</template>

<script>
import ContactBox from '@/components/shared/ContactBox'
export default {
  name: 'ActionAction',
  components: { ContactBox },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      // actionNote: new CallNote(),
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
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/forms';
@import '@/styles/mixins/inputs';
</style>
