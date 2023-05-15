<template>
  <div :class="{ background: showBackground }" id="chat">
    <Modal
      v-if="profileModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleCancel()
        }
      "
    >
      <div class="modal-container flex-col" style="justify-content: space-between;">
        <div class="modal-header">
          <div></div>
          <div style="display: flex; justify-content: space-between; width: 50%;">
            <h4 class="pointer" :class="profileOrTeam === 'profile' ? 'active' : ''" @click="profileOrTeam = 'profile'">Profile</h4>
            <h4 class="pointer" :class="profileOrTeam === 'team' ? 'active' : ''" @click="profileOrTeam = 'team'">Team</h4>
          </div>
          <div class="pointer" @click="handleCancel"></div>
        </div>
        <div v-if="profileOrTeam === 'profile'" class="modal-body flex-col" style="height: 60vh;">
          <div class="profile-img">
            <img src="@/assets/images/profile.svg" style="filter: invert(80%)" height="40px" alt="" />
          </div>
          <h3 style="margin-bottom: 2rem;">{{ user.fullName }}</h3>
          <h3>Organization:</h3>
          <h4 style="margin-bottom: 0.5rem;">{{ user.organizationRef.name }}</h4>
          <h3>Timezone:</h3>
          <h4 style="margin-bottom: 0.5rem;">{{ user.timezone }}</h4>
        </div>
        <div v-else-if="profileOrTeam === 'team'" class="modal-body flex-col">
          <div class="options__section">
            <button v-if="user.isAdmin" class="invite_button" type="submit" @click="showChangeAdmin">
              Change Admin
            </button>
            <button v-if="user.isAdmin" class="invite_button" type="submit" @click="handleNewTeam">
              Create New Team
            </button>

            <div class="tooltip">
              <button
                :disabled="team.list.length >= numberOfAllowedUsers"
                class="invite_button"
                type="submit"
                @click="handleInvite"
              >
                Invite Member

                <div v-if="team.list.length >= numberOfAllowedUsers">
                  <img
                    v-if="hasSlack"
                    style="height: 0.8rem; margin-left: 0.25rem"
                    src="@/assets/images/lock.svg"
                    alt=""
                  />
                </div>

                <div v-else>
                  <img
                    v-if="hasSlack"
                    style="height: 0.8rem; margin-left: 0.25rem"
                    src="@/assets/images/slackLogo.png"
                    alt=""
                  />
                  <img
                    v-else
                    style="height: 0.8rem; margin-left: 0.25rem"
                    src="@/assets/images/logo.png"
                    alt=""
                  />
                </div>
              </button>
              <small v-if="team.list.length >= numberOfAllowedUsers" class="tooltiptext"
                >User limit exceeded: {{ numberOfAllowedUsers }}</small
              >
            </div>
          </div>
          <div style="height: 50vh; justify-content: center; overflow-y: auto;">
            <div class="display-flex-team" style="margin-bottom: 0.5rem;">
              <div class="team-item__title">User</div>
              <div class="team-item__title">User Level</div>
              <div class="team-item__title">Status</div>
            </div>
            <div class="display-flex-team" v-for="member in usersInTeam" :key="member.id" @click="test(member)">
              <div class="team-item">{{ member.fullName.trim() ? member.fullName : member.email }}</div>
              <div class="team-item">{{ member.userLevel }}</div>
              <div class="team-item">{{ (!member.firstName && !member.first_name) ? 'Pending...' : (member.isActive || member.is_active) ? 'Registered' : 'Deactivated' }}</div>
            </div>
          </div>
        </div>
        <div style="display: flex; justify-content: space-around; align-items: flex-end; width: 25.5vw; margin-bottom: 1rem;">
          <div class="pointer" @click="logOut">
            <h4 style="margin: 0;">Log Out <img src="@/assets/images/logout.svg" alt="" height="13px" style="margin-left: 0.5rem;" /></h4>
          </div>
          <div class="pointer" @click="handleCancel">
            <h4 style="margin: 0;">Close</h4>
          </div>
        </div>
      </div>
    </Modal>
    <div @click="toggleSidebar" class="hamburger">
      <font-awesome-icon style="height: 22px; width: 22px" icon="fa-solid fa-bars" />
    </div>
    <aside id="left-sidebar">
      <LeftSideBar
        ref="sidebarRef"
        @show-background="toggleBackgroundOn"
        @hide-background="toggleBackgroundOff"
        :handleProfileOpen="handleProfileOpen"
      />
    </aside>
    <main id="main">
      <ChatBox />
    </main>
    <aside id="right-sidebar">
      <RightBar />
    </aside>
  </div>
</template>

<script>
import ChatBox from '../components/Chat/ChatBox.vue'
import RightBar from '../components/Chat/RightBar.vue'
import LeftSideBar from '../components/Chat/LeftSideBar.vue'
import Modal from '@/components/InviteModal'

import CollectionManager from '@/services/collectionManager'
import User from '@/services/users'

