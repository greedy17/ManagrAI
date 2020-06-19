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
            <h5>To remove Lead from all lists, leave all checkboxes blank</h5>
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
    <div v-if="!editAmount" class="amount section-shadow" @click="onEditAmount">
      Amount:
      <span>{{ lead.amount | currency }}</span>
    </div>
    <div v-else class="amount-editable section-shadow">
      Amount:
      <form class="amount-form" @submit.prevent="updateAmount">
        <input v-model="tempAmount" type="number" />
        <img class="save" src="@/assets/images/checkmark.svg" @click="updateAmount" />
        <img class="reset" src="@/assets/images/remove.svg" @click="resetAmount" />
      </form>
    </div>
    <div class="contacts">
      <div class="header section-shadow">
        <span>Contacts</span>
      </div>
      <div v-if="contactsLoading" class="contacts-loading contacts-container section-shadow">
        <ComponentLoadingSVG />
      </div>
      <div v-else-if="contacts.list.length" class="contacts-container">
        <div class="contact section-shadow" v-for="contact in contacts.list" :key="contact.id">
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
      <div class="header section-shadow" style="border-top: 1px solid #eeeeee; margin-top: 1rem;">
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
          </div>
        </template>
        <span v-else class="no-items-message">No Files</span>
      </div>
      <Modal v-if="fileUploadLoading" :width="10">
        <ComponentLoadingSVG />
      </Modal>
    </div>
  </div>
</template>

<script>
import LeadRating from '@/components/leads-detail/LeadRating'
import LeadList from '@/components/shared/LeadList'
import CollectionManager from '@/services/collectionManager'
import List from '@/services/lists'
import File from '@/services/files'
import Checkbox from '@/components/leads-new/CheckBox'

function fileSorter(firstFile, secondFile) {
  if (firstFile.filename.toLowerCase() > secondFile.filename.toLowerCase()) {
    return 1
  }
  if (secondFile.filename.toLowerCase() > firstFile.filename.toLowerCase()) {
    return -1
  }
  return 0
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

    contacts: {
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
    // NOTE (Bruno 5-7-20): The following code assumes ContactAPI.retrieve gets built in backend in a coming sprint.
    // Instead we may serialize contacts-data within LeadAPI.retrieve
    // fetchContacts() {
    //   let promises = []
    //   for (let i = 0; i < this.lead.linkedContacts.length; ++i) {
    //     let contactID = this.lead.linkedContacts[i]
    //     let promise = Contact.api.retrieve(contactID)
    //     promises.push(promise)
    //   }
    //   Promise.all(promises).then(() => {
    //     // this.contacts needs to be populated by the responses' data
    //     this.contactsLoading = false
    //   })
    // },
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
          timeout: 4000,
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
            timeout: 4000,
            message: `File uploaded as "${response.data.filename}"!`,
          })
        })
        .finally(() => (this.fileUploadLoading = false))
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

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
      width: 6rem;
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
</style>
