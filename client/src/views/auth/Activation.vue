<template>
  <div class="activation">
    <form v-if="!success" @submit.prevent="handleActivation">
      <h2>Activate Account</h2>
      <div class="errors">
        <!-- client side validations -->
        <div v-if="isFormValid !== null && !isFormValid && errors.passwordIsBlank">
          Fields may not be blank.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.passwordsDontMatch">
          Fields must match.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.passwordTooShort">
          Password must be 10 characters or longer.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.passwordEntirelyNumeric">
          Password may not be entirely numeric.
        </div>
        <!-- server side validations -->
        <div v-if="success !== null && !success && (errors[500] || errors[404] || errors[400])">
          Something went wrong. Please check your URL and/or request a new link.
        </div>
      </div>
      <input v-model="password" type="password" placeholder="password" />
      <input v-model="passwordConfirmation" type="password" placeholder="confirm password" />
      <button type="submit">Activate</button>
    </form>
    <div v-else class="success-prompt">
      <h2>Activation Successful</h2>
      <p>Please proceed to login screen.</p>
      <button @click="goToLogin">Proceed</button>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'Activation',
  components: {},
  data() {
    return {
      password: '',
      passwordConfirmation: '',
      isFormValid: null, // client side validations
      success: null, // server side validations
      errors: {},
    }
  },
  methods: {
    handleActivation() {
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

      let { uid, token } = this.$route.params
      let activationPromise = User.api.activate(uid, token, this.password)

      activationPromise
        .then(() => {
          this.success = true
        })
        .catch(error => {
          // NOTE: all form field-error validations are completed client side
          this.success = false
          let { status } = error.response
          if (status >= 500) {
            this.errors = { 500: true }
          } else if (status === 404) {
            // The uuid was proper format but did not belong to a user
            this.errors = { 404: true }
          } else if (status >= 400) {
            // Other 400-level status regards the token
            this.errors = { 400: true }
          }
        })
    },
    clientSideValidations() {
      let formErrors = {
        passwordIsBlank: this.passwordIsBlank,
        passwordsDontMatch: this.passwordsDontMatch,
        passwordTooShort: this.passwordTooShort,
        passwordEntirelyNumeric: this.passwordEntirelyNumeric,
      }
      let isFormValid =
        !this.passwordIsBlank &&
        !this.passwordsDontMatch &&
        !this.passwordTooShort &&
        !this.passwordEntirelyNumeric

      return [isFormValid, formErrors]
    },
    goToLogin() {
      this.$router.push({ name: 'Login' })
    },
  },
  computed: {
    passwordIsBlank() {
      return this.password.length === 0
    },
    passwordsDontMatch() {
      return this.password !== this.passwordConfirmation
    },
    passwordTooShort() {
      return this.password.length < 10
    },
    passwordEntirelyNumeric() {
      // if it is NaN --> it was not entirely numeric
      // if it is !NaN
      //      --> either entirely numeric, or
      //      --> at least 1st character is numeric
      // therefore turn castAsInteger back into string and compare with original
      if (this.passwordIsBlank) {
        return false
      }
      let castAsInteger = parseInt(this.password)
      let areEqualAfterRecast = castAsInteger.toString() === this.password
      return !Number.isNaN(castAsInteger) && areEqualAfterRecast
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.activation {
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
  @include standard-border();
  margin-top: 3.125rem;
  width: 31.25rem;
  height: 18.75rem;
  background-color: $white;
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
