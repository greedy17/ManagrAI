<template>
  <div class="login-page">
    <div class="login-page__form">
      <h2>Login</h2>
      <div class="login-page__form__fields">
        <FormField
          @input="execCheckEmail"
          :disabled="showPassword"
          v-model="loginForm.field.email.value"
          placeholder="email"
          :errors="loginForm.field.email.errors"
          large
        />
        <PulseLoadingSpinner v-if="!showPassword && loggingIn" />

        <FormField
          v-on:keyup.enter.native="handleLoginAttempt"
          :errors="loginForm.field.password.errors"
          v-if="showPassword"
          v-model="loginForm.field.password.value"
          inputType="password"
          placeholder="password"
          large
        />
      </div>
      <PulseLoadingSpinnerButton
        v-if="showPassword"
        :disabled="loggingIn || !loginForm.isValid"
        @click="handleLoginAttempt"
        class="primary-button"
        text="Log In"
        :loading="loggingIn"
      />
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
import FormField from '@/components/forms/FormField'

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
  @include base-font-styles();
  font-weight: bold;
  color: $main-font-gray;
  text-align: center;
}
.login-page {
  padding: 2rem 2rem;
  @media only screen and (max-width: 768px) {
    /* For mobile phones: */
    padding: 0rem;
  }
}
.login-page__form {
  @include standard-border();
  position: relative;
  left: 35%;
  padding: 1rem 2rem;
  margin-top: 3.125rem;
  width: 31.25rem;
  min-height: 15rem;
  height: auto;
  background-color: $white;
  display: flex;
  flex-flow: column;
  align-items: center;
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
