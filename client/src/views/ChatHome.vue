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
      <div class="modal-container">
        <div class="modal-header">
          <p class="pointer" @click="handleCancel">x</p>
        </div>

        <div class="modal-body-top">
          <div class="profile-img">
            <img
              src="@/assets/images/profile.svg"
              style="filter: invert(80%)"
              height="40px"
              alt=""
            />
            <h3 class="profile-name">{{ user.fullName }}</h3>
          </div>

          <div class="modal-row">
            <p>{{ user.organizationRef.name }}</p>
            <p>{{ user.timezone }}</p>
          </div>

          <div class="modal-nav-divider">
            <h4
              :class="profileOrTeam === 'profile' ? 'active' : ''"
              @click="profileOrTeam = 'profile'"
            >
              Profile
            </h4>
            <h4 :class="profileOrTeam === 'team' ? 'active' : ''" @click="profileOrTeam = 'team'">
              Team
            </h4>
          </div>
        </div>

        <div v-if="profileOrTeam === 'team'" class="modal-body">
          <div
            :class="{ graytone: !member.firstName && !member.first_name }"
            class="profile-row"
            v-for="member in usersInTeam"
            :key="member.id"
          >
            <font-awesome-icon @click="selectedOpp = null" icon="fa-solid fa-circle-user" />
            <p>
              {{ member.email }}
            </p>
            <p class="profile-level-p">{{ member.userLevel.toLowerCase() }}</p>
            <p>
              {{
                !member.firstName && !member.first_name
                  ? 'pending'
                  : member.isActive || member.is_active
                  ? 'registered'
                  : 'deactivated'
              }}
            </p>
          </div>
        </div>

        <div v-else-if="profileOrTeam === 'profile'" class="modal-body">
          <div class="profile-row">
            <font-awesome-icon @click="selectedOpp = null" icon="fa-solid fa-at" />

            <p class="full-width">{{ user.email }}</p>
          </div>

          <div class="profile-row">
            <font-awesome-icon @click="selectedOpp = null" icon="fa-solid fa-user-group" />
            <p class="full-width">{{ user.organizationRef.teamsRef[0].name }}</p>
          </div>
        </div>

        <div v-if="profileOrTeam === 'team'" class="modal-footer">
          <!-- <button v-if="user.isAdmin" class="invite_button" type="submit" @click="showChangeAdmin">
            Change Admin
          </button>
          <button v-if="user.isAdmin" class="invite_button" type="submit" @click="handleNewTeam">
            Create New Team
          </button> -->

          <button class="chat-button">
            <font-awesome-icon
              v-if="team.list.length >= numberOfAllowedUsers"
              icon="fa-solid fa-user-plus"
            />

            <font-awesome-icon v-else class="white-icon" icon="fa-solid fa-user-plus" />

            Add user
          </button>
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
    handleInvite() {
      console.log('handled')
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    usersInTeam() {
      console.log('this.team', this.team)
      return this.team.list.filter(
        (member) => member.team === this.user.team, //&& member.id !== this.user.id
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
  line-height: 1.5;
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
  display: flex;
  flex-direction: column;
  width: 475px;
  height: 600px;
  padding: 0 0.5rem 0 1rem;
  background-color: white;
  border-radius: 6px;
  overflow-y: scroll;
  overflow-x: hidden;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  font-size: 22px;
  color: $light-gray-blue;
  position: sticky;
  top: 0;

  p {
    margin: 0;
    padding: 0;
    margin: 0.25rem 0.25rem 0 0;
  }
}

.modal-body-top {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding-right: 0.5rem;
  position: sticky;
}

.modal-body {
  margin-top: 2rem;
  height: 230px;
  overflow-y: scroll;
}

.modal-footer {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: absolute;
  bottom: 0;
  width: 95%;
  padding-bottom: 0.75rem;
}

.modal-nav-divider {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  margin-top: 1rem;

  h4 {
    padding-top: 0;
    margin: 0;
    cursor: pointer;
    margin-right: 1rem;
    font-size: 14px;
    color: $light-gray-blue;
  }
}
.profile-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  font-size: 14px;
  margin-bottom: 8px;
  height: 30px;

  p {
    margin-right: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  p:first-of-type {
    width: 160px;
  }

  svg {
    color: $light-gray-blue;
    margin-right: 1rem;
    background-color: $grape;
    height: 13px;
    width: 13px;
    padding: 0.3rem;
    border-radius: 6px;
    margin-left: 1px;
  }
}
.full-width {
  width: 300px !important;
}
.profile-level-p {
  width: 60px;
}
.modal-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-size: 14px;

  p:first-of-type {
    margin-right: 0.5rem;
    color: $dark-green;
  }
  p:last-of-type {
    margin-right: 0.5rem;
    color: $light-gray-blue;
  }
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
  height: 120px;
  width: 120px;
}
.profile-name {
  position: absolute;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
  top: 88px;
  background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  font-size: 12px;
}
.bottom {
  position: relative;
  bottom: 0;
  margin-bottom: 1rem;
}
.active {
  color: $base-gray !important;
  border-bottom: 2px solid $base-gray;
}

.pointer {
  cursor: pointer;
}
.graytone {
  filter: grayscale(60%);
  color: $light-gray-blue;
}
.white-icon {
  background-color: white !important;
  border: 1px solid rgba(0, 0, 0, 0.1);
  height: 12px;
  width: 12px;
  padding: 0.3rem;
  border-radius: 6px;
}
.margin-bottom-s {
  margin-bottom: 0.5rem;
}

.chat-button {
  @include chat-button();
  padding: 0.5rem;
  svg {
    margin-right: 0.75rem;
    height: 14px;
    width: 14px;
    color: $base-gray;
  }
  font-size: 14px;
}
</style>
