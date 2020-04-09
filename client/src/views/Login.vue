<template>
  <div class="login">
    <NavBar />
    <div class="page-content">
      <form @submit.prevent="handleLogin">
        <h2>Login</h2>
        <div class="errors">
          <div v-if="valid !== null && !valid">Fields may not be blank.</div>
          <div v-else-if="success !== null && !success">Invalid email and/or password.</div>
          <div v-else class="hidden">Placeholder</div>
        </div>
        <input v-model="email" type="text" placeholder="email" />
        <input v-model="password" type="password" placeholder="password" />
        <button type="submit">Login</button>
      </form>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'Login',
  components: {},
  data() {
    return {
      email: '',
      password: '',
      valid: null, // client side validations
      success: null, //server side validations
    }
  },
  methods: {
    handleLogin() {
      this.success = null
      this.valid = this.clientSideValidations()
      if (!this.valid) {
        return
      }

      let loginPromise = User.api.login(this.email, this.password)

      loginPromise
        .then(response => {
          // TODO(Bruno 4-9-20):
          // there are checks that must take place before deciding
          // if this person can be logged in
          // the following is temporary code
          let token = response.data.token
          let user = response.data
          delete user.token
          this.$store.dispatch('updateUserToken', token)
          this.$store.dispatch('updateUser', user)
          this.$router.push({ name: 'LeadsIndex' })
          this.success = true
        })
        .catch(() => {
          this.success = false
        })
    },
    clientSideValidations() {
      return this.emailIsBlank || this.passwordIsBlank ? false : true
    },
  },
  computed: {
    emailIsBlank() {
      return !this.email.length
    },
    passwordIsBlank() {
      return !this.password.length
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';

.login {
  height: inherit;
  display: flex;
  flex-flow: column;
  background-color: $off-white;
}

.page-content {
  overflow-x: scroll;
  flex-grow: 1;
  display: flex;
  flex-flow: row;
  justify-content: center;
}

h2 {
  font-family: $base-font-family, $backup-base-font-family;
  color: $main-font-gray;
  text-align: center;
}

.hidden {
  visibility: hidden;
}

form {
  margin-top: 50px;
  width: 500px;
  height: 300px;
  background-color: white;
  border-radius: 5px;
  display: flex;
  flex-flow: column;
  align-items: center;
}

input {
  @include input-field();
  height: 40px;
  width: 250px;
  display: block;
  margin: 10px 0;
}

button {
  margin-top: 20px;
  height: 30px;
  width: 150px;
  border-radius: 5px;
  background-color: $dark-green;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #ffffff;

  &:hover {
    cursor: pointer;
  }
}
</style>
