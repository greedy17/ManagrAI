<template>
  <div class="login-signup-page">
    <div class="elements-container">
      <div>
        <img style="height: 66px" src="@/assets/images/logo.png" />
      </div>
      <div class="header">
        <h1>Welcome to Managr</h1>
        <h4>Log in with your Managr account to continue</h4>
      </div>
      <div class="display-flex space-around">
        <button class="button button-sizing" @click="goToLogin">Log In</button>
        <button class="second-button button-sizing" @click="goToRegister">Sign Up</button>
      </div>
      <div class="links">
        <p style="color: #4d4e4c">
          <a href="https://managr.ai/terms-of-service" target="_blank">Term of Service</a>
          |
          <a href="https://managr.ai/documentation" target="_blank">Documentation</a>
          |
          <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginOrSignup',
  data() {
    return {}
  },
  methods: {
    goToRegister() {
      this.$router.push({ name: 'RegisterSelection' })
    },
    goToLogin() {
      this.$router.push({ name: 'Login' })
    },
  },
  created() {
    this.$store.dispatch('updateGoogleSignIn', {})
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.login-signup-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.elements-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.display-flex {
  display: flex;
}
.space-around {
  width: 60%;
  justify-content: space-around;
}
.header {
  text-align: center;
}
.button {
  @include primary-button;
}
.second-button {
  @include gray-text-button;
  color: $dark-green;
}
.links {
  font-size: 13px;
  margin: 3rem;
  position: absolute;
  bottom: 0;
}
a {
  text-decoration: none;
  color: $light-gray-blue;
}
.button-sizing {
  // font-size: 16px;
  font-size: 13px;
  padding: 0.55rem 1.2rem;
}
</style>