<template>
  <div class="customizations">
    <div class="row-spread">
      <button
        @click="goToWorkflows"
        v-if="
          activeUpdateOpportunityForm &&
          activeCreateContactForm &&
          user.userLevel == 'REP' &&
          user.onboarding
        "
        class="continue-button margin-right-large margin-top-large bouncy"
      >
        Continue to workflows
      </button>

      <p v-else class="sub__"></p>
    </div>

    <p class="sub__">Required Forms</p>
    <div class="customizations__cards">
      <div class="card">
        <div class="card__header">
          <div class="card-img extra-padding">
            <img height="18px;width:auto" src="@/assets/images/salesforce.png" />
          </div>

          <div class="card-img overlap">
            <img height="24px" src="@/assets/images/logo.png" />
          </div>
        </div>

        <div class="card__body">
          <h3>Update Opportunity</h3>
          <p class="active-workflow" v-if="activeUpdateOpportunityForm">Active</p>
          <p v-else class="inactive-red">Please Activate!</p>
          <button
            @click="goToUpdateOpp"
            class="green__button"
            :class="activeUpdateOpportunityForm ? 'white__button' : ''"
          >
            {{ activeUpdateOpportunityForm ? 'View + Edit' : 'Activate Form' }}
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <div class="card-img extra-padding">
            <img height="18px;width:auto" src="@/assets/images/salesforce.png" />
          </div>

          <div class="card-img overlap">
            <img height="24px" src="@/assets/images/logo.png" />
          </div>
        </div>

        <div class="card__body">
          <h3>Create Opportunity</h3>
          <p class="active-workflow" v-if="hasCreateOppForm">Active</p>
          <p v-else class="inactive">Inactive</p>
          <router-link :to="{ name: 'CreateOpportunity' }">
            <button class="green__button" :class="hasCreateOppForm ? 'white__button' : ''">
              {{ hasCreateOppForm ? 'View + Edit' : 'Activate Form' }}
            </button>
          </router-link>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <div class="card-img extra-padding">
            <img height="18px;width:auto" src="@/assets/images/salesforce.png" />
          </div>

          <div class="card-img overlap">
            <img height="24px" src="@/assets/images/logo.png" />
          </div>
        </div>

        <div class="card__body">
          <h3>Create Contacts</h3>
          <p v-if="activeCreateContactForm" class="active-workflow">Active</p>
          <p v-else class="inactive">Inactive</p>
          <button @click="goToCreate" class="green__button">Activate Form</button>
        </div>
      </div>
    </div>

    <p class="sub__">Optional Forms</p>
    <div class="customizations__cards">
      <div class="card">
        <div class="card__header">
          <div class="card-img extra-padding">
            <img height="18px;width:auto" src="@/assets/images/salesforce.png" />
          </div>

          <div class="card-img overlap">
            <img height="24px" src="@/assets/images/logo.png" />
          </div>
        </div>

        <div class="card__body">
          <h3>Update Contacts</h3>
          <p class="active-workflow" v-if="hasUpdateContactForm">Active</p>
          <p v-else class="inactive">Inactive</p>
          <router-link :to="{ name: 'UpdateContacts' }">
            <button class="green__button">Activate Form</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <div class="card-img extra-padding">
            <img height="18px;width:auto" src="@/assets/images/salesforce.png" />
          </div>

          <div class="card-img overlap">
            <img height="24px" src="@/assets/images/logo.png" />
          </div>
        </div>

        <div class="card__body">
          <h3>Create Lead</h3>
          <p class="active-workflow" v-if="hasCreateLeadForm">Active</p>
          <p v-else class="inactive">Inactive</p>
          <router-link :to="{ name: 'CreateLeads' }">
            <button class="green__button">Activate Form</button>
          </router-link>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <div class="card-img extra-padding">
            <img height="18px;width:auto" src="@/assets/images/salesforce.png" />
          </div>

          <div class="card-img overlap">
            <img height="24px" src="@/assets/images/logo.png" />
          </div>
        </div>

        <div class="card__body">
          <h3>Update Lead</h3>
          <p class="active-workflow" v-if="hasUpdateLeadForm">Active</p>
          <p class="inactive">Inactive</p>
          <router-link :to="{ name: 'UpdateLeads' }">
            <button class="green__button">Activate Form</button>
          </router-link>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <div class="card-img extra-padding">
            <img height="18px;width:auto" src="@/assets/images/salesforce.png" />
          </div>

          <div class="card-img overlap">
            <img height="24px" src="@/assets/images/logo.png" />
          </div>
        </div>

        <div class="card__body">
          <h3>Create Account</h3>
          <p class="active-workflow" v-if="hasCreateAccountForm">Active</p>
          <p class="inactive">Inactive</p>
          <router-link :to="{ name: 'CreateAccounts' }">
            <button class="green__button">Activate Form</button>
          </router-link>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <div class="card-img extra-padding">
            <img height="18px;width:auto" src="@/assets/images/salesforce.png" />
          </div>

          <div class="card-img overlap">
            <img height="24px" src="@/assets/images/logo.png" />
          </div>
        </div>

        <div class="card__body">
          <h3>Update Account</h3>
          <p class="active-workflow" v-if="hasUpdateAccountForm">Active</p>
          <p class="inactive">Inactive</p>
          <router-link :to="{ name: 'UpdateAccounts' }">
            <button class="green__button">Activate Form</button>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'

