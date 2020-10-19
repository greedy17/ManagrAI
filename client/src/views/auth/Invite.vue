<template>
  <div class="invite-container">
    <form class="invite-form" v-if="!success" @submit.prevent="handleInvite">
      <h2>Invite</h2>

      <div class="errors">
        <!-- client side validations -->

        <div v-if="isFormValid !== null && !isFormValid && errors.emailIsBlank">
          Fields may not be blank.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.emailsDontMatch">
          Fields must match.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.invalidEmail">
          Must be a valid email address.
        </div>
        <div v-if="isFormValid !== null && !isFormValid && errors.invalidUserType">
          Must be a valid user type
        </div>
        <!-- server side validations -->
        <div v-if="success !== null && !success && errors[500]">
          Something went wrong. Please try again later.
        </div>
        <div v-if="success !== null && !success && errors[400]">
          The provided email is associated with an existing account.
        </div>
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
      <input class="invite-form__form-input" v-model="email" type="text" placeholder="email" />
      <input
        class="invite-form__form-input"
        v-model="emailConfirmation"
        type="text"
        placeholder="confirm email"
      />

      <div class="group">
        <DropDownSelect :items="userTypes" v-model="selectedUserType" />
      </div>

      <button type="submit">Invite</button>
    </form>
    <div v-else class="success-prompt">
      <h2>Success</h2>
      <p>
        An invitation will be sent to:
        <span :style="{ fontWeight: 'bold' }">{{ email }}</span
        >.
      </p>
      <button @click="resetData">Send Another</button>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'
import DropDownSelect from '@thinknimble/dropdownselect'
import Organization from '@/services/organizations'
import CollectionManager from '@/services/collectionManager'

export default {
  name: 'Invite',
  components: {
    DropDownSelect,
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
      selectedUserType: User.USER_TYPE_REP,
    }
  },
  watch: {},
  async created() {
    if (this.isStaff) {
      await this.organizations.refresh()
    } else {
      this.organization = this.$store.state.user.organization
    }
  },

  methods: {
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
    isIntegrationEnabled() {
      // if the user isStaff and the org is integration enabled
      if (this.isStaff && this.organization) {
        let org = this.organizationRef
        return org.isExternalsyncenabled
      }
      return false
    },
    userTypes() {
      let userTypes = [
        { key: 'Manager', value: User.USER_TYPE_MANAGER },
        { key: 'Representative', value: User.USER_TYPE_REP },
      ]
      if (this.isIntegrationEnabled) {
        userTypes.push({ key: 'Integration', value: User.USER_TYPE_INTEGRATION })
      }
      return userTypes
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
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  color: $main-font-gray;
  text-align: center;
}

form,
.success-prompt {
  @include standard-border();
  margin-top: 3.125rem;
  width: 31.25rem;

  background-color: $white;
  display: flex;
  flex-flow: column;
  align-items: center;
}

.invite-form__form-input {
  width: 20rem;
  height: 2.5rem;
  @include input-field();
}
.checkbox {
  width: auto;
  height: auto;
}

button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 1.875rem;
  width: 9.375rem;
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
  display: flex;
  flex-direction: column;
  > * {
    margin-top: 1rem;
  }
}
.invite-form__organization {
  height: 2.5rem;
  width: 20rem;
  display: flex;
  align-items: center;
  @include input-field();
}
::v-deep .dropdown {
  // manually setting the style for the dropdown here
  // width is set on the parent class

  .dropdown-input-container {
    width: 100%;
    align-items: center;
    border: none;

    &.disabled {
      border: 1px solid gray;
    }
  }
}
</style>
