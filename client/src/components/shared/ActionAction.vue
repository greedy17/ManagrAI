<template>
  <div class="flexbox-container">
    <div class="flexbox-container__column">
      <h4>Contacts</h4>
      <div
        class="form__element-error"
        v-if="showErrors && !linkedContactsValid"
        style="margin-bottom: 0.5rem;"
      >
        Select one or more contacts
      </div>
      <ContactBox
        v-for="contact in lead.linkedContactsRef"
        :contact="contact"
        @toggle="toggleActive($event)"
        :isActive="contactIsActive(contact.id)"
        :key="contact.id"
      />
    </div>

    <form @submit.prevent="onSubmit" class="flexbox-container__column" style="flex: 2">
      <div class="form">
        <div class="form__element">
          <div class="form__element-header">Type</div>
          <select
            class="form__select"
            v-model="action.actionType"
            v-if="!actionChoices.refreshing && actionChoices.list.length > 0"
          >
            <option v-for="(choice, index) in actionChoices.list" :key="index" :value="choice.id">{{
              choice.title
            }}</option>
          </select>
          <p v-if="!actionChoices.refreshing && actionChoices.list.length === 0">
            Organization has no action choices
          </p>
          <ComponentLoadingSVG v-if="actionChoices.refreshing" />
          <div class="form__element-error" v-if="showErrors && !actionTypeValid">
            Select an action from the list.
          </div>
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <textarea class="form__textarea" v-model="action.actionDetail" />
        </div>
      </div>
      <div
        class="form__element"
        style="display: flex; flex-direction: column; align-items: flex-end;"
      >
        <button type="submit" class="form__button" :disabled="saving">
          <span v-if="!saving">Save</span>
          <ComponentLoadingSVG v-if="saving" />
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import ContactBox from '@/components/shared/ContactBox'

import CollectionManager from '@/services/collectionManager'
import Action from '@/services/actions'
import ActionChoice from '@/services/action-choices'

export default {
  name: 'ActionAction',
  components: { ContactBox },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      action: Action.create({
        lead: this.lead.id,
      }),
      actionChoices: CollectionManager.create({
        ModelClass: ActionChoice,
      }),
      saving: false,
      showErrors: false,
    }
  },
  created() {
    this.refreshActionChoices()
  },
  computed: {
    formValid() {
      return this.actionTypeValid
    },
    linkedContactsValid() {
      return this.action.linkedContacts.length > 0
    },
    actionTypeValid() {
      return !!this.action.actionType
    },
  },
  methods: {
    reset() {
      this.action = Action.create({
        lead: this.lead.id,
        actionType: this.actionChoices.list.length > 0 ? this.actionChoices.list[0].id : null,
      })
    },
    async refreshActionChoices() {
      await this.actionChoices.refresh()
      if (this.actionChoices.list.length > 0) {
        this.action.actionType = this.actionChoices.list[0].id
      }
    },
    toggleActive(contactId) {
      if (this.action.linkedContacts.includes(contactId)) {
        this.action.linkedContacts = this.action.linkedContacts.filter(id => id !== contactId)
      } else {
        this.action.linkedContacts.push(contactId)
      }
    },
    contactIsActive(contactId) {
      return this.action.linkedContacts.includes(contactId)
    },
    onSubmit() {
      if (!this.formValid) {
        this.showErrors = true
        return
      } else {
        this.showErrors = false
      }

      this.saving = true
      Action.api
        .create(this.action)
        .then(() => {
          this.reset()
          this.$Alert.alert({
            type: 'success',
            timeout: 3000,
            message: `
              <p>Action saved.</p>
            `,
          })
        })
        .catch(error => {
          this.$Alert.alert({
            type: 'error',
            timeout: 3000,
            message: `
              <h3>Error</h3>
              <p>There was an error saving this action.</p>
            `,
          })
          // eslint-disable-next-line no-console
          console.error(error)
        })
        .finally(() => {
          this.saving = false
        })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/forms';
@import '@/styles/mixins/inputs';
</style>
