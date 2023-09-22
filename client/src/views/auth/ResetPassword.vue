<template>
  <div class="password-reset">
    <form @submit.prevent="handleSubmit">
      <h2>Enter and confirm a new password</h2>

      <input v-model="password" type="password" placeholder="New Password" />
      <input v-model="confirmPassword" type="password" placeholder="Confirm Password" />

      <button type="submit">Reset Password</button>
      <!-- <div style="margin-top: 1rem">
        <router-link :to="{ name: 'Login' }"> Back to login </router-link>
      </div> -->
    </form>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'ResetPassword',
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
        this.$toast('Please enter a new password', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.loading = false
        return
      }

      if (this.password !== this.confirmPassword) {
        this.$toast('Please make sure your passwords match', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.loading = false
        return
      }

      await User.api
        .resetPassword(this.password, userId, token)
        .then((res) => {
          this.$toast('Successfully reset password', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })

          this.$router.push({
            name: 'Login',
          })
        })
        .catch((e) => {
          this.$toast('Error. please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        })
        .finally((e) => {
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
  align-items: center;
  justify-content: center;
  background-color: $offer-white;
  height: 94vh;
}

h2,
p {
  font-family: $thin-font-family;
  padding: 0;
  margin: 0;
  font-weight: 400;
}

form {
  @include standard-border();
  width: 500px;
  padding: 64px;
  display: flex;
  flex-flow: column;
  align-items: flex-start;
  justify-content: center;
  color: $dark-black-blue;
  background-color: $offer-white;
  border-radius: 4px;
  gap: 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
  font-weight: 400;
}

input {
  @include input-field();
  height: 2.5rem;
  width: 100%;
  display: block;

  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;

  outline: none;

  &:disabled {
    border: 2px solid $dark-green;
  }
}

button {
  @include dark-blue-button();
}
</style>
