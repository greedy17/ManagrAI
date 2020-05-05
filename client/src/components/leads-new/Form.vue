<template>
  <div class="form">
    <div class="step-1">
      <div class="errors">
        <!-- client side validations -->
        <div v-if="isFormValid !== null && !isFormValid && errors.leadTitleIsBlank">
          Lead Title may not be blank.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.accountNotSelected">
          Account must be selected.
        </div>
      </div>
      <div class="form-field">
        <label>Lead Title</label>
        <input v-model="leadTitle" class="input" tabindex="1" type="text" placeholder="Title" />
      </div>
      <div class="form-field">
        <label>Account Relationship</label>
        <select tabindex="2" @change="onSelectAccount" :disabled="currentStep > 1">
          <option disabled :selected="selectedAccount == null" value="">Select Account</option>
          <option v-for="account in accounts.list" :key="account.id" :value="account.id">{{
            account.name
          }}</option>
        </select>
      </div>
      <div v-if="currentStep < 2" class="button-container">
        <button tabindex="3" @click="showStepTwo">Next</button>
      </div>
    </div>
    <div v-if="currentStep > 1" class="step-2">
      <div class="form-field">
        <label>Contacts</label>
        <p v-if="!contacts.list.length">No contacts available.</p>
        <ContactCheckBox
          v-else
          v-for="contact in contacts.list"
          :key="contact.id"
          :contact="contact"
          :checked="!!contactsToInclude[contact.id]"
          @checkbox-clicked="handleCheckboxClick"
        />
      </div>
      <div class="form-field">
        <AddContact
          v-for="n in addContactFormCount"
          :key="n"
          :form="addContactForms[n]"
          :error="errors.addContactForms && errors.addContactForms[n]"
        />
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
import Lead from '@/services/leads'
import Account from '@/services/accounts'
import Contact from '@/services/contacts'
import CollectionManager from '@/services/collectionManager'

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
      leadTitle: '',
      accounts: CollectionManager.create({ ModelClass: Account }),
      selectedAccount: null,
      contacts: CollectionManager.create({ ModelClass: Contact }),
      contactsToInclude: {},
      addContactFormCount: 1,
      addContactForms: {
        1: {
          firstName: '',
          lastName: '',
          title: '',
          email: '',
          phone: '',
        },
      },
      isFormValid: null, // client side validations
      success: null, //server side validations
      errors: {},
    }
  },
  created() {
    this.accounts.refresh()
  },
  methods: {
    onSelectAccount({ target: { value } }) {
      this.selectedAccount = value
    },
    showStepTwo() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data
      let validationResults = this.stepOneClientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      this.contacts.filters.account = this.selectedAccount
      this.contacts.refresh()
      this.$emit('clicked-next')
    },
    handleCheckboxClick({ status, contactID, email }) {
      // depending on payload status add or remove that key
      // plainObject is used instead of an array because of O(1) lookup for <ContactCheckBox />
      if (status) {
        this.contactsToInclude = Object.assign({}, this.contactsToInclude, {
          [contactID]: { email },
        })
      } else {
        let contactsToInclude = Object.assign({}, this.contactsToInclude)
        delete contactsToInclude[contactID]
        this.contactsToInclude = contactsToInclude
      }
    },
    addAnotherContactForm() {
      let newFormsCount = this.addContactFormCount + 1
      let blankForm = {
        firstName: '',
        lastName: '',
        title: '',
        email: '',
        phone: '',
      }
      let newForms = Object.assign({}, this.addContactForms, { [newFormsCount]: blankForm })
      this.addContactForms = newForms
      this.addContactFormCount = newFormsCount
    },
    async createLead() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data
      let validationResults = this.stepTwoClientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      this.loading = true

      // if it gets this far and any of the sub-forms are completed, need to create contact(s)
      let contacts = []
      for (let i = 0; i < this.addContactFormCount; ++i) {
        let n = i + 1
        let currentForm = this.addContactForms[n]
        let isValid = this.isContactFormValid(currentForm)
        // if isValid and any field has length, then form is completely filled
        if (isValid && currentForm.firstName.length) {
          // NOTE( Bruno 5-4-20):
          //       client-side form includes one phone number, so that is being sent as phoneNumber1
          //       server-side does not yet include contact.position, so that is not being sent for now
          let contactData = {
            first_name: currentForm.firstName,
            last_name: currentForm.lastName,
            email: currentForm.email,
            phone_number_1: currentForm.phone,
            account: this.selectedAccount,
          }
          contacts.push(contactData)
        }
      }
      contacts = [
        ...contacts,
        ...Object.keys(this.contactsToInclude).map(contactID => this.contactsToInclude[contactID]),
      ]

      Lead.api.create(this.leadTitle, this.selectedAccount, contacts).then(response => {
        this.$router.push({ name: 'LeadsDetail', params: { id: response.data.id } })
      })
    },
    stepOneClientSideValidations() {
      let formErrors = {
        leadTitleIsBlank: this.leadTitleIsBlank,
        accountNotSelected: this.accountNotSelected,
      }
      let isFormValid = !this.leadTitleIsBlank && !this.accountNotSelected

      return [isFormValid, formErrors]
    },
    stepTwoClientSideValidations() {
      // if any "Add Contact" field is filled in a sub-form, then all fields must be filled for that sub-form
      let formErrors = { addContactForms: {} }
      let areFormsValid = true

      for (let i = 0; i < this.addContactFormCount; ++i) {
        let n = i + 1
        let currentForm = this.addContactForms[n]
        let isValid = this.isContactFormValid(currentForm)
        if (!isValid) {
          formErrors.addContactForms[n] = true
          areFormsValid = false
        }
      }

      return [areFormsValid, formErrors]
    },
    isContactFormValid(formData) {
      // Must be entirely blank or fully completed
      let userInputPresent =
        formData.firstName.length ||
        formData.lastName.length ||
        formData.email.length ||
        formData.title.length ||
        formData.phone.length

      let anyFieldBlank =
        !formData.firstName.length ||
        !formData.lastName.length ||
        !formData.email.length ||
        !formData.title.length ||
        !formData.phone.length

      return !userInputPresent || (userInputPresent && !anyFieldBlank)
    },
  },
  computed: {
    leadTitleIsBlank() {
      return !this.leadTitle.length
    },
    accountNotSelected() {
      return !this.selectedAccount
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
    @include base-font-styles();
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

.errors {
  color: $coral;
}
</style>
