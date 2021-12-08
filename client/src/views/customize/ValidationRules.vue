<template>
  <div class="customizations">
    <h1 style="color: red; text-align: center">IN PROGRESS, TESTING</h1>
  </div>
</template>

<script>
import Modal from '@/components/Modal'

export default {
  name: 'ValidationRules',
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
