<template>
  <div :class="{ background: showBackground }" id="chat">
    <Modal
      v-if="chatModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), toggleChatModal()
        }
      "
    >
      <div class="chat-modal-container">
        <div class="chat-modal-header">
          <div>
            <h3 @click="test" class="elipsis-text" style="margin-bottom: 0.25rem">
              {{ chatData.resource }}
            </h3>
            <span class="gray-text smaller"
              >Your CRM fields have been auto-filled. Pleae review and click submit.</span
            >
          </div>

          <h4 v-if="!submitting" @click="toggleChatModal" style="cursor: pointer">x</h4>
          <img
            v-else
            class="spinning-load"
            src="@/assets/images/refresh.svg"
            height="18px"
            alt=""
          />
        </div>

        <div
          :class="{ disabled: submitting }"
          class="chat-body"
          v-for="(field, i) in formFields"
          :key="i"
        >
          <ChatFormField
            :placeholder="chatData.data[field.apiName]"
            :field="field"
            :resourceId="chatData.resourceId"
            :integrationId="chatData.integrationId"
            :chatData="chatData.data"
            @set-value="setUpdateValues"
            :stageFields="stageFields"
            :stagesWithForms="stagesWithForms"
          />
        </div>

        <div class="chat-modal-footer">
          <button :disabled="submitting" @click="toggleChatModal">Close</button>
          <button :disabled="submitting" @click="onSubmitChat">Submit</button>
        </div>
      </div>
    </Modal>
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
            <p>{{ user.organizationRef.name }} -</p>
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

          <div class="profile-row">
            <font-awesome-icon @click="selectedOpp = null" icon="fa-solid fa-layer-group" />
            <p class="full-width">{{ user.userLevel.toLowerCase() }}</p>
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

    <main v-if="currentView === 'home'" id="main">
      <ChatBox @toggle-chat-modal="toggleChatModal" />
    </main>
    <main v-else-if="currentView === 'meetings'" id="main">
      <ChatMeetings
        @set-opp="setOpp"
        :formFields="formFields"
        :stageFields="stageFields"
        :stagesWithForms="stagesWithForms"
      />
    </main>
    <main id="main" v-else>
      <ChatList @set-opp="setOpp" :formFields="formFields" @refresh-list="refreshLists" />
    </main>

    <aside id="right-sidebar">
      <RightBar
        ref="rightSideBar"
        @set-fields="setFormFields"
        @set-stages="setStageFields"
        @refresh-list="refreshLists"
      />
    </aside>
  </div>
</template>

<script>
import ChatBox from '../components/Chat/ChatBox.vue'
import RightBar from '../components/Chat/RightBar.vue'
import LeftSideBar from '../components/Chat/LeftSideBar.vue'
import Modal from '@/components/InviteModal'
import ChatFormField from '../components/Chat/ChatFormField.vue'
import CollectionManager from '@/services/collectionManager'
import ChatList from '../components/Chat/ChatList.vue'
import ChatMeetings from '../components/Chat/ChatMeetings.vue'
import User from '@/services/users'
import { CRMObjects } from '@/services/crm'

export default {
  name: 'Home',
  components: {
    ChatBox,
    RightBar,
    LeftSideBar,
    Modal,
    ChatFormField,
    ChatList,
    ChatMeetings,
  },
  data() {
    return {
      showBackground: false,
      profileModalOpen: false,
      submitting: false,
      profileOrTeam: 'profile',
      team: CollectionManager.create({ ModelClass: User }),
      chatModalOpen: false,
      chatData: null,
      formFields: [],
      stageFields: [],
      barOpen: true,
      stagesWithForms: null,
    }
  },
  created() {
    this.team.refresh()
  },
  watch: {},
  methods: {
    refreshLists() {
      this.$refs.sidebarRef.refreshList()
    },
    setOpp(name) {
      this.$refs.rightSideBar.changeSelectedOpp(null, name)
    },
    toggleLeftbarOn() {
      this.barOpen = true
    },
    toggleLeftbarOff() {
      this.barOpen = false
    },
    setUpdateValues(key, val, multi) {
      if (multi) {
        this.chatData.data[key] = this.chatData.data[key]
          ? this.chatData.data[key] + ';' + val
          : val.split(/&#39;/g)[0]
      } else {
        this.chatData.data[key] = val
      }
    },
    removeEmptyValues(obj) {
      for (let key in obj) {
        console.log(!!obj.hasOwnProperty(key))
        if (obj.hasOwnProperty(key)) {
          if (obj[key] === null || obj[key] === undefined || obj[key] === '') {
            delete obj[key]
          }
        }
      }
      return obj
    },

    async onSubmitChat() {
      this.submitting = true
      try {
        const res = await CRMObjects.api.updateResource({
          form_data: this.chatData.data,
          resource_type: this.chatData.resourceType,
          form_type: this.chatData.formType,
          resource_id: this.chatData.resourceId,
          integration_ids: [this.chatData.integrationId],
          chat_form_id: [this.chatData.formId],
          from_workflow: false,
          workflow_title: 'None',
          stage_name: null,
        })
        this.$store.dispatch('messageUpdated', { id: this.chatData.id, data: this.chatData.data })
      } catch (e) {
        console.log(e)
      } finally {
        this.$refs.rightSideBar.reloadOpps()
        setTimeout(() => {
          this.toggleChatModal()
        }, 1000)

        setTimeout(() => {
          this.submitting = false
        }, 2000)
      }
    },
    test() {
      console.log(this.chatData.data)
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
      // localStorage.isLoggedOut = true
    },
    toggleChatModal(data) {
      this.chatModalOpen = !this.chatModalOpen
      if (data) {
        this.chatData = data
      }
    },
    setFormFields(fields) {
      this.formFields = fields
    },
    setStageFields(fields, stagesWithForms) {
      this.stageFields = fields
      this.stagesWithForms = stagesWithForms
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
    currentView() {
      return this.$store.state.currentView
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
}

#main {
  flex: 1;
  width: 54vw;
  background-color: white;
  z-index: 5;
}

.elipsis-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 450px;
}

#right-sidebar {
  width: 450px;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
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

.chat-modal-container {
  display: flex;
  flex-direction: column;
  width: 525px;
  height: 90vh;
  padding: 0 1.5rem;
  background-color: white;
  border-radius: 8px;
  overflow-y: scroll;
  position: relative;
}

.chat-modal-header {
  position: sticky;
  background-color: white;
  top: 0;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  padding-bottom: 0.5rem;
}

.chat-modal-footer {
  position: sticky;
  padding: 1rem 0;
  background-color: white;
  bottom: 0;
  z-index: 1000;
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
  // border-top: 1px solid $soft-gray;
  margin-top: 1rem;

  button {
    @include chat-button();
    padding: 0.5rem 1rem;
    margin-left: 1rem;
    font-size: 12px;
  }

  button:last-of-type {
    background-color: $dark-green;
    color: white;
    border: none;
  }
}

.gray-text {
  color: $light-gray-blue;
}
.smaller {
  font-size: 12px;
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
  width: 260px !important;
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
    // color: $grape;
    font-weight: bold;
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
    margin-right: 1rem;
    height: 12px;
    width: 12px;
    color: $base-gray;
  }
  font-size: 14px;
}
.disabled {
  opacity: 0.5;
}
.spinning-load {
  animation: rotation 3s infinite linear;
  opacity: 0.3;
  cursor: not-allowed;
  margin-top: 1rem;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}
</style>
