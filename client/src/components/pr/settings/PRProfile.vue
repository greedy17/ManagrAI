<template>
  <div>
    <div>
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
          <!-- <div style="display: flex; align-items: flex-start; flex-direction: column">
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
          </div> -->
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
                :disabled="!selectedTeam"
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
          <!-- <FormField>
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
          </FormField> -->
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
    </div>
    <h1>Hi there</h1>
    <h1>Hi there</h1>
    <h1>Hi there</h1>
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
    if (this.user.isAdmin) {
      this.teamUsers = await this.getAllOrgUsers(this.user.organization)
    } else {
      this.teamUsers = [this.user]
    }
    console.log('teamUsers', this.teamUsers)
    this.userInviteForm = new UserInviteForm({
      role: User.roleChoices[0].key,
      userLevel: User.types.REP,
      organization: this.user.organization,
    })
    console.log('this.userInviteForm', this.userInviteForm)
    if ((this.isAdmin && this.orgHasSlackIntegration) || this.hasSlack) {
      try {
        const allTeams = await Organization.api.listTeams(this.user.id)
        console.log('allTeams', allTeams)
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

</style>