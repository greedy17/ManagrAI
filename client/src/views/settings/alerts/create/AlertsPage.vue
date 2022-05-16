<template>
  <div class="alerts-page">
    <div v-if="isOnboarding && !isAdmin" class="col">
      <h3>Popular Workflow Automations</h3>
      <p style="margin-top: -0.5rem" class="sub__">Step 2/2: Activate at least 3 workflows</p>
      <button
        class="orange_button bouncy"
        v-if="isOnboarding && user.activatedManagrConfigs.includes('Close Date Passed')"
        @click="onboardComplete"
      >
        Complete Onboarding
      </button>
    </div>
    <div v-else class="col">
      <h3>Popular Workflow Automations</h3>
      <p class="sub__">Activate the workflows that are relevant to you</p>
    </div>

    <div class="alert_cards">
      <div class="card">
        <div class="card__header">
          <h3>Log Meetings</h3>
        </div>
        <div class="card__body">
          <img style="height: 1.75rem; margin-right: 1rem" src="@/assets/images/zoom.png" alt="" />
          <img
            style="height: 1rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            class="filter-plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/gmailCal.png"
            alt=""
          />
        </div>
        <div class="card__footer">
          <button
            v-if="!hasZoomChannel"
            @click="goToLogZoom"
            :class="!isAdmin && isOnboarding ? 'orange_button bouncy' : 'orange_button'"
          >
            Activate
          </button>
          <p class="active-workflow" v-else>
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </p>
        </div>
      </div>

      <div
        :class="
          !(hasZoomChannel || recapChannel) && isOnboarding && !isAdmin ? 'onboarding card' : 'card'
        "
      >
        <div class="card__header">
          <h3>Close Date Passed</h3>
        </div>

        <div class="card__body">
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            class="filter-plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="
              hasSalesforceIntegration &&
              hasSlackIntegration &&
              !user.activatedManagrConfigs.includes('Close Date Passed')
            "
            @click="goToCloseDatePassed"
            :class="!isAdmin && isOnboarding ? 'orange_button bouncy' : 'orange_button'"
          >
            Activate
          </button>
          <h4 v-else-if="!(hasSalesforceIntegration && hasSlackIntegration)">
            Connect Slack & Salesforce to acivate
          </h4>
          <h4
            class="active-workflow"
            v-else-if="user.activatedManagrConfigs.includes('Close Date Passed')"
          >
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </h4>
        </div>
      </div>

      <div
        :class="
          !user.activatedManagrConfigs.includes('Close Date Passed') && isOnboarding && !isAdmin
            ? 'card onboarding'
            : 'card'
        "
      >
        <div class="card__header">
          <h3>Update Forecast</h3>
        </div>

        <div class="card__body">
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            class="filter-plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="
              hasSalesforceIntegration &&
              hasSlackIntegration &&
              !user.activatedManagrConfigs.includes('Update Forecast')
            "
            @click="goToUpdateForecast"
            :class="!isAdmin && isOnboarding ? 'orange_button bouncy' : 'orange_button'"
          >
            Activate
          </button>
          <h4 v-else-if="!(hasSalesforceIntegration && hasSlackIntegration)">
            Connect Slack & Salesforce to acivate
          </h4>
          <h4
            class="active-workflow"
            v-else-if="user.activatedManagrConfigs.includes('Update Forecast')"
          >
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </h4>
        </div>
      </div>

      <div
        :class="
          !user.activatedManagrConfigs.includes('Close Date Passed') && isOnboarding && !isAdmin
            ? 'card onboarding'
            : 'card'
        "
      >
        <div class="card__header">
          <h3>Deal Rotting</h3>
        </div>

        <div class="card__body">
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            class="filter-plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="
              hasSalesforceIntegration &&
              hasSlackIntegration &&
              !user.activatedManagrConfigs.includes('Deal Rotting')
            "
            @click="goToDealRotting"
            class="orange_button"
          >
            Activate
          </button>
          <h4 v-else-if="!(hasSalesforceIntegration && hasSlackIntegration)">
            Connect Slack & Salesforce to acivate
          </h4>
          <h4
            class="active-workflow"
            v-else-if="user.activatedManagrConfigs.includes('Deal Rotting')"
          >
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </h4>
        </div>
      </div>

      <div
        :class="
          !user.activatedManagrConfigs.includes('Close Date Passed') && isOnboarding && !isAdmin
            ? 'card onboarding'
            : 'card'
        "
      >
        <div class="card__header">
          <h3>Close Date Approaching</h3>
        </div>

        <div class="card__body">
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            class="filter-plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="
              hasSalesforceIntegration &&
              hasSlackIntegration &&
              !user.activatedManagrConfigs.includes('Close Date Approaching')
            "
            @click="goToCloseDateApproaching"
            class="orange_button"
          >
            Activate
          </button>
          <h4
            style="margin-top: -0.5rem"
            v-else-if="!(hasSalesforceIntegration && hasSlackIntegration)"
          >
            Connect Slack & Salesforce to acivate
          </h4>
          <h4
            class="active-workflow"
            v-else-if="user.activatedManagrConfigs.includes('Close Date Approaching')"
          >
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </h4>
        </div>
      </div>

      <div
        :class="
          !user.activatedManagrConfigs.includes('Close Date Passed') && isOnboarding && !isAdmin
            ? 'card onboarding'
            : 'card'
        "
      >
        <div class="card__header">
          <h3>Upcoming Next Step</h3>
        </div>

        <div class="card__body">
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            class="filter-plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="
              hasSalesforceIntegration &&
              hasSlackIntegration &&
              !user.activatedManagrConfigs.includes('Upcoming Next Step')
            "
            @click="goToNextStep"
            class="orange_button"
          >
            Activate
          </button>
          <h4 v-else-if="!(hasSalesforceIntegration && hasSlackIntegration)">
            Connect Slack & Salesforce to acivate
          </h4>
          <h4
            class="active-workflow"
            v-else-if="user.activatedManagrConfigs.includes('Upcoming Next Step')"
          >
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </h4>
        </div>
      </div>

      <div
        :class="
          !user.activatedManagrConfigs.includes('Required Field Empty') && isOnboarding && !isAdmin
            ? 'card onboarding'
            : 'card'
        "
      >
        <div class="card__header">
          <h3>Required Field Empty</h3>
        </div>

        <div class="card__body">
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            class="filter-plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="
              hasSalesforceIntegration &&
              hasSlackIntegration &&
              !user.activatedManagrConfigs.includes('Required Field Empty')
            "
            @click="goToEmptyField"
            class="orange_button"
          >
            Activate
          </button>
          <h4 v-else-if="!(hasSalesforceIntegration && hasSlackIntegration)">
            Connect Slack & Salesforce to acivate
          </h4>
          <h4
            class="active-workflow"
            v-else-if="user.activatedManagrConfigs.includes('Required Field Empty')"
          >
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </h4>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'
//Internal
import { UserOnboardingForm } from '@/services/users/forms'

