<template>
  <div class="text-action">
    <div class="message-recipient">
      <span>To:</span>
      <DropDownSelect
        v-if="leadLinkedContactsRef"
        :items.sync="leadLinkedContacts"
        displayKey="full_name"
        valueKey="id"
        v-model="recipients"
        multi
        searchable
        local
      />
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
      sendingMessage: false,
    }
  },
  created() {
    this.leadLinkedContacts = this.leadLinkedContactsRef
  },
  computed: {
    isComplete() {
      return this.body.length > 0 && this.recipients.length > 0
    },
    leadLinkedContactsRef: {
      get() {
        return this.$attrs.lead.linkedContactsRef
      },
    },
  },
  methods: {
    async sendMessage() {
      this.sendingMessage = true
      // get the ref to avoid having to search the backend again
      let contactRefs = this.leadLinkedContactsRef.filter(c => this.recipients.includes(c.id))

      await Messages.sendMessage(this.body, contactRefs, this.$attrs.lead.id)
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
.message-recipient {
  margin-bottom: 3rem;
  > .dropdown {
    width: 80%;
  }
}
</style>
