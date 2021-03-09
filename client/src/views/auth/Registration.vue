<template>
  <div class="registration">
    <img class="registration__logo" src="@/assets/images/logo.png" />
    <h2>Register</h2>

    <div class="registration__text">
      Create and customize your Managr account within minutes.
    </div>
    <!-- <form @submit.prevent="onSubmit"> -->
    <div class="registration__form">
      <div class="registration__input__label">
        Your Name
        <input
          v-model="registrationForm.field.fullName.value"
          type="text"
          class="registration__input"
        />
      </div>
      <div class="registration__input__label">
        Your Email
        <input
          v-model="registrationForm.field.email.value"
          type="text"
          class="registration__input"
        />
      </div>

      <div class="registration__input__label">
        Set a Password
        <input
          v-model="registrationForm.field.password.value"
          type="password"
          class="registration__input"
        />
      </div>

      <div class="registration__input__label">
        Re-enter Password
        <input v-model="reenterPassword" type="password" class="registration__input" />
      </div>

      <div class="registration__input__label">
        Company
        <input
          v-model="registrationForm.field.organizationName.value"
          type="text"
          class="registration__input"
        />
      </div>

      <div class="registration__input__label">
        Role
        <managrDropdown
          :options="User.roles.ROLE_CHOICES"
          placeholder="Your Role"
          @selected="onSelectRole"
        />
      </div>
      <div class="registration__privacy">
        By clicking Work With Managr, I agree to the <a href="">Terms of Service</a> and
        <a href="">Privacy Policy</a>
      </div>

      <Button class="registration__button" type="submit" @click="onSubmit" text="Sign Up" />

      <div style="margin-top: 1rem">
        <router-link :to="{ name: 'Login' }">
          Back to Login
        </router-link>
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

export default {
  name: 'Registration',
  components: {
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
      reenterPassword: '',
    }
  },
  methods: {
    onSelectRole(role) {
      this.registrationForm.field.role.value = role.key
    },
    async onSubmit() {
      //
      this.registrationForm.validate()

      // Do not continue if the form has errors
      if (this.registrationForm.errors.length > 0) {
        this.$Alert.alert({ type: 'error', message: 'Please complete all the fields.' })
        return
      }

      if (this.registrationForm.field.password.value !== this.reenterPassword) {
        this.$Alert.alert({
          type: 'error',
          message: 'Please make sure password and re-entered password match.',
        })
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
