<template>
  <div class="registration">
    <div class="registration-card">
      <img class="logo" src="@/assets/images/logo.png" />
      <h1>Register</h1>

      <template v-if="!isLoading">
        <!-- <template v-if="errorValidatingEmail">
    
        <div class="box" style="display: flex; flex-direction: column; align-items: center">
          <span>
            <small class="muted"
              >You have already activated your account, if you forgot your password you can reset it
              here
            </small>
          </span>
          <br />
          <router-link :to="{ name: 'ForgotPassword' }"> Forgot Password ? </router-link>
        </div>
      </template> -->
        <template>
          <div class="registration__text">
            Create and customize your Managr account with {{ organization }} within minutes.
          </div>
          <!-- <form @submit.prevent="onSubmit"> -->

          <div style="margin-top: -1rem" class="registration__form">
            <div class="form-card">
              <FormField
                label="Full Name"
                @blur="registrationForm.field.fullName.validate()"
                :errors="registrationForm.field.fullName.errors"
                v-model="registrationForm.field.fullName.value"
                large
                bordered
                placeholder=""
                id="fullname"
              />
              <FormField
                label="Your Email"
                @blur="registrationForm.field.email.validate()"
                :errors="registrationForm.field.email.errors"
                v-model="registrationForm.field.email.value"
                large
                bordered
                :disabled="true"
                placeholder=""
                id="email"
              />
              <FormField
                label="Set a Password"
                @blur="registrationForm.field.password.validate()"
                :errors="registrationForm.field.password.errors"
                v-model="registrationForm.field.password.value"
                placeholder=""
                intputType="password"
                large
                bordered
                id="password"
              />
              <FormField
                label="Re-Enter Password"
                @blur="registrationForm.field.confirmPassword.validate()"
                :errors="registrationForm.field.confirmPassword.errors"
                v-model="registrationForm.field.confirmPassword.value"
                placeholder=""
                inputType="password"
                large
                bordered
                id="renterpassword"
              />

              <div style="width: 100%; text-align: center">
                <p>
                  Your timezone:
                  <span style="color: #199e54; font-weight: bold">{{ userTime }}</span>
                </p>
                <p v-if="!changeZone" @click="selectZone" class="time">Change timezone ?</p>
                <p v-else @click="selectZone" class="time">Select your timezone:</p>
              </div>

              <FormField v-if="changeZone">
                <template v-slot:input>
                  <DropDownSearch
                    :items.sync="timezones"
                    v-model="registrationForm.field.timezone.value"
                    nullDisplay="Select your timezone"
                    searchable
                    local
                  />
                </template>
              </FormField>
            </div>

            <div style="margin-top: 1rem" class="registration__privacy">
              By clicking Sign Up, I agree to the
              <a href="https://managr.ai/terms-of-service" target="_blank">Terms of Service</a> and
              <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
            </div>

            <Button class="registration__button" type="submit" @click="onSubmit" text="Sign Up" />

            <div style="margin-top: 1rem">
              <router-link :to="{ name: 'Login' }">Back to Login</router-link>
            </div>
            <!-- </form> -->
          </div>
        </template>
      </template>
      <template v-else>
        <ComponentLoadingSVG />
      </template>
    </div>
  </div>
</template>

<script>
import User, { RepRegistrationForm } from '@/services/users'
import Button from '@thinknimble/button'
import FormField from '@/components/forms/FormField'
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
import DropDownSearch from '@/components/DropDownSearch'
import moment from 'moment-timezone'

export default {
  name: 'Register',
  components: {
    Button,
    FormField,
    ComponentLoadingSVG,
    DropDownSearch,
  },
  data() {
    return {
      User,
      submitting: false,
      registrationForm: new RepRegistrationForm(),
      reenterPassword: '',
      userId: null,
      token: null,
      email: null,
      isLoading: false,
      organization: null,
      errorValidatingEmail: false,
      timezones: moment.tz.names(),
      userTime: moment.tz.guess(),
      changeZone: false,
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
    selectZone() {
      this.changeZone = !this.changeZone
    },
    async retrieveEmail(id, token) {
      this.isLoading = true
      try {
        const res = await User.api.retrieveEmail(id, token)
        this.registrationForm.field.email.value = res.data.email
        this.organization = res.data.organization
      } catch (e) {
        this.errorValidatingEmail = true
        this.$Alert.alert({
          type: 'error',
          timeout: 3000,
          message: 'Unable to retrieve email',
        })
      } finally {
        this.isLoading = false
      }
    },
    async onSubmit() {
      //
      this.registrationForm.validate()

      // Do not continue if the form has errors
      if (!this.registrationForm.isValid) {
        this.$Alert.alert({
          type: 'error',
          message: 'Please complete all the fields.',
          timeout: 3000,
        })
        return
      }

      // Continue with user registration...
      this.submitting = true

      let user
      try {
        user = await User.api.activate(this.userId, this.token, this.registrationForm)
      } catch (error) {
        this.$Alert.alert({
          type: 'error',
          message: 'There was a problem creating your user account.',
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
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.registration {
  display: flex;
  padding: 2rem;
  flex-flow: column;
  justify-content: center;
  max-width: 24rem;
  margin: 1.5rem auto;

  &__text {
    color: $panther;
    font-family: #{$base-font-family};
    width: 100%;
    max-width: 20rem;
    margin-bottom: 4rem;
    text-align: center;
  }
  &__input {
    @include input-field-white();
  }
  &__input__label {
    font-size: 14px;
  }
  &__privacy {
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
  }

  &__button {
    @include primary-button();
    width: 19rem;
    border-radius: 3px;
    margin-top: 1rem;
  }
}
.logo {
  height: 4rem;
  margin-left: 37%;
}

.divider {
  height: 1px;
  background-color: #aaa;
  width: 100%;
  margin: 1rem;
}

.errors {
  width: 100%;
  padding: 1rem;
  background-color: rgb(155, 21, 21);
  color: white;
  font-weight: 500;
}

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
.form-card {
  display: flex;
  align-items: space-evenly;
  justify-content: space-evenly;
  flex-direction: row;
  flex-wrap: wrap;
  border-radius: 0.5rem;
  background-color: $panther;
  padding: 3rem;
  width: 50vw;
  color: white;
}

a {
  color: $dark-green;
  font-weight: bold;
}
.time {
  color: $very-light-gray;
  cursor: pointer;
  filter: opacity(60%);
  font-size: 0.9rem;
}
</style>
