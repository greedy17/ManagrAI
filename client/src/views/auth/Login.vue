<template>
  <div class="login-page">
    <header>
      <img class="blue-filter" src="@/assets/images/logo.png" height="36px" alt="" />
      <div class="header">
        <small>New to Managr ?</small>
        <router-link class="secondary-button" :to="{ name: 'RegisterSelection' }"
          >Create Account
        </router-link>
      </div>
    </header>

    <div :class="{ disabled: loggingIn }" class="login-form">
      <h2>Sign In</h2>

      <FormField
        type="email"
        id="emailfield"
        @blur="loginForm.field.email.validate()"
        v-model="loginForm.field.email.value"
        placeholder="Email address"
        :errors="loginForm.field.email.errors"
      />
      <PulseLoadingSpinner v-if="loggingIn" />
      <FormField
        id="passwordfield"
        @blur="loginForm.field.password.validate()"
        v-on:keyup.enter.native="handleLoginAttempt"
        :errors="loginForm.field.password.errors"
        @keyup.enter="handleLoginAttempt"
        v-model="loginForm.field.password.value"
        inputType="password"
        placeholder="password"
      />
      <PulseLoadingSpinnerButton
        :disabled="loggingIn || !loginForm.isValid"
        @click="handleLoginAttempt"
        class="login-button"
        style="font-size: 13px; width: 320px"
        text="Continue"
        :loading="loggingIn"
      />
      <!-- <div class="seperator">
        <span> OR </span>
      </div> -->
      <!-- <button id="custom-google-signin-button" class="google-signin-button" @click="signInWithGoogle">
        <img src="@/assets/images/google.svg" />
        <span>Continue with Google</span>
      </button> -->
      <!-- <button class="google-signin-button" @click="signInWithMicrosoft">
        <img src="@/assets/images/microsoft.svg" />
        <span>Continue with Microsoft</span>
      </button> -->

      <div class="row">
        <p class="pad-right">Forgot password?</p>
        <router-link :to="{ name: 'ForgotPassword' }"> Reset it </router-link>
      </div>
    </div>
    <div class="links">
      <p class="t-c">
        <a href="https://managr.ai/terms-of-service" target="_blank">Terms of Service</a>
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

import { PublicClientApplication, EventType } from '@azure/msal-browser'
// import { ConfidentialClientApplication } from '@azure/msal-node';

