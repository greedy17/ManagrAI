<template>
  <div class="customizations">
    <div class="row-spread width-100 margin-top-negative">
      <div>
        <h4 style="color: 4d4e4c">Field Mapping</h4>
        <p class="margin-top-negative sub__">Map CRM fields to Managr</p>
      </div>
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
    </div>

    <p class="sub__ green-background">Required</p>
    <div class="customizations__cards">
      <div class="card">
        <div class="card__header">
          <h3>Update Opportunity</h3>
          <p class="active-workflow" v-if="activeUpdateOpportunityForm">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>
        <div class="card__body">
          <img style="margin-right: 1rem" class="card-img" src="@/assets/images/salesforce.png" />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(40%)"
            src="@/assets/images/plusOne.svg"
            alt=""
            id="plus"
          />
          <img style="height: 1.5rem" src="@/assets/images/logo.png" />
        </div>
        <div class="card__footer">
          <button @click="goToUpdateOpp" class="green__button">View + Edit</button>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h3>Create Opportunity</h3>
          <p class="active-workflow" v-if="hasCreateOppForm">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img
            style="height: 1.25rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img style="height: 1.5rem; margin-right: 0.5rem" src="@/assets/images/logo.png" alt="" />
        </div>
        <div class="card__footer">
          <router-link :to="{ name: 'CreateOpportunity' }">
            <button class="green__button">View + Edit</button>
          </router-link>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h3>Create Contacts</h3>
          <p v-if="activeCreateContactForm" class="active-workflow">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>
        <div class="card__body">
          <img style="margin-right: 1rem" class="card-img" src="@/assets/images/salesforce.png" />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(40%)"
            src="@/assets/images/plusOne.svg"
            alt=""
            id="plus"
          />
          <img style="height: 1.5rem" src="@/assets/images/logo.png" />
        </div>
        <div class="card__footer">
          <button @click="goToCreate" class="green__button">View + Edit</button>
        </div>
      </div>
    </div>
    <p class="sub__ margin-top">Optional</p>

    <div class="margin-left-negative customizations__cards">
      <div class="card">
        <div class="card__header">
          <h3>Update Contacts</h3>
          <p class="active-workflow" v-if="hasUpdateContactForm">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img
            style="height: 1.25rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img style="height: 1.5rem; margin-right: 0.5rem" src="@/assets/images/logo.png" alt="" />
        </div>
        <div class="card__footer">
          <router-link :to="{ name: 'UpdateContacts' }">
            <button class="green__button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Create Lead</h3>
          <p class="active-workflow" v-if="hasCreateLeadForm">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img
            style="height: 1.25rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img style="height: 1.5rem; margin-right: 0.5rem" src="@/assets/images/logo.png" alt="" />
        </div>
        <div class="card__footer">
          <router-link :to="{ name: 'CreateLeads' }">
            <button class="green__button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Update Lead</h3>
          <p class="active-workflow" v-if="hasUpdateLeadForm">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img
            style="height: 1.25rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img style="height: 1.5rem; margin-right: 0.5rem" src="@/assets/images/logo.png" alt="" />
        </div>
        <div class="card__footer">
          <router-link :to="{ name: 'UpdateLeads' }">
            <button class="green__button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Create Account</h3>
          <p class="active-workflow" v-if="hasCreateAccountForm">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img
            style="height: 1.25rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img style="height: 1.5rem; margin-right: 0.5rem" src="@/assets/images/logo.png" alt="" />
        </div>
        <div class="card__footer">
          <router-link :to="{ name: 'CreateAccounts' }">
            <button class="green__button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Update Account</h3>
          <p class="active-workflow" v-if="hasUpdateAccountForm">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img
            style="height: 1.25rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img style="height: 1.5rem; margin-right: 0.5rem" src="@/assets/images/logo.png" alt="" />
        </div>
        <div class="card__footer">
          <router-link :to="{ name: 'UpdateAccounts' }">
            <button class="green__button">View + Edit</button>
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
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 2rem;
  margin-left: 20vw;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    border-radius: 0.5rem;
  }
}
.sub__ {
  font-size: 14px;
  color: $gray;
}
.card:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
  transform: scale(1.015);
}
.card {
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 0.5rem;
  width: 24vw;
  margin-right: 1rem;
  margin-bottom: 1rem;
  transition: all 0.25s;
  &__header {
    height: 2rem;
    padding: 1.25rem 1rem;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid $soft-gray;
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 5rem;
    font-size: 13px;
  }
  &__footer {
    display: flex;
    align-items: center;
    height: 2rem;
    font-size: 14px;
    justify-content: space-evenly;
  }
}
.active-workflow {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0.3rem;
  margin-left: 0.5rem;
  border: 1px solid $soft-gray;
  background-color: white;
  border-radius: 0.3rem;
  color: $dark-green;
  font-size: 12px;
  cursor: text;
  img {
    height: 1rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
    margin-left: 0.5rem;
  }
}
.card-img {
  width: 2rem;
  height: 1.25rem;
}

.green__button {
  border-radius: 0.33rem;
  padding: 0.5rem 1rem;
  font-size: 14px;
  color: white;
  background-color: $dark-green;
  border: none;
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
.margin-top {
  margin-top: 0.5rem;
}
.margin-top-large {
  margin-top: 2rem;
}
.margin-top-negative {
  margin-top: -0.75rem;
}
.margin-bottom {
  margin-bottom: 1rem;
}
.invert {
  filter: invert(60%);
}
.margin-left {
  margin-left: 1rem;
}
.margin-left-negative {
  margin-left: -2rem;
}
.margin-right-large {
  margin-right: 3.25rem;
}
.row-spread {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
}
.width-100 {
  width: 100%;
}
.continue-button {
  padding: 0.5rem 1rem;
  background-color: $dark-green;
  color: white;
  border: none;
  border-radius: 3px;
}
</style>
