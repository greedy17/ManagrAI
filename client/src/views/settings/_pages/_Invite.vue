<template>
  <div class="invite-container">
    <Modal
      v-if="uninviteModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleConfirmCancel()
        }
      "
    >
      <form v-if="true /*hasSlack*/" class="invite-form modal-form confirm-form form-height-small">
        <div class="header-confirm">
          <div class="flex-row-confirm">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Are you sure?</h3>
          </div>
          <div class="flex-row-confirm">
            <h4>
              By clicking Confirm, you will be removing this user from your organization.
            </h4>
          </div>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="handleUninvite(uninviteId)"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Confirm"
                :loading="loading"
                >Confirm</PulseLoadingSpinnerButton
              >
            </template>
          </div>
        </div>
      </form>
    </Modal>
    <Modal
      v-if="inviteOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetData()
        }
      "
    >
      <form v-if="hasSlack" class="invite-form" @submit.prevent="handleInvite" style="margin-top: 7.5rem;">
        <div class="header">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h3 class="invite-form__title">Invite Slack Users</h3>
          </div>
          <div class="flex-row">
            <img
              @click="handleCancel"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="filter: invert(30%); cursor: pointer;"
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
                  style="width: 33vw"
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
                  style="width: 33vw"
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
          <div v-if="user.organizationRef.isPaid && user.isAdmin" style="display: flex; align-items: flex-start; flex-direction: column">
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select Team"
                  @input="checkTeamLead"
                  v-model="selectedTeam"
                  :options="allTeams"
                  openDirection="below"
                  style="width: 33vw"
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
          <div v-if="user.organizationRef.isPaid && user.isAdmin" style="display: flex; align-items: flex-start; flex-direction: column">
            <div style="display: flex; height: 1rem; margin-bottom: 2rem; margin-left: 0.25rem;">
              <p style="margin: 0;">Make Team Lead</p>
              <input v-model="selectedTeamLead" :disabled="!selectedTeam || user.team === selectedTeam.id" type="checkbox" style="height: 1rem; align-self: center; width: 2rem; margin-top: 0.5rem;" />
            </div>
          </div>
        </div>
        <div class="invite-form__actions">
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="handleInvite"
                class="invite-button"
                style="width: 5rem; margin-right: 5%; height: 2rem; margin-top: 2rem;"
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
            <div v-if="!activationLink" class="cancel-button" @click="handleCancel">Cancel</div>
            <small v-else class="copyText">Copy above link and send to user</small>
          </template>
        </div>

        <div v-if="activationLink">
          <button @click="handleCancel" class="invite-button">Reset form</button>
        </div>
      </div>
    </Modal>
    <div class="invite-list__container" :style="selectedTeamUsers ? 'width: 70vw;' : ''">
      <!-- <div class="key">
        <div class="left-key">
          <h2>The {{ $store.state.user.organizationRef.name }} Team</h2>
        </div>
      </div> -->

      <div class="invite-list__section__container" style="margin-bottom: 2rem">
        <div
          style="display: flex; align-items: flex-start"
          class="invite-list__section__item section-header"
        >
          User
        </div>
        <div
          style="display: flex; align-items: flex-start"
          class="invite-list__section__item section-header"
        >
          User Level
        </div>
        <div
          style="display: flex; align-items: flex-start"
          class="invite-list__section__item section-header"
        >
          Status
        </div>
        <div
          style="display: flex; align-items: flex-start"
          class="invite-list__section__item section-header"
        >
          Integrations
        </div>
        <div style="position: relative; right: 3%"></div>
      </div>

      <div class="invite-list__section__container" v-if="!selectedTeamUsers">
        <!-- <img class="back-logo" src="@/assets/images/logo.png" /> -->
        <div
          style="display: flex; align-items: flex-start; font-size: 14px"
          class="invite-list__section__item col"
        >
          {{ user.fullName }}
          <p style="color: #beb5cc; font-size: 0.65rem; margin-top: 0.25rem">{{ user.email }}</p>
        </div>
        <div
          style="display: flex; align-items: flex-start; font-size: 14px"
          class="invite-list__section__item"
        >
          {{ user.userLevel == 'MANAGER' ? 'Team Leader (You)' : 'Rep(You)' }}
        </div>
        <div
          style="display: flex; align-items: flex-start; font-size: 14px"
          class="invite-list__section__item"
        >
          Registered
        </div>

        <div
          style="display: flex; align-items: flex-start"
          class="invite-list__section__item invite-list__status"
        >
          <span :class="user.slackRef ? '' : 'grayscale'">
            <img src="@/assets/images/slackLogo.png" height="18px" alt="" />
          </span>
          <span v-if="userCRM === 'SALESFORCE'" :class="user.hasSalesforceIntegration ? '' : 'grayscale'">
            <img src="@/assets/images/salesforce.png" height="18px" alt="" />
          </span>
          <span v-else-if="userCRM === 'HUBSPOT'" :class="user.hasHubspotIntegration ? '' : 'grayscale'">
            <img src="@/assets/images/hubspot-single-logo.svg" height="18px" alt="" />
          </span>
          <span :class="user.hasZoomIntegration ? '' : 'grayscale'">
            <img src="@/assets/images/zoom.png" alt="" height="18px" />
          </span>
          <span :class="user.nylasRef ? '' : 'grayscale'">
            <img src="@/assets/images/gmailCal.png" alt="" height="18px" />
          </span>
        </div>
        <div style="position: relative; right: 3%; cursor: text; visibility: hidden">
          <img src="@/assets/images/remove.svg" style="filter: invert(60%)" height="22px" alt="" />
        </div>
      </div>
      <div v-for="member in (selectedTeamUsers ? selectedTeamUsers : usersInTeam)" :key="member.id" class="invite-list__section__container">
        <template
          v-if="
            (member.id !== user.id &&
            member.team === $store.state.user.team &&
            !((member.firstName || member.first_name) && (!member.isActive && !member.is_active))) || selectedTeamUsers
          "
          @click="test(member)"
        >
          <div
            style="display: flex; align-items: flex-start; font-size: 14px"
            class="invite-list__section__item col"
            @click="test(member)"
          >
            <!-- {{member.isActive ? member.firstName : 'Pending'}} -->
            {{ (!member.firstName && !member.first_name) ? 'Pending' : member.isActive ? member.firstName : member.first_name }}
            <p style="color: #beb5cc; font-size: 0.65rem; margin-top: 0.25rem">
              {{ (!member.firstName && !member.first_name) ? member.email : (member.isActive || member.is_active) ? member.email : member.email }}
            </p>
          </div>
          <div
            v-if="member.userLevel == 'MANAGER' || member.user_level === 'MANAGER'"
            style="display: flex; align-items: flex-start; font-size: 14px"
            class="invite-list__section__item"
          >
            Manager
          </div>
          <div
            v-else-if="member.userLevel == 'SDR' || member.user_level === 'SDR'"
            style="display: flex; align-items: flex-start; font-size: 14px"
            class="invite-list__section__item"
          >
            SDR
          </div>
          <div
            v-else-if="member.userLevel == 'REP' || member.user_level === 'REP'"
            style="display: flex; align-items: flex-start; font-size: 14px"
            class="invite-list__section__item"
          >
            REP
          </div>
          <div
            style="display: flex; align-items: flex-start; font-size: 14px"
            class="invite-list__section__item"
          >
            <!-- {{ member.isActive ? 'Registered' : 'Pending...' }} -->
            {{ (!member.firstName && !member.first_name) ? 'Pending...' : (member.isActive || member.is_active) ? 'Registered' : 'Deactivated' }}
          </div>
          <div
            style="display: flex; align-items: flex-start"
            class="invite-list__section__item invite-list__status"
          >
            <span :class="(member.slackRef || member.slack_ref) ? '' : 'grayscale'">
              <img src="@/assets/images/slackLogo.png" height="18px" alt="" />
            </span>
            <span v-if="member.crm === 'SALESFORCE'" :class="(member.hasSalesforceIntegration || member.has_salesforce_integration) ? '' : 'grayscale'">
              <img src="@/assets/images/salesforce.png" height="18px" alt="" />
            </span>
            <span v-else-if="member.crm === 'HUBSPOT'" :class="(member.hasHubspotIntegration || member.has_hubspot_integration) ? '' : 'grayscale'">
              <img src="@/assets/images/hubspot-single-logo.svg" height="18px" alt="" />
            </span>
            <span v-else :class="'grayscale'">
              <img src="@/assets/images/revoke.svg" height="18px" alt="" />
            </span>
            <span :class="(member.hasZoomIntegration || member.has_zoom_integration) ? '' : 'grayscale'">
              <img src="@/assets/images/zoom.png" alt="" height="18px" />
            </span>
            <span :class="(member.nylasRef || member.nylas_ref) ? '' : 'grayscale'">
              <img src="@/assets/images/gmailCal.png" alt="" height="18px" />
            </span>
          </div>
          <div
            v-if="(!member.isAdmin && !member.is_admin) && (member.isActive || member.is_active)"
            style="position: relative; right: 3%; cursor: pointer"
            @click="openUninviteModal(member.id)"
          >
            <img src="@/assets/images/remove.svg" class="red" height="22px" alt="" />
          </div>
          <div v-else style="width: 28px;"></div>
        </template>
      </div>
    </div>
  </div>
