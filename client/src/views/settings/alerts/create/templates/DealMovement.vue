<template>
  <div class="alerts-page">
    <div v-if="!showLoader" class="col">
      <h2 @click="log" style="color: black; margin-top: -0.5rem" class="title">Deal Movement</h2>
      <p style="color: #5d5e5e" class="sub__">Activate workflows related to deal movement</p>
    </div>

    <div class="invert center-loader" v-if="showLoader">
      <img src="@/assets/images/loading-gif.gif" class="invert" style="height: 8rem" alt="" />
    </div>

    <div v-if="!showLoader" class="row">
      <div v-if="!advancedConfigActive" class="stage-item">
        <p>Stage Advanced</p>
        <button class="plus_button" @click="onAdvancing">
          <img src="@/assets/images/add.svg" alt="" />
        </button>
      </div>
      <div v-else class="added-item">
        <p>Stage Advanced</p>
        <button style="cursor: auto" class="plus_button">
          <img src="@/assets/images/configCheck.png" class="filtered" alt="" />
        </button>
      </div>

      <div v-if="!commitConfigActive" @click="onCommit" class="stage-item">
        <p>Moved to Commit</p>
        <button class="plus_button">
          <img src="@/assets/images/add.svg" alt="" />
        </button>
      </div>
      <div v-else class="added-item">
        <p>Moved to Commit</p>
        <button style="cursor: auto" class="plus_button">
          <img src="@/assets/images/configCheck.png" class="filtered" alt="" />
        </button>
      </div>

      <div v-if="!pushedConfigActive" @click="onPushing" class="stage-item">
        <p>Close Date Pushed</p>
        <button class="plus_button">
          <img src="@/assets/images/add.svg" alt="" />
        </button>
      </div>
      <div v-else class="added-item">
        <p>Close Date Pushed</p>
        <button style="cursor: auto" class="plus_button">
          <img src="@/assets/images/configCheck.png" class="filtered" alt="" />
        </button>
      </div>
    </div>

    <div
      v-if="
        !pushedConfigActive &&
        !advancedConfigActive &&
        !commitConfigActive &&
        !commit &&
        !pushing &&
        !advancing &&
        !showLoader
      "
      style="margin-top: 10%"
    >
      <h1 class="bouncy" style="color: #5d5e5e; font-weight: bold; text-align: center">0</h1>
      <h6 style="font-weight: bold; color: #5d5e5e; text-align: center">
        Nothing here, add a workflow to get started.. (o^^)o
      </h6>
    </div>

    <div v-if="!showLoader" class="alert-row">
      <div v-if="advancedConfigActive && !advancing" class="added-collection">
        <div class="added-collection__header">
          <p class="title">Stage Advanced</p>
          <span class="active">active</span>
        </div>
        <section class="added-collection__body">
          <p>Recieve alerts when deals advances to your selected stage</p>
        </section>
        <section class="added-collection__footer">
          <div class="edit" @click="onAdvancing">
            <img
              src="@/assets/images/edit.png"
              style="height: 1rem; filter: brightness(40%)"
              alt=""
            />
          </div>
        </section>
      </div>

      <div v-if="commitConfigActive && !commit" class="added-collection">
        <div class="added-collection__header">
          <p class="title">Moved to Commit</p>
          <span class="active">active</span>
        </div>
        <section class="added-collection__body">
          <p>Recieve alerts when deals move to commit.</p>
        </section>
        <section class="added-collection__footer">
          <div class="edit" @click="onCommit">
            <img
              src="@/assets/images/edit.png"
              style="height: 1rem; filter: brightness(40%)"
              alt=""
            />
          </div>
        </section>
      </div>

      <div v-if="pushedConfigActive && !pushing" class="added-collection">
        <div class="added-collection__header">
          <p class="title">Close date pushed</p>
          <span class="active">active</span>
        </div>
        <section class="added-collection__body">
          <p>Recieve alerts when Close Date's are pushed into a new month.</p>
        </section>
        <section class="added-collection__footer">
          <div class="edit" @click="onPushing">
            <img
              src="@/assets/images/edit.png"
              style="height: 1rem; filter: brightness(40%)"
              alt=""
            />
          </div>
        </section>
      </div>

      <transition name="fade">
        <div v-if="advancing">
          <StageAdvanced></StageAdvanced>
        </div>
      </transition>

      <transition name="fade">
        <div v-if="commit">
          <MovedToCommit></MovedToCommit>
        </div>
      </transition>

      <transition name="fade">
        <div v-if="pushing">
          <CloseDatePushed></CloseDatePushed>
        </div>
      </transition>
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
import MovedToCommit from '@/views/settings/alerts/create/templates/MovedToCommit'
import CloseDatePushed from '@/views/settings/alerts/create/templates/CloseDatePushed'
import StageAdvanced from '@/views/settings/alerts/create/templates/StageAdvanced'

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
  name: 'DealMovement',
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
    MovedToCommit,
    CloseDatePushed,
    StageAdvanced,
  },
  data() {
    return {
      channelOpts: new SlackListResponse(),
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      advancing: false,
      commit: false,
      pushing: false,
      showLoader: true,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: [],
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      users: CollectionManager.create({ ModelClass: User }),
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
    }
  },
  async created() {
    this.templates.refresh()
  },
  methods: {
    log() {
      console.log(this.realtimeConfigs)
    },
    onAdvancing() {
      this.advancing = !this.advancing
    },
    onCommit() {
      this.commit = !this.commit
    },
    onPushing() {
      this.pushing = !this.pushing
    },
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
    goToStageAdvanced() {
      this.$router.push({ name: 'StageAdvanced' })
    },
    goToMeetingLogged() {
      this.$router.push({ name: 'MeetingLogged' })
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
    goToNextStep() {
      this.$router.push({ name: 'NextStep' })
    },
    goToSaved() {
      this.$router.push({ name: 'ListTemplates' })
    },
    getWorkflowIds(arr1, arr2) {
      return arr1.some((item) => arr2.includes(item))
    },
  },
  mounted() {
    setTimeout(() => {
      this.showLoader = false
    }, 400)
  },
  computed: {
    realtimeConfigs() {
      return Object.values(this.$store.state.user.slackAccount.realtimeAlertConfigs)
    },
    commitConfigActive() {
      for (let i = 0; i < this.realtimeConfigs.length; i++) {
        if (this.realtimeConfigs[i]['Moved to Commit']) {
          return true
        }
      }
    },
    advancedConfigActive() {
      for (let i = 0; i < this.realtimeConfigs.length; i++) {
        if (this.realtimeConfigs[i]['Stage Advanced']) {
          return true
        }
      }
    },
    pushedConfigActive() {
      for (let i = 0; i < this.realtimeConfigs.length; i++) {
        if (this.realtimeConfigs[i]['Close date pushed']) {
          return true
        }
      }
    },
    workFlowIds() {
      let arr = []
      for (let i = 0; i < this.templates.list.length; i) {
        arr.push(this.templates.list[i].id)
      }
      return arr
    },
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
    recapChannel() {
      return this.$store.state.user.slackAccount.recapChannel
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
    configs() {
      return this.$store.state.user.activatedManagrConfigs
    },
    isAdmin() {
      return this.$store.state.user.isAdmin
    },
    hasZoomChannel() {
      return this.$store.state.user.slackAccount.zoomChannel
    },
    userLevel() {
      return this.$store.state.user.userLevel
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
h4 {
  font-size: 14px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
.invert {
  filter: invert(99%);
}
.center-loader {
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  height: 60vh;
}
.forecast__collection {
  display: flex;
  align-items: flex-start;
  justify-content: space-evenly;
  flex-direction: row;
  background-color: $white;
  box-shadow: 3px 4px 7px $very-light-gray;
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 1rem;
}
.edit {
  border: none;
  box-shadow: 1px 1px 1px $very-light-gray;
  background-color: transparent;
  border-radius: 50%;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}
.edit:hover {
  transform: scale(1.1);
  box-shadow: 2px 3px 4px $very-light-gray;
}
.plus_button {
  border: none;
  // box-shadow: 3px 4px 2px $very-light-gray;
  background-color: transparent;
  border-radius: 50%;
  padding: 0.2rem;
  margin-left: 0.25rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: bold;
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
.alert-row {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  // align-items:
}
.filtered {
  filter: invert(33%) sepia(52%) saturate(2452%) hue-rotate(130deg) brightness(68%) contrast(80%);
  height: 1.2rem;
}
.alerts-page {
  margin-top: 4.5rem;
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
.stage-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0rem 0.75rem;
  margin-right: 1rem;
  box-shadow: 3px 2px 2px $very-light-gray;
  border-radius: 7px;
  color: $base-gray;
  cursor: pointer;
  font-size: 12px;
}
.added-collection {
  background-color: white;
  box-shadow: 2px 2px 3px $very-light-gray;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 2.5rem;
  max-width: 20vw;
  max-height: 27vh;
  margin-right: 5vw;
  &__header {
    max-height: 3rem;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    border-bottom: 3px solid $soft-gray;
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
  }
  &__footer {
    display: flex;
    align-items: flex-end;
    height: 3rem;
    justify-content: flex-end;
  }
}
.added-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0rem 0.75rem;
  margin-right: 1rem;
  box-shadow: 1px 1px 1px $very-light-gray;
  border-radius: 7px;
  color: $base-gray;
  font-size: 12px;
  cursor: not-allowed;
}
.active {
  background-color: $lighter-green;
  border-radius: 0.33rem;
  border: none;
  padding: 0.25rem;
  font-size: 10px;
  margin-left: 0.5rem;
  color: white;
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
  font-size: 13px;
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
  align-items: flex-start;
  margin-left: 0.75rem;
  margin-top: 1rem;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 0.5rem 0rem;
  border-bottom: 2px solid $soft-gray;
  width: 98vw;
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
.spacer {
  height: 0.5rem;
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