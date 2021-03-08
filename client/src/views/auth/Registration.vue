<template>
  <div class="registration">
    <img class="registration__logo" src="@/assets/images/logo.png" />
    <h2>Welcome</h2>

    <div class="registration__text">
      Please enter your Leadership code provided by the managr team.
    </div>
    <form @submit.prevent="onSubmit">
      <h2>Create Account</h2>

      <div>
        <GoogleButton />
      </div>

      <div class="divider"></div>

      <input v-model="registrationForm.field.fullName.value" type="text" placeholder="Your Name" />
      <input v-model="registrationForm.field.email.value" type="text" placeholder="Your Email" />
      <input
        v-model="registrationForm.field.password.value"
        type="password"
        placeholder="Set a Password"
      />
      <input
        v-model="registrationForm.field.organizationName.value"
        type="text"
        placeholder="Company"
      />

      <div style="margin-top: 0.5rem;">
        <TNDropdown
          :options="User.roles.ROLE_CHOICES"
          placeholder="Your Role"
          @selected="onSelectRole"
        />
      </div>

      <!-- TODO: Use LoadingSpinnerButton and indicate when working -->
      <button type="submit">Submit</button>
      <!-- END TODO -->

      <div style="margin-top: 1rem">
        <router-link :to="{ name: 'Login' }">
          Have an account? Sign In
        </router-link>
      </div>
    </form>
  </div>
</template>

<script>
import User, { UserRegistrationForm } from '@/services/users'

import GoogleButton from '@/components/GoogleButton'
import TNDropdown from '@/components/TNDropdown'

export default {
  name: 'Register',
  components: {
    GoogleButton,
    TNDropdown,
  },
  data() {
    return {
      User,
      submitting: false,
      registrationForm: new UserRegistrationForm(),
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
  background-color: white;
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

form {
  background-color: $white;
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
