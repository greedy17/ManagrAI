<template>
  <div class="invite-container">
    <Modal v-if="inviteOpen" dimmed @close-modal="() => (inviteOpen = false)">
      <form class="invite-form" v-if="!success" @submit.prevent="handleInvite">
        <div class="errors">
          <!-- client side validations -->

          <div
            v-if="isFormValid !== null && !isFormValid && errors.emailIsBlank"
          >Fields may not be blank.</div>
          <div
            v-if="isFormValid !== null && !isFormValid && errors.emailsDontMatch"
          >Fields must match.</div>
          <div
            v-if="isFormValid !== null && !isFormValid && errors.invalidEmail"
          >Must be a valid email address.</div>
          <div
            v-if="isFormValid !== null && !isFormValid && errors.invalidUserType"
          >Must be a valid user type</div>
          <!-- server side validations -->
          <div
            v-if="success !== null && !success && errors[500]"
          >Something went wrong. Please try again later.</div>
          <div
            v-if="success !== null && !success && errors[400]"
          >The provided email is associated with an existing account.</div>
        </div>
        <div v-if="isStaff" class="group">
          <DropDownSelect
            :items="organizations.list"
            :itemsRef.sync="organizationRef"
            v-model="organization"
            displayKey="name"
            valueKey="id"
            nullDisplay="Select an Org"
            searchable
            :haseNext="!!organizations.pagination.next"
          />
        </div>
        <!-- type="text" instead of type="email" so we can control UI when invalid -->
        <div class="invite-form__title">Email</div>
        <input class="invite-form__form-input" v-model="email" type="text" />

        <div class="invite-form__title">Confirm Email</div>
        <input class="invite-form__form-input" v-model="emailConfirmation" type="text" />

        <div class="invite-form__title">Role</div>
        <div class="group">
          <DropDownSelect
            :items="userTypes"
            v-model="selectedUserType"
            class="invite-form__dropdown"
          />
        </div>

        <button type="submit">Invite</button>
        <div class="cancel-button" @click="handleCancel">Cancel</div>
      </form>
      <div v-if="success" class="success-prompt">
        <h2>Success</h2>
        <p>
          An invitation will be sent to:
          <span :style="{ fontWeight: 'bold' }">{{ email }}</span>.
        </p>
        <button @click="resetData">Send Another</button>
        <div class="cancel-button" @click="handleCancel">Close</div>
      </div>
    </Modal>
    <div class="invite-list__container">
      <div class="invite-list__title">Your Team</div>
      <div class="invite-list__section__container" style="margin-bottom: 1.5rem">
        <div class="invite-list__section__item invite-list__name">{{ user.fullName }}</div>
        <div
          class="invite-list__section__item invite-list__status"
        >{{ user.userLevel == 'Manager' ? 'Team Leader(You)' : 'Rep(You)' }}</div>
        <div class="invite-list__section__item invite-list__status">Registered</div>
      </div>
      <div
        v-for="member in team.list"
        :key="member.id"
        class="invite-list__section__container"
        v-if="member.id !==user.id"
      >
        <div class="invite-list__section__item invite-list__name">{{ member.email }}</div>
        <div
          class="invite-list__section__item invite-list__status"
        >{{ member.userLevel == 'Manager' ? 'Team Leader' : 'Rep' }}</div>
        <div
          class="invite-list__section__item invite-list__status"
        >{{ member.isActive ? 'Registered' : 'Pending' }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'
import DropDownSelect from '@thinknimble/dropdownselect'
import Organization from '@/services/organizations'
import CollectionManager from '@/services/collectionManager'
import Pagination from '@/services/pagination'
import Modal from '../../../components/Modal'

export default {
  name: 'Invite',
  components: {
    DropDownSelect,
    Modal,
  },
  props: {
    inviteOpen: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      email: '',
      emailConfirmation: '', // TODO(Bruno 4-9-20): Make this dynamic
      isFormValid: null,
      errors: {},
      success: null,
      link: '', // NOTE(Bruno 4-20-20): temporary, for staging purposes
      organization: null,
      organizations: CollectionManager.create({ ModelClass: Organization }),
      organizationRef: null,
      selectedUserType: User.types.REP,
      userTypes: [
        { key: 'Manager', value: User.types.MANAGER },
        { key: 'Representative', value: User.types.REP },
      ],
      showInvited: true,

      team: CollectionManager.create({ ModelClass: User }),

      user: null,
    }
  },
  watch: {},
  async created() {
    this.user = this.$store.state.user
    if (this.isStaff) {
      await this.organizations.refresh()
    } else {
      this.organization = this.$store.state.user.organization
    }

    this.team.refresh()
  },

  methods: {
    handleCancel() {
      this.$emit('cancel')
    },
    handleInvite() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}
      // check form data for this request
      let validationResults = this.clientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      let invitePromise = User.api.invite(this.email, this.selectedUserType, this.organization)

      invitePromise
        .then(response => {
          this.link = response.data.activation_link // NOTE(Bruno 4-20-20): this line is temporary, for staging purposes
          this.success = true
        })
        .catch(error => {
          // NOTE: all form field-error validations are completed client side
          this.success = false
          let { status } = error.response
          if (status >= 500) {
            this.errors = { 500: true }
          } else if (status >= 400) {
            // The email already belongs to account, be its state INVITED or otherwise
            this.errors = { 400: true }
          }
        })
      this.team.refresh()
    },
    clientSideValidations() {
      let formErrors = {
        emailIsBlank: this.emailIsBlank,
        emailsDontMatch: this.emailsDontMatch,
        invalidEmail: this.invalidEmail,
        invalidOrganization: this.invalidOrganization,
        invalidUserType: this.invalidUserType,
      }
      let isFormValid =
        !this.emailIsBlank &&
        !this.emailsDontMatch &&
        !this.invalidEmail &&
        !this.invalidOrganization &&
        !this.invalidUserType

      return [isFormValid, formErrors]
    },
    resetData() {
      this.email = ''
      this.emailConfirmation = ''
      this.type = User.USER_TYPE_MANAGER // TODO(Bruno 4-9-20): Make this dynamic
      this.isFormValid = null
      this.errors = {}
      this.success = null
      this.link = '' // NOTE(Bruno 4-20-20): temporary, for staging purposes
      this.isIntegrationAccount = false
      this.organization = null
      this.selectedUserType = User.USER_TYPE_REP
    },
  },
  computed: {
    isStaff() {
      // checking isStaff to see if they can create organizations or invite special users
      // on the backend only superusers can do this
      return this.$store.state.user.isStaff
    },

    emailIsBlank() {
      return !this.email.length
    },
    emailsDontMatch() {
      return this.email !== this.emailConfirmation
    },
    invalidEmail() {
      // NOTE: this was taken from http://emailregex.com/
      // eslint-disable-next-line no-useless-escape
      let regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return !regex.test(this.email)
    },
    invalidOrganization() {
      return !this.organization
    },
    invalidUserType() {
      return !this.selectedUserType
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
  height: 80vh;

  width: 80%;
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
  display: flex;
  flex-flow: column;
  align-items: center;
  height: 50vh;

  justify-content: space-evenly;
}

.invite-form__form-input {
  width: 20rem;
  height: 2.5rem;
  @include input-field-white();
}
.checkbox {
  width: auto;
  height: auto;
}

button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 2.5rem;
  width: 19rem;
  font-size: 14px;
}
.group {
  display: flex;
  flex-direction: row-reverse;
  justify-content: center;
  align-items: center;
  > * {
    margin: 0.5rem;
  }
}

.invite-form {
  border: none;
  width: 100%;
  height: 50vh;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;

  > * {
  }

  &__title {
    width: 19rem;
    text-align: left;
    font-size: 14px;
    margin: 1rem 0 0.5rem 0;
  }

  &__dropdown {
    @include input-field-white();
    padding: 0;
    border: 1px solid #eaebed !important;
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
    border: solid 2px #dcdddf;
    width: 0%;
    min-width: 40vw;
    padding: 25px 12px 322px 37px;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(132, 132, 132, 0.26);
    display: flex;
    background-color: white;

    align-items: flex-start;
    flex-direction: column;
  }

  &__section {
    &__container {
      width: 100%;
      display: flex;
    }

    &__item {
      flex: 1;
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
.cancel-button {
  width: 19rem;
  margin-top: 0.5rem;
  &:hover {
    cursor: pointer;
  }
}
</style>
