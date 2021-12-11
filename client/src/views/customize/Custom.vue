<template>
  <div class="customizations">
    <!-- <ul>
      <router-link :to="{ name: 'SlackFormSettings' }"
        >Stage <span style="font-weight: bold">Specific</span>
      </router-link>
     
      <router-link :to="{ name: 'UpdateContacts' }"
        >Update <span style="font-weight: bold">Contacts</span>
      </router-link>
      <router-link :to="{ name: 'CreateAccounts' }"
        >Create <span style="font-weight: bold">Accounts</span>
      </router-link>
      <router-link :to="{ name: 'UpdateAccounts' }"
        >Update <span style="font-weight: bold">Accounts</span>
      </router-link>
      <router-link :to="{ name: 'UpdateLeads' }"
        >Update <span style="font-weight: bold">Leads</span>
      </router-link>
      <router-link :to="{ name: 'CreateLeads' }"
        >Create <span style="font-weight: bold">Leads</span>
      </router-link>
    </ul> -->

    <div style="display: flex; align-items: center; flex-direction: column">
      <h2 style="color: black">Optional Field Mapping</h2>
      <p style="color: #5d5e5e; margin-top: -0.5rem" class="sub__">
        Map Slack fields to the corresponding SFDC fields.
      </p>
    </div>

    <div class="alert_cards">
      <div class="card__">
        <div class="card__header">
          <h3>Create <span style="color: #199e54">Opportunity</span></h3>
        </div>
        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 2rem">
          <router-link :to="{ name: 'CreateOpportunity' }">
            <button class="activate-button">Activate</button>
          </router-link>

          <!-- <h4 style="margin-top: -0.5rem" v-else-if="!hasZoomIntegration">
            Connect Zoom in order to activate
          </h4>
          <p style="margin-top: -0.5rem; font-weight: 900" v-else-if="hasZoomChannel">Activated</p> -->
        </div>
      </div>
      <div class="card__">
        <div class="card__header">
          <h3>Update <span style="color: #5f8cff">Contacts</span></h3>
        </div>
        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 2rem">
          <router-link :to="{ name: 'UpdateContacts' }">
            <button class="activate-button">Activate</button>
          </router-link>
          <!-- <h4 style="margin-top: -0.5rem" v-else-if="!hasZoomIntegration">
            Connect Zoom in order to activate
          </h4>
          <p style="margin-top: -0.5rem; font-weight: 900" v-else-if="hasZoomChannel">Activated</p> -->
        </div>
      </div>
      <div class="card__">
        <div class="card__header">
          <h3>Create <span style="color: #ddad3c">Lead</span></h3>
        </div>
        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 2rem">
          <router-link :to="{ name: 'CreateLeads' }">
            <button class="activate-button">Activate</button>
          </router-link>
          <!-- <h4 style="margin-top: -0.5rem" v-else-if="!hasZoomIntegration">
            Connect Zoom in order to activate
          </h4>
          <p style="margin-top: -0.5rem; font-weight: 900" v-else-if="hasZoomChannel">Activated</p> -->
        </div>
      </div>
      <div class="card__">
        <div class="card__header">
          <h3>Update <span style="color: #ddad3c">Lead</span></h3>
        </div>
        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 2rem">
          <router-link :to="{ name: 'UpdateLeads' }">
            <button class="activate-button">Activate</button>
          </router-link>
          <!-- <h4 style="margin-top: -0.5rem" v-else-if="!hasZoomIntegration">
            Connect Zoom in order to activate
          </h4>
          <p style="margin-top: -0.5rem; font-weight: 900" v-else-if="hasZoomChannel">Activated</p> -->
        </div>
      </div>
      <div class="card__">
        <div class="card__header">
          <h3>Create <span style="color: #fa646a">Account</span></h3>
        </div>
        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 2rem">
          <router-link :to="{ name: 'CreateAccounts' }">
            <button class="activate-button">Activate</button>
          </router-link>
          <!-- <h4 style="margin-top: -0.5rem" v-else-if="!hasZoomIntegration">
            Connect Zoom in order to activate
          </h4>
          <p style="margin-top: -0.5rem; font-weight: 900" v-else-if="hasZoomChannel">Activated</p> -->
        </div>
      </div>
      <div class="card__">
        <div class="card__header">
          <h3>Update <span style="color: #fa646a">Account</span></h3>
        </div>
        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 2rem">
          <router-link :to="{ name: 'UpdateAccounts' }">
            <button class="activate-button">Activate</button>
          </router-link>
          <!-- <h4 style="margin-top: -0.5rem" v-else-if="!hasZoomIntegration">
            Connect Zoom in order to activate
          </h4>
          <p style="margin-top: -0.5rem; font-weight: 900" v-else-if="hasZoomChannel">Activated</p> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Modal from '@/components/Modal'

export default {
  name: 'Custom',
  components: {
    Modal,
  },
  data() {
    return {}
  },
  computed: {
    orgHasSlackIntegration() {
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    user() {
      return this.$store.state.user
    },
  },
  methods: {
    goToUpdateOpp() {
      this.$router.push({ name: 'UpdateOpportunity' })
    },
    goToCreate() {
      this.$router.push({ name: 'CreateContacts' })
    },
    goToTemplates() {
      this.$router.push({ name: 'ListTemplates' })
    },
    // handleShowOptional() {
    //   this.showOptional = !this.showOptional
    // },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.activate-button {
  background-color: $dark-green;
  color: white;
  font-weight: bold;
  font-size: 16px;
  border-radius: 0.5rem;
  border: 2px solid $dark-green;
  padding: 0.25rem 1.5rem;
  cursor: pointer;
}
.customizations {
  margin-left: 14vw;
  margin-top: 4rem;
}

.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
  flex-wrap: wrap;
}
.card__ {
  background-color: $panther;
  border: none;
  width: 20vw;
  padding: 1.25rem;
  margin-right: 1rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 3px 4px 7px black;
  color: white;
  // @media only screen and (min-width: 768px) {
  //   flex: 1 0 24%;
  //   min-width: 21rem;
  //   max-width: 30rem;
  // }

  &header {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 3rem;
  }
  .col {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
  }
  .sub__ {
    font-size: 16px;
    margin-top: -0.5rem;
    color: $panther-silver;
  }
}
</style>
