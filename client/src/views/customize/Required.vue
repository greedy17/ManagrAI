<template>
  <div class="customizations">
    <div @click="test">
      <h3 style="color: 4d4e4c">Required Actions</h3>
      <p class="sub__">Map SFDC fields to their corresponding Slack fields.</p>
    </div>

    <div class="customizations__cards">
      <div class="card">
        <div class="card__header">
          <h3>Update Opportunity</h3>
          <p class="active-workflow" v-if="activeUpdateOpportunityForm">
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </p>
        </div>
        <!-- <img class="back-logo" src="@/assets/images/logo.png" /> -->
        <div class="card__body">
          <img style="margin-right: 1rem" class="card-img" src="@/assets/images/salesforce.png" />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(60%)"
            src="@/assets/images/plusOne.png"
            alt=""
            id="plus"
          />
          <img style="height: 1.5rem" src="@/assets/images/slackLogo.png" />
        </div>
        <div class="card__footer">
          <button @click="goToUpdateOpp" class="green__button">View + Edit</button>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h3>Create Contacts</h3>
          <p v-if="activeCreateContactForm" class="active-workflow">
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </p>
        </div>
        <!-- <img class="back-logo" src="@/assets/images/logo.png" /> -->
        <div class="card__body">
          <img style="margin-right: 1rem" class="card-img" src="@/assets/images/salesforce.png" />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(60%)"
            src="@/assets/images/plusOne.png"
            alt=""
            id="plus"
          />
          <img style="height: 1.5rem" src="@/assets/images/slackLogo.png" />
        </div>
        <div class="card__footer">
          <button @click="goToCreate" class="green__button">View + Edit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'

export default {
  name: 'Required',
  components: {},
  data() {
    return {
      createContactForm: null,
      updateOpportunityForm: null,
      activeUpdateOpportunityForm: null,
      activeCreateContactForm: null,
    }
  },
  watch: {
    updateOpportunityForm: 'hasOppForm',
    createContactForm: 'hasContactForm',
  },
  computed: {
    orgHasSlackIntegration() {
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
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
    async getForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.createContactForm = res.filter(
          (form) => form.formType === 'CREATE' && form.resource === 'Contact',
        )
        this.updateOpportunityForm = res.filter(
          (form) => form.formType === 'UPDATE' && form.resource === 'Opportunity',
        )
      } catch (error) {
        console.log(error)
      }
    },
    test() {
      // console.log(this.createContactForm)
      console.log(this.updateOpportunityForm[0].fields.length)
    },
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
  align-items: flex-start;
  margin-top: 2rem;
  margin-left: 25vw;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
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
    // margin-top: 0.1rem;
  }
}
.card-img {
  width: 2rem;
  height: 1.5rem;
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
  font-size: 14px;
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
