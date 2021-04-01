<template>
  <div class="registration">
    <img class="registration__logo" src="@/assets/images/logo.png" />
    <h2>Register</h2>

    <div class="registration__text">Create and customize your Managr account within minutes.</div>
    <!-- <form @submit.prevent="onSubmit"> -->

    <div class="registration__form">
      <FormField
        label="Your Name"
        @blur="registrationForm.field.fullName.validate()"
        :errors="registrationForm.field.fullName.errors"
        v-model="registrationForm.field.fullName.value"
        large
        bordered
        placeholder=""
      />
      <FormField
        label="Your Email"
        @blur="registrationForm.field.email.validate()"
        :errors="registrationForm.field.email.errors"
        v-model="registrationForm.field.email.value"
        large
        bordered
        placeholder=""
      />
      <FormField
        id="password"
        label="Set a Password"
        @blur="registrationForm.field.password.validate()"
        :errors="registrationForm.field.password.errors"
        v-model="registrationForm.field.password.value"
        placeholder=""
        type="password"
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
        type="password"
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
      />
      <div class="dropdown">
        <FormField :errors="registrationForm.field.role.errors" label="Role">
          <template v-slot:input>
            <DropDownSelect
              :items="userRoles"
              valueKey="key"
              displayKey="name"
              v-model="registrationForm.field.role.value"
              :itemsRef="userRoles"
              class="invite-form__dropdown"
              nullDisplay="Select user role"
              @input="registrationForm.field.role.validate()"
            />
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
        <a href>Terms of Service</a> and
        <a href>Privacy Policy</a>
      </div>

      <Button class="registration__button" type="submit" @click="onSubmit" text="Sign Up" />

      <div style="margin-top: 1rem">
        <router-link :to="{ name: 'Login' }">Back to Login</router-link>
      </div>
      <!-- </form> -->
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

export default {
  name: 'Registration',
  components: {
    FormField,
    DropDownSelect,
    GoogleButton,
    TNDropdown,
    managrDropdown,
    Button,
  },
  data() {
    return {
      User,
      submitting: false,
      registrationForm: new UserRegistrationForm(),
      userRoles: User.roleChoices,
    }
  },
  created() {
    this.registrationForm.dynamicValidators()
    const validCode = this.$route.params.validCode

    if (!validCode) {
      // redirects to enter code registration screen if they try to get there without putting in leaderrshop code
      this.$router.push({
        name: 'Register',
      })
    }
  },
  methods: {
    async onSubmit() {
      //
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
        })
        throw error
      } finally {
        this.submitting = false
      }

      // Update the user in the store to "log in" and navigate to integrations
      this.$store.commit('UPDATE_USER', user)
      this.$store.commit('UPDATE_USERTOKEN', user.token)

      this.$router.push({ name: 'InviteUsers' })
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
  margin: 0 auto;

  &__logo {
    height: 5rem;
    object-fit: contain;
  }
  &__text {
    color: #{$mid-gray};
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
.dropdown {
  ::v-deep .tn-dropdown__selection-container {
    border-radius: 4px;
    background-color: $white;
    border: 1px solid #eaebed;
    box-sizing: border-box;
    line-height: 1.29;
    letter-spacing: 0.5px;
  }
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

h2 {
  @include base-font-styles();
  font-weight: bold;
  color: $main-font-gray;
  text-align: center;
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
</style>