</template>
<script>
import User from '@/services/users'
import { UserInviteForm } from '@/services/users/forms'
import CollectionManager from '@/services/collectionManager'
import Modal from '../../../components/InviteModal'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import FormField from '@/components/forms/FormField'
import SlackOAuth, { SlackUserList } from '@/services/slack'
import Organization from '@/services/organizations'

export default {
  name: 'Invite',
  components: {
    Modal,
    PulseLoadingSpinnerButton,
    FormField,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    inviteOpen: {
      type: Boolean,
      default: false,
    },
    handleEdit: {
      type: Function,
    },
    selectedTeamUsers: {
      type: Array,
    },
  },
  data() {
    return {
      activationLink: null,
      selectedMember: null,
      selectedLevel: null,
      selectedTeam: null,
      selectedTeamLead: false,
      allTeams: null,
      organization: null,
      slackMembers: new SlackUserList(),
      uninviteId: '',
      uninviteModal: false,
      userTypes: [
        { key: 'Manager', value: User.types.MANAGER },
        { key: 'Representative', value: User.types.REP },
        { key: 'SDR', value: User.types.SDR },
      ],
      userTypesNoSlack: [
        { key: 'Representative', value: User.types.REP },
        { key: 'SDR', value: User.types.SDR },
      ],
      team: CollectionManager.create({ ModelClass: User }),
      loading: false,
      userInviteForm: new UserInviteForm({
        role: User.roleChoices[0].key,
        userLevel: User.types.REP,
        organization: this.$store.state.user.organization,
      }),
    }
  },
  async created() {
    const allTeams = await Organization.api.listTeams(this.user.id)
    this.allTeams = allTeams.results
    if (this.user.isAdmin) {
      const userTeam = this.allTeams.filter(team => team.id === this.user.team)
      this.selectedTeam = userTeam[0] ? userTeam[0] : null
    } else {
      const orgUsers = await User.api.getAllOrgUsers(this.user.organization)
      let admin = orgUsers.filter(user => user.is_admin)[0]
      this.selectedTeam = admin ? admin.team : null
    }
    this.refresh()
    await this.listUsers()
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    onCopy: function () {
      this.$toast('Link copied.', {
        timeout: 2000,
        position: 'top-left',
        type: 'success',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
      this.handleCancel()
    },
    onError: function () {
      this.$toast('Error copying template', {
        timeout: 2000,
        position: 'top-left',
        type: 'error',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
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
    async refresh() {
      if (!this.user.isAdmin && !this.user.userLevel === 'MANAGER') {
        this.$router.push({ name: 'ListTemplates' })
      }
      this.organization = this.$store.state.user.organization
      this.team.refresh()
    },
    async handleCancel() {
      await this.refresh()
      this.resetData()
      this.$emit('cancel')
      this.activationLink = null
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
      if (this.user.organizationRef.isPaid && this.user.isAdmin && !this.selectedTeam) {
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
        this.inviteOpen = !this.inviteOpen
        this.selectedMember = null
        this.selectedLevel = null
        this.selectedTeam = null
        this.selectedTeamLead = false
      }
    },
    handleConfirmCancel() {
      this.uninviteModal = false
      this.uninviteId = ''
    },
    openUninviteModal(memberId) {
      this.uninviteModal = true
      this.uninviteId = memberId
    },
    async handleUninvite(id) {
      this.loading = true
      try {
        const res = await User.api.uninvite(id)
        this.$toast('User Removed Successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        await this.refresh()
        // this.resetData()
        this.uninviteModal = false
      } catch (e) {
        console.log(e)
        this.$toast('Something went wrong', {
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
        const res = await User.api.invite(this.userInviteForm.value)
        this.activationLink = res.data.activation_link_ref
        this.$toast('Invite link created successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        await this.refresh()
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

        // this.inviteOpen = !this.inviteOpen
      }
    },
    resetData() {
      this.userInviteForm.field.organization.value = this.$store.state.user.organization
      this.selectedMember = null
      this.selectedLevel = null
      this.selectedTeam = null
      this.selectedTeamLead = false
    },
    customTeamLabel(props) {
      if (this.user.team === props.id) {
        return "Your Team"
      } else {
        return props.name
      }
    },
  },
  computed: {
    hasSlack() {
      return !!this.$store.state.user.slackRef
    },
    user() {
      return this.$store.state.user
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    usersInTeam() {
      return this.team.list.filter(
        (member) =>
          member.id !== this.$store.state.user.id && member.team === this.$store.state.user.team,
      )
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

::placeholder {
  // color: #35495e;
  color: $very-light-gray;
  padding-left: 1rem;
}
.grayscale {
  filter: grayscale(99%);
}
input {
  width: 16vw;
  height: 2.5rem;
  border-radius: 5px;
  border: 1px solid #e8e8e8;
}
.red {
  filter: invert(42%) sepia(36%) saturate(937%) hue-rotate(308deg) brightness(114%) contrast(96%);
}
input:focus {
  outline: none;
}
.col {
  display: flex;
  flex-direction: column;
}
.copyText {
  color: $dark-green;
  margin-top: 1rem;
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
.invert {
  filter: invert(80%);
}
.section-header {
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 0.75px;
  color: $light-gray-blue;
}
// .key {
//   display: flex;
//   align-items: center;
//   width: 100%;
//   font-size: 0.75rem;
//   margin-bottom: 1.5rem;
//   margin-left: 16px;
// }
// .left-key {
//   display: flex;
//   width: 100%;
//   flex-direction: row;
//   justify-self: flex-start;
//   align-items: center;
// }
.header {
  margin-top: -1.5rem;
  width: 100%;
  display: flex;
  justify-content: space-between;
}
.header-confirm {
  margin-top: -1.5rem;
  width: 100%;
  // display: flex;
  // justify-content: space-around;
}
// .back-logo {
//   position: absolute;
//   z-index: -1;
//   opacity: 0.06;
//   filter: alpha(opacity=50);
//   height: 28%;
//   margin-top: -7rem;
//   margin-left: -2rem;
// }
.invite-container {
  display: flex;
  flex-flow: row;
  justify-content: center;
  width: 100%;
}
form {
  width: 100%;
  min-height: 30vh;
  background-color: $white;
  height: 50vh;
  justify-content: space-evenly;
}
.invite-button {
  background-color: $dark-green;
  border-radius: 6px;
  color: white;
  border: none;
  margin-top: 1rem;
  width: 15vw;
  font-size: 16px;
  box-shadow: none;
}
// button {
//   @include primary-button();
//   margin-top: 1.25rem;
//   height: 2.5rem;
//   width: 19rem;
//   font-size: 14px;
// }
.invite-form {
  border: none;
  border-radius: 0.75rem;
  min-width: 37vw;
  // min-height: 64vh;
  display: flex;
  align-items: center;
  justify-content: space-around;
  flex-direction: column;
  background-color: white;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
    font-size: 22px;
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
  height: 30vh;
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
      z-index: 2;
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
.flex-row-confirm {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  width: 90%;
  margin: 0 auto;
  letter-spacing: 1px;
  h4 {
    font-size: 16px;
    margin-bottom: 2rem;
  }
}
.logo {
  height: 24px;
  margin-left: 0.25rem;
  margin-right: 0.5rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
</style>
