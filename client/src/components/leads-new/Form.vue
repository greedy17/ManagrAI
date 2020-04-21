<template>
  <div class="form">
    <div class="step-1">
      <div class="form-field">
        <label>Lead Title</label>
        <input class="input" tabindex="1" type="text" placeholder="Title" />
      </div>
      <div class="form-field">
        <label>Account Relationship</label>
        <select tabindex="2">
          <option value="">Once the AccountsAPI works, this dropdown will be populated</option>
        </select>
      </div>
      <div v-if="currentStep < 2" class="button-container">
        <button tabindex="3" @click="showStepTwo">Next</button>
      </div>
    </div>
    <div v-if="currentStep > 1" class="step-2">
      <div class="form-field">
        <label>Contacts</label>
        <ContactCheckBox
          v-for="contact in accountContacts"
          :key="contact.id"
          :contact="contact"
          :checked="!!contactsToInclude[contact.id]"
          @checkbox-clicked="handleCheckboxClick"
        />
      </div>
      <div class="form-field">
        <AddContact v-for="n in addContactSubForms" :key="n" />
      </div>
      <div class="form-field">
        <label @click="addAnotherContactForm" class="add-another-button">
          <img class="icon" src="@/assets/images/add.svg" alt="icon" />
          Add Another
        </label>
      </div>
      <div class="button-container">
        <button tabindex="3" @click="createLead">Next</button>
      </div>
    </div>
  </div>
</template>

<script>
import ContactCheckBox from '@/components/leads-new/ContactCheckBox'
import AddContact from '@/components/leads-new/AddContact'

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
  name: 'Form',
  props: {
    currentStep: {
      type: Number,
      required: true,
    },
  },
  components: {
    ContactCheckBox,
    AddContact,
  },
  data() {
    return {
      accountContacts: exampleContacts,
      contactsToInclude: {},
      addContactSubForms: 1,
    }
  },
  methods: {
    showStepTwo() {
      this.$emit('clicked-next')
    },
    handleCheckboxClick({ status, contactID }) {
      // depending on payload status add or remove that key
      // plainObject is used instead of an array because of O(1) lookup for <ContactCheckBox />
      if (status) {
        this.contactsToInclude = Object.assign({}, this.contactsToInclude, { [contactID]: true })
      } else {
        this.contactsToInclude = Object.assign({}, this.contactsToInclude, { [contactID]: false })
      }
    },
    addAnotherContactForm() {
      this.addContactSubForms += 1
    },
    createLead() {
      alert('Once we have the newly created Lead, we can route the user to its page')
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.step-1,
.step-2 {
  @include standard-border();
  background-color: $white;
  height: auto;
  width: 45rem;
  display: flex;
  flex-flow: column;
  align-items: center;
  box-sizing: border-box;
  padding: 2rem 0;
}

.step-2 {
  margin-top: 3rem;
  margin-bottom: 5rem;
}

.form-field {
  width: 90%;
  display: flex;
  flex-flow: column;
  margin-bottom: 1rem;

  label {
    font-family: $base-font-family, $backup-base-font-family;
    color: $main-font-gray;
    font-weight: bold;
    margin-bottom: 1rem;
  }

  .input {
    @include input-field();
    height: 2rem;
    margin-bottom: 1rem;
  }

  select {
    @include pointer-on-hover();
    height: 2rem;
  }
}

.button-container {
  display: flex;
  flex-flow: row;
  width: inherit;

  button {
    @include primary-button();
    margin: 1rem 5% 0 auto;
  }
}

.icon {
  height: 1.4rem;
  width: 1.4rem;
  margin-right: 1rem;
}

.add-another-button {
  @include pointer-on-hover();
  display: flex;
  flex-flow: row;
  align-items: center;
}
</style>
