<template>
  <div class="password-reset">
    <header>
      <img class="blue-filter" src="@/assets/images/logo.png" height="36px" alt="" />
      <div class="header">
        <small>Sign In</small>
        <router-link class="secondary-button" :to="{ name: 'Login' }">Back to login</router-link>
      </div>
    </header>
    <form @submit.prevent="handleSubmit">
      <h2>Forgot Password ?</h2>
      <p class="password-reset__title">Enter your email address & we'll send you a reset link.</p>

      <input v-model="email" type="text" placeholder="Email" />

      <button :disabled="!email" type="submit">Send Link</button>
    </form>

    <div></div>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'ForgotPassword',
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
          this.$toast('Please check your email for instructions on how to reset password', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.$router.push({ name: 'Login' })
        })
        .catch((error) => {
          this.$toast('There was an error please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
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
  padding: 0 32px 32px 32px;
  height: 100vh;
  font-family: $thin-font-family;
  font-weight: 400;
  color: $dark-black-blue;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
}

.secondary-button {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  background-color: white;
  padding: 8px 16px;
  img {
    filter: invert(25%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

h2,
p {
  font-family: $thin-font-family;
  padding: 0;
  margin: 0;
  font-weight: 400;
}
a {
  text-decoration: none;
  color: $off-gray;
  font-size: 13px;
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
  font-family: $thin-font-family;
  display: block;
  margin: 0;
  border: 1px solid #e8e8e8;
}

button {
  @include dark-blue-button();
  padding: 10px 16px;
  border: none;
  font-size: 14px;
  font-family: $thin-font-family;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.row {
  display: flex;
  align-items: center;
  justify-content: center;
}

input {
  outline: none;
  width: 100%;
}

.blue-filter {
  filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
    contrast(90%);
}

.header {
  display: flex;
  flex-direction: row;
  align-items: center;
  small {
    margin-right: 16px;
  }
}
header {
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  font-family: $thin-font-family;
  font-size: 16px;
  padding-top: 12px;
}
</style>
