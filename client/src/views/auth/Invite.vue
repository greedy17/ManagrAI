<template>
  <div class="invite">
    <NavBar />
    <div class="page-content">
      <form v-if="!success" @submit.prevent="handleInvite">
        <h2>Invite</h2>
        <div class="errors">
          <!-- client side validations -->
          <div v-if="isFormValid !== null && !isFormValid && errors.emailIsBlank">
            Fields may not be blank.
          </div>
          <div v-if="isFormValid !== null && !isFormValid && errors.emailsDontMatch">
            Fields must match.
          </div>
          <div v-if="isFormValid !== null && !isFormValid && errors.invalidEmail">
            Must be a valid email address.
          </div>
          <!-- server side validations -->
          <div v-if="success !== null && !success && errors[500]">
            Something went wrong. Please try again later.
          </div>
          <div v-if="success !== null && !success && errors[400]">
            The provided email is associated with an existing account.
          </div>
        </div>
        <!-- type="text" instead of type="email" so we can control UI when invalid -->
        <input v-model="email" type="text" placeholder="email" />
        <input v-model="emailConfirmation" type="text" placeholder="confirm email" />
        <button type="submit">Invite</button>
      </form>
      <div v-else class="success-prompt">
        <h2>Success</h2>
        <p>
          An invitation will be sent to:
          <span :style="{ fontWeight: 'bold' }">{{ email }}</span
          >.
        </p>
        <!-- NOTE(Bruno 4-20-20): below code is temporary, for testing on staging -->
        <div
          :style="{
            wordBreak: 'all',
            padding: '0 1rem',
            display: 'flex',
            flexFlow: 'column',
            alignItems: 'center',
            opacity: '0.4',
          }"
        >
          <div>(For Testing/Staging) Link:</div>
          {{ link }}
        </div>
        <!-- end of temp code -->
        <button @click="resetData">Send Another</button>
      </div>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'

const initialData = {
  email: '',
  emailConfirmation: '',
  type: 'MANAGER', // TODO(Bruno 4-9-20): Make this dynamic
  isFormValid: null,
  errors: {},
  success: null,
  link: '', // NOTE(Bruno 4-20-20): temproary, for staging purposes
}

export default {
  name: 'Invite',
  components: {},
  data() {
    return Object.assign({}, initialData)
  },

  methods: {
    handleInvite() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data for this request
      let validationResults = this.clientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      let organization = this.$store.state.user.organization
      let invitePromise = User.api.invite(this.email, this.type, organization)

      invitePromise
        .then(response => {
          this.link = response.data.activation_link // NOTE(Bruno 4-20-20): this line is temporary, for staging purposes
          this.success = true
        })
        .catch(error => {
          // NOTE: all form field-error validations are completed client side
          this.success = false
          let { status } = error.response
          if (status >= 500) {
            this.errors = { 500: true }
          } else if (status >= 400) {
            // The email already belongs to account, be its state INVITED or otherwise
            this.errors = { 400: true }
          }
        })
    },
    clientSideValidations() {
      let formErrors = {
        emailIsBlank: this.emailIsBlank,
        emailsDontMatch: this.emailsDontMatch,
        invalidEmail: this.invalidEmail,
      }
      let isFormValid = !this.emailIsBlank && !this.emailsDontMatch && !this.invalidEmail

      return [isFormValid, formErrors]
    },
    resetData() {
      Object.assign(this, initialData)
    },
  },
  computed: {
    emailIsBlank() {
      return !this.email.length
    },
    emailsDontMatch() {
      return this.email !== this.emailConfirmation
    },
    invalidEmail() {
      // NOTE: this was taken from http://emailregex.com/
      // eslint-disable-next-line no-useless-escape
      let regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return !regex.test(this.email)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.invite {
  height: inherit;
  display: flex;
  flex-flow: column;
  background-color: $off-white;
}

.page-content {
  flex-grow: 1;
  display: flex;
  flex-flow: row;
  justify-content: center;
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  color: $main-font-gray;
  text-align: center;
}

form,
.success-prompt {
  margin-top: 3.125rem;
  width: 31.25rem;
  height: 18.75rem;
  background-color: $white;
  border-radius: 5px;
  display: flex;
  flex-flow: column;
  align-items: center;
}

input {
  @include input-field();
  height: 2.5rem;
  width: 15.65rem;
  display: block;
  margin: 0.375rem 0;
}

button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 1.875rem;
  width: 9.375rem;
}
</style>
