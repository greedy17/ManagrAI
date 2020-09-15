<template>
  <div class="form">
    <div class="step-1">
      <div class="errors">
        <!-- client side validations -->
        <div v-if="isFormValid !== null && !isFormValid && errors.leadTitleIsBlank">
          Opportunity Title may not be blank.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.accountNotSelected">
          Account must be selected.
        </div>
      </div>
      <div class="form-field">
        <label>Opportunity Title</label>
        <input
          v-model="leadTitle"
          :disabled="currentStep > 1"
          class="input"
          tabindex="0"
          type="text"
          placeholder="Title"
        />
      </div>
      <div class="form-field">
        <label>Account Relationship</label>
        <select
          ref="accountsDropdown"
          tabindex="0"
          :disabled="currentStep > 1"
          v-model="selectedAccount"
        >
          <option disabled :value="null">Select Account</option>
          <option v-for="account in accounts.list" :key="account.id" :value="account.id">
            {{ account.name }}
          </option>
        </select>
      </div>
      <div v-if="currentStep == 1" class="button-container">
        <span tabindex="0" @click="toCreateAccount">ADD NEW ACCOUNT</span>
      </div>
      <div v-if="currentStep == 1" class="button-container">
        <button tabindex="0" :disabled="loading" @click="toAddContacts">Next</button>
      </div>
    </div>
    <div v-if="currentStep == 2" class="step-2">
      <div class="errors">
        <!-- client side validations -->
        <div v-if="isFormValid !== null && !isFormValid && errors.newAccountNameIsBlank">
          Account name may not be blank.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.newAccountUrlIsBlank">
          Account URL may not be blank.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.newAccountTypeNotSelected">
          Must select account type.
        </div>
      </div>
      <div class="form-field">
        <label>New Account</label>
        <input
          v-model="newAccountName"
          :disabled="currentStep > 2"
          class="input"
          tabindex="0"
          type="text"
          placeholder="Name"
        />
        <input
          v-model="newAccountURL"
          :disabled="currentStep > 2"
          class="input"
          tabindex="0"
          type="text"
          placeholder="URL"
        />
      </div>
      <div class="form-field">
        <label>Account Type</label>
        <select tabindex="0" v-model="newAccountType" :disabled="currentStep > 2">
          <option disabled :value="null">Select Type</option>
          <option v-for="type in ACCOUNT_TYPES" :key="type" :value="type">{{ type }}</option>
        </select>
      </div>
      <div v-if="currentStep == 2" class="button-container">
        <button tabindex="0" :disabled="loading" @click="createAccount">Next</button>
      </div>
    </div>
    <div v-if="currentStep == 3" class="step-3">
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
          v-for="(contactForm, idx) in addContactForms"
          :key="idx"
          :form="contactForm"
          :error="errors.addContactForms && errors.addContactForms[idx]"
        />
      </div>
      <div class="form-field">
        <label @click="addAnotherContactForm" class="add-another-button">
          <img class="icon" src="@/assets/images/add.svg" alt="icon" />
          Add Another
        </label>
      </div>
      <div class="button-container">
        <button tabindex="0" :disabled="loading" @click="createLead">Next</button>
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

const ACCOUNT_TYPE_RENEWAL = 'RENEWAL'
const ACCOUNT_TYPE_NEW = 'NEW'
const ACCOUNT_TYPES = [ACCOUNT_TYPE_NEW, ACCOUNT_TYPE_RENEWAL]

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
      loading: false,
      leadTitle: '',
      accounts: CollectionManager.create({
        ModelClass: Account,
        filters: {
          pageSize: 2698,
          ordering: 'name',
        },
      }),
      selectedAccount: null,
      newAccountName: '',
      newAccountURL: '',
      newAccountType: null,
      ACCOUNT_TYPES,
      contacts: CollectionManager.create({ ModelClass: Contact }),
      contactsToInclude: {},
      addContactForms: [
        {
          firstName: '',
          lastName: '',
          title: '',
          email: '',
          phone: '',
        },
      ],
      isFormValid: null, // client side validations
      success: null, //server side validations
      errors: {},
    }
  },
  created() {
    this.accounts.refresh()
  },
  methods: {
    toAddContacts() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data
      let validationResults = this.toAddContactsClientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      this.contacts.filters.account = this.selectedAccount
      this.contacts.refresh()
      this.$emit('to-add-contacts')
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
      let blankForm = {
        firstName: '',
        lastName: '',
        title: '',
        email: '',
        phone: '',
      }
      this.addContactForms.push(blankForm)
    },
    createLead() {
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
      for (let i = 0; i < this.addContactForms.length; ++i) {
        let currentForm = this.addContactForms[i]
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
            title: currentForm.title,
          }
          contacts.push(contactData)
        }
      }
      contacts = [...contacts, ...Object.values(this.contactsToInclude)]

      Lead.api.create(this.leadTitle, this.selectedAccount, contacts).then(response => {
        this.$router.push({ name: 'LeadsDetail', params: { id: response.data.id } })
      })
    },
    toAddContactsClientSideValidations() {
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

      for (let i = 0; i < this.addContactForms.length; ++i) {
        let currentForm = this.addContactForms[i]
        let isValid = this.isContactFormValid(currentForm)
        if (!isValid) {
          formErrors.addContactForms[i] = true
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
    toCreateAccount() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data
      let validationResults = this.toCreateAccountClientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      this.selectedAccount = null
      this.$emit('to-create-account') // more descriptive events
    },
    onSelectAccountType({ target: { value } }) {
      this.newAccountType = value
    },
    toCreateAccountClientSideValidations() {
      let formErrors = {
        leadTitleIsBlank: this.leadTitleIsBlank,
      }
      let isFormValid = !this.leadTitleIsBlank

      return [isFormValid, formErrors]
    },
    createAccount() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data
      let validationResults = this.createAccountClientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]

      if (!this.isFormValid) {
        return
      }

      this.loading = true

      let data = {
        name: this.newAccountName,
        url: this.newAccountURL,
        type: this.newAccountType,
      }

      Account.api.create(data).then(account => {
        this.accounts.list = [...this.accounts.list, account]
        this.selectedAccount = account.id
        this.loading = false
        this.$emit('to-add-contacts')
      })
    },
    createAccountClientSideValidations() {
      let formErrors = {
        newAccountNameIsBlank: this.newAccountNameIsBlank,
        newAccountUrlIsBlank: this.newAccountUrlIsBlank,
        newAccountTypeNotSelected: this.newAccountTypeNotSelected,
      }
      let isFormValid =
        !this.newAccountNameIsBlank && !this.newAccountUrlIsBlank && !this.newAccountTypeNotSelected

      return [isFormValid, formErrors]
    },
  },
  computed: {
    leadTitleIsBlank() {
      return !this.leadTitle.length
    },
    accountNotSelected() {
      return !this.selectedAccount
    },
    newAccountNameIsBlank() {
      return !this.newAccountName.length
    },
    newAccountUrlIsBlank() {
      return !this.newAccountURL.length
    },
    newAccountTypeNotSelected() {
      return !this.newAccountType
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
.step-2,
.step-3 {
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

.step-2,
.step-3 {
  margin-top: 3rem;
}

.step-3 {
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

  span {
    @include pointer-on-hover();
    margin: 0.2rem 5% 1rem auto;
    font-weight: 600;
    font-size: 0.8rem;
  }

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
