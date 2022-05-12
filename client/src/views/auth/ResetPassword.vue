<template>
  <div class="password-reset">
    <form @submit.prevent="handleSubmit">
      <h2 class="password-reset__title">
        Enter and confirm a new password below.
      </h2>

      <input v-model="password" type="password" placeholder="New Password" />
      <input v-model="confirmPassword" type="password" placeholder="Confirm Password" />

      <button type="submit">Reset Password</button>
      <div style="margin-top: 1rem">
        <router-link :to="{ name: 'Login' }">
          Back to login
        </router-link>
      </div>
    </form>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'ResetPassword',
  components: {},
  data() {
    return {
      password: '',
      confirmPassword: '',
    }
  },
  methods: {
    async handleSubmit() {
      this.loading = true

      const userId = this.$route.params.userId
      const token = this.$route.params.token

      if (!this.password.length || !this.confirmPassword.length) {
        this.$Alert.alert({
          type: 'error',
          message: 'Please enter a new password',
          timeout: 2000,
        })
        this.loading = false
        return
      }

      if (this.password !== this.confirmPassword) {
        this.$Alert.alert({
          type: 'error',
          message: 'Please make sure you passwords match',
          timeout: 2000,
        })
        this.loading = false
        return
      }

      await User.api
        .resetPassword(this.password, userId, token)
        .then(res => {
          this.$Alert.alert({
            type: 'success',
            message: `Successfully Reset Password`,
            timeout: 5000,
          })

          this.$router.push({
            name: 'Login',
          })
        })
        .catch(e => {
          this.$Alert.alert({
            type: 'error',
            message: `There was an error, please try again later`,
            timeout: 5000,
          })
        })
        .finally(e => {
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

  &__title {
    padding: 0 1rem 1rem 1rem;
  }
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  color: $main-font-gray;
  text-align: center;
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

  &:disabled {
    border: 2px solid $dark-green;
  }
}

button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 1.875rem;
  min-width: 12rem;
}
</style>
