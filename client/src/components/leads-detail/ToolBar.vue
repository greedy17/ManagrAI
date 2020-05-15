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
      <LeadRating :label="true" :rating="lead.rating" @updated-rating="emitUpdatedRating" />
    </div>
    <div class="lead-lists">
      <div class="header">Lists</div>
      <div class="container">
        <p v-if="!lead.lists">N/A</p>
        <LeadList
          v-else
          class="list"
          v-for="list in lists.list"
          :key="list.id"
          :listName="list.title"
          :dark="true"
        />
      </div>
    </div>
    <div class="account-link" @click="goToAccount">{{ lead.accountRef.name }}</div>
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
      <div v-else class="contacts-container">
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
    </div>
    <div class="files">
      <div class="header section-shadow">
        <span>Files</span>
      </div>
      <div class="files-container">
        <template v-if="files.lists > 0">
          <div class="file section-shadow" v-for="file in files.lists" :key="file">
            <img class="icon" src="@/assets/images/document.svg" alt="icon" />
            {{ file }}
          </div>
        </template>
        <span class="no-items-message">No Files</span>
      </div>
    </div>
  </div>
</template>

<script>
import LeadRating from '@/components/leads-detail/LeadRating'
import LeadList from '@/components/shared/LeadList'
import CollectionManager from '@/services/collectionManager'

// import Contact from '@/services/contacts'

export default {
  name: 'ToolBar',
  components: {
    LeadRating,
    LeadList,
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
    files: {
      type: Object,
      default: () => CollectionManager.create(),
    },
  },
  data() {
    return {
      editAmount: false,
      tempAmount: this.lead.amount,

      contactsLoading: false,
      // start @ true once things built out, if going the ContactAPI.retrieve route
    }
  },

  methods: {
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
    goToAccount() {
      alert("This should route to account's page")
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

.toolbar {
  @include standard-border();
  background-color: $white;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  height: 50rem;
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
  }

  .container {
    display: flex;
    flex-flow: column;

    p {
      margin-left: 1rem;
    }

    .list {
      margin-bottom: 0.625rem;
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
  }
  .file {
    display: flex;
    flex-flow: row;
    align-items: center;
    height: 3rem;
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
  width: 25%;
  margin: 1rem 0.75rem;
}
</style>
