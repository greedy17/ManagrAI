<template>
  <div class="invite-users">
    <h2 style="font-size: 1.5rem; color: black">Build Your Team</h2>
    <div style="color: #5d5e5e" class="invite-users__text">
      Invite your team sales representatives to join you on Managr
    </div>

    <button class="invite_button" type="submit" @click="handleInvite">Invite Team Member</button>
    <Invite class="invite-users__inviter" :inviteOpen="inviteOpen" @cancel="handleCancel" />

    <!-- <button class="continue_button" type="submit" @click="handleContinue">Continue</button> -->
  </div>
</template>

<script>
import User from '@/services/users'
import Invite from '../settings/_pages/_Invite'

export default {
  name: 'InviteUsers',
  components: { Invite },
  data() {
    return {
      inviteOpen: false,
    }
  },
  methods: {
    handleInvite() {
      this.inviteOpen = !this.inviteOpen
    },
    handleCancel() {
      this.inviteOpen = false
    },
    handleContinue() {
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

.invite-users {
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  margin-top: 4rem;
  &__logo {
    height: 5rem;
  }

  &__text {
    font-family: #{$base-font-family};
    width: 100%;
    margin-top: -1rem;
    margin-bottom: 1.5rem;
  }

  &__input {
    @include input-field-white();
  }

  &__inviter {
    margin-top: 2rem;
  }

  &__continue-button {
    width: 19rem;
    margin-top: 3rem;
  }
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  text-align: center;
  font-size: 20px;
  margin-bottom: 2rem;
}

.input {
  &__container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
}

.hidden {
  display: none;
}

.invite_button {
  color: $white;
  background-color: $dark-green;
  width: 12.5vw;
  height: 6vh;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  border: none;
}

.continue_button {
  color: white;
  background-color: $panther-purple;
  width: 10vw;
  height: 5vh;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  border: none;
  margin-top: 2rem;
}

.invite_button:hover,
.continue_button:hover {
  cursor: pointer;
}
</style>
