<template>
  <div class="toolbar">
    <!-- Hidding WIP as Marcy requested PB 05/15/2020
   <div class="top-menu">
      <img class="edit icon" src="@/assets/images/pencil.svg" alt="icon" />
      <img class="more icon" src="@/assets/images/more_horizontal.svg" alt="icon" />
    </div> -->
    <div class="lead-name">
      <h2>{{ lead.title }}</h2>
    </div>
    <div class="rating">
      <LeadRating
        :label="true"
        :rating="lead.rating"
        @close-modal="listModal.isOpen = false"
        @updated-rating="emitUpdatedRating"
      />
    </div>
    <div class="lead-lists">
      <div :style="{ display: 'flex', flexFlow: 'row', justifyContent: 'center' }">
        <button class="add-to-a-list" @click="openListsModal">Add to a List</button>
      </div>
      <div class="header">Lists</div>
      <div class="container">
        <Modal v-if="listModal.isOpen" dimmed :width="40" @close-modal="closeListModal">
          <ComponentLoadingSVG v-if="myLists.refreshing" />
          <template v-else>
            <h3>Check all lists this lead should be in:</h3>
            <div v-for="list in myLists.list" :key="list.id" class="list-items">
              <span
                class="list-items__item__select"
                :style="{ display: 'flex', flexFlow: 'row', alignItems: 'center' }"
              >
                <Checkbox
                  name="lists"
                  @checkbox-clicked="toggleSelectedList(list)"
                  :checked="!!selectedLists[list.id]"
                />
                <span class="list-items__item">{{ list.title }}</span>
              </span>
            </div>
            <h5>To remove Opportunity from all lists, leave all checkboxes blank</h5>
            <div :style="{ display: 'flex', flexFlow: 'row' }">
              <button class="update-lists" @click="onUpdateLists">Save</button>
            </div>
          </template>
        </Modal>
        <span v-if="lists.list.length <= 0" class="list" :style="{ marginLeft: '1rem' }">
          None
        </span>
        <LeadList
          @remove-lead="removeLeadFromList($event, i)"
          v-else
          class="list"
          v-for="(list, i) in allLists"
          :key="list.id"
          :listName="list.title"
          :listId="list.id"
          :dark="true"
        />
      </div>
    </div>
    <div class="account-link" @click="goToProspect">{{ lead.accountRef.name }}</div>
    <div v-if="!editAmount" class="amount" @click="onEditAmount">
      Amount:
      <span>{{ lead.amount | currency }}</span>
    </div>
    <div v-else class="amount-editable">
      Amount:
      <form class="amount-form" @submit.prevent="updateAmount">
        <input v-model="tempAmount" type="number" />
        <img class="save" src="@/assets/images/checkmark.svg" @click="updateAmount" />
        <img class="reset" src="@/assets/images/remove.svg" @click="resetAmount" />
      </form>
    </div>
    <div
      v-if="!editExpectedCloseDate"
      class="expected-close-date section-shadow"
      @click="onEditExpectedCloseDate"
    >
      Expected Close Date: <span>{{ lead.expectedCloseDate | dateShort }}</span>
    </div>
    <div v-else class="expected-close-date-editable">
      Expected Close Date:
      <form class="expected-close-date-form" @submit.prevent="() => {}">
        <input
          v-model="tempExpectedCloseDate"
          @change="updateExpectedCloseDate"
          type="date"
          class="form__input"
        />
        <img
          class="reset"
          src="@/assets/images/remove.svg"
          @click="editExpectedCloseDate = false"
        />
      </form>
    </div>
    <div class="contacts">
      <div class="header section-shadow">
        <span>Contacts</span>
        <img
          class="contacts-modal-icon"
          style="margin: 0 1rem 0 auto;"
          src="@/assets/images/more_horizontal.svg"
          @click.stop="openContactsModal"
        />
      </div>
      <div v-if="contactsLoading" class="contacts-loading contacts-container section-shadow">
        <ComponentLoadingSVG />
      </div>
      <div v-else-if="leadContacts.list.length" class="contacts-container">
        <div class="contact section-shadow" v-for="contact in leadContacts.list" :key="contact.id">
          <img src="@/assets/images/sara-smith.png" alt="contact image" />
          <span class="name">{{
            contact.fullName.length > 0 ? contact.fullName : contact.email
          }}</span>
          <div class="phone button">
            <img class="icon" src="@/assets/images/telephone.svg" alt="icon" />
          </div>
          <div class="text button">
            <img class="icon" src="@/assets/images/sms.svg" alt="icon" />
          </div>
          <div class="email button">
            <img class="icon" src="@/assets/images/email.svg" alt="icon" />
          </div>
        </div>
      </div>
      <div v-else class="container">
        <span class="no-items-message">No Contacts</span>
      </div>
    </div>
    <div class="files">
      <div
        class="header section-shadow"
        :style="
          leadContacts.list.length
            ? ' margin-top: 1rem;'
            : 'border-top: 1px solid #eeeeee; margin-top: 1rem;'
        "
      >
        <span>Files</span>
        <img
          class="add"
          style="margin: 0 1rem 0 auto;"
          src="@/assets/images/add.svg"
          @click="$refs.file.click()"
        />
        <input type="file" accept="*" hidden ref="file" @change="onFileUpload" />
      </div>
      <div class="container">
        <template v-if="this.lead.filesRef.length > 0">
          <div class="file section-shadow" v-for="file in sortedFiles" :key="file.id">
            <img class="icon" src="@/assets/images/document.svg" alt="icon" />
            {{ file.filename }}
            <img
              class="add"
              style="margin: 0 1rem 0 auto;"
              src="@/assets/images/remove.svg"
              @click="deleteFile(file)"
            />
          </div>
        </template>
        <span v-else class="no-items-message">No Files</span>
      </div>
    </div>
    <Modal v-if="fileUploadLoading" :width="10">
      <ComponentLoadingSVG />
    </Modal>
    <Modal v-if="contactsModal.isOpen" :width="45" dimmed @close-modal="closeContactsModal">
      <ComponentLoadingSVG v-if="accountContacts.refreshing" />
      <div v-else class="step-3">
        <div class="form-field">
          <h2 style="text-align: center; margin-bottom: 3.5rem;">Manage Contacts</h2>
          <label>Account Contacts</label>
          <p v-if="!accountContacts.list.length">No contacts available.</p>
          <ContactCheckBox
            v-else
            v-for="contact in accountContacts.list"
            :key="contact.id"
            :contact="contact"
            :checked="!!contactsModal.selectedContacts[contact.id]"
            @checkbox-clicked="handleCheckboxClick"
          />
        </div>
        <div class="form-field">
          <AddContact
            v-for="(contactForm, idx) in contactsModal.addContactForms"
            :key="idx"
            :form="contactForm"
            :error="
              contactsModal.errors.addContactForms && contactsModal.errors.addContactForms[idx]
            "
          />
        </div>
        <div class="form-field">
          <label @click="addAnotherContactForm" class="add-another-button">
            <img class="icon" src="@/assets/images/add.svg" alt="icon" />
            Add Another
          </label>
        </div>
        <div class="button-container">
          <button tabindex="0" v-if="!contactsModal.loading" @click="updateContacts">
            Update
          </button>
          <ComponentLoadingSVG v-else style="margin: 1rem 1rem 0 auto;" />
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import LeadRating from '@/components/leads-detail/LeadRating'
import LeadList from '@/components/shared/LeadList'
import CollectionManager from '@/services/collectionManager'
import List from '@/services/lists'
import File from '@/services/files'
import Checkbox from '@/components/leads-new/CheckBox'
import Contact from '@/services/contacts'
import ContactCheckBox from '@/components/leads-new/ContactCheckBox'
import AddContact from '@/components/leads-new/AddContact'

