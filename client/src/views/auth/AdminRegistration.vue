<template>
  <div class="registration">
    <div class="registration-card">
      <!-- <img class="background-img" src="@/assets/images/logo.png" height="48px" alt="" /> -->
      <div style="width: 100vw; height: 94vh" class="registration__form">
        <div :class="{ disable: generatingToken }" class="form-card">
          <div class="center">
            <img src="@/assets/images/logo.png" height="60px" alt="" />
            <h2 class="logo-title">Welcome to Managr</h2>
            <small class="gray-blue" style="margin: 8px 0px 16px 8px"
              >Fill out the form below to get started</small
            >
          </div>

          <!-- <button v-if="!generatingToken">Fill out register form</button>

          <div v-if="!generatingToken" class="seperator">
            <span> OR </span>
          </div> -->

          <!-- <div v-if="!generatingToken" class="seperator">
            <span> OR </span>
          </div> -->

          <div class="fields-container">
            <span class="col top-field">
              <label for="role">Select Product</label>
              <Multiselect
                placeholder="Select your role"
                @input="selectRole($event)"
                v-model="userRole"
                :options="userRoles"
                openDirection="below"
                style="width: 26vw; padding: 0; margin-top: 6px"
                selectLabel="Enter"
                label="name"
                id="key"
              >
                <template slot="noResult">
                  <p>No results.</p>
                </template>
              </Multiselect>
            </span>

            <span class="">
              <label for="name">Full Name</label>
              <input
                @blur="registrationForm.field.fullName.validate()"
                :errors="registrationForm.field.fullName.errors"
                v-model="registrationForm.field.fullName.value"
                placeholder="Enter Full Name"
                id="name"
              />
            </span>

            <span>
              <label for="email">Email</label>
              <input
                @blur="registrationForm.field.email.validate()"
                :errors="registrationForm.field.email.errors"
                v-model="registrationForm.field.email.value"
                type="email"
                id="email"
                placeholder="Enter Email"
              />
            </span>

            <span>
              <label for="password">Set a Password</label>
              <input
                id="password"
                @blur="showVals(registrationForm.field.password)"
                @input="registrationForm.field.password.validate()"
                :errors="registrationForm.field.password.errors"
                v-model="registrationForm.field.password.value"
                type="password"
                placeholder="Must be 9 characters or longer"
              />
              <div class="column" v-for="(message, i) in errorMessages" :key="i">
                <small class="error">{{ message }}</small>
              </div>
            </span>

            <span>
              <label for="confirm-password">Re-Enter Password</label>
              <input
                id="confirm-password"
                label="Re-Enter Password"
                @blur="registrationForm.field.confirmPassword.validate()"
                :errors="registrationForm.field.confirmPassword.errors"
                v-model="registrationForm.field.confirmPassword.value"
                type="password"
                placeholder="Must be 9 characters or longer"
              />
            </span>

            <span class="col">
              <label for="company">Company Name</label>
              <input
                @blur="registrationForm.field.organizationName.validate()"
                :errors="registrationForm.field.organizationName.errors"
                v-model="registrationForm.field.organizationName.value"
                placeholder="Enter Company Name"
                id="company"
              />
            </span>
          </div>

          <div class="form-card__footer">
            <div>
              By signing up, I agree to Managr's
              <a href="https://managr.ai/terms-of-service" target="_blank">Terms</a>
              &
              <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>.
              <!-- and -->
              <!-- <a href="https://managr.ai/privacy-policy" target="_blank"></a>. -->
            </div>

            <button
              :disabled="!validatedForm"
              :class="{ disabled: !validatedForm }"
              class="registration__button"
              type="submit"
              @click="onSubmit"
            >
              Sign Up
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import User, { UserRegistrationForm } from '@/services/users'
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'

import Button from '@thinknimble/button'
import FormField from '@/components/forms/FormField'
import moment from 'moment-timezone'

import Salesforce from '@/services/salesforce'
import Hubspot from '@/services/hubspot'

import PipelineLoader from '@/components/PipelineLoader'
import { decryptData, encryptData } from '../../encryption'

