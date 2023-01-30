<template>
  <div class="registration">
    <div>
      <template v-if="!isLoading">
        <template v-if="errorValidatingEmail">
          <div class="box" style="display: flex; flex-direction: column; align-items: center">
            <span>
              <small
                >You have already activated your account, if you forgot your password you can reset
                it here
              </small>
            </span>
            <br />
            <router-link :to="{ name: 'ForgotPassword' }"> Forgot Password ? </router-link>
          </div>
        </template>
        <template v-else>
          <div class="registration__form">
            <div class="form-card">
              <h2>Register</h2>

              <span>
                <label for="fullname">Full Name</label>
                <input
                  @blur="registrationForm.field.fullName.validate()"
                  :errors="registrationForm.field.fullName.errors"
                  v-model="registrationForm.field.fullName.value"
                  id="fullname"
                />
              </span>

              <span>
                <label for="email">Email</label>
                <input
                  label="Your Email"
                  @blur="registrationForm.field.email.validate()"
                  :errors="registrationForm.field.email.errors"
                  v-model="registrationForm.field.email.value"
                  type="email"
                  id="email"
                />
              </span>

              <span>
                <label for="password">Set a Pasword</label>
                <input
                  @blur="showVals(registrationForm.field.password)"
                  @input="registrationForm.field.password.validate()"
                  :errors="registrationForm.field.password.errors"
                  v-model="registrationForm.field.password.value"
                  type="password"
                  id="password"
                />
                <div class="column" v-for="(message, i) in errorMessages" :key="i">
                  <small class="error">{{ message }}</small>
                </div>
              </span>

              <span>
                <label for="renterpassword">Re-Enter Password</label>
                <input
                  @blur="registrationForm.field.confirmPassword.validate()"
                  :errors="registrationForm.field.confirmPassword.errors"
                  v-model="registrationForm.field.confirmPassword.value"
                  type="password"
                  id="renterpassword"
                />
              </span>

              <!-- <div style="width: 100%; text-align: center">
                <p>
                  Your timezone:
                  <span style="color: #41b883; font-weight: bold">{{ userTime }}</span>
                </p>
                <p v-if="!changeZone" @click="selectZone" class="time">Change timezone ?</p>
                <p v-else @click="selectZone" class="time">Select your timezone:</p>
              </div> -->

              <Multiselect
                :placeholder="userTime"
                @input="test($event)"
                v-model="selectedZone"
                :options="timezones"
                openDirection="above"
                style="width: 45vw"
                selectLabel="Enter"
                label="key"
              >
                <template slot="noResult">
                  <p>No results.</p>
                </template>
              </Multiselect>

              <div class="form-card__footer">
                <div>
                  By clicking Sign Up, I agree to the
                  <a href="https://managr.ai/terms-of-service" target="_blank">Terms of Service</a>
                  and
                  <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
                </div>

                <Button
                  class="registration__button"
                  type="submit"
                  @click="onSubmit"
                  text="Sign Up"
                />
              </div>
            </div>

            <!-- <div style="margin-top: 1rem">
              <router-link :to="{ name: 'Login' }">Back to Login</router-link>
            </div> -->
          </div>
        </template>
      </template>
      <template v-else>
        <p>...</p>
      </template>
    </div>
  </div>
</template>

<script>
import User, { RepRegistrationForm } from '@/services/users'
import Button from '@thinknimble/button'
import moment from 'moment-timezone'

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
      email: null,
      isLoading: false,
      organization: null,
      errorValidatingEmail: false,
      timezones: moment.tz.names(),
      userTime: moment.tz.guess(),
      changeZone: false,
      selectedZone: null,
    }
  },
  async created() {
    this.userId = this.$route.params.userId
    this.token = this.$route.params.magicToken
    await this.retrieveEmail(this.userId, this.token)
    this.timezones = this.timezones.map((tz) => {
      return { key: tz, value: tz }
    })
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
    test(n) {
      this.registrationForm.field.timezone.value = n.value
    },
    async retrieveEmail(id, token) {
      this.isLoading = true
      try {
        const res = await User.api.retrieveEmail(id, token)
        this.registrationForm.field.email.value = res.data.email
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

      // Do not continue if the form has errors
      // if (!this.registrationForm.isValid) {
      //   this.$toast('Please complete all fields', {
      //     timeout: 2000,
      //     position: 'top-left',
      //     type: 'error',
      //     toastClassName: 'custom',
      //     bodyClassName: ['custom'],
      //   })
      //   return
      // }

      // Continue with user registration...
      this.submitting = true

      let user
      try {
        user = await User.api.activate(this.userId, this.token, this.registrationForm)
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
      this.$store.commit('UPDATE_USER', user)
      this.$store.commit('UPDATE_USERTOKEN', user.token)
      this.$router.push({ name: 'Integrations' })
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

input:focus {
  outline: none;
}
a {
  text-decoration: none;
}
.registration {
  display: flex;
  padding: 2rem 0rem 0rem 0rem;
  flex-flow: column;
  justify-content: center;
  // max-width: 24rem;
  // margin: 1.5rem auto;

  &__text {
    color: $base-gray;
    font-family: #{$base-font-family};
    margin-bottom: 2rem;
    text-align: center;
    font-size: 14px;
  }
  &__privacy {
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
  }

  &__button {
    @include primary-button();
    width: 10rem;
    border-radius: 6px;
    margin-top: 1rem;
    box-shadow: none;
  }
}
input:focus {
  outline: none;
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
  width: 45vw;
  border-radius: 4px;
  padding: 10px;
  border: 1px solid $soft-gray;
}
input:focus {
  outline: none;
}
label {
  font-size: 13px;
  color: $light-gray-blue;
}
.form-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-evenly;
  flex-direction: column;
  gap: 12px;
  border-radius: 6px;
  background-color: white;
  // border: 1px solid #e8e8e8;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  padding: 1rem 2rem;
  width: 50vw;
  color: $base-gray;
  letter-spacing: 0.75px;

  &__footer {
    font-size: 12px;
  }
}
a {
  color: $dark-green;
  font-weight: bold;
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
::v-deep .input-content {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
::v-deep .input-form__active {
  border: none;
}
</style>
