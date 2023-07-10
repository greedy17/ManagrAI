<template>
    <div class="registration">
      <div class="registration-card">
        <div style="width: 100vw; height: 94vh" class="registration__form">
          <div :class="{ disable: generatingToken }" class="form-card">
            <div class="center">
              <img src="@/assets/images/logo.png" height="66px" alt="" />
              <h1 class="logo-title">Welcome to Managr</h1>
              <small class="gray-blue" style="margin: 0px 0px 16px 8px"
                >Register with Google to continue</small
              >
            </div>
            <button id="custom-google-signin-button" class="google-signin-button" @click="signInWithGoogle">
              <img src="@/assets/images/google.svg" />
              <span>Continue with Google</span>
            </button>
            <!-- <button class="google-signin-button" @click="signInWithMicrosoft">
              <img src="@/assets/images/microsoft.svg" />
              <span>Continue with Microsoft</span>
            </button> -->
            <div class="seperator">
              <span> OR </span>
            </div>
            <button
              class="register-button-hs"
              @click="goToRegister"
            >
              Register with company email
            </button>
            <div class="row2">
              <p class="pad-right">Already have an account?</p>
              <router-link class="login-link" style="text-decoration: none;" :to="{ name: 'Login' }">Log in</router-link>
            </div>
            <div class="form-card__footer">
              <!-- <div>
                By signing up, I agree to the
                <a href="https://managr.ai/terms-of-service" target="_blank">Terms</a> and
                <a href="https://managr.ai/privacy-policy" target="_blank">Policies</a>.
              </div> -->
              <!-- <div class="links">
                <p style="color: #4d4e4c">
                  <a href="https://managr.ai/terms-of-service" target="_blank">Term of Service</a>
                  |
                  <a href="https://managr.ai/documentation" target="_blank">Documentation</a>
                  |
                  <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
                </p>
              </div> -->
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
      </div>
    </div>
  </template>
  <script>
  import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'
  import Button from '@thinknimble/button'
  import FormField from '@/components/forms/FormField'
  import PipelineLoader from '@/components/PipelineLoader'
  import User from '@/services/users'

  import { PublicClientApplication } from '@azure/msal-browser'