export default {
  name: 'Registration',
  components: {
    FormField,
    Button,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    PulseLoadingSpinner,
    PipelineLoader,
  },
  data() {
    return {
      User,
      submitting: false,
      generatingToken: false,
      registrationForm: new UserRegistrationForm(),
      userRoles: User.roleChoices,
      timezones: moment.tz.names(),
      userTime: moment.tz.guess(),
      changeZone: false,
      validatedForm: false,
      userRole: { key: 'PR', name: 'Public Relations' },
      selectedZone: null,
      errorMessages: [],
      selectedCrm: null,
    }
  },
  watch: {
    registrationForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (
          val.field.fullName.value &&
          val.field.email.value &&
          val.field.password.value &&
          val.field.confirmPassword.value &&
          val.field.organizationName.value
        ) {
          this.validatedForm = true
        } else {
          this.validatedForm = false
        }
      },
    },
  },
  async created() {
    const validCode = this.$route.params.validCode

    if (!validCode && !this.$route.query.code) {
      this.$router.push({
        name: 'Register',
      })
    }
    this.timezones = this.timezones.map((tz) => {
      return { key: tz, value: tz }
    })

    if (this.$route.query.code) {
      this.generatingToken = true
      this.selectedCrm = this.$route.query.state
      let key
      let user
      try {
        const modelClass = this.selectedCrmSwitcher
        let res = await modelClass.api.sso(this.$route.query.code)
        key = res.key
        user = res.user
      } catch (e) {
        console.log(e)
      } finally {
        // const encryptedKey = encryptData(key, process.env.VUE_APP_SECRET_KEY)
        // const encryptedUser = encryptData(user, process.env.VUE_APP_SECRET_KEY)
        // this.$store.commit('UPDATE_USER', encryptedUser)
        this.$store.commit('UPDATE_USER', user)
        // this.$store.commit('UPDATE_USERTOKEN', encryptedKey)
        this.$store.commit('UPDATE_USERTOKEN', key)
        this.generatingToken = false
        this.selectedCrm = null
        this.$router.push({ name: 'Login' })
        // if (this.isPR) {
        //   this.$router.push({ name: 'PRSummaries' })
        // } else {
        //   this.$router.push({ name: 'Home' })
        // }
      }
    }
    this.selectRole(this.userRole)
  },
  methods: {
    test() {
      console.log(this.registrationForm.field.timezone.value)
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
    showVals(val) {
      let validations = val.errors
      let messages = validations.map((val) => val.message)
      this.errorMessages = messages
    },
    selectTime(n) {
      this.registrationForm.field.timezone.value = n.value
    },
    selectRole(n) {
      console.log('userRole', this.userRole)
      console.log('n', n)
      this.registrationForm.field.role.value = n.key
    },
    async onSubmit() {
      this.registrationForm.validate()

      if (
        this.registrationForm.field.password.value !==
        this.registrationForm.field.confirmPassword.value
      ) {
        this.$toast('Please make sure password match.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }

      if (!this.registrationForm.isValid) {
        this.$toast('Please complete all fields.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      const splitEmail = this.registrationForm.field.email.value.split('@')
      // if (splitEmail[splitEmail.length - 1] === 'gmail.com') {
      //   this.$toast('Please use a company email.', {
      //     timeout: 2000,
      //     position: 'top-left',
      //     type: 'error',
      //     toastClassName: 'custom',
      //     bodyClassName: ['custom'],
      //   })
      //   return
      // }

      this.submitting = true

      let user
      try {
        user = await User.api.register(this.registrationForm)
        if (user.status === 400) {
          for (let key in user.data) {
            this.$toast(user.data[key][0], {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          }
          return
        }
        else if (user.status === 500) {
          for (let key in user.data) {
            this.$toast(user.data[key], {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          }
          return
        } else {
          this.$router.push({ name: 'Login' })
        }
      } catch (error) {
        this.$toast('There was a problem creating your account.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        throw error
      } finally {
        this.submitting = false
      }

      // Update the user in the store to "log in" and navigate to integrations
      // const encryptedUser = encryptData(user, process.env.VUE_APP_SECRET_KEY)
      // const encryptedKey = encryptData(user.token, process.env.VUE_APP_SECRET_KEY)
      // this.$store.commit('UPDATE_USER', encryptedUser)
      // this.$store.commit('UPDATE_USERTOKEN', encryptedKey)

      // this.$store.commit('UPDATE_USER', user)
      // this.$store.commit('UPDATE_USERTOKEN', user.token)
      // if (this.isPR) {
      //   this.$router.push({ name: 'PRSummaries' })
      // } else {
      //   this.$router.push({ name: 'Home' })
      // }
    },
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
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    isPR() {
      return this.$store.state.user.role === 'PR'
    },
  },
  mounted() {
    this.registrationForm.field.timezone.value = this.userTime
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
    width: 26vw;
    border-radius: 6px;
    padding: 12px;
    font-size: 16px;
    margin: 1rem 0rem 0rem 0rem;
    box-shadow: none;
    z-index: 10;
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
  gap: 12px;
  border-radius: 6px;
  background-color: white;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  padding: 2rem 3rem 2rem 3rem;
  margin-top: 2rem;
  width: 33vw;
  color: $base-gray;
  letter-spacing: 0.75px;

  &__footer {
    width: 100%;
    font-size: 12px;
    margin-top: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
}
.registration__form {
  background-color: transparent !important;
  display: flex;
  justify-content: center;
  align-items: center;
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
  margin-top: 6px;
}
input::placeholder {
  color: $very-light-gray;
  font-size: 12px;
}
input:focus {
  outline: none;
}
label {
  font-size: 13px;
  color: $base-gray;
}
a {
  color: $light-gray-blue;
  font-weight: bold;
}
.disabled {
  background-color: $soft-gray !important;
}

.logo-title {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 28px;
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
.fields-container {
  height: 40vh;
  overflow-x: auto;
  gap: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.top-field {
  margin-top: 7rem;
}
</style>