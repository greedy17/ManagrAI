<template>
  <div class="customizations">
    <div style="display: flex; align-items: flex-start; margin-left: 10vw; flex-direction: column">
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
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            alt=""
            id="plus"
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 1.5rem">
          <router-link :to="{ name: 'CreateOpportunity' }">
            <button class="activate-button">View + Edit</button>
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
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            alt=""
            id="plus"
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 1.5rem">
          <router-link :to="{ name: 'UpdateContacts' }">
            <button class="activate-button">View + Edit</button>
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
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            alt=""
            id="plus"
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 1.5rem">
          <router-link :to="{ name: 'CreateLeads' }">
            <button class="activate-button">View + Edit</button>
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
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            id="plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 1.5rem">
          <router-link :to="{ name: 'UpdateLeads' }">
            <button class="activate-button">View + Edit</button>
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
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            alt=""
            id="plus"
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 1.5rem">
          <router-link :to="{ name: 'CreateAccounts' }">
            <button class="activate-button">View + Edit</button>
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
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            alt=""
            id="plus"
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
        </div>
        <div style="margin-top: 1.5rem">
          <router-link :to="{ name: 'UpdateAccounts' }">
            <button class="activate-button">View + Edit</button>
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

#plus {
  filter: invert(90%);
}
.activate-button {
  background-color: $dark-green;
  color: white;
  font-weight: bold;
  font-size: 14px;
  border: none;
  border-radius: 0.33rem;
  padding: 0.5rem 1rem;
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

// .back-logo {
//   position: absolute;
//   opacity: 0.06;
//   filter: alpha(opacity=50);
//   height: 20%;
//   margin-top: 2rem;
//   margin-right: -10rem;
// }
.card__ {
  background-color: $white;
  border: none;
  width: 20vw;
  padding: 1.25rem;
  margin-right: 1.25rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 3px 4px 7px $very-light-gray;
  color: $base-gray;
  // @media only screen and (min-width: 768px) {
  //   flex: 1 0 24%;
  //   min-width: 21rem;
  //   max-width: 30rem;
  // }
  h3 {
    font-size: 1.2rem;
  }
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
