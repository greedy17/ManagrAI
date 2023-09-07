<template>
  <div class="registration">
    <header>
      <img class="blue-filter" src="@/assets/images/logo.png" height="36px" alt="" />

      <div class="header">
        <small>Registration Form</small>
      </div>
    </header>

    <div :class="{ disable: generatingToken }" class="form-card">
      <h2>Account Registration</h2>
      <div class="col full-width">
        <label for="company">Company Name</label>
        <input
          class="full-width"
          @blur="registrationForm.field.organizationName.validate()"
          :errors="registrationForm.field.organizationName.errors"
          v-model="registrationForm.field.organizationName.value"
          placeholder="Enter Company Name"
          id="company"
        />
      </div>

      <div class="col full-width">
        <label for="role">Select Product</label>
        <Multiselect
          placeholder="Select product"
          class="full-width"
          style="margin-top: 8px"
          @input="selectRole($event)"
          v-model="userRole"
          :options="userRoles"
          openDirection="below"
          selectLabel="Enter"
          label="name"
          id="key"
        >
          <template slot="noResult">
            <p>No results.</p>
          </template>
        </Multiselect>
      </div>

      <div class="input-wrap full-width">
        <div class="col">
          <label for="name">Full Name</label>
          <input
            @blur="registrationForm.field.fullName.validate()"
            :errors="registrationForm.field.fullName.errors"
            v-model="registrationForm.field.fullName.value"
            placeholder="Enter Full Name"
            id="name"
          />
        </div>

        <div class="col">
          <label for="email">Email</label>
          <input
            @blur="registrationForm.field.email.validate()"
            :errors="registrationForm.field.email.errors"
            v-model="registrationForm.field.email.value"
            type="email"
            id="email"
            placeholder="Enter Email"
          />
        </div>

        <div class="col">
          <label for="password">Set a Password</label>
          <input
            id="password"
            @blur="showVals(registrationForm.field.password)"
            @input="registrationForm.field.password.validate()"
            :errors="registrationForm.field.password.errors"
            v-model="registrationForm.field.password.value"
            type="password"
            placeholder="Must be 10 characters or longer"
          />
          <div class="column" v-for="(message, i) in errorMessages" :key="i">
            <small class="error">{{ message }}</small>
          </div>
        </div>

        <div class="col">
          <label for="confirm-password">Re-Enter Password</label>
          <input
            id="confirm-password"
            label="Re-Enter Password"
            @blur="registrationForm.field.confirmPassword.validate()"
            :errors="registrationForm.field.confirmPassword.errors"
            v-model="registrationForm.field.confirmPassword.value"
            type="password"
            placeholder="Must be 10 characters or longer"
          />
        </div>
      </div>

      <div class="row mar-top">
        <div>
          <small>By signing up, I agree to Managr's</small>
          <a href="https://managr.ai/terms-of-service" target="_blank">Terms</a>
          <small>&</small>
          <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>.
        </div>

        <button
          :disabled="!validatedForm"
          :class="{ disabled: !validatedForm }"
          class="primary-button"
          type="submit"
          @click="onSubmit"
        >
          Sign Up
        </button>
      </div>
    </div>

    <div></div>
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
      isLoading: false,
      userId: '',
      token: '',
      organization: null,
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
    console.log(this.$route.params)

    // if (!validCode && !this.$route.query.code) {
    //   this.$router.push({
    //     name: 'Register',
    //   })
    // }
    await this.retrieveEmail(this.$route.params.code)
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
    test(log) {
      console.log('log', log)
    },
    async retrieveEmail(code) {
      this.isLoading = true
      try {
        console.log('code', code)
        const res = await User.api.retrieveEmail(code)
        console.log('res retrieveEmail', res)
        this.registrationForm.field.email.value = res.data.email
        this.registrationForm.field.organizationName.value = res.data.organization
        this.registrationForm.field.role.value = res.data.role
        this.registrationForm.field.fullName.value = res.data.first_name + ' ' + res.data.last_name
        this.userId = res.data.id
        this.token = res.data.magic_token
        this.organization = res.data.organization
      } catch (e) {
        // this.errorValidatingEmail = true
        console.log('e', e)
        this.$toast('Unable to retrieve email', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.isLoading = false
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
    showVals(val) {
      let validations = val.errors
      let messages = validations.map((val) => val.message)
      this.errorMessages = messages
    },
    selectTime(n) {
      this.registrationForm.field.timezone.value = n.value
    },
    selectRole(n) {
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
        this.$toast(this.registrationForm.errors[0].errors[0].message, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      const splitEmail = this.registrationForm.field.email.value.split('@')
      if (splitEmail[splitEmail.length - 1] === 'gmail.com') {
        this.$toast('Please use a company email.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }

      this.submitting = true

      let user
      try {
        // user = await User.api.register(this.registrationForm)
        user = await User.api.activate(this.userId, this.token, this.registrationForm)
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
        } else if (user.status === 500) {
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

.input-wrap {
  display: flex;
  align-items: center;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 16px;

  div {
    input {
      width: 227px;
    }
  }
}

.col {
  display: flex;
  flex-direction: column;
}
.full-width {
  width: 100%;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
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
  flex-flow: column;
  align-items: flex-start;
  justify-content: center;
  color: $dark-black-blue;
  background-color: $offer-white;
  border-radius: 4px;
  gap: 16px;
  width: 600px;
  padding: 64px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
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
  border-radius: 4px;
  padding: 10px;
  border: 1px solid $soft-gray;
  color: $base-gray;
  font-family: $thin-font-family;
  margin-top: 8px;
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
  color: $darker-blue;
  font-family: $base-font-family;
  text-decoration: none;

  font-size: 13px;
  margin: 0 4px;
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
.blue-filter {
  filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
    contrast(90%);
}

.primary-button {
  @include dark-blue-button();
  text-align: center;
  margin-bottom: 6px;
  width: 100px;
  padding: 8px;
  box-shadow: none;

  &:disabled {
    background-color: $off-white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    opacity: 0.7;
  }
}

.mar-top {
  margin-top: 16px;
}
</style>