/**
 * External Components
 */
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'
import { decryptData, encryptData } from '../../encryption'
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
    isPR() {
      return this.$store.state.user.role === 'PR'
    },
    hasSalesforceIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.salesforceAccount
    },
    hasSlackIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
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
        const userAPI = User.fromAPI(user)
        // const encryptedUser = encryptData(userAPI, process.env.VUE_APP_SECRET_KEY)
        // const encryptedKey = encryptData(key, process.env.VUE_APP_SECRET_KEY)
        // this.$store.dispatch('updateUserToken', encryptedKey)
        // this.$store.dispatch('updateUser', encryptedUser)
        this.$store.commit('UPDATE_USER', userAPI)
        this.$store.dispatch('updateUserToken', key)
        localStorage.token = key
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
        // localStorage.dateTime = Date.now()
        this.$router.push({ name: 'ListTemplates' })
      }
    }
  },
  async mounted() {
    // const googleInitData = await User.api.googleInit()
    // window.google.accounts.id.initialize({
    //   client_id: googleInitData.client_id,
    //   callback: this.onGoogleSignIn,
    //   login_uri: googleInitData.login_uri,
    // })
    // Attach event listener to the custom button
    // const customButton = document.getElementById('custom-google-signin-button');
    // customButton.addEventListener('click', this.signInWithGoogle);
  },
  methods: {
    async checkAccountStatus() {
      this.loginForm.field.email.validate()
      if (this.loginForm.field.email.isValid) {
        this.loggingIn = true
        try {
          await User.api.checkStatus(this.loginForm.field.email.value)
          // this.showPassword = true
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
        const userAPI = User.fromAPI(user)
        // const encryptedUser = encryptData(userAPI, process.env.VUE_APP_SECRET_KEY)
        // const encryptedKey = encryptData(key, process.env.VUE_APP_SECRET_KEY)
        // this.$store.dispatch('updateUserToken', encryptedKey)
        // this.$store.dispatch('updateUser', encryptedUser)
        this.$store.commit('UPDATE_USER', userAPI)
        this.$store.dispatch('updateUserToken', key)
        localStorage.token = key
        // localStorage.dateTime = Date.now()
        this.$router.push({ name: 'ListTemplates' })
        this.loggingIn = false
        // localStorage.isLoggedOut = false
      }
    },
    async handleLoginAttempt() {
      this.loginForm.validate()
      if (this.loginForm.isValid) {
        this.loggingIn = true
        try {
          const response = await User.api.login({ ...this.loginForm.value }).then((response) => {
            localStorage.setItem('tokenReceivedAt', Date.now().toString())
            let token = response.data.token
            let userData = response.data
            delete userData.token
            const userAPI = User.fromAPI(userData)
            this.$store.dispatch('updateUserToken', token)
            localStorage.setItem('token', token)
            this.$store.commit('UPDATE_USER', userAPI)
            if (this.isPR) {
              this.$router.push({ name: 'PRSummaries' })
            }
          })
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
          // localStorage.isLoggedOut = false
        }
      }
    },
    async verifyIdToken(idToken) {
      const response = await fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + idToken)
      const tokenInfo = await response.json()
      return tokenInfo
    },
    async signInWithMicrosoft() {
      const config = {
        auth: {
          clientId: 'ead3f8ef-4a75-4620-b660-5d9c0999f8bc',
          authority: 'https://login.microsoftonline.com/common',
          redirectUri: 'http://localhost:8080/auth/callback',
        },
        cache: {
          cacheLocation: 'localStorage',
        },
      }

      const myMSALObj = new PublicClientApplication(config)
      // const cca = new ConfidentialClientApplication(config)

      const authRequest = {
        scopes: ['user.read'],
        prompt: 'select_account',
      }

      // myMSALObj.loginRedirect({
      //   scopes: ['user.read'],
      // })

      try {
        const res = await myMSALObj.loginPopup(authRequest)
      } catch (e) {
        console.log('Error during sign-in:', e)
      }
    },
    signInWithGoogle() {
      // Trigger the Google Sign-In flow
      window.google.accounts.id.prompt()
    },
    async onGoogleSignIn(response) {
      // Handle the Google Sign-In response
      if (response.credential) {
        const idToken = response.credential
        const verifiedToken = await this.verifyIdToken(idToken)

        const { email } = verifiedToken

        if (verifiedToken) {
          // Use the token for authentication or further processing
          this.newToken = true
          // When logging out, call this function again, but with verifiedToken being an empty object
          this.$store.dispatch('updateGoogleSignIn', verifiedToken)

          // Call get endpoint for user by email
          // const userEmail = await User.api.getUserByEmail(email)
          let userEmail
          try {
            const emailRes = await User.api.checkStatus(email)
            userEmail = true
          } catch (e) {
            userEmail = false
          }
          if (userEmail) {
            // Log in with SSO endpoint if they have an account
            const response = await User.api.loginSSO({ email, sso: true })
            let token = response.data.token
            let userData = response.data
            delete userData.token
            // const userAPI = User.fromAPI(userData)
            // const encryptedUser = encryptData(userAPI, process.env.VUE_APP_SECRET_KEY)
            // const encryptedKey = encryptData(token, process.env.VUE_APP_SECRET_KEY)
            // this.$store.dispatch('updateUserToken', encryptedKey)
            this.$store.dispatch('updateUserToken', token)
            localStorage.token = token
            this.$store.dispatch('updateUser', User.fromAPI(userData))
            if (this.isPR) {
              this.$router.push({ name: 'PRSummaries' })
            } else {
              this.$router.push({ name: 'Home' })
            }
          } else {
            // Else, send them to screen for them to get a password and org
            this.$router.push({ name: 'GoogleRegister' })
          }
        } else {
          console.error('ID token not found in credential:', response.credential)
        }
      } else {
        // Sign-In was unsuccessful
        console.error('Google Sign-In failed:', response.error)
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

.header {
  display: flex;
  flex-direction: row;
  align-items: center;
  small {
    margin-right: 16px;
  }
}
header {
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  font-family: $thin-font-family;
  font-size: 16px;
  padding-top: 12px;
}

h2 {
  font-family: $thin-font-family;
  padding: 0;
  margin: 0;
}
::v-deep .tn-input:focus {
  outline: none;
}

input {
  font-family: $thin-font-family;
}

::v-deep .input-content {
  border: 1px solid #e8e8e8;
  border-radius: 4px;

  &::placeholder {
    font-family: $thin-font-family;
    color: $very-light-gray;
  }
}
::v-deep .input-form {
  width: 320px;
}
::v-deep .input-form__active {
  border: none;
}

.logo {
  margin-top: 16px;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.blue-filter {
  filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
    contrast(90%);
}
input:focus {
  outline: none;
}

.login-page {
  padding: 0 32px 32px 32px;
  height: 100vh;
  font-family: $base-font-family;
  font-weight: 400;
  color: $dark-black-blue;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
}
.login-form {
  display: flex;
  flex-flow: column;
  align-items: flex-start;
  justify-content: center;
  color: $dark-black-blue;
  background-color: $offer-white;
  border-radius: 4px;
  gap: 16px;
  padding: 64px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
}
.login-button {
  @include dark-blue-button();
  text-align: center;
  margin-bottom: 6px;
  width: 320px;
  padding: 12px;
  box-shadow: none;

  &:disabled {
    background-color: $off-white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    opacity: 0.7;
  }
}

.secondary-button {
  @include dark-blue-button();
  width: 120px;
  padding: 8px;
  font-family: $thin-font-family;
}

::v-deep .haAclf {
  width: 23vw;
}
a {
  text-decoration: none;
  color: $off-gray;
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

  p {
    margin: 0;
  }
}
.column {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.pad-right {
  padding-right: 0.3em;
}
.links {
  font-size: 13px;
  font-family: $thin-font-family;
}

.t-c {
  a {
    margin: 0 16px;
  }
}

.logo-title {
  display: flex;
  flex-direction: row;
  align-items: center;
}
// .seperator {
//   border-bottom: 1px solid $soft-gray;
//   width: 100%;
//   position: relative;
//   margin: 16px 0px;

//   span {
//     position: absolute;
//     left: 46%;
//     top: -8px;
//     background-color: white;
//     padding: 0 8px;
//     color: $light-gray-blue;
//     font-size: 13px;
//   }
// }

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

.seperator {
  border-bottom: 1px solid $soft-gray;
  width: 100%;
  position: relative;
  margin: 8px 0px;
  span {
    position: absolute;
    left: 10vw;
    top: -8px;
    background-color: white;
    padding: 0 8px;
    color: $light-gray-blue;
    font-size: 13px;
  }
}

.google-signin-button {
  @include gray-text-button;
  display: flex;
  justify-content: start;
  font-size: 15px;
  padding: 0.65rem;
  width: 23vw;
  span {
    margin-left: 0.5rem;
  }
  img {
    height: 22px;
  }
}
</style>
