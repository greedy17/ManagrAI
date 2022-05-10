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

import { quillEditor } from 'vue-quill-editor'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
//Internal
import FormField from '@/components/forms/FormField'
import AlertGroup from '@/views/settings/alerts/create/_AlertGroup'
import AlertSummary from '@/views/settings/alerts/create/_AlertSummary'
import ListContainer from '@/components/ListContainer'
import ListItem from '@/components/ListItem'
import SlackNotificationTemplate from '@/views/settings/alerts/create/SlackNotificationTemplate'
import { UserOnboardingForm } from '@/services/users/forms'
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'
import ExpandablePanel from '@/components/ExpandablePanel'
import Modal from '@/components/Modal'

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
  components: {
    ExpandablePanel,
    ListContainer,
    ListItem,
    SlackMessagePreview,
    AlertGroup,
    SlackNotificationTemplate,
    quillEditor,
    ToggleCheckBox,
    FormField,
    AlertSummary,
    PulseLoadingSpinnerButton,
    Modal,
  },
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
.dot {
  filter: invert(40%) sepia(96%) saturate(431%) hue-rotate(94deg) brightness(101%) contrast(82%);
  height: 0.5rem;
  border-radius: 50%;
  margin-left: 0.2rem;
  margin-bottom: 0.2rem;
}
.activated {
  color: $dark-green;
  font-weight: bold;
  margin-top: -0.5rem;
}
.quill-editor {
  width: 100%;
}
textarea {
  @extend .textarea;
}

.box__header {
  &__status {
    display: flex;
    &--error {
      color: $coral;
      fill: $coral;
    }
    &--success {
      color: $dark-green;
      fill: $dark-green;
    }
  }
}
.alerts-page {
  margin-left: 10vw;
  margin-top: 3.5rem;
  color: $base-gray;
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

.alerts-page__settings {
  display: flex;
  align-items: center;
  justify-content: space-evenly;

  &__frequency {
    display: flex;
    align-items: center;
    &-label {
      @include muted-font();
      margin: 0 0.5rem;
    }
  }
  &-remove {
    justify-self: end;
  }
}
.filter-plus {
  filter: invert(90%);
}
.btn {
  &--danger {
    @include button-danger();
  }
  &--primary {
    @include primary-button();
  }
  &--secondary {
    @include secondary-button();
  }

  &--icon {
    @include --icon();
  }
}
.muted--link {
  @include muted-font();
  @include pointer-on-hover();
  &--important {
    color: red;
    font-weight: bold;
    font-size: 11px;
  }
}
.gray {
  color: $gray;
}
.slate {
  color: $slate-gray;
}
.pad {
  padding-bottom: 1rem;
  margin-top: -1rem;
}
.pink {
  color: $candy;
  font-weight: bold;
}
.purple {
  color: $grape;
  font-weight: bold;
}
.mar {
  margin-top: -2rem;
}
.center {
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.sub {
  font-size: 12px;
  margin-left: 0.5rem;
}
.sub__ {
  font-size: 14px;
  margin-top: -0.5rem;
  color: $gray;
}
.title {
  color: $base-gray;
  font-weight: 900;
}
.group {
  display: flex;
  flex-direction: row;
  height: auto;
  margin: 0.5rem;
  padding: 0.5rem;
}
.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: space-evenly;
  margin-top: 1rem;
}
.row_ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 2rem;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-top: 10rem;
}
.bottom {
  margin-bottom: 1.25rem;
  height: 170px;
}
.left {
  margin-bottom: 2rem;
}
.space {
  margin-bottom: 0.5rem;
}
.add__group {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-top: 3rem;
  padding-bottom: 1rem;
  border-bottom: 3px solid $mid-gray;
}
.bolder {
  font-size: 16px;
  margin-left: 1rem;
  cursor: pointer;
  color: $base-gray;
}
.bolder:hover {
  border-bottom: 2px solid $candy;
  color: $candy;
}
.alertsModal {
  color: $candy;
  text-decoration: underline;
  cursor: pointer;
}
.modal__container {
  overflow-y: scroll;
}
.blue {
  color: $slate-gray;
}
.top {
  border-top: 3px solid $grape;
}
.templates {
  border-bottom: 1px solid $gray;
}
input {
  width: 130px;
  text-align: center;
  height: 36px;
  border-radius: 0.25rem;
  margin-top: 0.75rem;
  border: none;
  border-bottom: 1px solid $slate-gray;
  font-weight: bold;
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
.cs__button {
  width: 9rem;
  background-color: transparent;
  color: $panther-silver;
  font-weight: bold;
  font-size: 16px;
  height: 2rem;
  border-radius: 0.5rem;
  border: none;
  cursor: not-allowed;
}
</style>
