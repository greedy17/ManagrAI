<template>
  <div class="registration">
    <header>
      <img class="blue-filter" src="@/assets/images/logo.png" height="36px" alt="" />

      <div class="header">
        <small>Registration Form</small>
      </div>
    </header>

    <template v-if="!isLoading">
      <template v-if="errorValidatingEmail">
        <div class="forgot-box">
          <small
            >You have already activated your account, if you forgot your password you can reset it
            here
          </small>

          <br />
          <router-link :to="{ name: 'ForgotPassword' }"> Forgot Password ? </router-link>
        </div>
      </template>

      <template v-else>
        <div class="form-card">
          <h2>Account Registration</h2>
          <div class="column">
            <label for="fullname">Full Name</label>
            <input
              @blur="registrationForm.field.fullName.validate()"
              :errors="registrationForm.field.fullName.errors"
              v-model="registrationForm.field.fullName.value"
              id="fullname"
              placeholder="Enter Full Name"
            />
          </div>

          <div class="column">
            <label for="email">Email</label>
            <input
              label="Your Email"
              @blur="registrationForm.field.email.validate()"
              :errors="registrationForm.field.email.errors"
              v-model="registrationForm.field.email.value"
              type="email"
              id="email"
              placeholder="Enter Email"
            />
          </div>

          <div class="column">
            <label for="password">Set a Password</label>
            <input
              @blur="showVals(registrationForm.field.password)"
              @input="registrationForm.field.password.validate()"
              :errors="registrationForm.field.password.errors"
              v-model="registrationForm.field.password.value"
              type="password"
              id="password"
              placeholder="Must be 10 characters or longer"
            />
            <div class="column" v-for="(message, i) in errorMessages" :key="i">
              <small class="error">{{ message }}</small>
            </div>
          </div>

          <div class="column">
            <label for="renterpassword">Re-Enter Password</label>
            <input
              @blur="registrationForm.field.confirmPassword.validate()"
              :errors="registrationForm.field.confirmPassword.errors"
              v-model="registrationForm.field.confirmPassword.value"
              type="password"
              id="renterpassword"
              placeholder="Must be 10 characters or longer"
            />
          </div>

          <div class="row">
            <small>
              By signing up, I agree to Managr's
              <a href="https://managr.ai/terms-of-service" target="_blank">Terms </a>
              &
              <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>.
            </small>

            <button
              :disabled="!validatedForm"
              class="primary-button"
              type="submit"
              @click="onSubmit"
            >
              Sign Up
            </button>
          </div>
        </div>
      </template>
    </template>

    <div></div>
  </div>
</template>

<script>
import User, { RepRegistrationForm } from '@/services/users'
import Button from '@thinknimble/button'
import moment from 'moment-timezone'
import { encryptData } from '../../encryption'

export default {
  name: 'Register',
  components: {
    Button,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      User,
      submitting: false,
      registrationForm: new RepRegistrationForm(),
      userId: null,
      token: null,
      code: null,
      email: null,
      isLoading: false,
      organization: null,
      errorValidatingEmail: false,
      errorMessages: [],
      timezones: moment.tz.names(),
      userTime: moment.tz.guess(),
      changeZone: false,
      selectedZone: null,
      validatedForm: false,
    }
  },
  async created() {
    // this.userId = this.$route.params.userId
    // this.token = this.$route.params.magicToken
    this.code = this.$route.params.code
    await this.retrieveEmail(this.code)
    this.timezones = this.timezones.map((tz) => {
      return { key: tz, value: tz }
    })
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
          val.field.confirmPassword.value
        ) {
          this.validatedForm = true
        } else {
          this.validatedForm = false
        }
      },
    },
  },
  methods: {
    showVals(val) {
      let validations = val.errors
      let messages = validations.map((val) => val.message)
      this.errorMessages = messages
    },
    // selectZone() {
    //   this.changeZone = !this.changeZone
    // },
    async retrieveEmail(code) {
      this.isLoading = true
      try {
        const res = await User.api.retrieveEmail(code)
        this.registrationForm.field.email.value = res.data.email
        this.userId = res.data.id
        this.token = res.data.magic_token
        this.organization = res.data.organization
      } catch (e) {
        this.errorValidatingEmail = true
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
      // Do not continue if the form has errors
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
      // Continue with user registration...
      this.submitting = true
      let user
      try {
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
      // this.$store.commit('UPDATE_USER', user)
      // this.$store.commit('UPDATE_USERTOKEN', encryptedKey)
      // this.$store.commit('UPDATE_USERTOKEN', user.token)
      this.$router.push({ name: 'Login' })
      // if (this.isPR) {
      //   this.$router.push({ name: 'PRSummaries' })
      // } else {
      //   this.$router.push({ name: 'Home' })
      // }
    },
  },
  computed: {
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

a {
  color: $dark-blue;
  font-family: $base-font-family;
  text-decoration: none;
  font-size: 13px;
  margin: 0 4px;
}
.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 90vh;
}
.center-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin-bottom: 16px;
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

.disabled {
  background-color: $soft-gray !important;
}
// .time {
//   color: $base-gray;
//   cursor: pointer;
//   font-size: 14px;
// }
// .time:hover {
//   color: $gray;
// }
h1 {
  font-weight: bold;
  color: $main-font-gray;
  text-align: center;
  font-size: 1.6rem;
}
.registration__form {
  background-color: transparent !important;
  display: flex;
  flex-flow: column;
  align-items: center;
}
input {
  width: 100%;
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
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
}
.logo-title {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.gray-blue {
  color: $light-gray-blue;
}

::v-deep .input-content {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
::v-deep .input-form__active {
  border: none;
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

.forgot-box {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $dark-black-blue;
  background-color: $offer-white;
  border-radius: 4px;
  padding: 64px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
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

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}
</style>
