<template>
  <div class="registration">
    <div class="registration-card">
      <div class="header">
        <img class="logo" src="@/assets/images/logo.png" />
        <h2>Register</h2>
      </div>

      <div class="registration__text">Create and customize your Managr account within minutes.</div>
      <!-- <form @submit.prevent="onSubmit"> -->
      <div class="registration__form">
        <div class="form-card">
          <FormField
            label="Full Name"
            @blur="registrationForm.field.fullName.validate()"
            :errors="registrationForm.field.fullName.errors"
            v-model="registrationForm.field.fullName.value"
            large
            bordered
            placeholder=""
            id="name"
          />
          <FormField
            label="Your Email"
            @blur="registrationForm.field.email.validate()"
            :errors="registrationForm.field.email.errors"
            v-model="registrationForm.field.email.value"
            large
            bordered
            placeholder=""
            id="email"
          />
          <FormField
            id="password"
            label="Set a Password"
            @blur="registrationForm.field.password.validate()"
            :errors="registrationForm.field.password.errors"
            v-model="registrationForm.field.password.value"
            placeholder=""
            inputType="password"
            large
            bordered
          />
          <FormField
            id="confirm-password"
            label="Re-Enter Password"
            @blur="registrationForm.field.confirmPassword.validate()"
            :errors="registrationForm.field.confirmPassword.errors"
            v-model="registrationForm.field.confirmPassword.value"
            placeholder=""
            inputType="password"
            large
            bordered
          />
          <FormField
            label="Company"
            @blur="registrationForm.field.organizationName.validate()"
            :errors="registrationForm.field.organizationName.errors"
            v-model="registrationForm.field.organizationName.value"
            placeholder=""
            large
            bordered
            id="company"
          />

          <FormField :errors="registrationForm.field.role.errors" label="Role">
            <template v-slot:input>
              <Multiselect
                placeholder="Select User Role"
                @input="tester($event)"
                v-model="userRole"
                :options="userRoles"
                openDirection="below"
                style="width: 18vw"
                selectLabel="Enter"
                label="name"
              >
                <template slot="noResult">
                  <p>No results.</p>
                </template>
              </Multiselect>

              <!-- <DropDownSearch
                :items="userRoles"
                valueKey="key"
                displayKey="name"
                v-model="registrationForm.field.role.value"
                :itemsRef="userRoles"
                class="invite-form__dropdown"
                nullDisplay="Select user role"
                @input="registrationForm.field.role.validate()"
              /> -->
            </template>
          </FormField>

          <div style="width: 100%; text-align: center">
            <p>
              Your timezone: <span style="color: #41b883; font-weight: bold">{{ userTime }}</span>
            </p>
            <p v-if="!changeZone" @click="selectZone" class="time">Change timezone ?</p>
            <p v-else @click="selectZone" class="time">Select your timezone:</p>
          </div>

          <FormField v-if="changeZone">
            <template v-slot:input>
              <Multiselect
                placeholder="Select time zone"
                @input="test($event)"
                v-model="selectedZone"
                :options="timezones"
                openDirection="below"
                style="width: 16vw"
                selectLabel="Enter"
                label="key"
              >
                <template slot="noResult">
                  <p>No results.</p>
                </template>
              </Multiselect>

              <!-- <DropDownSearch
                :items.sync="timezones"
                v-model="registrationForm.field.timezone.value"
                nullDisplay="Select your timezone"
                searchable
                local
              /> -->
            </template>
          </FormField>
        </div>
        <!-- <div class="registration__input__label">
        Company
        <input
          v-model="registrationForm.field.organizationName.value"
          type="text"
          class="registration__input"
        />
      </div> -->
        <div class="registration__privacy">
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
    </div>
  </div>
</template>

<script>
import User, { UserRegistrationForm } from '@/services/users'

