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
        <div class="invite-form__title" style="color: #ff7649">Invite Users to Managr</div>
        <div class="invite-form__subtitle" style="color: #ddad3c">
          {{ $store.state.user.organizationRef.name }}
        </div>
        <div class="form_field">
          <FormField
            label="Email"
            @blur="userInviteForm.field.email.validate()"
            :errors="userInviteForm.field.email.errors"
            v-model="userInviteForm.field.email.value"
            placeholder=""
            large
            bordered
          />
        </div>
        <div class="form_field">
          <FormField
            label="Confirm Email"
            @blur="userInviteForm.field.confirmEmail.validate()"
            :errors="userInviteForm.field.confirmEmail.errors"
            v-model="userInviteForm.field.confirmEmail.value"
            large
            placeholder=""
            bordered
          />
        </div>

        <div class="dropdown">
          <FormField :errors="userInviteForm.field.userLevel.errors" label="User Level">
            <template v-slot:input>
              <DropDownSelect
                :items="userTypes"
                v-model="userInviteForm.field.userLevel.value"
                class="invite-form__dropdown"
                nullDisplay="Select user level"
                :itemsRef="userTypes"
                @input="userInviteForm.field.userLevel.validate()"
              />
            </template>
          </FormField>
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
          <div @click="onConfirmSlackInvite" style="display: flex; align-items: center">
            <CheckBox :checked="userInviteForm.field.slackInvite.value" />
            <span style="margin-top: 0.25rem; margin-left: 0.25rem; color: #beb5cc"
              >Send Slack Invite</span
            >
          </div>
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
      <div class="invite-list__title" style="color: #beb5cc">Your Team:</div>
      <div class="invite-list__section__container" style="margin-bottom: 1.5rem">
        <div class="invite-list__section__item invite-list__name">
          {{ user.fullName }}
        </div>
        <div class="invite-list__section__item invite-list__status">
          {{ user.userLevel == 'MANAGER' ? 'Team Leader(You)' : 'Rep(You)' }}
        </div>
        <div class="invite-list__section__item invite-list__status" style="color: #5f8cff">
          Registered
        </div>
      </div>
      <div v-for="member in team.list" :key="member.id" class="invite-list__section__container">
        <template v-if="member.id !== user.id">
          <div class="invite-list__section__item invite-list__name">
            {{ member.email }}
          </div>
          <div class="invite-list__section__item invite-list__status">
            {{ member.userLevel == 'MANAGER' ? 'Manager' : 'Rep' }}
          </div>
          <div :class="member.isActive ? 'registered' : 'unregistered'">
            {{ member.isActive ? 'Registered' : 'Pending..' }}
          </div>
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

export default {
  name: 'Invite',
  components: {
    DropDownSelect,
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
  },

  methods: {
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
        const res = await User.api.invite(this.userInviteForm.value)

        this.$Alert.alert({
          message: `<h3 style="color:white;"> An invitation was sent to ${res.data.email}</h3>`,
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
      }
    },

    resetData() {
      this.userInviteForm.reset()
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
  margin-left: 8%;
  ::v-deep .tn-dropdown__selection-container {
    border-radius: 4px;
    background-color: $white;
    border: 1px solid #eaebed;
    box-sizing: border-box;
    line-height: 1.29;
    letter-spacing: 0.5px;
    width: 18vw;
    height: 6vh;
    color: $panther;
  }

  ::v-deep .tn-dropdown__options__option {
    color: $panther-gray;
    font-weight: bold;
  }
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  color: $main-font-gray;
  text-align: center;
}

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
  background-color: white;
  color: $panther-orange;
  margin-top: 2.5rem;
  height: 2.5rem;
  width: 18vw;
  font-size: 16px;
  font-weight: bold;
}
.invite-button:hover {
  background-color: white;
  color: $panther-orange;
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
  width: 100%;
  height: 80vh;
  min-height: 30rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background-color: $panther;
  > .form_field {
    flex: 0 0 auto;
  }

  > .tn-input {
  }
  > .invite-form__dropdown {
    color: red;
  }
  &__title {
    @include base-font-styles();
    padding: 2rem 2rem;
    font-size: 16px;
    font-weight: bold;
    text-transform: uppercase;
    text-align: left;
  }
  &__actions {
    display: flex;
    flex-direction: column;
    align-items: center;
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
    font-size: 1rem;
    font-weight: bold;
    margin-bottom: 2rem;
  }
  &__container {
    background-color: $panther;
    border: none;
    width: 0%;
    min-width: 40vw;
    padding: 1.5rem 1rem 1.5rem 1.5rem;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 black;
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

  &__name {
    font-size: 0.75rem;
    font-weight: bold !important;
    font-family: #{$bold-font-family};
    text-align: left;
  }
  &__status {
    font-size: 0.75rem;
  }
}
.registered {
  width: 33%;
  font-size: 0.75rem;
  color: $panther-blue;
}
.unregistered {
  width: 33%;
  font-size: 0.75rem;
  color: $panther-turq;
}

.cancel-button {
  width: 19rem;
  margin-top: 0.5rem;
  position: relative;
  right: 1px;
  &:hover {
    cursor: pointer;
  }
}
</style>
