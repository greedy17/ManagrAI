<template>
  <div class="customizations">
    <div>
      <h3>Optional Actions</h3>
      <p class="sub__">Map Slack fields to the corresponding SFDC fields.</p>
    </div>

    <div class="customizations__cards">
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
            <button class="activate-button">View + Edit</button>
          </router-link>
        </div>
      </div>
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
            <button class="activate-button">View + Edit</button>
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
            <button class="activate-button">View + Edit</button>
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
            <button class="activate-button">View + Edit</button>
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
            <button class="activate-button">View + Edit</button>
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
            <button class="activate-button">View + Edit</button>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'

export default {
  name: 'Custom',
  watch: {
    createOppForm: 'checkCreateOpp',
    updateContactForm: 'checkUpdateContact',
    createLeadForm: 'checkCreateLead',
    createAccountForm: 'checkCreateAccount',
    updateLeadForm: 'checkUpdateLead',
    updateAccountForm: 'checkUpdateAccount',
  },
  data() {
    return {
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
  created() {
    this.getForms()
  },

  computed: {
    user() {
      return this.$store.state.user
    },
  },
  methods: {
    async getForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

#plus {
  filter: invert(90%);
}
.activate-button {
  background-color: $dark-green;
  color: white;
  font-size: 14px;
  border: none;
  border-radius: 0.3rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
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
.customizations {
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 3.5rem;
  margin-left: 20vw;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    border-radius: 0.5rem;
  }
}
.sub__ {
  font-size: 14px;
  margin-top: -0.5rem;
  color: $gray;
}
.card:hover {
  transform: scale(1.015);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.card {
  background-color: white;
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
</style>
