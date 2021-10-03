<template>
  <div class="customizations">
    <Modal ref="optionalModal">
      <template v-slot:header>
        <h2>Optional Forms</h2>
      </template>

      <template v-slot:body>
        <div>
          <p style="font-weight: bold; margin-bottom: 2rem">
            Click on any of the links below to fill out the corresponding form:
          </p>
          <ul>
            <router-link :to="{ name: 'CreateOpportunity' }"
              >Create <span style="font-weight: bold">Opportunity</span>
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
          </ul>
        </div>
      </template>
    </Modal>

    <h2 style="color: black" class="title">Make updates to Salesforce from Slack</h2>
    <p style="font-weight: bold; margin-top: -0.5rem; margin-bottom: 2rem; color: #5d5e5e">
      Map your desired CRM fields to Managr.
    </p>

    <div class="customizations__cards">
      <div class="card">
        <div class="card__header">
          <h2 class="title">Update <span>Opportunity</span></h2>
          <button @click="goToUpdateOpp" class="green__button">View + Edit</button>
        </div>
        <div class="form_images">
          <div style="margin-left: 2rem">
            <img class="card-img" src="@/assets/images/salesforce.png" />
            <img style="height: 2.5rem; margin-left: 1rem" src="@/assets/images/slackLogo.png" />
          </div>
          <!-- <p
            style="
              color: #199e54;
              margin-right: 3rem;
              font-weight: bold;
              text-shadow: 0 0 20px #199e54;
            "
          >
            Complete
          </p> -->
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h2 class="title">Create <span>Contacts</span></h2>
          <button @click="goToCreate" class="green__button">View + Edit</button>
        </div>
        <div class="form_images">
          <div style="margin-left: 2rem">
            <img class="card-img" src="@/assets/images/salesforce.png" />
            <img style="height: 2.5rem; margin-left: 1rem" src="@/assets/images/slackLogo.png" />
          </div>
          <!-- <p
            style="
              color: #199e54;
              margin-right: 3rem;
              font-weight: bold;
              text-shadow: 0 0 20px #199e54;
            "
          >
            Complete
          </p> -->
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h2 class="title">Optional Forms</h2>
          <button @click="$refs.optionalModal.openModal()" class="green__button">View</button>
        </div>
        <div class="form_images">
          <div style="margin-left: 2rem">
            <p style="color: #beb5cc; margin-right: 3rem; font-weight: bold">
              These forms are not required.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- <button v-if="user.isAdmin" class="slack-button">Continue</button> -->
    <button @click="goToTemplates" class="slack-button">Activate Workflow Automations</button>
  </div>
</template>

<script>
import Modal from '@/components/Modal'

export default {
  name: 'CustomizeLandingPage',
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

.customizations {
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 4rem;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
  }
  &__subtitle {
    font-size: 14px;
    margin-bottom: 2rem;
  }
}

.card {
  background-color: $panther;
  border: none;
  width: 30vw;
  height: 25vh;
  margin-right: 2rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 4px 7px black;
  @media only screen and (min-width: 768px) {
    flex: 1 0 24%;
    min-width: 21rem;
    max-width: 30rem;
  }

  &__header {
    display: flex;
    align-items: center;
    flex-direction: row;
    justify-content: space-evenly;
    height: 5rem;
  }

  &__title {
    margin: 0 0 0 1rem;
  }
}

.card-img {
  width: 3.5rem;
}

.card-text {
  font-size: 14px;
  font-weight: bold;
  color: $panther-silver;
  text-align: center;
}

.slack-button {
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  font-weight: bold;
  color: white;
  background-color: $dark-green;
  border: none;
  cursor: pointer;

  &--disabled {
    background-color: $panther-silver !important;
    color: $panther-gray;
    height: 2.75rem;
    width: 12rem;
    border-radius: 0.5rem;
    border: none;
    margin: 0rem 0 2rem 0;
    font-size: 1.25rem;
    font-weight: bold;
    cursor: not-allowed;
  }
}

.green__button {
  height: 2.5rem;
  width: 8rem;
  border-radius: 0.5rem;
  font-size: 1.025rem;
  font-weight: bold;
  color: white;
  background-color: $dark-green;
  border: none;
  cursor: pointer;
}

.form_images {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 22px;
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

// .optional_button {
//   height: 2.75rem;
//   width: 16rem;
//   border: none;
//   margin: 0rem 0 0.5rem 0;
//   font-size: 1.05rem;
//   font-weight: bold;
//   color: $panther-silver;
//   background: transparent;
//   cursor: pointer;
// }
</style>