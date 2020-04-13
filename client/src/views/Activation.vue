<template>
  <div class="invite">
    <NavBar />
    <div class="page-content">
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

.invite {
  height: inherit;
  display: flex;
  flex-flow: column;
  background-color: $off-white;
}

.page-content {
  overflow-x: scroll;
  flex-grow: 1;
  display: flex;
  flex-flow: row;
  justify-content: center;
}

h2 {
  font-family: $base-font-family, $backup-base-font-family;
  color: $main-font-gray;
  text-align: center;
}

form,
.success-prompt {
  margin-top: 50px;
  width: 500px;
  height: 300px;
  background-color: white;
  border-radius: 5px;
  display: flex;
  flex-flow: column;
  align-items: center;
}

input {
  @include input-field();
  height: 40px;
  width: 250px;
  display: block;
  margin: 5px 0;
}

button {
  margin-top: 20px;
  height: 30px;
  width: 150px;
  border-radius: 5px;
  background-color: $dark-green;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #ffffff;

  &:hover {
    cursor: pointer;
  }
}
</style>
