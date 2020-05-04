<template>
  <div class="text-action">
    <div class="contacts-container">
      <div
        v-for="contact in contacts"
        :key="contact.id"
        class="contact"
        :class="{ 'active-contact': contactsToInclude[contact.id] }"
        @click="toggleContactInclusion(contact.id)"
      >
        <img class="contact-img" src="@/assets/images/sara-smith.png" alt="contact image" />
        <span class="contact-name">{{ contact.fullName }}</span>
        <div class="contact-phone-number-container">
          <img class="telephone-icon" src="@/assets/images/telephone.svg" alt="icon" />
          <span class="contact-phone-number">{{ contact.phone }}</span>
        </div>
      </div>
    </div>
    <textarea class="note-detail" placeholder="Detail" />
    <div class="save-button-container">
      <span class="save-button">Save</span>
    </div>
  </div>
</template>

<script>
let exampleContacts = [
  {
    id: 1,
    fullName: 'Sara Smith',
    title: 'COO',
    phone: '123-456-7890',
    email: 'sara@samsung.com',
  },
  {
    id: 2,
    fullName: 'Jake Murray',
    title: 'CFO',
    phone: '123-456-7899',
    email: 'jake@samsung.com',
  },
]

export default {
  name: 'TextAction',
  data() {
    return {
      contacts: exampleContacts,
      contactsToInclude: {},
    }
  },
  methods: {
    toggleContactInclusion(contactID) {
      // depending on payload status add or remove that key
      // plainObject is used instead of an array because of O(1) lookup
      if (this.contactsToInclude[contactID]) {
        this.contactsToInclude = Object.assign({}, this.contactsToInclude, { [contactID]: false })
      } else {
        this.contactsToInclude = Object.assign({}, this.contactsToInclude, { [contactID]: true })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

.text-action {
  width: 100%;
  display: flex;
  flex-flow: column;
}

.contacts-container {
  display: flex;
  flex-flow: column;
  width: 40%;
}

.contact {
  @include pointer-on-hover();
  border: 2px solid $white;
  padding: 0.2rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 2%;
}

.contact-img {
  height: 1.5rem;
  width: 1.5rem;
  border-radius: 50%;
}

.contact-name {
  @include base-font-styles();
  margin-left: auto;
  width: 25%;
  font-size: 11px;
  line-height: 1.45;
  color: $main-font-gray;
}

.contact-phone-number-container {
  @include pointer-on-hover();
  width: 50%;
  height: 1.5rem;
  padding: 0.125rem;
  margin-left: auto;
  background-color: $soft-gray;
  border-radius: 5px;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.telephone-icon {
  height: 1rem;
  width: 1rem;
  margin-left: 0.375rem;
}

.contact-phone-number {
  @include base-font-styles();
  margin-left: 0.375rem;
  font-size: 11px;
  font-weight: bold;
  line-height: 1.45;
  color: $main-font-gray;
}

.active-contact {
  border: 2px solid $dark-green;
}

input {
  @include input-field();
  height: 2.5rem;
}

textarea {
  @include input-field();
  resize: none;
  height: 94%;
  flex-grow: 1;
  margin: 2% 0;
  font-size: 14px;
}

.save-button-container {
  display: flex;
  flex-flow: row;
}

.save-button {
  @include primary-button();
  margin-left: auto;
}
</style>
