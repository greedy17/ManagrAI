<template>
  <div class="invite-container">
    <Modal
      v-if="inviteOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetData()
        }
      "
    >
      <form class="invite-form" @submit.prevent="handleInvite">
        <div class="header">
          <h3 class="invite-form__title">Invite Users via Slack</h3>
          <h4 class="invite-form__subtitle">
            {{ $store.state.user.organizationRef.name }}
          </h4>
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
                  style="min-width: 15vw"
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
                      <img src="@/assets/images/plusOne.png" alt="" />
                    </p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.png" alt="" />
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
                  style="min-width: 15vw"
                  selectLabel="Enter"
                  label="key"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.png" alt="" />
                      Select User Level
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
        </div>
        <div class="invite-form__actions">
          <template>
            <PulseLoadingSpinnerButton
              @click="handleInvite"
              class="invite-button"
              text="Invite"
              :loading="loading"
              >Invite</PulseLoadingSpinnerButton
            >
            <div class="cancel-button" @click="handleCancel">Cancel</div>
          </template>
        </div>
      </form>
    </Modal>
    <div class="invite-list__container">
      <div class="key">
        <div class="left-key">
          <h2>The {{ $store.state.user.organizationRef.name }} Team:</h2>
        </div>
        <div class="right-key">
          <p class="complete">Complete</p>
          <p class="incomplete">Incomplete</p>
        </div>
      </div>

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
      </div>

      <div class="invite-list__section__container">
        <img class="back-logo" src="@/assets/images/logo.png" />
        <div
          style="display: flex; align-items: flex-start; color: #199e54; font-size: 13px"
          class="invite-list__section__item col"
        >
          {{ user.fullName }}
          <p style="color: #beb5cc; font-size: 0.65rem; margin-top: 0.25rem">{{ user.email }}</p>
        </div>
        <div
          style="display: flex; align-items: flex-start; font-size: 13px"
          class="invite-list__section__item"
        >
          {{ user.userLevel == 'MANAGER' ? 'Team Leader(You)' : 'Rep(You)' }}
        </div>
        <div
          style="display: flex; align-items: flex-start; font-size: 13px"
          class="invite-list__section__item"
        >
          Registered
        </div>

        <div
          style="display: flex; align-items: flex-start"
          class="invite-list__section__item invite-list__status"
        >
          <span :class="user.slackRef ? 'active' : 'inactive'">
            <img src="@/assets/images/slackLogo.png" style="height: 0.8rem" alt="" />
          </span>
          <span :class="user.hasSalesforceIntegration ? 'active' : 'inactive'">
            <img src="@/assets/images/salesforce.png" style="height: 0.8rem" alt="" />
          </span>
          <span :class="user.hasZoomIntegration ? 'active' : 'inactive'">
            <img src="@/assets/images/zoom.png" alt="" style="height: 0.8rem" />
          </span>
          <span :class="user.nylasRef ? 'active' : 'inactive'">
            <img src="@/assets/images/gmailCal.png" alt="" style="height: 0.8rem" />
          </span>
        </div>
      </div>
      <div v-for="member in team.list" :key="member.id" class="invite-list__section__container">
        <template v-if="member.id !== user.id">
          <div
            style="display: flex; align-items: flex-start; font-size: 13px"
            class="invite-list__section__item col"
          >
            {{ member.firstName ? member.firstName : 'Pending' }}
            <p style="color: #beb5cc; font-size: 0.65rem; margin-top: 0.25rem">
              {{ member.email }}
            </p>
          </div>
          <div
            v-if="member.userLevel == 'MANAGER'"
            style="display: flex; align-items: flex-start; font-size: 13px"
            class="invite-list__section__item"
          >
            Manager
          </div>
          <div
            v-else-if="member.userLevel == 'SDR'"
            style="display: flex; align-items: flex-start; font-size: 13px"
            class="invite-list__section__item"
          >
            SDR
          </div>
          <div
            v-else-if="member.userLevel == 'REP'"
            style="display: flex; align-items: flex-start; font-size: 13px"
            class="invite-list__section__item"
          >
            REP
          </div>
          <div
            style="display: flex; align-items: flex-start; font-size: 13px"
            class="invite-list__section__item"
          >
            {{ member.isActive ? 'Registered' : 'Pending..' }}
          </div>
          <div
            style="display: flex; align-items: flex-start"
            class="invite-list__section__item invite-list__status"
          >
            <span :class="member.slackRef ? 'active' : 'inactive'">
              <img src="@/assets/images/slackLogo.png" style="height: 0.8rem" alt="" />
            </span>
            <span :class="member.hasSalesforceIntegration ? 'active' : 'inactive'">
              <img src="@/assets/images/salesforce.png" style="height: 0.8rem" alt="" />
            </span>
            <span :class="member.hasZoomIntegration ? 'active' : 'inactive'">
              <img src="@/assets/images/zoom.png" alt="" style="height: 0.8rem" />
            </span>
            <span :class="member.nylasRef ? 'active' : 'inactive'">
              <img src="@/assets/images/gmailCal.png" alt="" style="height: 0.8rem" />
            </span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
