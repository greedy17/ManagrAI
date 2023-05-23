<template>
  <div class="login-page">
    <div :class="{ disabled: loggingIn }" class="login-page__form">
      <div class="center">
        <img src="@/assets/images/logo.png" height="66px" alt="" />
        <h1>Welcome Back</h1>
        <small class="gray-blue">Enter your email & password to login to Managr</small>
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
        style="font-size: 14px"
        text="Log in"
        :loading="loggingIn"
      />
      <h5 style="margin: 0.5rem;">Or</h5>
      <button id="google-signin-button" class="google-signin-button" @click="signInWithGoogle">Sign In with Google</button>
      <div class="row">
        <p class="pad-right">New to Managr?</p>
        <router-link :to="{ name: 'RegisterSelection' }">Sign Up! </router-link>
      </div>
      <div class="row">
        <p class="pad-right">Forgot password?</p>
        <router-link :to="{ name: 'ForgotPassword' }"> Reset it. </router-link>
      </div>
    </div>
    <div class="links">
      <p style="color: #4d4e4c">
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
import Salesforce from '@/services/salesforce'
import Hubspot from '@/services/hubspot'
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
      selectedCrm: null,
      showPassword: false,
      newToken: false,
      loginForm: new UserLoginForm(),
      execCheckEmail: debounce(this.checkAccountStatus, 900),
    }
  },
  computed: {
    selectedCrmSwitcher() {
      switch (this.selectedCrm) {
        case 'SALESFORCE':
          return Salesforce
        case 'HUBSPOT':
          return Hubspot
        default:
          return null
      }
    },
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
  },
  async created() {
    this.$store.dispatch('updateGoogleSignIn', {})
    if (this.$route.query.code) {
      this.selectedCrm = this.$route.query.state
      let modelClass = this.selectedCrmSwitcher
      this.loggingIn = true
      let key
      let user
      try {
        let res = await modelClass.api.sso(this.$route.query.code)
        key = res.key
        user = res.user
        this.$store.dispatch('updateUserToken', key)
        this.$store.dispatch('updateUser', User.fromAPI(user))
      } catch (error) {
        const e = error
        this.$toast(`This method's for user's who signed up via ${this.selectedCrm}. Try again.`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loggingIn = false
        localStorage.dateTime = Date.now()
        this.$router.push({ name: 'ListTemplates' })
      }
    }
  },
  mounted() {
    window.google.accounts.id.initialize({
      client_id: '1053178983159-40pr5voodgitli9ap0v9uifj8d3p9mgq.apps.googleusercontent.com',
      callback: this.onGoogleSignIn,
    });
    window.google.accounts.id.renderButton(
      document.getElementById('google-signin-button'),
      { theme: 'outline', size: 'large' }
    );

    console.log('this.newToken', this.newToken)
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
    async onGetAuthLink(integration) {
      this.generatingToken = true
      this.selectedCrm = integration

      let modelClass = this.selectedCrmSwitcher
      try {
        let res = await modelClass.api.getAuthLinkSSO()
        if (res.link) {
          window.location.href = res.link
        }
      } finally {
        this.generatingToken = false
      }
    },
    async handleSSOLogin() {
      this.loggingIn = true
      let key
      let user
      try {
        let res = await Salesforce.api.connect(this.$route.query.code)
        console.log('RESPONSE IS HERE: ', res)
        // key = res.key
        // user = res.user
        // delete user.token
      } catch (error) {
        const e = error
        this.$toast('Trouble logging in with Salesforce, please try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.$store.dispatch('updateUserToken', key)
        this.$store.dispatch('updateUser', User.fromAPI(user))
        localStorage.dateTime = Date.now()
        this.$router.push({ name: 'ListTemplates' })
        this.loggingIn = false
        localStorage.isLoggedOut = false
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
    async verifyIdToken(idToken) {
      const response = await fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + idToken);
      const tokenInfo = await response.json();
      return tokenInfo;
    },
    signInWithGoogle() {
      // Trigger the Google Sign-In flow
      window.google.accounts.id.prompt();
    },
    async onGoogleSignIn(response) {
      // Handle the Google Sign-In response
      if (response.credential) {
        const idToken = response.credential
        console.log('idToken', idToken)
        const verifiedToken = await this.verifyIdToken(idToken)

        console.log('verifiedToken', verifiedToken)

        const { name, email } = verifiedToken;

        console.log('User name:', name);
        console.log('User email:', email);

        if (verifiedToken) {
          // Use the token for authentication or further processing
          console.log('Google ID token:', verifiedToken);
          this.newToken = true
          // When logging out, call this function again, but with verifiedToken being an empty object
          this.$store.dispatch('updateGoogleSignIn', verifiedToken)
          console.log('this.newToken 2', this.newToken)

          // Call get endpoint for user by email
          // Log in with SSO endpoint if they have an account
          // Else, send them to screen for them to get a password and org
          this.$router.push({ name: 'GoogleRegister' })
        } else {
          console.error('ID token not found in credential:', response.credential);
        }
      } else {
        // Sign-In was unsuccessful
        console.error('Google Sign-In failed:', response.error);
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

.center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
}
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
  margin-top: 5rem;
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: flex-start;
  color: $base-gray;
  gap: 12px;
  border-radius: 6px;
  background-color: white;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  padding: 2rem 3rem;
  width: 29vw;

  // @media only screen and (max-width: 768px) {

  //   width: 100%;
  //   height: 100%;
  //   padding: 0rem;
  //   left: 0;
  //   display: block;
  //   border: 0;
  // }
}
.login-button {
  @include primary-button();
  margin-bottom: 6px;
  width: 23vw;
  padding: 14px;
  box-shadow: none;
}
a {
  text-decoration: none;
  color: $light-gray-blue;
}
label {
  font-size: 15px;
}
.button-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
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
.pad-right {
  padding-right: 0.3em;
}
.links {
  font-size: 13px;
  margin: 3rem;
}
::v-deep .input-content {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
::v-deep .input-form__active {
  border: none;
}
.logo-title {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.seperator {
  border-bottom: 1px solid $soft-gray;
  width: 100%;
  position: relative;
  margin: 16px 0px;

  span {
    position: absolute;
    left: 46%;
    top: -8px;
    background-color: white;
    padding: 0 8px;
    color: $light-gray-blue;
    font-size: 13px;
  }
}

.gray-blue {
  color: $light-gray-blue;
}

.register-button {
  @include primary-button();
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  color: $base-gray;
  background-color: white;
  border: 1px solid $soft-gray;
  width: 23vw;
  padding: 12px 2px;

  img {
    margin-right: 16px;
  }
}

.register-button-hs {
  @include primary-button();
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  color: $base-gray;
  background-color: white;
  border: 1px solid $soft-gray;
  width: 23vw;
  padding: 10px 2px;

  img {
    margin-right: 16px;
  }
}

.disabled {
  opacity: 0.6;
  cursor: text !important;
}

.google-signin-button {
  border: none;
  background: none;
}
</style>
