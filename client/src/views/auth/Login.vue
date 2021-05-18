<template>
  <div class="login">
    <form @submit.prevent="handleSubmit">
      <h2>Login</h2>
      <div class="errors">
        <!-- client side validations -->
        <div
          v-if="
            isFormValid !== null && !isFormValid && (errors.emailIsBlank || errors.passwordIsBlank)
          "
        >
          {{ errors.emailIsBlank ? 'Field' : 'Fields' }} may not be blank.
        </div>
        <!-- server side validations -->
        <div v-else-if="success !== null && !success && errors[500]">
          Something went wrong, please retry later.
        </div>
        <div v-else-if="success !== null && !success && errors.invalidEmail">
          Invalid or not-activated email.
        </div>
        <div v-else-if="success !== null && !success && errors.invalidPassword">
          Incorrect password.
        </div>
      </div>
      <input :disabled="currentStep > 1" v-model="email" type="text" placeholder="email" />
      <input
        :class="{ hidden: currentStep < 2 }"
        ref="passwordInput"
        v-model="password"
        type="password"
        placeholder="password"
      />
      <button type="submit">{{ currentStep === 1 ? 'Next' : 'Login' }}</button>
      <div style="margin-top: 1rem">
        <router-link :to="{ name: 'Register' }"> No account? Sign Up </router-link>
      </div>
      <div style="margin-top: 1rem">
        <router-link :to="{ name: 'ForgotPassword' }"> Forgot Password? </router-link>
      </div>
      <div style="margin-top: 1rem">
        <p>
          <a href="https://managr.ai/terms-of-service" target="_blank">Term of Service</a>
          |
          <a href="https://managr.ai/documentation" target="_blank">Documentation</a>
          |
          <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
        </p>
      </div>
    </form>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'Login',
  components: {},
  data() {
    return {
      currentStep: 1,
      email: '', // step 1
      password: '', // step 2
      isFormValid: null, // client side validations
      success: null, //server side validations
      errors: {},
    }
  },
  methods: {
    handleSubmit() {
      if (this.currentStep === 1) {
        this.checkAccountStatus()
      } else {
        this.handleLoginAttempt()
      }
    },
    checkAccountStatus() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data for this request
      let validationResults = this.emailClientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      let checkStatusPromise = User.api.checkStatus(this.email)

      checkStatusPromise
        .then(() => {
          this.currentStep = 2
          // setTimeout(..., 0) is used to focus once JS Stack is clear -- for some reason this is needed, even though the
          // element is already on the DOM by this point (it is always present, see template).
          setTimeout(() => this.$refs.passwordInput.focus(), 0)
        })
        .catch((error) => {
          if (error.response.status >= 500) {
            this.errors[500] = true
            this.success = false
          } else if (error.response.status >= 400) {
            // handle invalid or inactive email
            this.errors.invalidEmail = true
            this.success = false
          }
        })
    },
    handleLoginAttempt() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data for this request
      let validationResults = this.passwordClientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      let loginPromise = User.api.login(this.email, this.password)

      loginPromise
        .then((response) => {
          // NOTE(Bruno 4-21-20): currently everyone logged in is a 'Manager', when this changes there may be a need to update below code
          let token = response.data.token
          let userData = response.data
          delete userData.token
          this.$store.dispatch('updateUserToken', token)
          this.$store.dispatch('updateUser', User.fromAPI(userData))
          if (this.$route.query.redirect) {
            this.$router.push(this.$route.query.redirect)
          } else {
            this.$router.push({ name: 'Integrations' })
          }
          this.success = true
        })
        .catch((error) => {
          if (!error.response || !error.response.status) {
            this.$Alert.alert({
              message: 'An Unknown Error occured please reach out to support',
              timeout: 3000,
              type: 'error',
            })
          }
          if (error.response.status >= 500) {
            this.errors[500] = true
            this.success = false
          } else if (error.response.status >= 400) {
            // handle invalid password
            this.errors.invalidPassword = true
            this.success = false
          }
        })
    },
    emailClientSideValidations() {
      let formErrors = {
        emailIsBlank: this.emailIsBlank,
      }
      let isFormValid = !this.emailIsBlank

      return [isFormValid, formErrors]
    },
    passwordClientSideValidations() {
      let formErrors = {
        passwordIsBlank: this.passwordIsBlank,
      }
      let isFormValid = !this.passwordIsBlank

      return [isFormValid, formErrors]
    },
  },
  computed: {
    emailIsBlank() {
      return !this.email.length
    },
    passwordIsBlank() {
      return !this.password.length
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.login {
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

form {
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
  margin: 0.625rem 0;

  &:disabled {
    border: 2px solid $dark-green;
  }
}

button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 1.875rem;
  width: 9.375rem;
}

.hidden {
  display: none;
}
</style>
