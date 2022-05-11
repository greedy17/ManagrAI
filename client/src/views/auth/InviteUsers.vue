<template>
  <div class="invite-users">
    <div class="invite-users__header">
      <h3 style="color: #4d4e4c">Manage Your Team</h3>

      <button class="invite_button" type="submit" @click="handleInvite">
        Invite Member
        <img
          style="height: 0.8rem; margin-left: 0.25rem"
          src="@/assets/images/slackLogo.png"
          alt=""
        />
      </button>
    </div>

    <Invite class="invite-users__inviter" :inviteOpen="inviteOpen" @cancel="handleCancel" />
  </div>
</template>

<script>
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
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 60vw;
    padding: 0.25rem;
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
  color: $dark-green;
  background-color: white;
  border-radius: 0.25rem;
  transition: all 0.25s;
  padding: 0.75rem;
  font-weight: bolder;
  font-size: 14px;
  border: 1px solid #e8e8e8;
}

.invite_button:hover,
.continue_button:hover {
  cursor: pointer;
  transform: scale(1.025);
  box-shadow: 1px 2px 3px #e8e8e8;
}
</style>
