<template>
  <div class="login-page">
    <div class="login-page__form">
      <div class="column">
        <img src="@/assets/images/logo.png" class="logo" alt="logo" />
        <h2>Log in to Managr</h2>
        <!-- <p class="enter-email">Please enter your email and password</p> -->
      </div>
      <FormField
        type="email"
        @input="execCheckEmail"
        @blur="loginForm.field.email.validate()"
        :disabled="showPassword"
        v-model="loginForm.field.email.value"
        placeholder="enter email"
        :errors="loginForm.field.email.errors"
      />
      <PulseLoadingSpinner v-if="!showPassword && loggingIn" />
      <FormField
        @blur="loginForm.field.password.validate()"
        v-on:keyup.enter.native="handleLoginAttempt"
        :errors="loginForm.field.password.errors"
        v-if="showPassword"
        @keyup.enter="handleLoginAttempt"
        v-model="loginForm.field.password.value"
        inputType="password"
        placeholder="password"
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
      <div class="row" style="margin-bottom: 1rem">
        <p class="pad-right">Forgot password?</p>
        <router-link :to="{ name: 'ForgotPassword' }"> Reset it. </router-link>
      </div>
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
</template>

<script>
/**
 * Services
 */
import User from '@/services/users'
import { UserLoginForm } from '@/services/users/forms'
import debounce from 'lodash.debounce'
import FormField from '@/components/forms/FormField'
/**
 * External Components
 */
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'
/**
 * internal Components
 */
export default {
  name: 'Login',
  components: { PulseLoadingSpinnerButton, PulseLoadingSpinner, FormField },
  data() {
    return {
      loggingIn: false,
      showPassword: false,
      loginForm: new UserLoginForm(),
      execCheckEmail: debounce(this.checkAccountStatus, 900),
    }
  },
  computed: {
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
  },
  mounted() {
    if (document.getElementById('fullstory')) {
      let el = document.getElementById('fullstory')
      el.remove()
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
          localStorage.dateTime = Date.now()
          // if (this.$route.query.redirect) {
          //   this.$router.push(this.$route.query.redirect)
          // }
          if (!this.hasSalesforceIntegration && !this.hasSlackIntegration) {
            this.$router.push({ name: 'Integrations' })
          } else {
            this.$router.push({ name: 'ListTemplates' })
          }
        } catch (error) {
          const e = error

          if (!error.response || !error.response.status) {
            this.$toast('An Unknown Error occured please reach out to support', {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          } else if (error.response.status >= 400) {
            this.$toast('Incorrect Email/Password combo', {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          }
        } finally {
          this.loggingIn = false
          localStorage.isLoggedOut = false
        }
      }
    },
  },
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
::v-deep .tn-input:focus {
  outline: none;
}

::placeholder {
  color: $mid-gray;
}
.logo {
  margin-top: 16px;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
input:focus {
  outline: none;
}
.login-page {
  padding: 2rem 2rem 0 2rem;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  color: white;
  letter-spacing: 0.75px;
  @media only screen and (max-width: 768px) {
    /* For mobile phones: */
    padding: 0rem;
  }
}
.login-page__form {
  background-color: $white;
  border-radius: 6px;
  width: 20rem;
  margin-top: 5rem;
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
  color: $base-gray;
  // border: 1px solid #e8e8e8;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);

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
button {
  @include primary-button();
  margin-bottom: 6px;
  width: 256px;
  height: 6vh;
  background-color: #41b883 !important;
  color: white !important;
  box-shadow: none;
}
a {
  text-decoration: none;
  color: $light-gray-blue;
}
label {
  font-size: 15px;
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
// .enter-email {
//   @include muted-font();
//   margin-top: -0.5rem;
//   color: $light-gray-blue;
// }
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
::v-deep .input-content {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
::v-deep .input-form__active {
  border: none;
}
</style>
