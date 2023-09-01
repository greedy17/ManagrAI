<template>
  <div class="settings">
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
            @click="handleInviteNonSlack"
            text="Generate Link"
            :loading="loading"
            :disabled="!userInviteForm.field.email.value || loading"
          ></PulseLoadingSpinnerButton>
        </div>
        <div v-if="activationLink" class="vertical-margin">
          <h3>Your link:</h3>
          <div>
            <p class="small-text">{{ activationLink }}</p>
            <button
              class="primary-button extra-margin-top"
              @click="copyText"
              :loading="loading"
              :disabled="!activationLink || loading"
            >
              <img src="@/assets/images/link.svg" height="12px" alt="" /> {{ copyTip }}
            </button>
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
          <h3 class="team-width thin-font extra-mar-left">Invite</h3>
        </div>

        <div class="row smaller-text">
          <div class="team-width">{{ user.fullName.trim() ? user.fullName : '[NO NAME]' }}</div>
          <div class="team-width">{{ user.email }}</div>
          <div class="team-width">{{  }}</div>
        </div>

        <div v-for="teamUser in team.list" :key="teamUser.id" class="row smaller-text">
          <div v-if="teamUser.id !== user.id" class="team-width thin-font">
            {{ teamUser.fullName.trim() ? teamUser.fullName : '[NO NAME]' }}
          </div>
          <div v-if="teamUser.id !== user.id" class="team-width thin-font">
            {{ teamUser.email }}
          </div>
          <div v-if="teamUser.id !== user.id && !teamUser.fullName.trim()" @click="copyUserLink(teamUser.activationLinkRef)" class="invite-link-button-container wrapper thin-font">
            <img 
              src="@/assets/images/link.svg"
              class="invite-link-button"
            />
            <div style="margin-left: -20px" class="tooltip">{{ copyTip }}</div>
          </div>
          <!-- {{ teamUser.activationLinkRef }} hi -->
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
        if (e.response.status === 426) {
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
        this.disableInput = true
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
}
.extra-margin-top {
  margin-top: 1.5rem;
}
.invite-link-button-container {
  background-color: $dark-black-blue;
  border-radius: 100%;
  width: 1.375rem;
  height: 1.375rem;
  margin-left: 4rem;
  cursor: pointer;
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
.extra-mar-left {
  margin-left: 3.5rem;
}
</style>