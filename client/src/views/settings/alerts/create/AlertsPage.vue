<template>
  <div class="alerts-page">
    <div class="col">
      <h2 style="color: black" class="title">Smart Alert Templates</h2>
      <p style="color: #5d5e5e" class="sub__">
        Keep your pipeline up to date by activating smart alerts
      </p>
    </div>

    <div class="alert_cards">
      <div class="card__">
        <div class="card__header">
          <h3 style="font-size: 1.3rem">
            Close Date<span style="color: #199e54"> Approaching</span>
          </h3>
        </div>

        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div style="margin-top: 2rem">
          <button
            v-if="hasSalesforceIntegration && hasSlackIntegration"
            @click="goToCloseDateApproaching"
            class="orange_button"
          >
            Activate
          </button>
          <h4 style="margin-top: -0.5rem" v-else>Connect Slack & Salesforce to acivate</h4>
        </div>
      </div>

      <div class="card__">
        <div class="card__header">
          <h3>Close Date <span style="color: #fa646a">Passed</span></h3>
        </div>

        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div style="margin-top: 2rem">
          <button
            v-if="hasSalesforceIntegration && hasSlackIntegration"
            @click="goToCloseDatePassed"
            class="orange_button"
          >
            Activate
          </button>
          <h4 style="margin-top: -0.5rem" v-else>Connect Slack & Salesforce to acivate</h4>
        </div>
      </div>

      <div class="card__">
        <div class="card__header">
          <h3>Deal <span style="color: #fa646a">Rotting</span></h3>
        </div>

        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div style="margin-top: 2rem">
          <button
            v-if="hasSalesforceIntegration && hasSlackIntegration"
            @click="goToDealRotting"
            class="orange_button"
          >
            Activate
          </button>
          <h4 style="margin-top: -0.5rem" v-else>Connect Slack & Salesforce to acivate</h4>
        </div>
      </div>

      <div class="card__">
        <div class="card__header">
          <h3>Update <span style="color: #199e54">Forecast</span></h3>
        </div>

        <div class="row">
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1.75rem; margin-right: 1rem"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 2.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div style="margin-top: 2rem">
          <button
            v-if="hasSalesforceIntegration && hasSlackIntegration"
            @click="goToUpdateForecast"
            class="orange_button"
          >
            Activate
          </button>
          <h4 style="margin-top: -0.5rem" v-else>Connect Slack & Salesforce to acivate</h4>
        </div>
      </div>

      <div v-if="user.userLevel !== 'MANAGER'" class="card__">
        <div class="card__header">
          <h3>Log <span style="color: #5f8cff">Zoom Meetings</span></h3>
        </div>
        <div class="row">
          <img style="height: 2.25rem" src="@/assets/images/zoom.png" alt="" />
        </div>
        <div style="margin-top: 2rem">
          <button v-if="hasZoomIntegration" @click="goToLogZoom" class="orange_button">
            Activate
          </button>
          <h4 style="margin-top: -0.5rem" v-else>Connect Zoom in order to activate</h4>
        </div>
      </div>
      <div v-else class="card__">
        <div class="card__header">
          <h3>Zoom <span style="color: #5f8cff">Meeting Recaps</span></h3>
        </div>
        <div class="row">
          <img style="height: 2.25rem" src="@/assets/images/zoom.png" alt="" />
        </div>
        <div style="margin-top: 2rem">
          <button
            v-if="hasZoomIntegration && hasSlackIntegration"
            @click="goToZoomRecap"
            class="orange_button"
          >
            Activate
          </button>
          <h4 style="margin-top: -0.5rem" v-else>Connect Zoom and Slack in order to activate</h4>
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
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'
import DropDownSearch from '@/components/DropDownSearch'
import ExpandablePanel from '@/components/ExpandablePanel'
import Modal from '@/components/Modal'

/**
 * Services
 */

import AlertTemplate, {
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertOperandForm,
} from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import {
  SObjectField,
  SObjectValidations,
  SObjectPicklist,
  NON_FIELD_ALERT_OPTS,
  SOBJECTS_LIST,
} from '@/services/salesforce'
import User from '@/services/users'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
export default {
  name: 'AlertsPage',
  components: {
    ExpandablePanel,
    DropDownSearch,
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
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      users: CollectionManager.create({ ModelClass: User }),
    }
  },
  methods: {
    showList() {
      this.listVisible = !this.listVisible
    },
    showDropDown() {
      this.dropdownVisible = !this.dropdownVisible
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
    goToZoomRecap() {
      this.$router.push({ name: 'ZoomRecap' })
    },
  },
  computed: {
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    hasZoomIntegration() {
      return !!this.$store.state.user.zoomAccount && this.$store.state.user.hasZoomIntegration
    },
    hasGongIntegration() {
      return !!this.$store.state.user.gongAccount && this.$store.state.user.hasGongIntegration
    },
    hasSalesloftIntegration() {
      return (
        !!this.$store.state.user.salesloftAccount && this.$store.state.user.hasSalesloftIntegration
      )
    },
    orgHasSlackIntegration() {
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    hasNylasIntegration() {
      return !!this.$store.state.user.nylas
    },
    userCanIntegrateSlack() {
      return this.$store.state.user.isAdmin
    },
    userTargetsOpts() {
      if (this.user.userLevel == 'MANAGER') {
        return [
          ...this.alertTargetOpts.map((opt) => {
            return {
              id: opt.value,
              fullName: opt.key,
            }
          }),
          ...this.users.list,
        ]
      } else {
        return [{ fullName: 'Myself', id: 'SELF' }]
      }
    },
    recipientOpts() {
      if (this.user.userLevel == 'MANAGER') {
        return [
          ...this.alertRecipientOpts.map((opt) => {
            return {
              id: opt.value,
              fullName: opt.key,
            }
          }),
          ...this.users.list,
        ]
      } else {
        return [{ fullName: 'Myself', id: 'SELF' }]
      }
    },
    formValue() {
      return this.alertTemplateForm.value
    },
    editor() {
      return this.$refs['message-body'].quill
    },
    selection() {
      return this.editor.selection.lastRange
    },
    alertObj() {
      return {
        title: this.formValue.title,
        message: this.formValue.alertMessages[0].body,
        resourceType: this.selectedResourceType,
      }
    },
    user() {
      return this.$store.state.user
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
  mounted() {
    console.log(this.user)
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
  margin-left: 8vw;
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
  width: 22.5vw;
  height: 29vh;
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
.alerts-page__message-options-body__bindings__fields {
  // margin: 3rem 0rem;
  // width: 40rem;
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
  font-size: 16px;
  margin-top: -0.5rem;
  color: $panther-silver;
}
.title {
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
  align-items: center;
  color: white;
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
  font-weight: bold;
  font-size: 16px;
  border-radius: 0.5rem;
  border: 2px solid $dark-green;
  padding: 0.25rem 1.5rem;
  cursor: pointer;
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