import GoogleButton from '@/components/GoogleButton'
import TNDropdown from '@/components/TNDropdown'
import managrDropdown from '@/components/managrDropdown'
import Button from '@thinknimble/button'
import FormField from '@/components/forms/FormField'
import DropDownSelect from '@thinknimble/dropdownselect'
import DropDownSearch from '@/components/DropDownSearch'
import moment from 'moment-timezone'

export default {
  name: 'Registration',
  components: {
    FormField,
    DropDownSelect,
    GoogleButton,
    TNDropdown,
    managrDropdown,
    Button,
    DropDownSearch,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      User,
      submitting: false,
      registrationForm: new UserRegistrationForm(),
      userRoles: User.roleChoices,
      timezones: moment.tz.names(),
      userTime: moment.tz.guess(),
      changeZone: false,
      userRole: null,
      selectedZone: null,
    }
  },
  created() {
    const validCode = this.$route.params.validCode

    if (!validCode) {
      // redirects to enter code registration screen if they try to get there without putting in leaderrshop code
      this.$router.push({
        name: 'Register',
      })
    }
    this.timezones = this.timezones.map((tz) => {
      return { key: tz, value: tz }
    })
  },
  methods: {
    selectZone() {
      this.changeZone = !this.changeZone
    },
    test(n) {
      this.registrationForm.field.timezone.value = n.value
    },
    tester(n) {
      this.registrationForm.field.role.value = n.key
    },
    async onSubmit() {
      this.registrationForm.validate()

      // Do not continue if the form has errors
      if (!this.registrationForm.isValid) {
        this.$Alert.alert({ type: 'error', message: 'Please complete all the fields.' })
        return
      }
      // Continue with user registration...
      this.submitting = true

      let user
      try {
        user = await User.api.register(this.registrationForm)
      } catch (error) {
        this.$Alert.alert({
          type: 'error',
          message: 'There was a problem creating your user account.',
          timeout: 2000,
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
  computed: {
    user() {
      return this.$store.state.user
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

.registration {
  display: flex;
  padding: 2rem;
  flex-flow: column;
  justify-content: center;
  max-width: 24rem;
  margin: 1.5rem auto;

  &__text {
    color: $base-gray;
    font-family: #{$base-font-family};
    margin-bottom: 1rem;
    text-align: center;
    font-size: 14px;
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
    margin-top: 0.5rem;
  }

  &__button {
    @include primary-button();
    width: 19rem;
    border-radius: 3px;
    margin-top: 1rem;
    box-shadow: none;
  }
}

.header {
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    height: 1.5rem;
    margin-right: 0.25rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}

.time {
  color: $base-gray;
  cursor: pointer;
  font-size: 14px;
}
.time:hover {
  color: $gray;
}
.dropdown {
  align-items: center;
  width: 18vw;
  margin: 0;
}
::v-deep .input-content {
  width: 16rem;
}
::v-deep .tn-dropdown__selection-container {
  display: flex;
  align-items: center;
  text-align: center;
  border-radius: 4px;
  background-color: $white;
  border: 1px solid #eaebed;
  line-height: 1.29;
  letter-spacing: 0.5px;
  height: 2.5rem;
}
::v-deep .tn-dropdown__options__option {
  color: $panther;
}
::v-deep .tn-dropdown__options__container {
  background-color: white;
}
::v-deep .tn-dropdown--medium {
  width: 16rem;
}
.form-card {
  display: flex;
  align-items: space-evenly;
  justify-content: space-evenly;
  flex-direction: row;
  flex-wrap: wrap;
  border-radius: 0.3rem;
  background-color: white;
  border: 1px solid #e8e8e8;
  padding: 2rem;
  width: 50vw;
  color: $base-gray;
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

.registration__form {
  background-color: transparent !important;
  display: flex;
  flex-flow: column;
  align-items: center;
}

input {
  height: 2.5rem;
  width: 100%;
  display: block;
  margin: 1rem;

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
a {
  color: $dark-green;
  font-weight: bold;
}
</style>