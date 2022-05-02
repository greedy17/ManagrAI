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
        </div>

        <div class="card__body">
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
        <div class="card__footer">
          <router-link :to="{ name: 'CreateOpportunity' }">
            <button class="activate-button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Update Contacts</h3>
        </div>

        <div class="card__body">
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
        <div class="card__footer">
          <router-link :to="{ name: 'UpdateContacts' }">
            <button class="activate-button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Create Lead</h3>
        </div>

        <div class="card__body">
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
        <div class="card__footer">
          <router-link :to="{ name: 'CreateLeads' }">
            <button class="activate-button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Update Lead</h3>
        </div>

        <div class="card__body">
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
        <div class="card__footer">
          <router-link :to="{ name: 'UpdateLeads' }">
            <button class="activate-button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Create Account</h3>
        </div>

        <div class="card__body">
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
        <div class="card__footer">
          <router-link :to="{ name: 'CreateAccounts' }">
            <button class="activate-button">View + Edit</button>
          </router-link>
        </div>
      </div>
      <div class="card">
        <div class="card__header">
          <h3>Update Account</h3>
        </div>

        <div class="card__body">
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
  font-size: 14px;
  border: none;
  border-radius: 0.3rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
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
  &__subtitle {
    font-size: 14px;
    margin-bottom: 2rem;
  }
}
.sub__ {
  font-size: 14px;
  margin-top: -0.5rem;
  color: $gray;
}
.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.card {
  background-color: white;
  box-shadow: 2px 2px 3px $very-light-gray;
  border-radius: 0.5rem;
  width: 24vw;
  margin-right: 1rem;
  margin-bottom: 1rem;
  &__header {
    height: 2rem;
    padding: 1.25rem 1rem;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    border-bottom: 3px solid $soft-gray;
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
