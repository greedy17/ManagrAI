<template>
  <div class="invite-users">
    <h2>Build Your Team</h2>
    <div class="invite-users__text">
      Invite your team sales representatives to join your team
    </div>

    <button type="submit" @click="handleInvite">Invite Team Member</button>
    <Invite class="invite-users__inviter" :inviteOpen="inviteOpen" @cancel="handleCancel" />
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.invite-users {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background-color: transparent;
  &__logo {
    height: 5rem;
  }

  &__text {
    font-family: #{$base-font-family};
    width: 100%;

    margin-bottom: 2rem;
  }

  &__input {
    @include input-field-white();
  }

  &__inviter {
    margin-top: 5rem;
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

button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 2.25rem;
  border-radius: 3px;
  width: 10rem;
  font-size: 0.75rem;
}

.hidden {
  display: none;
}
</style>