import { decryptData } from '../../encryption'

  export default {
    name: 'RegisterSelection',
    components: {
      FormField,
      Button,
      Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
      PulseLoadingSpinner,
      PipelineLoader,
    },
    data() {
      return {
        generatingToken: false,
      }
    },
    watch: {
      
    },
    async created() {

    },
    mounted() {
      window.google.accounts.id.initialize({
        client_id: '1053178983159-40pr5voodgitli9ap0v9uifj8d3p9mgq.apps.googleusercontent.com',
        callback: this.onGoogleSignIn,
      });

      // Attach event listener to the custom button
      const customButton = document.getElementById('custom-google-signin-button');
      customButton.addEventListener('click', this.signInWithGoogle);
    },
    methods: {
      goToRegister() {
        this.$router.push({ name: 'Register' })
      },
      async verifyIdToken(idToken) {
        const response = await fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + idToken);
        const tokenInfo = await response.json();
        return tokenInfo;
      },
      signInWithMicrosoft() {
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

        myMSALObj.loginRedirect({
          scopes: ['user.read'],
        })
      },
      signInWithGoogle() {
        // Trigger the Google Sign-In flow
        window.google.accounts.id.prompt();
      },
      async onGoogleSignIn(response) {
        // Handle the Google Sign-In response
        if (response.credential) {
          const idToken = response.credential
          const verifiedToken = await this.verifyIdToken(idToken)

          const { name, email } = verifiedToken;

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
            } catch(e) {
              console.log(e)
              userEmail = false
            }
            if (userEmail) {
              // Log in with SSO endpoint if they have an account
              const response = await User.api.loginSSO({ email })
              let token = response.data.token
              let userData = response.data
              delete userData.token
              this.$store.dispatch('updateUserToken', token)
              this.$store.dispatch('updateUser', User.fromAPI(userData))
              if (!this.hasSalesforceIntegration && !this.hasSlackIntegration) {
                this.$router.push({ name: 'Integrations' })
              } else {
                this.$router.push({ name: 'ListTemplates' })
              }
            } else {
              // Else, send them to screen for them to get a password and org
              this.$router.push({ name: 'GoogleRegister' })
            }
          } else {
            console.error('ID token not found in credential:', response.credential);
          }
        } else {
          // Sign-In was unsuccessful
          console.error('Google Sign-In failed:', response.error);
        }
      },
    },
    computed: {
      user() {
        const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
        return decryptedUser
      },
    },
  }
  </script>
  <style lang="scss" scoped>
  @import '@/styles/variables';
  @import '@/styles/mixins/inputs';
  @import '@/styles/mixins/buttons';
  @import '@/styles/mixins/utils';
  ::v-deep .tn-input__label {
    color: $light-gray-blue;
  }
  .invert {
    filter: invert(60%);
  }
  .center {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    width: 100%;
  }
  .col {
    display: flex;
    flex-direction: column;
  }
  .row {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    width: 102%;
  }

  .row2 {
    display: flex;
    flex-direction: row;
    align-items: center;
    font-size: 13px;
    margin-bottom: -16px;
  }
  .pad-right {
    padding-right: 0.3em;
  }
  .registration-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
  }
  .background-img {
    position: absolute;
    height: 400px;
    left: 80%;
    bottom: 0;
  }
  .registration {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 0rem;
    // max-width: 24rem;
    // margin: 1.5rem auto;
    &__text {
      color: $base-gray;
      font-family: #{$base-font-family};
      margin-bottom: 1rem;
      text-align: center;
      font-size: 14px;
    }
    &__privacy {
      padding: 0.5rem 1rem;
      font-size: 0.75rem;
      margin-top: 0.5rem;
      letter-spacing: 0.75px;
    }
    &__button {
      @include primary-button();
      justify-self: center;
      width: 100%;
      border-radius: 6px;
      margin: 1rem 0;
      width: 23vw;
      padding: 20px 8px !important;
      box-shadow: none;
    }
  }
  .time {
    color: $base-gray;
    cursor: pointer;
    font-size: 14px;
  }
  ::v-deep .multiselect__placeholder {
    color: $light-gray-blue;
  }
  .time:hover {
    color: $gray;
  }
  .form-card {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    margin-top: 7rem;
    gap: 12px;
    border-radius: 6px;
    background-color: white;
    box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
    padding: 2rem 3rem 3rem 3rem;
    width: 30vw;
    color: $base-gray;
    letter-spacing: 0.75px;
    &__footer {
      width: 100%;
      font-size: 12px;
      margin-top: 0px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
  }
  .registration__form {
    background-color: transparent !important;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-direction: column;
    height: 95vh;
    z-index: 10;
  }
  .error {
    color: red;
    font-size: 10px;
    margin-right: 12px;
  }
  .column {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
  }
  input {
    width: 26vw;
    border-radius: 4px;
    padding: 10px;
    border: 1px solid $soft-gray;
    color: $base-gray;
    letter-spacing: 0.5px;
    font-family: #{$base-font-family};
  }
  input:focus {
    outline: none;
  }
  label {
    font-size: 13px;
    color: $base-gray;
  }
  a {
    text-decoration: none;
    color: $light-gray-blue;
  }
  .disabled {
    background-color: $soft-gray !important;
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
    margin: 8px 0px;
    span {
      position: absolute;
      left: 48%;
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
    font-size: 15px;
    padding: 0.65rem;
    img {
      margin-right: 16px;
    }
  }
  h2 {
    margin-bottom: 0.5rem;
  }
  .disable {
    opacity: 0.7;
    background-color: white;
    cursor: text !important;
  }
  .links {
    font-size: 13px;
    letter-spacing: 0.75px;
    // margin: 3rem;
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

  .login-link {
    text-decoration: none;
    color: $dark-green;
  }
  </style>