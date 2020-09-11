<template>
  <div class="text-action">
    <template v-if="!isTextConnected">
      <div>
        <span class="muted">
          Please Enable Text Integration to use this feature in your settings
        </span>
      </div>
    </template>
    <template v-else>
      <div class="message-recipients">
        <div class="selected-recipients">
          <span>To:</span>
          <div class="contacts">
            <div
              :key="c.id"
              v-for="(c, index) in this.leadLinkedContactsRef.filter(c =>
                recipients.includes(c.id),
              )"
            >
              <div
                class="selected-recipients__contact"
                :class="{ invalid: ~invalidSelectedContacts.findIndex(i => i.id == c.id) }"
                @click="removeRecipient(index)"
              >
                <svg class="icon-remove" viewBox="0 0 24 24">
                  <use xlink:href="@/assets/images/remove.svg#remove" />
                </svg>
                <img class="image" src="@/assets/images/sara-smith.png" alt="contact image" />
                <span>{{ c.full_name }}</span>
              </div>
            </div>
          </div>
          <div class="dd__contacts">
            <DropDownSelect
              v-if="leadLinkedContactsRef"
              :items="leadLinkedContacts"
              :itemsRef.sync="recipientsRef"
              displayKey="full_name"
              valueKey="id"
              v-model="recipients"
              multi
              searchable
              closeOnSelect
              local
              hidden
            />
          </div>
        </div>
      </div>
      <div class="message-content">
        <textarea class="form__textarea" rows="8" placeholder="Detail" v-model="body" />
      </div>

      <div class="save-button-container">
        <button :disabled="sendingMessage || !isComplete" class="button" @click="sendMessage">
          <ComponentLoadingSVG v-if="sendingMessage" />
          <span v-if="!sendingMessage">Send Text</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script>
import DropDownSelect from '@/components/forms/DropDownSelect'
import Messages from '@/services/messages'
export default {
  name: 'TextAction',
  components: { DropDownSelect },
  data() {
    return {
      contacts: [],
      body: '',
      contactsToInclude: {},
      recipients: [],
      leadLinkedContacts: [],
      recipientsRef: [],
      sendingMessage: false,
    }
  },
  created() {
    this.leadLinkedContacts = this.leadLinkedContactsRef
  },
  computed: {
    isTextConnected() {
      return !!this.$store.state.user.textConnected
    },
    isComplete() {
      return this.body.length > 0 && this.recipients.length > 0
    },
    leadLinkedContactsRef: {
      get() {
        return this.$attrs.lead.linkedContactsRef
      },
    },
    invalidSelectedContacts() {
      //gets selected contacts that have no phone number
      return this.leadLinkedContactsRef.filter(
        c => this.recipients.includes(c.id) && c.phone_number_1.length < 1,
      )
    },
  },
  methods: {
    removeRecipient(i) {
      this.recipients.splice(i, 1)
    },
    resetText() {
      this.recipients = []
      this.body = ''
    },
    async sendMessage() {
      this.sendingMessage = true
      // get the ref to avoid having to search the backend again
      let contactRefs = this.leadLinkedContactsRef.filter(c => this.recipients.includes(c.id))
      this.sendingMessage = false
      if (this.invalidSelectedContacts.length > 0) {
        let invalidContacts = this.invalidSelectedContacts.map(c => c.full_name).join(', ')
        this.$Alert.alert({
          type: 'error',
          message: `<h4> Cannot Send Message to the following contact(s) <strong>${invalidContacts}<strong> because of invalid phone number please remove contacts</h4>`,
          timeout: 5000,
        })

        return
      }
      try {
        await Messages.sendMessage(this.body, contactRefs, this.$attrs.lead.id)

        this.resetText()
      } catch (e) {
        let { response } = { ...e }
        if (response.status == 400) {
          this.$Alert.alert({
            type: 'error',
            message: `<h4> Cannot Send Message to the following contact(s) <strong>${response.data.detail.invalid_phone}<strong> because of invalid phone number please remove contacts</h4>`,
            timeout: 5000,
          })
        }
      }

      this.sendingMessage = false
    },
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

@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';

.text-action {
  width: 100%;
  display: flex;
  flex-flow: column;
  > * {
    margin: 1rem;
  }
}
.dropdown-search {
  width: 100px;
}
::v-deep .dropdown {
  // manually setting input style here

  .dropdown-input-container {
    width: 100%;
    border-radius: 30px;
    border: 1px solid $soft-gray;
    > input[type='text'] {
      min-width: 0;
      padding: 0;
    }
    &.disabled {
      border: 1px solid gray;
    }
  }
}
.dd__contacts {
  width: 15rem;
  height: 2rem;
  display: flex;
  align-items: center;
}

.save-button-container {
  display: flex;
  flex-flow: row;
}

.save-button {
  @include primary-button();
  margin-left: auto;
}
.message-content {
  display: flex;
  width: 90%;
}

.selected-recipients {
  display: flex;

  .contacts {
    display: flex;
    max-width: 50rem;
    overflow-x: scroll;
  }

  &__contact {
    &:hover {
      cursor: pointer;
    }
    > .icon-remove {
      width: 10px;
      height: 10px;
    }
    display: flex;
    margin: 0rem 1rem;
    align-items: center;
    background-color: rgba($color: $light-gray-blue, $alpha: 0.2);
    border-radius: 10px;

    padding: 0.2rem 1rem;
    border-radius: 0.3rem;

    max-width: 10rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
.invalid {
  background-color: rgba(230, 0, 0, 0.4);
  color: rgba(240, 0, 15, 1);
}
.image {
  height: 1.4rem;
  width: 1.4rem;
  border-radius: 50%;
  margin-right: 0.5rem;
}
</style>
