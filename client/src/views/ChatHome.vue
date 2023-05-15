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
            <h4 class="pointer" @click="profileOrTeam = 'profile'">Profile</h4>
            <h4 class="pointer" @click="profileOrTeam = 'team'">Team</h4>
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
          <div>Team</div>
        </div>
        <div style="display: flex; justify-content: space-around; align-items: flex-end; width: 40vw;">
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
    }
  },
  created() {},
  watch: {},
  methods: {
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
</style>