export default {
  name: 'Required',
  data() {
    return {
      createContactForm: null,
      updateOpportunityForm: null,
      activeUpdateOpportunityForm: null,
      activeCreateContactForm: null,

      hasCreateOppForm: null,
      hasUpdateContactForm: null,
      hasCreateLeadForm: null,
      hasCreateAccountForm: null,
      hasUpdateLeadForm: null,
      hasUpdateAccountForm: null,
      createOppForm: null,
      updateContactForm: null,
      createLeadForm: null,
      createAccountForm: null,
      updateLeadForm: null,
      updateAccountForm: null,
    }
  },
  watch: {
    updateOpportunityForm: 'hasOppForm',
    createContactForm: 'hasContactForm',

    createOppForm: 'checkCreateOpp',
    updateContactForm: 'checkUpdateContact',
    createLeadForm: 'checkCreateLead',
    createAccountForm: 'checkCreateAccount',
    updateLeadForm: 'checkUpdateLead',
    updateAccountForm: 'checkUpdateAccount',
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  created() {
    this.getForms()
  },
  methods: {
    hasOppForm() {
      let fields = this.updateOpportunityForm[0].fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
      if (fields.length > 2) {
        this.activeUpdateOpportunityForm = true
      }
    },
    hasContactForm() {
      let fields = this.createContactForm[0].fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
      if (fields.length > 0) {
        this.activeCreateContactForm = true
      }
    },
    checkCreateOpp() {
      let fields = this.createOppForm[0].fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
      if (fields.length > 0) {
        this.hasCreateOppForm = true
      }
    },
    checkUpdateContact() {
      let fields = this.updateContactForm[0].fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
      if (fields.length > 0) {
        this.hasUpdateContactForm = true
      }
    },
    checkCreateLead() {
      let fields = this.createLeadForm[0].fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
      if (fields.length > 0) {
        this.hasCreateLeadForm = true
      }
    },
    checkCreateAccount() {
      let fields = this.createAccountForm[0].fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
      if (fields.length > 0) {
        this.hasCreateAccountForm = true
      }
    },
    checkUpdateLead() {
      let fields = this.updateLeadForm[0].fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
      if (fields.length > 0) {
        this.hasUpdateLeadForm = true
      }
    },
    checkUpdateAccount() {
      let fields = this.updateAccountForm[0].fieldsRef.filter(
        (field) => field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments',
      )
      if (fields.length > 0) {
        this.hasUpdateAccountForm = true
      }
    },
    async getForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.createContactForm = res.filter(
          (form) => form.formType === 'CREATE' && form.resource === 'Contact',
        )
        this.updateOpportunityForm = res.filter(
          (form) => form.formType === 'UPDATE' && form.resource === 'Opportunity',
        )

        this.createOppForm = res.filter(
          (form) => form.formType === 'CREATE' && form.resource === 'Opportunity',
        )
        this.updateContactForm = res.filter(
          (form) => form.formType === 'UPDATE' && form.resource === 'Contact',
        )
        this.createLeadForm = res.filter(
          (form) => form.formType === 'CREATE' && form.resource === 'Lead',
        )
        this.createAccountForm = res.filter(
          (form) => form.formType === 'CREATE' && form.resource === 'Account',
        )
        this.updateLeadForm = res.filter(
          (form) => form.formType === 'UPDATE' && form.resource === 'Lead',
        )
        this.updateAccountForm = res.filter(
          (form) => form.formType === 'UPDATE' && form.resource === 'Account',
        )
      } catch (error) {
        console.log(error)
      }
    },
    goToUpdateOpp() {
      this.$router.push({ name: 'UpdateOpportunity' })
    },
    goToCreate() {
      this.$router.push({ name: 'CreateContacts' })
    },
    goToWorkflows() {
      this.$router.push({ name: 'CreateNew' })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
.customizations {
  padding: 0px 8px 0px 80px;
  margin-top: -40px;
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    border-radius: 0.5rem;
  }
}
.sub__ {
  font-size: 14px;
  color: $light-gray-blue;
  padding: 0;
}
// .card:hover {
//   box-shadow: 1px 2px 2px $very-light-gray;
//   transform: scale(1.015);
// }
.card {
  background-color: $white;
  padding: 16px 24px;
  border: 1px solid #e8e8e8;
  margin-right: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  width: 380px;
  min-height: 140px;
  &__header {
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    // border-radius: 6px;
    // padding: 4px 8px;
    // background-color: $off-white;
    // border: 1px solid $soft-gray;
    img {
      margin: 0;
      padding: 0;
    }
  }
  &__body {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin-left: 12px;
    h3 {
      margin: 0;
      padding: 0;
      font-size: 16px;
    }
    p {
      font-size: 13px;
    }
  }
}
.inactive {
  color: $very-light-gray;
  background-color: $off-white;
  border-radius: 6px;
  font-size: 14px;
  padding: 4px 8px;
}
.inactive-red {
  color: $coral;
  background-color: $light-red;
  border-radius: 6px;
  font-size: 14px;
  padding: 4px 8px;
}
.active-workflow {
  color: $dark-green;
  background-color: $white-green;
  border-radius: 6px;
  font-size: 14px;
  padding: 4px 8px;
  cursor: text;
  img {
    height: 1rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
    margin-left: 0.5rem;
  }
}
.card-img {
  background-color: white;
  border-radius: 100%;
  padding: 6px 8px 2px 4px;
  box-shadow: 1px 1px 1px $very-light-gray;
}
.extra-padding {
  padding: 10px 8px 6px 8px;
}
.overlap {
  z-index: 2;
  margin-left: -12px;
  box-shadow: 1px 1px 0.5px 0.5px $very-light-gray;
  // background-color: white;
}
.green__button {
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 11px;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  border: none;
}
.white__button {
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 11px;
  color: $dark-green;
  background-color: white;
  border: 0.5px solid $dark-green;
  cursor: pointer;
}

a {
  color: $dark-green;
  text-decoration: none;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
  transition: all 0.5s;
}
a:hover {
  transform: scale(1.025);
}
ul {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.margin-top-large {
  margin-top: 2rem;
}
.margin-right-large {
  margin-right: 3.25rem;
}
.row-spread {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  margin-top: -24px;
}
.continue-button {
  padding: 0.5rem 1rem;
  background-color: $dark-green;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}
</style>
