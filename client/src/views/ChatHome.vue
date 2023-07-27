<template>
  <div :class="{ background: showBackground }" id="chat">
    <Modal
      v-if="inviteOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleInviteCancel()
        }
      "
    >
      <form
        v-if="hasSlack || (this.isAdmin && this.orgHasSlackIntegration)"
        class="invite-form form-height-small"
        @submit.prevent="handleInvite"
        style="margin-top: 7.5rem; height: 50vh"
      >
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Invite Slack Users</h3>
          </div>
          <div class="flex-row">
            <img
              @click="handleInviteCancel"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="filter: invert(30%); cursor: pointer"
            />
          </div>
        </div>

        <div
          style="display: flex; justify-content: center; flex-direction: column; margin-top: -3rem"
        >
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select Slack User"
                  @input="mapMember"
                  v-model="selectedMember"
                  :options="slackMembers.members"
                  openDirection="below"
                  style="width: 33vw; margin-bottom: 1rem"
                  selectLabel="Enter"
                  track-by="id"
                  label="realName"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results. Try loading more</p>
                  </template>
                  <template slot="afterList">
                    <p class="multi-slot__more" @click="listUsers(slackMembers.nextCursor)">
                      Load More
                      <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                    </p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Slack User
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select User Level"
                  @input="mapUserLevel"
                  v-model="selectedLevel"
                  :options="userTypes"
                  openDirection="below"
                  style="width: 33vw; margin-bottom: 1rem"
                  selectLabel="Enter"
                  label="key"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select User Level
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
          <div
            v-if="user.isAdmin"
            style="display: flex; align-items: flex-start; flex-direction: column"
          >
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select Team"
                  @input="checkTeamLead"
                  v-model="selectedTeam"
                  :options="allTeams"
                  openDirection="below"
                  style="width: 33vw; margin-bottom: 1rem"
                  selectLabel="Enter"
                  :customLabel="customTeamLabel"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Team
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
          <div
            v-if="user.isAdmin"
            style="display: flex; align-items: flex-start; flex-direction: column"
          >
            <div style="display: flex; height: 1rem; margin-bottom: 2rem; margin-left: 0.25rem">
              <p style="margin: 0">Make Team Lead</p>
              <input
                v-model="selectedTeamLead"
                :disabled="!selectedTeam || user.team === selectedTeam.id"
                type="checkbox"
                style="height: 1rem; align-self: center; width: 2rem; margin-top: 0.5rem"
              />
            </div>
          </div>
        </div>
        <div class="invite-form__actions">
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="handleInvite"
                class="invite-button"
                style="width: 5rem; margin-right: 5%; height: 2rem; margin-top: 2rem"
                text="Invite"
                :loading="loading"
                >Invite</PulseLoadingSpinnerButton
              >
            </template>
          </div>
        </div>
      </form>
      <div v-else class="invite-form" style="padding: 2rem">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Invite Users to Managr</h3>
          </div>
        </div>

        <div style="margin-top: 1rem">
          <FormField>
            <template v-slot:input>
              <Multiselect
                placeholder="Select User Level"
                @input="mapUserLevel"
                v-model="selectedLevel"
                :options="userTypesNoSlack"
                openDirection="below"
                style="min-width: 16vw"
                selectLabel="Enter"
                label="key"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select User Level
                  </p>
                </template>
              </Multiselect>
            </template>
          </FormField>
          <div class="form_field">
            <input
              v-model="userInviteForm.field.email.value"
              placeholder="Enter User email"
              type="email"
            />
          </div>
        </div>

        <div class="invite-form__actions-noslack">
          <template>
            <PulseLoadingSpinnerButton
              v-if="!activationLink"
              @click="handleInviteNonSlack"
              class="invite-button"
              text="Invite"
              :loading="loading"
              >Invite</PulseLoadingSpinnerButton
            >
            <span style="margin-top: 1rem; cursor: pointer" v-else
              ><small
                v-clipboard:copy="activationLink"
                v-clipboard:success="onCopy"
                v-clipboard:error="onError"
                >{{ activationLink }}
                <img
                  src="@/assets/images/copy.svg"
                  height="18px"
                  style="margin-left: 0.5rem"
                  alt="" /></small
            ></span>
            <div v-if="!activationLink" class="cancel-button" @click="handleInviteCancel">
              Cancel
            </div>
            <small v-else class="copyText">Copy above link and send to user</small>
          </template>
        </div>

        <div v-if="activationLink">
          <button @click="handleInviteCancel" class="invite-button">Reset form</button>
        </div>
      </div>
    </Modal>
    <Modal
      v-if="configureModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleCancel()
        }
      "
    >
      <div class="configure-modal-container">
        <ConfigureModal
          :configPage="configPage"
          @change-config-page="changeConfigPage"
          ref="configModal"
        />
      </div>
    </Modal>
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
            <h3 class="elipsis-text" style="margin-bottom: 0.25rem">
              {{ formOpen ? currentOpp.name : chatData.resource }}
            </h3>
            <span v-if="!formOpen" class="gray-text smaller"
              >Your CRM fields have been auto-filled. Pleae review and click submit.</span
            >
            <span class="gray-text smaller" v-else> Update {{ currentOpp.name }} </span>
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
            :placeholder="toString(formData[field.apiName])"
            :field="field"
            :chatData="formOpen ? formData : chatData"
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

          <button class="chat-button" @click="handleInviteOpen">Add</button>
        </div>
      </div>
    </Modal>

    <div @click="toggleSidebar" class="hamburger">
      <font-awesome-icon style="height: 22px; width: 22px" icon="fa-solid fa-bars" />
    </div>
    <aside :class="{ closed: leftBarClosed }" id="left-sidebar">
      <LeftSideBar
        ref="sidebarRef"
        @show-background="toggleBackgroundOn"
        @hide-background="toggleBackgroundOff"
        @toggle-Left-bar="toggleLeftBar"
        :handleProfileOpen="handleProfileOpen"
        :handleConfigureOpen="handleConfigureOpen"
      />
    </aside>

    <main v-if="currentView === 'home'" id="main">
      <ChatBox
        ref="chatBox"
        @set-opp="setOpp"
        @set-view="setView"
        @set-open-form="setOpenForm"
        @toggle-chat-modal="toggleChatModal"
        @remove-opp="removeOpp"
      />
    </main>
    <!-- <main v-else-if="currentView === 'meetings'" id="main">
      <ChatMeetings
        @set-opp="setOpp"
        :formFields="formFields"
        :stageFields="stageFields"
        :stagesWithForms="stagesWithForms"
      />
    </main> -->
    <main id="main" v-else>
      <ChatList
        @set-opp="setOpp"
        @handleConfigureOpen="handleConfigureOpen"
        :formFields="formFields"
        @refresh-list="refreshLists"
        @open-change-config="openChangeConfig"
      />
    </main>
    <aside id="right-sidebar">
      <RightBar
        ref="rightSideBar"
        @set-fields="setFormFields"
        @set-stages="setStageFields"
        @refresh-list="refreshLists"
        @open-settings="handleConfigureOpen"
        :formFields="formFields"
        :stageFields="stageFields"
        :stagesWithForms="stagesWithForms"
      />
    </aside>
  </div>
