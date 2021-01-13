<template>
  <div class="register">
    <form @submit.prevent="handleSubmit">
      <h2>Create Account</h2>

      <div>
        <GoogleButton />
      </div>

      <div class="divider"></div>

      <!-- Show form-level errors -->
      <!-- TODO: Live-validate OR validate the form on submission -->
      <div class="errors"></div>
      <!-- END TODO -->
      <!-- End form-level errors -->

      <input v-model="email" type="text" placeholder="Your Email" />
      <input v-model="password" type="password" placeholder="Set a Password" />
      <input v-model="organizationName" type="text" placeholder="Company" />

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
import User from '@/services/users'

import GoogleButton from '@/components/GoogleButton'

export default {
  name: 'Register',
  components: {
    GoogleButton,
  },
  data() {
    return {
      email: '',
      password: '',
      organizationName: '',
    }
  },
  methods: {
    onSubmit() {},
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.register {
  display: flex;
  padding: 2rem;
  flex-flow: row;
  justify-content: center;
  max-width: 24rem;
  margin: 0 auto;
  background-color: white;
}

.divider {
  height: 1px;
  background-color: #aaa;
  width: 100%;
  margin: 1rem;
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
