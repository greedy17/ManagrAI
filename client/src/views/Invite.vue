<template>
  <div class="invite">
    <NavBar />
    <div class="page-content">
      <form @submit.prevent="handleInvite">
        <h2>Invite</h2>
        <input v-model="email" type="text" placeholder="email" />
        <button type="submit">Invite</button>
      </form>
    </div>
  </div>
</template>

<script>
// import User from '@/services/users'

export default {
  name: 'Invite',
  components: {},
  data() {
    return {
      email: '',
      type: 'MANAGER',
      organization: 'd94ae832-91cf-4e3b-84d1-42249ac7f0d4',
    }
  },
  methods: {
    handleInvite() {
      // let invitePromise = User.api.invite(this.email, this.type, this.organization)
      // TODO(Bruno 4-8-20): Work with the response once app is live in staging
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';

.invite {
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
  margin: 5px 0;
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