/**
 * Services
 */

import AlertTemplate, { AlertTemplateForm } from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager } from '@thinknimble/tn-models'
import {
  SObjectField,
  NON_FIELD_ALERT_OPTS,
  SOBJECTS_LIST,
} from '@/services/salesforce'
import User from '@/services/users'
import { SlackListResponse } from '@/services/slack'

export default {
  name: 'AlertsPage',
  data() {
    return {
      channelOpts: new SlackListResponse(),
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: [],
      userOnboardingForm: new UserOnboardingForm({}),
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      users: CollectionManager.create({ ModelClass: User }),
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
    }
  },
  async created() {
    this.templates.refresh()
  },
  methods: {
    handleUpdate() {
      User.api
        .update(this.user.id, this.userOnboardingForm.value)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
      this.$router.push({ name: 'Pipelines' })
    },
    onboardComplete() {
      this.userOnboardingForm.field.onboarding.value = false
      this.handleUpdate()
    },
    goToCloseDateApproaching() {
      this.$router.push({ name: 'CloseDateApproaching' })
    },
    goToCloseDatePassed() {
      this.$router.push({ name: 'CloseDatePassed' })
    },
    goToDealRotting() {
      this.$router.push({ name: 'DealRotting' })
    },
    goToUpdateForecast() {
      this.$router.push({ name: 'UpdateForecast' })
    },
    goToLogZoom() {
      this.$router.push({ name: 'LogZoom' })
    },
    goToNextStep() {
      this.$router.push({ name: 'NextStep' })
    },
    goToEmptyField() {
      this.$router.push({ name: 'RequiredFieldEmpty' })
    },
  },
  computed: {
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    recapChannel() {
      return this.$store.state.user.slackAccount.recapChannel
    },
    user() {
      return this.$store.state.user
    },
    isAdmin() {
      return this.$store.state.user.isAdmin
    },
    hasZoomChannel() {
      return this.$store.state.user.slackAccount.zoomChannel
    },
    isOnboarding() {
      return this.$store.state.user.onboarding
    },
    selectedResourceType: {
      get() {
        return this.alertTemplateForm.field.resourceType.value
      },
      set(val) {
        this.alertTemplateForm.field.resourceType.value = val
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
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
.onboarding {
  filter: blur(10px);
}

.alerts-page {
  margin-left: 10vw;
  margin-top: 3.5rem;
  color: $base-gray;
}
.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 0.5rem;
  padding-right: 0.5rem;
  padding-bottom: 0.5rem;
}
.card:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
  transform: scale(1.015);
}
.card {
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 0.5rem;
  width: 22vw;
  margin-right: 1rem;
  margin-bottom: 1rem;
  transition: all 0.25s;
  &__header {
    height: 2rem;
    padding: 1.25rem 1rem;
    font-size: 12px;
    font-weight: 400;
    display: flex;
    align-items: center;
    justify-content: flex-start;
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

.filter-plus {
  filter: invert(90%);
}
.sub__ {
  font-size: 14px;
  margin-top: -0.5rem;
  color: $gray;
}
.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.orange_button {
  background-color: $dark-green;
  color: white;
  font-size: 14px;
  border-radius: 0.3rem;
  border: 2px solid $dark-green;
  padding: 0.25rem 1.25rem;
  cursor: pointer;
}
.active-workflow {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1.5rem;
  margin-right: 1rem;
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
    margin-left: 0.75rem;
    margin-top: 0.1rem;
  }
}
</style>
