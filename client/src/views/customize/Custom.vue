<template>
  <div class="customizations">
    <div v-if="!isOnboarding" class="col">
      <h2 style="color: black; margin-top: -0.5rem">Popular Workflow Automations</h2>
      <p style="color: #5d5e5e" class="sub__">Activate the workflows that are relevant to you</p>
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

.customizations {
  margin-left: 20vw;
  margin-top: 4rem;
  &__previous-step {
    @include muted-font(12);
  }
  &__groups {
    &__group {
      display: flex;
    }
  }
  &__message {
    display: flex;
    height: 20rem;
    &-template {
      margin: 0rem 1rem;
      &__notification {
        width: 30rem;
        margin: 1rem 0rem;
      }
      &__message {
        width: 40rem;
        margin: 1rem 0rem;
      }
    }
  }
}

.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
  margin-top: 2rem;
  flex-wrap: wrap;
}
.card__ {
  background-color: $panther;
  border: none;
  width: 20vw;
  padding: 1.25rem;
  margin-right: 1.25rem;
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
    color: white;
  }
  .sub__ {
    font-size: 16px;
    margin-top: -0.5rem;
    color: $panther-silver;
  }
}
</style>
