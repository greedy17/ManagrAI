<template>
  <div class="invite-users">
    <div v-if="getUser.userLevel === 'MANAGER'" class="invite-users__header">
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

    <Invite
      v-if="getUser.userLevel === 'MANAGER' || isAdmin"
      class="invite-users__inviter"
      :inviteOpen="inviteOpen"
      @cancel="handleCancel"
    />

    <section>
      <header class="invite-users__header">
        <h3 style="color: #4d4e4c">Update your Info</h3>

        <button class="invite_button" type="submit" @click="handleUpdate">
          Update
          <img style="height: 0.8rem; margin-left: 0.25rem" src="@/assets/images/logo.png" alt="" />
        </button>
      </header>

      <form class="update-container">
        <input
          v-model="profileForm.field.firstName.value"
          placeholder="First Name"
          :errors="profileForm.field.firstName.errors"
          id="user-input"
        />
        <input
          v-model="profileForm.field.lastName.value"
          placeholder="Last Name"
          :errors="profileForm.field.lastName.errors"
          id="user-input"
        />

        <Multiselect
          placeholder="Select Timezone"
          style="width: 16rem"
          v-model="selectedTimezone"
          @input="setTime"
          :options="timezones"
          openDirection="below"
          selectLabel="Enter"
          label="key"
          track-by="value"
        />
      </form>
    </section>
  </div>
</template>

<script>
import Invite from '../settings/_pages/_Invite'
import User from '@/services/users'
import { UserProfileForm } from '@/services/users/forms'
import moment from 'moment-timezone'

export default {
  name: 'InviteUsers',
  components: { Invite, Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect') },
  data() {
    return {
      inviteOpen: false,
      selectedTimezone: null,
      user: this.getUser,
      timezones: moment.tz.names(),
      profileForm: new UserProfileForm({}),
      loading: false,
    }
  },
  methods: {
    setTime() {
      this.profileForm.field.timezone.value = this.selectedTimezone.value
    },
    handleInvite() {
      this.inviteOpen = !this.inviteOpen
    },
    handleCancel() {
      this.inviteOpen = false
    },
    handleUpdate() {
      this.loading = true
      User.api
        .update(this.getUser.id, this.profileForm.value)
        .then((response) => {
          this.$Alert.alert({
            message: 'Successfully Updated Profile info',
            type: 'success',
            timeout: 2000,
          })
          this.$store.dispatch('updateUser', User.fromAPI(response.data))

          this.resetProfileForm()
        })
        .catch((e) => {
          console.log(e)
          this.resetProfileForm()
        })
    },
    resetProfileForm() {
      this.profileForm.firstName = this.getUser.firstName
      this.profileForm.lastName = this.getUser.lastName
      this.profileForm.timezone = this.getUser.timezone
      this.loading = false
    },
  },
  async created() {
    this.profileForm = new UserProfileForm({
      firstName: this.getUser.firstName,
      lastName: this.getUser.lastName,
      timezone: this.getUser.timezone,
    })
    this.timezones = this.timezones.map((tz) => {
      return { key: tz, value: tz }
    })
  },
  computed: {
    getUser() {
      return this.$store.state.user
    },
    isAdmin() {
      return this.$store.state.user.isAdmin
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.update-container {
  background-color: $white;
  border: 1px solid #e8e8e8;
  color: $base-gray;
  width: 60vw;
  height: 40vh;
  overflow: scroll;
  padding: 1.5rem 0rem 1.5rem 1rem;
  border-radius: 5px;
  display: flex;
  align-items: flex-start;
  flex-direction: column;
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 16rem;
  margin-bottom: 1rem;
  font-family: $base-font-family;
}
#user-input:focus {
  outline: none;
}
.invite-users {
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  margin-top: 4rem;
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 60vw;
    padding: 0.25rem;
  }

  &__inviter {
    margin-top: 2rem;
  }
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  text-align: center;
  font-size: 20px;
  margin-bottom: 2rem;
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

.invite_button:hover {
  cursor: pointer;
  transform: scale(1.025);
  box-shadow: 1px 2px 3px #e8e8e8;
}
</style>