function fileSorter(firstFile, secondFile) {
  if (firstFile.filename.toLowerCase() > secondFile.filename.toLowerCase()) {
    return 1
  }
  if (secondFile.filename.toLowerCase() > firstFile.filename.toLowerCase()) {
    return -1
  }
  return 0
}

function contactsModalReducer(acc, contact) {
  acc[contact.id] = contact
  return acc
}

function listsModalReducer(acc, list) {
  acc[list.id] = list
  return acc
}

function listSorter(firstList, secondList) {
  if (firstList.title.toLowerCase() > secondList.title.toLowerCase()) {
    return 1
  }
  if (secondList.title.toLowerCase() > firstList.title.toLowerCase()) {
    return -1
  }
  return 0
}

export default {
  name: 'ToolBar',
  components: {
    LeadRating,
    LeadList,
    Checkbox,
    ContactCheckBox,
    AddContact,
  },
  props: {
    lead: {
      type: Object,
      required: true,
    },
    lists: {
      type: Object,
      default: () => CollectionManager.create(),
    },
    leadContacts: {
      type: Object,
      default: () => CollectionManager.create(),
    },
  },
  data() {
    return {
      //leads to add to a list
      addToList: [],
      listModal: {
        isOpen: false,
      },
      contactsModal: {
        loading: false,
        isOpen: false,
        selectedContacts: {},
        errors: {},
        addContactForms: [
          {
            firstName: '',
            lastName: '',
            title: '',
            email: '',
            phone: '',
          },
        ],
      },
      accountContacts: CollectionManager.create({
        ModelClass: Contact,
        filters: {
          account: this.lead.account,
        },
      }),
      fileUploadLoading: false,
      myLists: CollectionManager.create({
        ModelClass: List,
        filters: {
          byUser: this.$store.state.user.id,
          ordering: 'title',
        },
      }),
      editAmount: false,
      tempAmount: this.lead.amount,
      editExpectedCloseDate: false,
      tempExpectedCloseDate: null,
      contactsLoading: false,
      // start @ true once things built out, if going the ContactAPI.retrieve route
      selectedLists: {},
    }
  },

  computed: {
    usersLists() {
      return this.myLists.list
    },
    allLists() {
      return this.lists.list
    },
    sortedFiles() {
      let copy = [...this.lead.filesRef]
      return copy.sort(fileSorter)
    },
  },
  methods: {
    async removeLeadFromList(listId, listIndex) {
      await List.api.removeFromList([this.lead.id], listId)
      this.lists.list.splice(listIndex, 1)
    },
    async addLeadsToList() {
      // make backend endpoint for this to be easier
      let promises = this.addToList.map(l => List.api.addToList([this.lead.id], l))
      try {
        await Promise.all(promises)
      } finally {
        this.listModal.isOpen = false
      }
    },
    addToPendingList(id) {
      let index = this.addToList.findIndex(i => i == id)
      if (index > -1) {
        this.addToList.splice(index, 1)
      } else {
        this.addToList.push(id)
      }
    },
    async openListsModal() {
      await this.myLists.refresh()
      this.selectedLists = this.lists.list.reduce(listsModalReducer, {})
      this.listModal.isOpen = true
    },
    closeListModal() {
      this.listModal.isOpen = false
      this.selectedLists = {}
    },
    goToProspect() {
      this.$router.push({ name: 'Prospect' })
    },
    emitUpdatedRating(rating) {
      this.$emit('updated-rating', rating)
    },
    onEditAmount() {
      this.editAmount = true
    },
    updateAmount() {
      this.$emit('updated-amount', this.tempAmount)
      this.editAmount = false
    },
    resetAmount() {
      this.tempAmount = this.lead.amount
      this.editAmount = false
    },
    onEditExpectedCloseDate() {
      let date
      if (this.lead.expectedCloseDate) {
        date = new Date(this.lead.expectedCloseDate).toISOString().split('T')[0]
      } else {
        date = new Date().toISOString().split('T')[0]
      }
      this.tempExpectedCloseDate = date
      this.editExpectedCloseDate = true
    },
    updateExpectedCloseDate() {
      this.$emit('updated-expected-close-date', this.tempExpectedCloseDate)
      this.editExpectedCloseDate = false
    },
    toggleSelectedList(list) {
      if (this.selectedLists[list.id]) {
        let copy = { ...this.selectedLists }
        delete copy[list.id]
        this.selectedLists = copy
      } else {
        this.selectedLists = { ...this.selectedLists, [list.id]: list }
      }
    },
    onUpdateLists() {
      let selectedLeads = [this.lead.id]
      let selectedLists = Object.keys(this.selectedLists)
      List.api.bulkUpdate(selectedLeads, selectedLists).then(() => {
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Lists updated!',
        })
        this.lists.list = Object.values(this.selectedLists).sort(listSorter)
        this.closeListModal()
      })
    },
    onFileUpload(e) {
      let file = e.target.files[0]
      this.fileUploadLoading = true
      File.api
        .create(file, this.lead.id)
        .then(response => {
          this.lead.filesRef = [...this.lead.filesRef, response.data]
          this.$Alert.alert({
            type: 'success',
            timeout: 3000,
            message: `File uploaded as "${response.data.filename}"!`,
          })
        })
        .finally(() => (this.fileUploadLoading = false))
    },
    deleteFile(file) {
      File.api.delete(file.id).then(() => {
        this.lead.filesRef = this.lead.filesRef.filter(f => f.id !== file.id)
      })
    },
    async openContactsModal() {
      await this.accountContacts.refresh()
      this.contactsModal.selectedContacts = this.leadContacts.list.reduce(contactsModalReducer, {})
      this.contactsModal.isOpen = true
    },
    closeContactsModal() {
      this.contactsModal.isOpen = false
      this.contactsModal.selectedContacts = {}
    },
    handleCheckboxClick({ status, contactID, email }) {
      if (status) {
        this.contactsModal.selectedContacts = {
          ...this.contactsModal.selectedContacts,
          [contactID]: { email },
        }
      } else {
        let selectedContacts = { ...this.contactsModal.selectedContacts }
        delete selectedContacts[contactID]
        this.contactsModal.selectedContacts = selectedContacts
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
      this.contactsModal.addContactForms.push(blankForm)
    },
    async updateContacts() {
      // reset component data when submission begins, in case of prior request
      this.contactsModal.errors = {}

      // check form data
      let validationResults = this.contactsModalValidations()
      let isFormValid = validationResults[0]
      this.contactsModal.errors = validationResults[1]
      if (!isFormValid) {
        return
      }

      this.contactsModal.loading = true

      // if it gets this far and any of the sub-forms are completed, need to create contact(s)
      let contacts = []
      for (let i = 0; i < this.contactsModal.addContactForms.length; ++i) {
        let currentForm = this.contactsModal.addContactForms[i]
        let isValid = this.isContactFormValid(currentForm)
        // if isValid and any field has length, then form is completely filled
        if (isValid && currentForm.firstName.length) {
          let contactData = {
            firstName: currentForm.firstName,
            lastName: currentForm.lastName,
            email: currentForm.email,
            phone: currentForm.phone,
          }
          contacts.push(contactData)
        }
      }
      let account = this.lead.account

      if (contacts.length) {
        let promises = contacts.map(cData =>
          Contact.api.create(cData.firstName, cData.lastName, cData.email, cData.phone, account),
        )
        Promise.all(promises)
          .then(responses => {
            let newContactIDs = responses.map(r => r.data.id)
            let selectedContactIDs = Object.keys(this.contactsModal.selectedContacts)
            return [...newContactIDs, ...selectedContactIDs]
          })
          .then(allContactsForLead => {
            return Contact.api.linkToLeads(allContactsForLead, [this.lead.id])
          })
          .then(response => {
            this.$Alert.alert({
              type: 'success',
              timeout: 3000,
              message: 'Contacts updated!',
            })
            this.leadContacts.list = response.data.map(c => Contact.fromAPI(c))
            this.closeContactsModal()
          })
          .finally(() => {
            this.contactsModal.loading = false
          })
      } else {
        let selectedContactIDs = Object.keys(this.contactsModal.selectedContacts)
        Contact.api
          .linkToLeads(selectedContactIDs, [this.lead.id])
          .then(response => {
            this.$Alert.alert({
              type: 'success',
              timeout: 3000,
              message: 'Contacts updated!',
            })
            this.leadContacts.list = response.data.map(c => Contact.fromAPI(c))
            this.closeContactsModal()
          })
          .finally(() => {
            this.contactsModal.loading = false
          })
      }
    },
    contactsModalValidations() {
      // if any "Add Contact" field is filled in a sub-form, then all fields must be filled for that sub-form
      let formErrors = { addContactForms: {} }
      let areFormsValid = true

      for (let i = 0; i < this.contactsModal.addContactForms.length; ++i) {
        let currentForm = this.contactsModal.addContactForms[i]
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/forms';

.toolbar {
  @include standard-border();
  background-color: $white;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  min-height: 50rem;
  width: 100%;
  display: flex;
  flex-flow: column;
}

.toolbar,
.toolbar > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 14px;
}

.top-menu {
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 2.125rem;
  padding: 0 0.75rem;

  .icon {
    height: 1.25rem;
    opacity: 0.4;
  }

  .edit {
    margin-right: auto;
  }

  .more {
    margin-left: auto;
  }
}

.lead-name {
  padding: 0 15%;
  text-align: center;
}

.rating {
  display: flex;
  flex-flow: row;
  justify-content: center;
}

.lead-lists {
  padding: 1.25rem 1.25rem 0.625rem 1.25rem;
  border-bottom: 5px solid $coral;

  .header {
    margin-bottom: 0.625rem;
    font-weight: bold;
  }

  .container {
    display: flex;
    flex-flow: column;
    overflow-y: scroll;

    p {
      margin-left: 1rem;
    }

    .list {
      margin: 0.625rem;
      height: 1.75rem;
    }
  }
}

.account-link {
  @include pointer-on-hover();
  @include disable-text-select();
  height: 3rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  color: $dark-green;
  text-decoration: underline;

  &:hover {
    font-weight: bold;
  }
}

.amount {
  @include pointer-on-hover();
  height: 3rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;

  &:hover {
    font-weight: bold;
  }

  span {
    margin-left: 0.5rem;
  }
}

.amount-editable {
  @include pointer-on-hover();
  height: 4rem;
  display: flex;
  flex-flow: column;
  align-items: center;
  font-size: 1.125rem;
  margin-bottom: 0.75rem;

  span {
    margin-left: 0.5rem;
  }

  form {
    width: 100%;
    box-sizing: border-box;
    padding: 0 10%;
    margin-top: 0.5rem;
    display: flex;
    flex-flow: row;
    align-items: center;

    input {
      @include input-field();
      margin-left: 0.5rem;
      width: 10rem;
    }

    .save {
      background-color: $dark-green;
      border-radius: 3px;
      margin-left: auto;
    }

    .reset {
      background-color: $silver;
      border-radius: 3px;
      margin-left: auto;
    }
  }
}

.expected-close-date {
  @include pointer-on-hover();
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  padding-bottom: 1rem;

  &:hover {
    font-weight: bold;
  }

  span {
    margin-left: 0.5rem;
  }
}

.expected-close-date-editable {
  @include pointer-on-hover();
  height: 4rem;
  display: flex;
  flex-flow: column;
  align-items: center;
  margin-bottom: 0.75rem;

  span {
    margin-left: 0.5rem;
  }

  form {
    width: 100%;
    box-sizing: border-box;
    padding: 0 10%;
    margin-top: 0.5rem;
    display: flex;
    flex-flow: row;
    align-items: center;

    input {
      @include input-field();
      margin-left: 0.5rem;
      width: 12rem;
    }

    .save {
      background-color: $dark-green;
      border-radius: 3px;
      margin-left: auto;
    }

    .reset {
      background-color: $silver;
      border-radius: 3px;
      margin-left: auto;
    }
  }
}

.contacts {
  .header {
    padding-left: 1.25rem;
    height: 3.375rem;
    display: flex;
    flex-flow: row;
    align-items: center;

    span {
      font-weight: bold;
    }
  }

  .container {
    min-height: 3rem;
    display: flex;
    flex-flow: column;
  }

  .contact {
    display: flex;
    flex-flow: row;
    align-items: center;
    height: 3rem;
    padding-left: 1.25rem;
    font-size: 14px;

    img {
      height: 1.25rem;
      border-radius: 50%;
      margin-right: 1rem;
    }

    .phone {
      margin-left: auto;
    }

    .text {
      margin-left: 0.5rem;
    }

    .email {
      margin: 0 0.5rem;
    }

    .button {
      @include pointer-on-hover();
      height: 1.5rem;
      width: 1.5rem;
      background-color: $soft-gray;
      border-radius: 5px;
      display: flex;
      flex-flow: row;
      align-items: center;
      justify-content: center;

      .icon {
        height: 1rem;
        margin: auto;
      }
    }
  }
}

.contacts-loading {
  height: 3rem;
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
}

.files {
  .header {
    padding-left: 1.25rem;
    height: 3.375rem;
    display: flex;
    flex-flow: row;
    align-items: center;

    span {
      font-weight: bold;
    }

    .add {
      @include pointer-on-hover();
      background-color: $soft-gray;
      border-radius: 5px;
      height: 1.5rem;
      width: 1.5rem;
    }
  }

  .container {
    min-height: 3rem;
    display: flex;
    flex-flow: column;
  }

  .file {
    display: flex;
    flex-flow: row;
    align-items: center;
    min-height: 3rem;
    padding-left: 1.25rem;
    font-size: 14px;

    .add {
      @include pointer-on-hover();
      border-radius: 5px;
      height: 1.25rem;
      opacity: 0.6;
    }

    .icon {
      height: 1.25rem;
      opacity: 0.6;
      margin-right: 1rem;
    }
  }
}
.no-items-message {
  font-weight: bold;
  align-self: center;
  margin: 1rem 0.75rem;
}
.list-items {
  display: flex;
  padding: 1rem;
  border-bottom: 1px solid $mid-gray;
  &__item {
    flex: 2;
    margin: 0.5rem;

    &__select {
      flex: 0.5;
    }
  }
}

.add-to-a-list {
  @include primary-button;
  width: 70%;
  margin-bottom: 1rem;
}

.update-lists {
  @include primary-button;
  margin-left: auto;
}

.contacts-modal-icon {
  @include pointer-on-hover;
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
    margin: 1rem 1rem 0 auto;
  }
}

.form-field {
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

  .add-another-button {
    @include pointer-on-hover();
    display: flex;
    flex-flow: row;
    align-items: center;

    .icon {
      height: 1.4rem;
      width: 1.4rem;
      margin-right: 1rem;
    }
  }
}
</style>
