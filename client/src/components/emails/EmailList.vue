<template>
  <div>
    <div class="email__row">
      <div class="form__element-header">{{ label }}:</div>
      <div class="email__contact-tag" v-for="contactObject in emails" :key="contactObject.email">
        {{ contactObject.email }} <span @click="removeEmail(contactObject)">&nbsp;[X]</span>
      </div>
      <span v-if="!showAddBox" @click="showEmailBox()">
        &nbsp;[ + ]
      </span>
      <span v-if="showAddBox" @click="hideEmailBoxes()">
        &nbsp;[ - ]
      </span>
    </div>
    <div class="box" v-if="showAddBox">
      <div class="box__tab-header">
        <div
          :class="{ 'box__tab--active': showLeadContacts, box__tab: !showLeadContacts }"
          v-if="lead.linkedContactsRef"
          @click="showLeadContacts = !showLeadContacts"
        >
          Lead Contacts
        </div>
        <div
          :class="{ 'box__tab--active': !showLeadContacts, box__tab: showLeadContacts }"
          @click="showLeadContacts = !showLeadContacts"
        >
          New Contact
        </div>
      </div>
      <div class="box__content" v-if="showLeadContacts && lead.linkedContactsRef">
        <!-- NOTE: THIS SHOULD SHOW THE LEAD CONTACTS ONCE WE ARE HOOKED UP TO THE LEAD PAGE -->
        <div class="form__element">
          <div class="form__element-header">Name</div>
          <select class="form__select" v-model="selectedContact">
            <option :value="null">Select Contact From Lead</option>
            <option v-for="contact in lead.linkedContactsRef" :value="contact" :key="contact.id">{{
              contact.full_name
            }}</option>
          </select>
        </div>
        <div class="form__element">
          <button
            class="form__button"
            @click="
              addEmail(generateContactObject(selectedContact.full_name, selectedContact.email))
            "
          >
            Add
          </button>
        </div>
      </div>
      <div class="box__content" v-if="!showLeadContacts">
        <div class="new-email-box">
          <div class="form__element">
            <div class="form__element-header">Email</div>
            <input class="form__input" type="text" v-model="newContactEmail" />
          </div>
          <div class="form__element">
            <div class="form__element-header">Name</div>
            <input class="form__input" type="text" v-model="newContactName" />
          </div>
          <div class="form__element">
            <button
              class="button"
              @click="addEmail(generateContactObject(newContactName, newContactEmail))"
            >
              Add New Email
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmailList',
  props: {
    emails: {
      type: Array,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    lead: {
      type: Object,
      default: () => {
        return {}
      },
    },
  },
  data() {
    return {
      selectedContact: null,
      newContactEmail: '',
      newContactName: '',
      showAddBox: false,
      showLeadContacts: true,
    }
  },
  created() {
    if (!this.lead.linkedContactsRef) {
      this.showLeadContacts = false
    }
  },
  methods: {
    hideEmailBoxes() {
      this.showAddBox = false
    },
    showEmailBox() {
      this.showAddBox = true
    },
    addEmail(contactObject) {
      this.$emit('add', contactObject)
    },
    removeEmail(contactObject) {
      this.$emit('remove', contactObject)
    },
    generateContactObject(name, email) {
      this.showAddBox = false
      return {
        name: name,
        email: email,
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';
@import '@/styles/emails';
@import '@/styles/forms';
@import '@/styles/layout';
@import '@/styles/mixins/inputs';

.new-email-box {
  width: 100%;
}
</style>
