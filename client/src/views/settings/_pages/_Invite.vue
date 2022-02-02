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
        <h2 class="invite-form__title">Invite Users via Slack</h2>
        <h2 class="invite-form__subtitle" style="color: #199e54; margin-top: -4rem">
          {{ $store.state.user.organizationRef.name }}
        </h2>
        <div
          style="display: flex; justify-content: center; flex-direction: column; margin-top: -3rem"
        >
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <p style="margin-left: -2.2rem">Slack Users:</p>
            <FormField>
              <template v-slot:input>
                <DropDownSearch
                  :items.sync="slackMembers.members"
                  v-model="userInviteForm.field.slackId.value"
                  displayKey="realName"
                  valueKey="id"
                  nullDisplay="Search Users"
                  :hasNext="!!slackMembers.nextCursor"
                  @load-more="listUsers(slackMembers.nextCursor)"
                  searchable
                  local
                >
                </DropDownSearch>
              </template>
            </FormField>
          </div>
          <div style="display: flex; align-items: flex-start; flex-direction: column">
            <p style="margin-left: -2.2rem">User Level:</p>
            <FormField>
              <template v-slot:input>
                <DropDownSearch
                  :items.sync="userTypes"
                  v-model="userInviteForm.field.userLevel.value"
                  nullDisplay="Select user level"
                  local
                  searchable
                  valueKey="value"
                  @input="userInviteForm.field.userLevel.validate()"
                />
              </template>
            </FormField>
          </div>
        </div>
        <!-- <div class="dropdown">
          <FormField :errors="userInviteForm.field.role.errors" label="Role">
            <template v-slot:input>
              <DropDownSelect
                :items="userRoles"
                valueKey="key"
                displayKey="name"
                v-model="userInviteForm.field.role.value"
                :itemsRef="userRoles"
                class="invite-form__dropdown"
                nullDisplay="Select user role"
                @input="userInviteForm.field.role.validate()"
              />
            </template>
          </FormField>
        </div> -->
        <div class="invite-form__actions">
          <!-- <div @click="onConfirmSlackInvite" style="display: flex; align-items: center">
            <CheckBox :checked="userInviteForm.field.slackInvite.value" />
            <span style="margin-top: 0.25rem; margin-left: 0.25rem">Send Slack Invite</span>
          </div> -->
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
        <!-- <div style="color: white" class="invite-list__section__item invite-list__status">
          Active workflows: {{user.}}
        </div> -->
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
          <!-- <div class="invite-list__section__item invite-list__status">
            <p>3</p>
          </div> -->
        </template>
      </div>
    </div>
  </div>