export default {
  name: 'Home',
  components: {
    ChatBox,
    RightBar,
    LeftSideBar,
    Modal,
  },
  data() {
    return {
      showBackground: false,
      profileModalOpen: false,
      profileOrTeam: 'profile',
      team: CollectionManager.create({ ModelClass: User }),
    }
  },
  created() {
    this.team.refresh()
  },
  watch: {},
  methods: {
    test(log) {
      console.log('log', log)
    },
    toggleSidebar() {
      this.$refs.sidebarRef.toggleSidebar()
    },
    toggleBackgroundOn() {
      this.showBackground = true
    },
    toggleBackgroundOff() {
      this.showBackground = false
    },
    handleProfileOpen() {
      this.profileModalOpen = true
    },
    handleCancel() {
      this.profileModalOpen = false
    },
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
      localStorage.isLoggedOut = true
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    usersInTeam() {
      console.log('this.team', this.team)
      return this.team.list.filter(
        (member) =>
          member.team === this.user.team //&& member.id !== this.user.id 
      )
    },
    hasSlack() {
      return !!this.$store.state.user.slackRef
    },
    numberOfAllowedUsers() {
      return this.$store.state.user.organizationRef.numberOfAllowedUsers
    },
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
@import '@/styles/modals';

body {
  overflow: auto;
  margin: 0;
  height: 100vh;
  width: 100vw;
  background-color: $off-white;
}

.chat-display {
  display: flex;
}

#chat {
  height: 100vh;
  width: 100vw;
  display: flex;
  font-family: $base-font-family;
  color: $chat-font-color;
  letter-spacing: 0.4px;
}

.hamburger {
  display: none;
  height: 50px;
  width: 50px;
  position: fixed;
  top: 1rem;
  left: 1.5rem;
  cursor: pointer;
}

#left-sidebar {
  width: 260px;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
}
#main {
  flex: 1;
  width: 54vw;
  background-color: $off-white;
  z-index: 5;
}

#right-sidebar {
  width: 400px;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
}

@media (max-width: 1000px) {
  #chat {
    flex-direction: column;
    padding-top: 2rem;
  }

  .hamburger {
    display: block;
  }

  #left-sidebar {
    position: absolute;
    /* styles for mobile sidebar */
  }

  #main {
    order: 2;
    width: 100%;
    height: 75%;
  }

  #right-sidebar {
    width: 100%;
    height: 40%;
    order: 1;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    /* styles for mobile "right / top bar" */
  }
}

@media (min-width: 1000px) {
  .background {
    background-color: transparent !important;
  }

  .background::after {
    position: relative;
    background-color: transparent !important;
  }
}

.background {
  position: relative;
}

.background::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5); /* Adjust the opacity by modifying the last value */
  pointer-events: none; /* Allow click events to pass through to the children */
  z-index: 100; /* Ensure the overlay appears above the children */
}

.modal-container {
  @include medium-modal();
  width: 30vw;
  padding: 24px 24px 8px 24px;
  margin-top: 5rem;
  // border: 1px solid #e8e8e8;
  h3 {
    margin: 0.5rem 0;
  }
  h4 {
    margin: 0;
  }
}
.flex-col {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.modal-header {
  display: flex; 
  justify-content: space-between; 
  width: 100%; 
  align-items: flex-start;
}
.pointer {
  cursor: pointer;
}
.profile-img {
  margin-top: 1rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: $off-white;
  border: 1px solid $soft-gray;
  border-radius: 100%;
  height: 19vh;
  width: 19vh;
}
.bottom {
  position: relative;
  bottom: 0;
  margin-bottom: 1rem;
}
.active {
  text-decoration: underline;
  color: $dark-green;
}
.display-flex-team {
  display: flex;
  // justify-content: space-between;
  align-items: center;
  margin: 0 auto;
  // width: 25vw;
}
.team-item {
  width: 8vw;
  margin-bottom: 0.25rem;
  // overflow-x: auto;
  word-wrap: break-word;
  text-align: center;
  &__title {
    width: 8vw;
    text-decoration: underline;
    text-align: center;
  }
}
.options {
  // border: 1px solid $soft-gray;
  top: 10vh;
  left: 20vw;
  padding: 16px 8px 8px 8px;
  border-radius: 6px;
  background-color: white;
  z-index: 20;
  box-shadow: 1px 1px 2px 1px $very-light-gray;
  font-size: 14px;
  letter-spacing: 0.75px;

  p {
    padding: 4px !important;
    margin-bottom: 6px !important;
    width: 100%;
    display: flex;
    align-items: flex-start;
  }
  p:hover {
    background-color: $off-white;
    color: $dark-green;
    border-radius: 6px;
    cursor: pointer;
  }

  &__section {
    margin: 0px 8px 8px -8px;
    padding: 8px 8px 8px 0px;
    display: flex;
    flex-direction: row;
    align-items: center;
  }
}
.invite_button {
  @include gray-text-button();
  display: flex;
  flex-direction: row;
  padding: 8px 12px;
  margin-left: 8px;
}
.tooltip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2px 0px;
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white !important;
  text-align: center;
  border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 4px 0px;
  border-radius: 6px;
  font-size: 13px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 160px;
  top: 60%;
  left: 38%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
</style>