</template>

<script>
import ChatBox from '../components/Chat/ChatBox.vue'
import RightBar from '../components/Chat/RightBar.vue'
import LeftSideBar from '../components/Chat/LeftSideBar.vue'
import ConfigureModal from '../components/Chat/Configure/ConfigureModal.vue'
import Modal from '@/components/InviteModal'
import ChatFormField from '../components/Chat/ChatFormField.vue'
import CollectionManager from '@/services/collectionManager'
import ChatList from '../components/Chat/ChatList.vue'
import ChatMeetings from '../components/Chat/ChatMeetings.vue'
import User from '@/services/users'
import { CRMObjects } from '@/services/crm'
import { decryptData } from '../encryption'
import { UserInviteForm } from '@/services/users/forms'
import Invite from '@/views/settings/_pages/_Invite'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import FormField from '@/components/forms/FormField'
import SlackOAuth, { SlackUserList } from '@/services/slack'
import Organization from '@/services/organizations'

export default {
  name: 'Home',
  components: {
    ChatBox,
    RightBar,
    LeftSideBar,
    ConfigureModal,
    Modal,
    ChatFormField,
    ChatList,
    ChatMeetings,
    Invite,
    PulseLoadingSpinnerButton,
    FormField,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      showBackground: false,
      profileModalOpen: false,
      configureModalOpen: false,
      configPage: 'integrations',
      submitting: false,
      profileOrTeam: 'profile',
      team: CollectionManager.create({ ModelClass: User }),
      chatModalOpen: false,
      chatData: null,
      formFields: [],
      stageFields: [],
      barOpen: true,
      leftBarClosed: false,
      stagesWithForms: null,
      formData: null,
      formOpen: false,
      inviteOpen: false,
      selectedTeam: null,
      selectedTeamLead: false,
      loading: false,
      selectedMember: null,
      selectedLevel: null,
      activationLink: null,
      allTeams: [],
      slackMembers: new SlackUserList(),
      userTypes: [
        { key: 'Manager', value: User.types.MANAGER },
        { key: 'Representative', value: User.types.REP },
        { key: 'SDR', value: User.types.SDR },
      ],
      userTypesNoSlack: [
        { key: 'Representative', value: User.types.REP },
        { key: 'SDR', value: User.types.SDR },
      ],
      userInviteForm: null,
    }
  },
  async created() {
    this.team = CollectionManager.create({ ModelClass: User })
    this.userInviteForm = new UserInviteForm({
      role: User.roleChoices[0].key,
      userLevel: User.types.REP,
      organization: this.user.organization,
    })
    if ((this.isAdmin && this.orgHasSlackIntegration) || this.hasSlack) {
      try {
        const allTeams = await Organization.api.listTeams(this.user.id)
        this.allTeams = allTeams.results
        if (this.user.isAdmin) {
          const userTeam = this.allTeams.filter((team) => team.id === this.user.team)
          this.selectedTeam = userTeam[0] ? userTeam[0] : null
        } else {
          const orgUsers = await User.api.getAllOrgUsers(this.user.organization)
          let admin = orgUsers.filter((user) => user.is_admin)[0]
          this.selectedTeam = admin ? admin.team : null
        }
        await this.listUsers()
      } catch (e) {
        console.log(e)
      }
      this.team.refresh()
    }

    if (this.$route.query.code) {
      this.handleConfigureOpen()
    }
  },
  watch: {},
  methods: {
    setOpenForm() {
      this.formOpen = false
    },
    openChangeConfig(page) {
      this.configPage = page
      this.configureModalOpen = true
    },
    changeConfigPage(page) {
      this.configPage = page
    },
    toString(data) {
      let type = typeof data
      if (type === 'number') {
        let newData = data.toString()
        return newData
      } else {
        return data
      }
    },
    handleInviteOpen() {
      this.inviteOpen = true
      this.profileModalOpen = false
      // this.selectingOption = false
    },
    toggleLeftBar() {
      this.leftBarClosed = !this.leftBarClosed
    },
    refreshLists() {
      this.$refs.sidebarRef.refreshList()
    },
    async noSlackRefresh() {
      this.team.refresh()
      // this.inviteOpen = false
      // this.profileModalOpen = true
    },
    async refresh() {
      this.team.refresh()
      this.inviteOpen = false
      this.profileModalOpen = true
    },
    customTeamLabel(props) {
      if (this.user.team === props.id) {
        return 'Your Team'
      } else {
        return props.name
      }
    },
    setOpp(name) {
      this.$refs.rightSideBar.changeSelectedOpp(null, name)
    },
    setView(name) {
      if (name === 'meetings' && this.currentOpp) {
        this.$refs.rightSideBar.setMeetingOpp(this.currentOpp)
      }
      this.$refs.rightSideBar.switchMainView(name)
    },
    toggleLeftbarOn() {
      this.barOpen = true
    },
    toggleLeftbarOff() {
      this.barOpen = false
    },
    setUpdateValues(key, val, multi) {
      if (multi) {
        this.formData[key] = this.formData[key]
          ? this.formData[key] + ';' + val
          : val.split(/&#39;/g)[0]
      } else {
        this.formData[key] = val
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
        const res = await CRMObjects.api
          .updateResource({
            form_data: this.formData,
            resource_type: this.formOpen
              ? this.user.crm === 'HUBSPOT'
                ? 'Deal'
                : 'Opportunity'
              : this.chatData.resource_type,
            form_type: this.formOpen ? 'UPDATE' : this.chatData.form_type,
            resource_id: this.formOpen ? this.currentOpp.id : this.chatData.resource_id,
            integration_ids: [
              this.formOpen ? this.currentOpp.integration_id : this.chatData.integration_id,
            ],
            from_workflow: false,
            workflow_title: 'None',
            stage_name: null,
          })
          .then((response) => {
            if (!this.formOpen) {
              User.api
                .editMessage({
                  message_id: this.chatData.id,
                  value: `Successfully updated ${this.chatData.resource}!`,
                  user_type: 'bot',
                  conversation_id: this.chatData.conversation,
                  failed: false,
                  updated: true,
                  data: this.formData,
                })
                .then((response) => {
                  this.$refs.chatBox.getConversations()
                  this.$refs.rightSideBar.reloadOpps()
                })
            }
          })
      } catch (e) {
        console.log(e)
        User.api
          .addMessage({
            value: e.data.error,
            user_type: 'bot',
            conversation_id: this.conversation.id,
            failed: true,
            data: {},
          })
          .then((response) => {
            this.$refs.chatBox.getConversations()
          })
      } finally {
        setTimeout(() => {
          this.toggleChatModal()
          this.formOpen = false
        }, 1000)
        setTimeout(() => {
          this.submitting = false
        }, 2000)
      }
    },
    resetData() {
      this.userInviteForm.field.organization.value = this.user.organization
      this.selectedMember = null
      this.selectedLevel = null
      this.selectedTeam = null
      this.selectedTeamLead = false
    },
    async handleInvite() {
      // reset component data when submission begins, in case of prior request
      this.loading = true
      this.userInviteForm.validate()
      if (!this.userInviteForm.isValid) {
        this.loading = false
        this.$toast('Please check form for errors', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      if (this.user.isAdmin && !this.selectedTeam) {
        this.loading = false
        this.$toast('Please select a team', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      // check form data for this request
      try {
        this.userInviteForm.field.team.value = this.selectedTeam.id
        this.userInviteForm.field.teamLead.value = this.selectedTeamLead
        this.userInviteForm.field.email.value = this.slackMembers.members.filter(
          (member) => member.id == this.userInviteForm.field.slackId.value,
        )[0].profile.email
        const res = await User.api.invite(this.userInviteForm.value)
        this.$toast('Invitation Sent', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        await this.refresh()
        this.$emit('handleRefresh')
        this.resetData()
      } catch (e) {
        let err = e.response.data
        if (err.email) {
          this.$toast('Email error', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } finally {
        this.loading = false
        // this.profileModalOpen = true
        // this.inviteOpen = !this.inviteOpen
        this.selectedMember = null
        this.selectedLevel = null
        this.selectedTeam = null
        this.selectedTeamLead = false
      }
    },
    async handleInviteNonSlack() {
      // reset component data when submission begins, in case of prior request
      this.loading = true
      this.userInviteForm.validate()
      if (!this.userInviteForm.isValid) {
        this.loading = false
        this.$toast('Please check form for errors', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      // check form data for this request
      try {
        this.userInviteForm.field.team.value = this.user.team
        const res = await User.api.invite(this.userInviteForm.value)
        this.activationLink = res.data.activation_link_ref
        this.$toast('Invite link created successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        await this.noSlackRefresh()
        this.resetData()
      } catch (e) {
        this.$toast('Error sending invite', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loading = false
      }
    },
    mapMember() {
      this.userInviteForm.field.slackId.value = this.selectedMember.id
    },
    mapUserLevel() {
      this.userInviteForm.field.userLevel.value = this.selectedLevel.value
    },
    checkTeamLead() {
      if (this.selectedTeam && this.user.team === this.selectedTeam.id) {
        this.selectedTeamLead = false
      }
    },
    async listUsers(cursor = null) {
      const res = await SlackOAuth.api.listUsers(cursor)
      const results = new SlackUserList({
        members: [...this.slackMembers.members, ...res.members],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.slackMembers = results
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
    handleConfigureOpen(name) {
      this.configureModalOpen = true

      // setTimeout(() => {
      //   console.log('name', name)
      //   this.$refs.configModal.changeConfigPage(name)
      // }, 300)
    },
    handleCancel() {
      this.profileModalOpen = false
      this.configureModalOpen = false
    },
    handleInviteCancel() {
      this.profileModalOpen = true
      this.inviteOpen = false
    },
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
      // localStorage.isLoggedOut = true
    },
    toggleChatModal(data, formOpen) {
      this.chatModalOpen = !this.chatModalOpen
      if (data && !formOpen) {
        let jsonString = data.data
        jsonString = JSON.parse(jsonString)
        this.formData = jsonString
        this.chatData = data
      } else if (data && formOpen) {
        //  let jsonString = data.data
        // jsonString = jsonString.replace(/'/g, '"')
        // jsonString = jsonString.replace(/\bNone\b/g, 'null')
        // jsonString = JSON.parse(jsonString)
        this.formData = data
        this.formOpen = formOpen
      }
    },
    setFormFields(fields) {
      this.formFields = fields
    },
    setStageFields(fields, stagesWithForms) {
      this.stageFields = fields
      this.stagesWithForms = stagesWithForms
    },

    // handleInvite() {
    //   console.log('handled')
    // },
    removeOpp() {
      this.$refs.rightSideBar.deselectOpp()
    },
  },
  computed: {
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    usersInTeam() {
      return this.team.list.filter(
        (member) => member.team === this.user.team, //&& member.id !== this.user.id
      )
    },
    hasSlack() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.slackRef
    },
    numberOfAllowedUsers() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.organizationRef.numberOfAllowedUsers
    },
    currentView() {
      return this.$store.state.currentView
    },
    currentOpp() {
      return this.$store.state.currentOpp
    },
    orgHasSlackIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    isAdmin() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.isAdmin
    },
  },
}
</script>

<style lang="scss" scoped>
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
.closed {
  width: 60px !important;
  transform: all;
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
  position: relative;
}

.hamburger {
  display: none;
  height: 50px;
  width: 50px;
  position: fixed;
  top: 1rem;
  left: 1.5rem;
  cursor: pointer;
  z-index: 10;
}

#left-sidebar {
  width: 60px;
  transition: transform 0.3s ease;
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

.configure-modal-container {
  display: flex;
  flex-direction: column;
  width: 80vw;
  height: 90vh;
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
.invite-form {
  @include small-modal();
  min-width: 37vw;
  // min-height: 64vh;
  align-items: center;
  justify-content: space-between;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
    font-size: 22px;
    margin-top: 1rem;
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    margin-top: -4rem;
  }
  &__inner_actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    border-top: 1px solid $soft-gray;
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
  }
}
.form-height-small {
  height: 20vh;
  margin-top: 10rem;
}
.invite-list {
  &__container {
    background-color: $white;
    // border: 1px solid #e8e8e8;
    color: $base-gray;
    width: 92vw;
    height: 60vh;
    overflow: scroll;
    padding: 1.5rem 0rem 1.5rem 1rem;
    border-radius: 5px;
    display: flex;
    align-items: flex-start;
    flex-direction: column;
  }
  &__section {
    &__container {
      width: 100%;
      display: flex;
      // margin-bottom: 0.5rem;
      // z-index: 2;
      margin-left: 16px;
    }
    &__item {
      width: 33%;
      overflow-wrap: break-word;
    }
  }
  &__status {
    img {
      margin-right: 16px;
    }
  }
}
.cancel-button {
  margin-top: 1rem;
  position: relative;
  right: 1px;
  color: $gray;
  &:hover {
    cursor: pointer;
  }
}
.header {
  // margin-top: -1.5rem;
  width: 100%;
  display: flex;
  justify-content: space-between;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  // width: 90%;
  margin: 0 5%;
  letter-spacing: 1px;
  h4 {
    font-size: 20px;
  }
}
.logo {
  height: 24px;
  margin-left: 0.25rem;
  margin-right: 0.5rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.invite-button {
  @include primary-button();
  margin: 1rem 0;
  width: 15vw;
  font-size: 16px;
}
.form_field {
  input {
    width: 16vw;
    padding: 8px 16px;
    outline: none;
    border: 1px solid $soft-gray;
    border-radius: 4px;
    margin-top: 0.5rem;
  }
}
</style>
