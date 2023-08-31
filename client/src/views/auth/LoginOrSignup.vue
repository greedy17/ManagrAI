<template>
  <div class="login-signup-page">
    <header>
      <img class="blue-filter" src="@/assets/images/logo.png" height="36px" alt="" />

      <div class="header">
        <small>Welcome!</small>
      </div>
    </header>

    <div class="column">
      <div class="column">
        <h1>Welcome to Managr</h1>
        <h4>Log in with your Managr account to continue</h4>
      </div>

      <div class="row">
        <button class="primary-button" @click="goToLogin">Log In</button>
        <button class="secondary-button" @click="goToRegister">Sign Up</button>
      </div>

      <div class="links">
        <p class="t-c">
          <a href="https://managr.ai/terms-of-service" target="_blank">Terms of Service</a>
          |
          <a href="https://managr.ai/documentation" target="_blank">Documentation</a>
          |
          <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
        </p>
      </div>
    </div>

    <div></div>
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

.primary-button {
  @include dark-blue-button();
  text-align: center;
  width: 100px;
  padding: 8px;
  box-shadow: none;

  &:disabled {
    background-color: $off-white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    opacity: 0.7;
  }
}

.secondary-button {
  @include dark-blue-button();
  background-color: white;
  text-align: center;
  width: 100px;
  padding: 8px;
  box-shadow: none;
  color: $dark-black-blue;

  &:disabled {
    background-color: $off-white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    opacity: 0.7;
  }
}

h1 {
  margin: 0;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.column {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  margin-top: -32px;
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

.links {
  font-size: 13px;
  font-family: $thin-font-family;
}

.t-c {
  a {
    margin: 0 16px;
  }
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
.blue-filter {
  filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
    contrast(90%);
}
</style>