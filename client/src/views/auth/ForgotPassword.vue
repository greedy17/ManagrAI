<template>
  <div class="password-reset">
    <form @submit.prevent="handleSubmit">
      <h2 class="password-reset__title">
        Please enter your email address, and a link to reset your password will be sent to you
        shortly.
      </h2>

      <input v-model="email" type="text" placeholder="email" />

      <button type="submit">Send Link</button>
      <div style="margin-top: 1rem">
        <router-link :to="{ name: 'Login' }"> Back to login </router-link>
      </div>
    </form>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'ForgotPassword',
  components: {},
  data() {
    return {
      email: '', // step 1
    }
  },
  methods: {
    handleSubmit() {
      this.loading = true
      User.api
        .requestPasswordReset(this.email)
        .then((response) => {
          this.$Alert.alert({
            type: 'success',
            message: 'Please check your email for instructions on how to reset password',
            timeout: 2000,
          })

          this.$router.push({ name: 'Login' })
        })
        .catch((error) => {
          this.$Alert.alert({
            type: 'error',
            message: 'There was an error, please try again',
            timeout: 2000,
          })
        })
        .finally(() => {
          this.loading = false
        })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.password-reset {
  display: flex;
  flex-flow: row;
  justify-content: center;
  margin-top: 4rem;
  &__title {
    padding: 0 1rem 1rem 1rem;
  }
}

h2 {
  // @include base-font-styles();
  font-size: 16px;
  color: $base-gray;
  text-align: center;
}
a {
  text-decoration: none;
  color: $dark-green;
}
form {
  @include standard-border();
  margin-top: 3.125rem;
  width: 31.25rem;

  background-color: $white;
  display: flex;
  flex-flow: column;
  align-items: center;
  padding: 2rem;
}

input {
  @include input-field();
  height: 2.5rem;
  width: 15.65rem;
  display: block;
  margin: 0.625rem 0;
  border: 1px solid #e8e8e8;

  &:disabled {
    border: 2px solid $dark-green;
  }
}

button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 1.875rem;
  width: 9.375rem;
  box-shadow: none;
}
</style>
