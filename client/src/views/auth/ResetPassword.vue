<template>
  <div class="password-reset">
    <form @submit.prevent="handleSubmit">
      <h2 class="password-reset__title">
        Enter and confirm a new password below.
      </h2>

      <input v-model="password" type="password" placeholder="New Password" />
      <input v-model="confirmPassword" type="password" placeholder="Confirm Password" />

      <button type="submit">Reset Password</button>
      <div style="margin-top: 1rem">
        <router-link :to="{ name: 'Login' }">
          Back to login
        </router-link>
      </div>
    </form>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'ResetPassword',
  components: {},
  data() {
    return {
      password: '',
      confirmPassword: '',
    }
  },
  methods: {
    async handleSubmit() {
      this.loading = true

      const userId = this.$route.params.userId
      const token = this.$route.params.token

      if (!this.password.length || !this.confirmPassword.length) {
        this.$Alert.alert({
          type: 'error',
          message: 'Please enter a new password',
          timeout: 2000,
        })
        this.loading = false
        return
      }

      if (this.password !== this.confirmPassword) {
        this.$Alert.alert({
          type: 'error',
          message: 'Please make sure you passwords match',
          timeout: 2000,
        })
        this.loading = false
        return
      }

      await User.api
        .resetPassword(this.password, userId, token)
        .then(res => {
          this.$Alert.alert({
            type: 'success',
            message: `Successfully Reset Password`,
            timeout: 5000,
          })

          this.$router.push({
            name: 'Login',
          })
        })
        .catch(e => {
          this.$Alert.alert({
            type: 'error',
            message: `There was an error, please try again later`,
            timeout: 5000,
          })
        })
        .finally(e => {
          this.loading = false
        })
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
        .catch(error => {
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
        .then(response => {
          // NOTE(Bruno 4-21-20): currently everyone logged in is a 'Manager', when this changes there may be a need to update below code
          let token = response.data.token
          let userData = response.data
          delete userData.token
          this.$store.dispatch('updateUserToken', token)
          this.$store.dispatch('updateUser', User.fromAPI(userData))
          this.$store.dispatch('updateStages')
          if (this.$route.query.redirect) {
            this.$router.push(this.$route.query.redirect)
          } else {
            this.$router.push({ name: 'Integrations' })
          }
          this.success = true
        })
        .catch(error => {
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

.password-reset {
  display: flex;
  flex-flow: row;
  justify-content: center;

  &__title {
    padding: 0 1rem 1rem 1rem;
  }
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

  background-color: $white;
  display: flex;
  flex-flow: column;
  align-items: center;
  padding: 2rem;
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
