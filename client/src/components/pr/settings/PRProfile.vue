<template>
  <div class="settings">
    <!-- deleteUserModal -->
    <Modal v-if="deleteUserModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="() => deleteUserModal = false"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Deactivate</h3>
              <h5 class="regen-body-title">
                {{ `Are you sure you want to deactivate ${deleteUserName && deleteUserName.email ? deleteUserName.email : `this user`}?` }}
              </h5>
            </div>
            <!-- <textarea v-autoresize v-model="newTemplate" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="() => deleteUserModal = false"
            >
              Cancel
            </div>
            <div class="red-button" @click="deactivateUser">Deactivate</div>
          </div>
        </div>
      </div>
    </Modal>
    <!-- paidWarningModal -->
    <Modal v-if="paidWarningModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="() => paidWarningModal = false"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Purchase additional user</h3>
              <h5 class="regen-body-title">
                {{ `By clicking purchase you agree to be charged for an additional user.` }}
              </h5>
            </div>
            <!-- <textarea v-autoresize v-model="newTemplate" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="() => paidWarningModal = false"
            >
              Cancel
            </div>
            <div class="save-button" @click="handleInviteNonSlack">Purchase</div>
          </div>
        </div>
      </div>
    </Modal>
    <!-- reactivateUserModal -->
    <Modal v-if="reactivateUserModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="() => reactivateUserModal = false"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Reactivate User</h3>
              <h5 class="regen-body-title">
                {{ `By clicking Reactivate you are enabling ${reactivateUser.email} to access Managr` }}
              </h5>
            </div>
            <!-- <textarea v-autoresize v-model="newTemplate" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="() => reactivateUserModal = false"
            >
              Cancel
            </div>
            <div class="save-button" @click="reactivate">Reactivate</div>
          </div>
        </div>
      </div>
    </Modal>
    <!-- reactivatePaidUserModal -->
    <Modal v-if="reactivatePaidUserModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="() => reactivatePaidUserModal = false"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Purchase additional user</h3>
              <h5 class="regen-body-title">
                {{ `By clicking purchase you agree to be charged for an additional user.` }}
              </h5>
            </div>
            <!-- <textarea v-autoresize v-model="newTemplate" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="() => reactivatePaidUserModal = false"
            >
              Cancel
            </div>
            <div class="save-button" @click="reactivatePaid">Purchase</div>
          </div>
        </div>
      </div>
    </Modal>
    <div>
      <!-- <h1>Settings</h1> -->
      <h1>{{ user.organizationRef.name }} - Users</h1>

      <div class="bar-header">
        <small
          @click="changeActivePage('users')"
          class="pointer"
          :class="{ active: page === 'users' }"
          >Users</small
        >
        <small
          @click="changeActivePage('invite')"
          class="pointer"
          :class="{ active: page === 'invite' }"
          >Invite</small
        >
        <!-- <small @click="changeActivePage('profile')" class="pointer" :class="{ active: page === 'profile' }">Profile</small> -->
      </div>

      <div v-if="page === 'invite'">
        <div>
          <div class="vertical-margin">
            <h3>Invite Users</h3>
          </div>
        </div>

        <div v-if="userInviteForm" class="row">
          <input
            v-model="userInviteForm.field.email.value"
            placeholder="Enter User email"
            type="email"
            class="input"
            :disabled="disableInput"
          />

          <PulseLoadingSpinnerButton
            class="primary-button"
            v-if="!activationLink"
            @click="aboveInviteLimit ? handleInviteNonSlack() : openPaidWarningModal()"
            text="Generate Link"
            :loading="loading"
            :disabled="!userInviteForm.field.email.value || loading"
          ></PulseLoadingSpinnerButton>
        </div>
        <div v-if="activationLink" class="vertical-margin">
          <h3>Your link:</h3>
          <div>
            <p class="small-text">{{ activationLink }}</p>
            <div class="display-flex">
              <button
                class="secondary-button extra-margin-top"
                @click="clearInvite"
                :loading="loading"
                :disabled="!activationLink || loading"
              >
                <!-- <img src="@/assets/images/trash.svg" height="12px" alt="" />  -->
                Clear
              </button>
              <button
                class="primary-button extra-margin-top mar-left"
                @click="copyText"
                :loading="loading"
                :disabled="!activationLink || loading"
              >
                <img src="@/assets/images/link.svg" height="12px" alt="" /> {{ copyTip }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="page === 'users'">
        <!-- <div>
          <div class="vertical-margin">
            <h3>Users</h3>
          </div>
        </div> -->

        <div class="row margin-top margin-bottom">
          <h3 class="team-width thin-font">Name</h3>
          <h3 class="team-width thin-font">Email</h3>
          <!-- <h3 class="less-team-width thin-font extra-mar-left">Invite</h3> -->
          <h3 v-if="user.isAdmin" class="team-width thin-font extra-mar-left">Actions</h3>
        </div>

        <div class="users-container">
          <div class="row smaller-text">
            <div class="team-width">{{ user.fullName.trim() ? user.fullName : '[INVITED]' }}</div>
            <div class="team-width">{{ user.email }}</div>
            <div class="team-width">{{  }}</div>
            <div class="team-width">{{  }}</div>
          </div>
  
          <div v-for="teamUser in orderedActive" :key="teamUser.id" class="row smaller-text">
            <div v-if="teamUser.id !== user.id" class="team-width thin-font">
              {{ !teamUser.isActive && teamUser.fullName.trim() ? '[INACTIVE]' : (teamUser.fullName.trim() ? teamUser.fullName : '[INVITED]') }}
            </div>
            <div v-if="teamUser.id !== user.id" class="team-width thin-font">
              {{ teamUser.email }}
            </div>
            <!-- <div v-if="teamUser.id !== user.id && !teamUser.fullName.trim()" @click="copyUserLink(teamUser.activationLinkRef)" class="invite-link-button-container wrapper thin-font">
              <img 
                src="@/assets/images/link.svg"
                class="invite-link-button"
              />
              <div style="margin-left: -20px" class="tooltip">{{ copyTip }}</div>
            </div>
            <div v-else-if="teamUser.id !== user.id" class="invite-link-button-container-nothing wrapper thin-font"></div> -->
            <div v-if="user.isAdmin">
              <div v-if="(teamUser.id !== user.id) && teamUser.isActive" @click="openDeleteModal(teamUser)" class="invite-link-button-container red-background wrapper thin-font">
                <img 
                  src="@/assets/images/remove-user.svg"
                  class="invite-link-button"
                />
                <div style="margin-left: -20px" class="tooltip">{{ 'Deactivate' }}</div>
              </div>
              <div v-else-if="teamUser.id !== user.id && !teamUser.isActive && teamUser.fullName.trim()" @click="openReactivateeModal(teamUser)" class="invite-link-button-container green-background wrapper thin-font">
                <img 
                  src="@/assets/images/user.svg"
                  class="invite-link-button"
                />
                <div style="margin-left: -20px" class="tooltip">{{ 'Reactivate' }}</div>
              </div>
              <div v-else-if="teamUser.id !== user.id && !teamUser.fullName.trim()" @click="copyUserLink(teamUser.activationLinkRef)" class="invite-link-button-container wrapper thin-font">
                <img 
                  src="@/assets/images/link.svg"
                  class="invite-link-button"
                />
                <div style="margin-left: -20px" class="tooltip">{{ copyTip }}</div>
              </div>
              <!-- <div v-else-if="teamUser.id !== user.id" class="invite-link-button-container-nothing wrapper thin-font"></div> -->
            </div>
          </div>
        </div>
      </div>
      <div v-if="page === 'profile'">
        <div>
          <div class="profile-img">
            <img
              src="@/assets/images/profile.svg"
              style="filter: invert(80%)"
              height="40px"
              alt=""
            />
            <h3 class="profile-name">{{ user.fullName }}</h3>
          </div>

          <div class="row org-timezone-container">
            <p>{{ user.organizationRef.name }} -</p>
            <p>{{ user.timezone }}</p>
          </div>
        </div>

        <div>
          <div class="row small-gap">
            <!-- <font-awesome-icon icon="fa-solid fa-at" /> -->

            Email:

            <p>{{ user.email }}</p>
          </div>

          <!-- <div class="row">
            <font-awesome-icon icon="fa-solid fa-user-group" />
            <p>{{ user.organizationRef.teamsRef[0].name }}</p>
          </div> -->

          <!-- <div class="row">
            <font-awesome-icon icon="fa-solid fa-layer-group" />
            <p>{{ user.userLevel.toLowerCase() }}</p>
          </div> -->
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import CollectionManager from '@/services/collectionManager'
import User from '@/services/users'
import Organization from '@/services/organizations'
import { UserInviteForm } from '@/services/users/forms'
import SlackOAuth, { SlackUserList } from '@/services/slack'
import FormField from '@/components/forms/FormField'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

export default {
  name: 'PRProfile',
  components: {
    FormField,
    PulseLoadingSpinnerButton,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      page: 'users',
      copyTip: 'Copy link',
      disableInput: false,
      inviteOpen: false,
      selectedMember: null,
      slackMembers: new SlackUserList(),
      selectedLevel: null,
      userTypes: [
        { key: 'Manager', value: User.types.MANAGER },
        { key: 'Representative', value: User.types.REP },
        { key: 'SDR', value: User.types.SDR },
      ],
      userTypesNoSlack: [
        { key: 'Representative', value: User.types.REP },
        { key: 'SDR', value: User.types.SDR },
      ],
      selectedTeam: null,
      selectedTeamLead: false,
      allTeams: [],
      team: CollectionManager.create({ ModelClass: User }),
      loading: false,
      userInviteForm: {},
      activationLink: '',
      deleteUserModal: false,
      deleteUserName: null,
      reactivateUserModal: false,
      reactivatePaidUserModal: false,
      reactivateUserId: null,
      paidWarningModal: false,
    }
  },
  async created() {
    this.team = CollectionManager.create({ ModelClass: User })
    this.teamUsers = this.listAllUsers()
    // if (this.user.isAdmin) {
    //   this.teamUsers = await this.getAllOrgUsers(this.user.organization)
    // } else {
    //   this.teamUsers = [this.user]
    // }
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
        // const allForms = await SlackOAuth.api.getOrgCustomForm()
        // this.$store.commit('SAVE_CRM_FORMS', allForms)
      } catch (e) {
        console.log(e)
      }
    }
    this.userInviteForm.field.userLevel.value = User.types.REP
    this.team.refresh()
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    openPaidWarningModal() {
      this.paidWarningModal = true
    },
    openReactivateeModal(user) {
      this.reactivateUserModal = true
      this.reactivateUser = user
    },
    openDeleteModal(user) {
      this.deleteUserModal = true
      this.deleteUserName = user
    },
    async copyUserLink(link) {
      try {
        await navigator.clipboard.writeText(link)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          // this.activationLink = ''
          this.copyTip = 'Copy link'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyText() {
      this.disableInput = false
      this.userInviteForm.field.email.value = null
      try {
        await navigator.clipboard.writeText(this.activationLink)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          // this.activationLink = ''
          this.copyTip = 'Copy link'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    changeActivePage(page) {
      this.page = page
    },
    handleInviteCancel() {
      this.inviteOpen = false
    },
    async listUsers(cursor = null) {
      const res = await SlackOAuth.api.listUsers(cursor)

      const results = new SlackUserList({
        members: [...this.slackMembers.members, ...res.members],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.slackMembers = results
    },
    async getAllOrgUsers(orgId) {
      const res = await User.api.getAllOrgUsers(orgId)
      return res
    },
    async listAllUsers() {
      const res = await User.api.list({ pagination: null })
      return res
    },
    async refresh() {
      this.team.refresh()
      this.inviteOpen = false
    },
    async noSlackRefresh() {
      this.team.refresh()
      // this.inviteOpen = false
      // this.profileModalOpen = true
    },
    clearInvite() {
      this.activationLink = ''
      this.disableInput = false
    },
    resetData() {
      this.userInviteForm.field.organization.value = this.user.organization
      this.selectedMember = null
      this.selectedLevel = null
      this.selectedTeam = null
      this.selectedTeamLead = false
    },
    async reactivate() {
      try {
        const data = {...this.reactivateUser, isActive: true}
        const res = await User.api.update(this.reactivateUser.id, data)
        this.team.refresh()
      } catch(e) {
        console.log('Error in reactivate: ', e)
        this.$toast('Something went wrong. Please try again later', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.reactivateUserModal = false
      }
    },
    async reactivatePaid() {
      try {
        const data = {...this.reactivateUser, isActive: true}
        const res = await User.api.update(this.reactivateUser.id, data)
        this.team.refresh()
      } catch(e) {
        console.log('Error in reactivatePaid: ', e)
        this.$toast('Something went wrong. Please try again later', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.reactivatePaidUserModal = false
      }
    },
    async deactivateUser() {
      try {
        const res = await User.api.uninvite(this.deleteUserName.id)
        this.team.refresh()
      } catch(e) {
        console.log('Error in deactivateUser: ', e)
        this.$toast('Something went wrong. Please try again later', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.deleteUserModal = false
      }
    },
    async deleteUser() {
      try {
        const res = await User.api.uninvite(this.deleteUserName.id)
        this.team.refresh()
      } catch(e) {
        console.log('Error in deleteUser: ', e)
        this.$toast('Something went wrong. Please try again later', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.deleteUserModal = false
      }
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
        // this.$emit('handleRefresh')
        this.resetData()
      } catch (e) {
        let err = e.response.data
        if (e.response.status === 426) {
          this.$toast('Max users reached. Please upgrade', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (err.email) {
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
      this.paidWarningModal = false
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
        this.disableInput = true
      } catch (e) {
        if (e.response.status === 426) {
          // Upgrade modal here
          this.$toast('Max users reached, upgrade to add more', {
            timeout: 2500,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Error creating link, try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } finally {
        setTimeout(() => {
          this.loading = false
        }, 500)
      }
    },
    customTeamLabel(props) {
      if (this.user.team === props.id) {
        return 'Your Team'
      } else {
        return props.name
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
  },
  computed: {
    hasSlack() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.slackRef
    },
    orgHasSlackIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    user() {
      return this.$store.state.user
    },
    isAdmin() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.isAdmin
    },
    activeUsers() {
      return this.team.list.filter(user => user.isActive)
    },
    aboveInviteLimit() {
      return this.activeUsers >= this.user.organizationRef.numberOfAllowedUsers
    },
    orderedActive() {
      const active = []
      const noName = []
      const inactive = []
      for (let i = 0; i < this.team.list.length; i++) {
        const el = this.team.list[i]
        console.log('el', el)
        if (el.isActive) {
          active.push(el)
        } else if (!el.isActive && el.fullName.trim()) {
          inactive.push(el)
        } else {
          noName.push(el)
        }
      }
      return [...active, ...noName, ...inactive]
    },
  },
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';

.settings {
  padding: 96px 144px 32px 144px;
  height: 100vh;
  font-weight: 400;
  font-family: $base-font-family;
  color: $dark-black-blue;
  @media only screen and (max-width: 600px) {
    padding: 0rem 2rem 0.5rem 2rem;
    height: 90vh;
    h1 {
      margin: 0.55rem 0 0.25rem;
    }
  }
}

.bar-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  position: sticky;
  top: 0;
  margin: 0;
  padding: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
  // height: 66px;
  // background-color: white;
  z-index: 10;
  font-family: $thin-font-family;

  small {
    font-size: 14px;
    margin-right: 2rem;
    color: $off-gray;
    padding: 16px 0;
  }
}

.input {
  width: 400px;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 8px 16px;
  line-height: 1.75;
  outline: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $base-font-family;
  font-weight: 400;
  border: 1px solid rgba(0, 0, 0, 0.1);
  resize: none;
  text-align: left;
  color: $dark-black-blue;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
  // justify-content: space-between;
}

.primary-button {
  @include dark-blue-button();
  padding: 11px 12px;
  font-size: 13px;
  border: none;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.secondary-button {
  @include dark-blue-border-button();
  padding: 11px 12px;
  font-size: 13px;
  border: 1px solid $soft-gray;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.vertical-margin {
  margin: 32px 0;
}

.active {
  color: $dark-black-blue !important;
  border-bottom: 0.75px solid $dark-black-blue;
}

.not-allowed {
  cursor: not-allowed;
}
.pointer {
  cursor: pointer;
}
h3 {
  margin: 0;
}
h1,
h3 {
  font-family: $thin-font-family;
}

.team-width {
  width: 10rem;
  padding: 8px 0;
  overflow-x: auto;
  @media only screen and (max-width: 600px) {
    width: 4.5rem;
  }
}
.less-team-width {
  width: 5rem;
  padding: 8px 0;
  overflow-x: auto;
  @media only screen and (max-width: 600px) {
    width: 4.5rem;
  }
}
.border-right {
  border-right: 1px solid $soft-gray;
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
.org-timezone-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 4px;
  // justify-content: center;
  font-size: 14px;
  p:first-of-type {
    margin-right: 0rem;
    // color: $grape;
    font-weight: bold;
  }
  p:last-of-type {
    margin-right: 0.5rem;
    color: $light-gray-blue;
  }
}
.small-gap {
  gap: 6px;
}
.underline {
  text-decoration: underline;
}
.smaller-text {
  font-size: 14px;
}
.margin-top {
  margin-top: 1rem;
}
.margin-bottom {
  margin-bottom: 0.25rem;
}
.thin-font {
  font-family: $thin-font-family;
}

.small-text {
  font-family: $thin-font-family;
  font-size: 15px;
  @media only screen and (max-width: 600px) {
    width: 100%;
    overflow-x: auto;
  }
}
.extra-margin-top {
  margin-top: 1.5rem;
}
.invite-link-button-container {
  background-color: $dark-black-blue;
  border-radius: 100%;
  // width: 1.375rem;
  // height: 1.375rem;
  width: 1.5rem;
  height: 1.5rem;
  margin-left: 5rem;
  cursor: pointer;
  img {
    margin: 0 auto;
  }
}
.red-background {
  background-color: $coral !important;
}
.green-background {
  background-color: $dark-green !important;
}
.invite-link-button-container-nothing {
  // width: 1.375rem;
  // height: 1.375rem;
  width: 1.5rem;
  height: 1.5rem;
  margin-left: 5rem;
}
.invite-link-button {
  height: 14px;
  filter: invert(99%);
  margin: 0.25rem;
}
.wrapper {
  display: flex;
  align-items: center;
  // background-color: ;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -20px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}
.mar-left {
  margin-left: 1rem;
}
.extra-mar-left {
  margin-left: 4.5rem;
}
.display-flex {
  display: flex;
}
.users-container {
  overflow-y: auto;
  height: 64vh;
}
.paid-modal {
  margin-top: 132px;
  font-family: $thin-font-family;
}
.regen-container {
  width: 500px;
  max-height: 500px;
  position: relative;
  overflow-y: scroll;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}
.paid-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.paid-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.regen-header-title {
  margin: 0.25rem 0;
}
.regen-header-subtitle {
  font-size: 12px;
  color: $light-gray-blue;
  margin: 0.5rem 0;
}
.regen-body {
  margin: 0.5rem 0;
  border-bottom: 1px solid $soft-gray;
}
.paid-body {
  margin: 0.5rem 0;
}
.regen-body-title {
  margin: 0 0 0 0;
}
.paid-title {
  margin-top: 0;
  margin-bottom: 2rem;
}
.paid-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: 0;
  padding-top: 16px;
  padding-bottom: 8px;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cancel-button {
  @include gray-text-button();
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}
.save-button {
  @include dark-blue-button();
  &:hover {
    scale: 1;
    opacity: 0.9;
    box-shadow: none;
  }
  margin-left: 0.5rem;
}
.red-button {
  @include button-danger();
  &:hover {
    scale: 1;
    opacity: 0.9;
    box-shadow: none;
  }
  margin-left: 0.5rem;
}
</style>