</template>
<script>
import User from '@/services/users'
import { UserInviteForm } from '@/services/users/forms'
import DropDownSelect from '@thinknimble/dropdownselect'
import Organization from '@/services/organizations'
import CollectionManager from '@/services/collectionManager'
import Modal from '../../../components/InviteModal'
import Button from '@thinknimble/button'
import CheckBox from '@/components/CheckBoxUpdated'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import FormField from '@/components/forms/FormField'
import SlackOAuth, { SlackUserList } from '@/services/slack'
import DropDownSearch from '@/components/DropDownSearch'
export default {
  name: 'Invite',
  components: {
    DropDownSelect,
    DropDownSearch,
    Modal,
    PulseLoadingSpinnerButton,
    FormField,
    CheckBox,
  },
  props: {
    inviteOpen: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
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
  watch: {},
  async created() {
    this.refresh()
    await this.listUsers()
  },
  methods: {
    console(wrd) {
      console.log(wrd)
    },
    async listUsers(cursor = null) {
      const res = await SlackOAuth.api.listUsers(cursor)
      const results = new SlackUserList({
        members: [...this.slackMembers.members, ...res.members],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.slackMembers = results
      // console.log(res)
      // console.log(results)
      // console.log(this.slackMembers)
    },
    onConfirmSlackInvite() {
      if (!this.userInviteForm.field.slackInvite.value) {
        let confirmSlack = confirm(
          'This will post a message to the channel you selected tagging the user to sign up',
        )
        if (confirmSlack) {
          this.userInviteForm.field.slackInvite.value = true
        }
      } else {
        this.userInviteForm.field.slackInvite.value = false
      }
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
  // beforeMount() {
  //   console.log(this.user)
  // },
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

.complete {
  border-bottom: 2.9px solid $dark-green;
  border-radius: 10%;
  margin-right: 0.5rem;
  color: $base-gray;
}
.incomplete {
  border-bottom: 2px solid $coral;
  color: $base-gray;
  border-radius: 10%;
}
.back-logo {
  position: absolute;
  opacity: 0.06;
  filter: alpha(opacity=50);
  height: 28%;
  margin-top: -7rem;
  margin-left: -2rem;
}
::v-deep .tn-dropdown__selection-container {
  box-shadow: 3px 4px 7px $very-light-gray;
  border: none;
}

::v-deep .tn-dropdown__options__container {
  width: 17vw;
  margin-left: -2.2rem;
}

::v-deep .tn-dropdown__selected-items__item-selection {
  color: $panther;
}

.active {
  border-bottom: 2px solid $dark-green;
  padding: 0.2rem;
  border-radius: 10%;
  margin-right: 0.25rem;
}
.inactive {
  border-bottom: 2px solid $coral;
  padding: 0.2rem;
  border-radius: 10%;
  margin-right: 0.25rem;
}
.invite-container {
  display: flex;
  flex-flow: row;
  justify-content: center;
  // height: 80vh;
  width: 80%;
}
/*
Override dropdown select input field
*/
.dropdown {
}
::v-deep .tn-dropdown__selection-container {
  min-width: 17vw;
  margin-left: -2.2rem;
}
// ::v-deep .tn-dropdown__options__option {
//   color: $base-gray;
//   font-weight: bold;
// }
form,
.success-prompt {
  //   margin-top: 3.125rem;
  width: 100%;
  background-color: $white;
  height: 50vh;
  justify-content: space-evenly;
}
.checkbox {
  width: auto;
  height: auto;
}
.invite-button {
  background-color: $dark-green;
  color: white;
  margin-top: 2.5rem;
  height: 2.5rem;
  width: 18vw;
  font-size: 16px;
  font-weight: bold;
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
  height: 90vh;
  display: flex;
  align-items: center;
  // justify-content: center;
  flex-direction: column;
  background-color: white;
  color: $base-gray;
  > .form_field {
    flex: 0 0 auto;
  }
  > .tn-input {
    width: 12rem;
  }
  > .invite-form__dropdown {
    color: red;
  }
  &__title {
    font-weight: bold;
    text-align: left;
  }
  &__actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: -4rem;
  }
}
.invite-form__organization {
  height: 2.5rem;
  width: 20rem;
  display: flex;
  align-items: center;
  @include input-field();
}
.invite-list {
  &__title {
    font-weight: bold;
    margin-bottom: 2rem;
  }
  &__container {
    background-color: $white;
    border: none;
    color: $base-gray;
    min-width: 60vw;
    padding: 1.5rem 0rem 1.5rem 1rem;
    border-radius: 5px;
    box-shadow: 3px 4px 7px $very-light-gray;
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

    &__heading {
      width: 25%;
    }
  }
  &__name {
    font-size: 0.75rem;
    font-weight: bold !important;
    font-family: #{$bold-font-family};
    text-align: left;
    color: #f2fff8;
  }
  &__status {
    font-size: 0.75rem;
  }
}
.registered {
  width: 33%;
  font-size: 0.75rem;
  color: $dark-green;
}
.unregistered {
  width: 33%;
  font-size: 0.75rem;
  color: $panther-silver;
}
.cancel-button {
  margin-top: 1rem;
  position: relative;
  right: 1px;
  &:hover {
    cursor: pointer;
  }
}
::v-deep .dimmed {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>