<script>
import User from '@/services/users'
import { UserInviteForm } from '@/services/users/forms'
import Organization from '@/services/organizations'
import CollectionManager from '@/services/collectionManager'
import Modal from '../../../components/InviteModal'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import FormField from '@/components/forms/FormField'
import SlackOAuth, { SlackUserList } from '@/services/slack'
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
  },
  data() {
    return {
      selectedMember: null,
      selectedLevel: null,
      sendSlackInvite: false,
      organization: null,
      organizations: CollectionManager.create({ ModelClass: Organization }),
      organizationRef: null,
      slackMembers: new SlackUserList(),
      inviteRecipient: '',
      selectedUserType: User.types.REP,
      userTypes: [
        { key: 'Manager', value: User.types.MANAGER },
        { key: 'Representative', value: User.types.REP },
        { key: 'SDR', value: User.types.SDR },
      ],
      showInvited: true,
      team: CollectionManager.create({ ModelClass: User }),
      user: null,
      userRoles: User.roleChoices,
      loading: false,
      userInviteForm: new UserInviteForm({
        role: User.roleChoices[0].key,
        userLevel: User.types.REP,
        organization: this.$store.state.user.organization,
      }),
    }
  },
  async created() {
    this.refresh()
    await this.listUsers()
  },
  methods: {
    mapMember() {
      this.userInviteForm.field.slackId.value = this.selectedMember.id
    },
    mapUserLevel() {
      this.userInviteForm.field.userLevel.value = this.selectedLevel.value
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
      this.user = this.$store.state.user
      if (!this.user.isAdmin && !this.user.userLevel === 'MANAGER') {
        this.$router.push({ name: 'Integrations' })
      }
      if (this.user.isStaff) {
        await this.organizations.refresh()
      }
      this.organization = this.$store.state.user.organization
      this.team.refresh()
    },
    async handleCancel() {
      await this.refresh()
      this.resetData()
      this.$emit('cancel')
    },
    async handleInvite() {
      // reset component data when submission begins, in case of prior request
      this.loading = true
      this.userInviteForm.validate()
      if (!this.userInviteForm.isValid) {
        this.loading = false
        this.$Alert.alert({
          type: 'error',
          message: 'Please check form errors',
          timeout: 2000,
        })
        return
      }
      // check form data for this request
      try {
        this.userInviteForm.field.email.value = this.slackMembers.members.filter(
          (member) => member.id == this.userInviteForm.field.slackId.value,
        )[0].profile.email
        const res = await User.api.invite(this.userInviteForm.value)
        console.log(res)
        this.$Alert.alert({
          message: 'Your invitation was sent',
          type: 'success',
          timeout: 3000,
        })
        await this.refresh()
        this.resetData()
      } catch (e) {
        let err = e.response.data
        if (err.email) {
          this.$Alert.alert({
            type: 'error',
            message: `Looks like a ${err.email}`,
            timeout: 2000,
          })
        }
      } finally {
        this.loading = false
        this.inviteOpen = !this.inviteOpen
      }
    },
    resetData() {
      this.userInviteForm.field.organization.value = this.$store.state.user.organization
    },
  },
  computed: {
    isStaff() {
      return this.$store.state.user.isStaff
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.col {
  display: flex;
  flex-direction: column;
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
.section-header {
  font-size: 15px;
  font-weight: bold;
}
.key {
  display: flex;
  align-items: center;
  width: 100%;
  font-size: 0.75rem;
  margin-bottom: 1.5rem;
}
.right-key {
  display: flex;
  flex-direction: row;
  width: 35%;
  justify-content: flex-start;
}
.left-key {
  display: flex;
  width: 100%;
  flex-direction: row;
  justify-self: flex-start;
}
.header {
  margin-top: -1rem;
}
.complete {
  border-bottom: 2.9px solid $dark-green;

  margin-right: 0.5rem;
  color: $base-gray;
}
.incomplete {
  border-bottom: 2px solid $coral;
  color: $base-gray;
}
.back-logo {
  position: absolute;
  opacity: 0.06;
  filter: alpha(opacity=50);
  height: 28%;
  margin-top: -7rem;
  margin-left: -2rem;
}

.active {
  border-bottom: 2px solid $dark-green;
  padding: 0.2rem;

  margin-right: 0.25rem;
}
.inactive {
  border-bottom: 2px solid $coral;
  padding: 0.2rem;

  margin-right: 0.25rem;
}
.invite-container {
  display: flex;
  flex-flow: row;
  justify-content: center;
  width: 80%;
}
form {
  width: 100%;
  background-color: $white;
  height: 50vh;
  justify-content: space-evenly;
}
.invite-button {
  background-color: $dark-green;
  color: white;
  margin-top: 2.5rem;
  width: 15vw;
  font-size: 16px;
  box-shadow: none;
}
button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 2.5rem;
  width: 19rem;
  font-size: 14px;
}
.invite-form {
  border: none;
  border-radius: 0.75rem;
  min-width: 27vw;
  min-height: 64vh;
  display: flex;
  align-items: center;
  flex-direction: column;
  background-color: white;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
  }
  &__subtitle {
    color: $dark-green;
  }
  &__actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: -4rem;
  }
}
.invite-list {
  &__container {
    background-color: $white;
    border: 1px solid #e8e8e8;
    color: $base-gray;
    width: 60vw;
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
      margin-bottom: 0.5rem;
    }
    &__item {
      width: 33%;
      overflow-wrap: break-word;
    }
  }
  &__status {
    font-size: 0.75rem;
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
</style>