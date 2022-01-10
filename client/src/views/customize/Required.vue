<template>
  <div class="customizations">
    <div style="width: 61%">
      <h2 style="color: 4d4e4c">Required Field Mapping</h2>
      <p
        style="
          font-weight: bold;
          margin-top: -0.5rem;
          margin-bottom: 2rem;
          color: #5d5e5e;
          font-size: 0.975rem;
        "
      >
        Map Slack fields to the corresponding SFDC fields.
      </p>
    </div>

    <div class="customizations__cards">
      <div class="card">
        <div class="card__header">
          <h3 class="title">Update <span style="color: #199e54">Opportunity</span></h3>
          <div style="margin-left: 1rem; display: flex; flex-direction: row">
            <img class="card-img" src="@/assets/images/salesforce.png" />
            <img style="height: 1.5rem; margin-left: 1rem" src="@/assets/images/slackLogo.png" />
          </div>
        </div>
        <!-- <img class="back-logo" src="@/assets/images/logo.png" /> -->
        <div class="center">
          <button @click="goToUpdateOpp" class="green__button">View + Edit</button>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h2 class="title">Create <span style="color: #5f8cff">Contacts</span></h2>
          <div style="margin-left: 1rem; display: flex; flex-direction: row">
            <img class="card-img" src="@/assets/images/salesforce.png" />
            <img style="height: 1.5rem; margin-left: 1rem" src="@/assets/images/slackLogo.png" />
          </div>
        </div>
        <!-- <img class="back-logo" src="@/assets/images/logo.png" /> -->
        <div class="center">
          <button @click="goToCreate" class="green__button">View + Edit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Modal from '@/components/Modal'

export default {
  name: 'Required',
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
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 3.5rem;
  margin-left: 18vw;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    padding: 1rem;
    border-radius: 0.5rem;
  }
  &__subtitle {
    font-size: 14px;
    margin-bottom: 2rem;
  }
}

.card {
  background-color: white;
  border: none;
  min-width: 24vw;
  max-width: 44vw;
  min-height: 25vh;
  margin-right: 1rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 4px 7px $very-light-gray;
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
  width: 1.75rem;
}

.card-text {
  font-size: 14px;
  font-weight: bold;
  color: $panther-silver;
  text-align: center;
}
.back-logo {
  position: absolute;
  opacity: 0.06;
  filter: alpha(opacity=50);
  height: 28%;
  margin-top: -1.5rem;
  margin-left: -2rem;
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
  border-radius: 0.33rem;
  padding: 0.5rem 1rem;
  font-size: 15px;
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
  font-size: 21px;
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
.center {
  display: flex;
  align-items: center;
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
