<template>
  <div class="login-page">
    <div class="login-page__form">
      <div class="column">
        <img src="@/assets/images/logo.png" alt="logo" />
        <h2>Log in to Managr</h2>
        <p class="enter-email">Please enter your email and password</p>
      </div>
      <!-- <label for="email">Email</label> -->
      <input
        type="email"
        @input="execCheckEmail"
        :disabled="showPassword"
        v-model="loginForm.field.email.value"
        placeholder="email"
        :errors="loginForm.field.email.errors"
      />
      <PulseLoadingSpinner v-if="!showPassword && loggingIn" />
      <input
        @blur="loginForm.field.password.validate()"
        v-on:keyup.enter.native="handleLoginAttempt"
        :errors="loginForm.field.password.errors"
        v-if="showPassword"
        v-model="loginForm.field.password.value"
        type="password"
      />
      <PulseLoadingSpinnerButton
        :disabled="loggingIn || !loginForm.isValid"
        @click="handleLoginAttempt"
        class="login-button"
        text="Log in"
        :loading="loggingIn"
      />
      <div class="row">
        <p class="pad-right">New to Managr?</p>
        <router-link :to="{ name: 'Register' }">Sign Up! </router-link>
      </div>
      <div class="row">
        <p class="pad-right">Forgot password?</p>
        <router-link :to="{ name: 'ForgotPassword' }"> Reset it. </router-link>
      </div>
      <div class="links">
        <p>
          <a href="https://managr.ai/terms-of-service" target="_blank">Term of Service</a>
          |
          <a href="https://managr.ai/documentation" target="_blank">Documentation</a>
          |
          <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Services
 */
import User from '@/services/users'
import { UserLoginForm } from '@/services/users/forms'
import debounce from 'lodash.debounce'
/**
 * External Components
 */
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'
/**
 * internal Components
 */
import FormField from '@/components/forms/inputs/FormField'

export default {
  name: 'Login',
  components: { FormField, PulseLoadingSpinnerButton, PulseLoadingSpinner },
  data() {
    return {
      loggingIn: false,
      showPassword: false,
      loginForm: new UserLoginForm(),
      execCheckEmail: debounce(this.checkAccountStatus, 900),
    }
  },
  methods: {
    async checkAccountStatus() {
      this.loginForm.field.email.validate()
      if (this.loginForm.field.email.isValid) {
        this.loggingIn = true
        try {
          await User.api.checkStatus(this.loginForm.field.email.value)
          this.showPassword = true
        } catch (e) {
          console.log(e)
          this.loginForm.field.email.errors.push({
            code: 'invalidAccount',
            message: 'Account inactive or does not exist',
          })
        } finally {
          this.loggingIn = false
        }
      }
    },
    async handleLoginAttempt() {
      this.loginForm.validate()
      if (this.loginForm.isValid) {
        this.loggingIn = true
        try {
          const response = await User.api.login({ ...this.loginForm.value })
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
        } catch (error) {
          const e = error

          if (!error.response || !error.response.status) {
            this.$Alert.alert({
              message: 'An Unknown Error occured please reach out to support',
              timeout: 3000,
              type: 'error',
            })
          } else if (error.response.status >= 400) {
            this.$Alert.alert({
              message: 'Incorrect Email/Password combination',
              timeout: 3000,
              type: 'error',
            })
          }
        } finally {
          this.loggingIn = false
        }
      }
    },
  },
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

h2 {
  font-weight: bold;
  text-align: center;
}
input {
  margin-bottom: 0.3rem;
  width: 22vw;
  height: 6vh;
  border-radius: 0.3rem;
  border: 2px solid $soft-gray;
}
input:focus {
  outline: 2px solid $lighter-green;
}

::placeholder {
  color: $mid-gray;
  padding: 0.5rem;
}

.login-page {
  padding: 2rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  @media only screen and (max-width: 768px) {
    /* For mobile phones: */
    padding: 0rem;
  }
}
::v-deep .form-field__input {
  margin-left: 0.2rem;
}

.login-page__form {
  background-color: $white;
  border-radius: 0.5rem;
  width: 30vw;
  margin-top: 1rem;
  box-shadow: 4px 5px 9px $very-light-gray;
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
  color: $base-gray;

  @media only screen and (max-width: 768px) {
    /* For mobile phones: */
    width: 100%;
    height: 100%;
    padding: 0rem;
    left: 0;
    display: block;
    border: 0;
  }
}

/* input {
  @include input-field();
  height: 2.5rem;
  width: 15.65rem;
  display: block;
  margin: 0.625rem 0;

  &:disabled {
    border: 2px solid $dark-green;
  }
}
 */
button {
  @include primary-button();
  margin-bottom: 6px;
  width: 22vw;
  height: 6vh;
  background-color: #199e54 !important;
  color: white !important;
}

a {
  text-decoration: none;
  color: $gray;
}

label {
  font-size: 15px;
}
.hidden {
  display: none;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 13px;
  margin-bottom: -16px;
}
.column {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}
.enter-email {
  @include muted-font();
  margin-top: -0.5rem;
  color: $gray;
}
img {
  height: 80px;
  margin-top: 4rem;
  padding-top: 0.5rem;
}
.pad-right {
  padding-right: 0.3em;
}
.links {
  font-size: 13px;
  margin: 2rem;
}
/* #email,
#password {
  border: 1px solid $soft-gray;
  border-radius: 3px;
  margin-top: 5px;
  background-color: #ffffff;
} */
</style>
