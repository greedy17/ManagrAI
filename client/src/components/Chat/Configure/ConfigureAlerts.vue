<template>
  <div class="alerts">
    <!-- <AlertsHeader
      v-if="!isOnboarding"
      page="workflows"
      title="Workflows"
      :saving="false"
      :currentAlert="currentAlert"
      :creating="buildingCustom"
      :editing="editingWorkflow"
      :canSave="canSave"
      :isPaid="isPaid"
      :deleteId="currentAlert ? currentAlert.id : ''"
      :subtitle="currentAlert ? currentAlert.title : ''"
      :buttonText="'Create Workflow'"
      @cancel="closeBuilder"
      @save-item="saveWorkflow"
      @update-item="updateWorkflow"
      @delete-item="deleteWorkflow"
      @button-action="switchBuildCustom"
    /> -->

    <!-- <div class="onboarding-header" v-else>
      <div>
        <h3 class="left-margin">Getting started</h3>
      </div>

   

      <div style="margin-right: 16px">
        <button @click="onboardComplete" :disabled="!hasZoomChannel" class="primary-button">
          Complete
        </button>
      </div>
    </div> -->

    <div style="margin-top: 0rem" v-if="buildingCustom && !editingWorkflow && !creatingTemplate">
      <BuildYourOwn 
        :closeBuilder="closeBuilder" 
        :canSave="canSave"
        ref="workflowBuilder" 
        @can-save="setCanSave" 
        @save-item="saveWorkflow"
        @update-item="updateWorkflow"
        @delete-item="deleteWorkflow"
      />
    </div>

    <div style="margin-top: 0rem" v-if="editingWorkflow && !buildingCustom && !creatingTemplate">
      <AlertsEditPanel 
        :closeBuilder="closeBuilder" 
        :fromConfig="true" 
        :alert="currentAlert" 
        ref="editAlertsPanel" 
        @save-item="saveWorkflow"
        @update-item="updateWorkflow"
        @delete-item="deleteWorkflow"
      />
    </div>

    <div style="margin-top: 0rem" v-if="creatingTemplate && !editingWorkflow && !buildingCustom">
      <div v-if="templateName === 'CloseDatePassed'">
        <CloseDatePassed :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'UpcomingNextStep'">
        <NextStepDate :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'LargeOpportunities'">
        <LargeOpps :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'EmptyField'">
        <EmptyField :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'ClosingThisMonth'">
        <ClosingThisMonth :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'ClosingNextMonth'">
        <ClosingNextMonth :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'ClosingThisQuarter'">
        <ClosingThisQuarter :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'TeamPipeline'">
        <TeamPipeline :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'CloseDateApproaching'">
        <CloseDateApproaching :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'DealReview'">
        <DealRotting :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === '30DayPipeline'">
        <UpdateForecast :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'LogZoom'">
        <LogZoom :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
      <div v-if="templateName === 'ZoomRecap'">
        <ZoomRecap :noRenderHeader="true" :closeBuilder="closeBuilder" />
      </div>
    </div>

    <ConfigureWorkflows
      v-show="!buildingCustom && !editingWorkflow && !creatingTemplate"
      :key="$route.fullPath"
      @edit-workflow="openEditWorkflow"
      @create-template="openCreateTemplate"
      :templates="templates"
      :config="config"
      :switchBuildCustom="switchBuildCustom"
    ></ConfigureWorkflows>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
// import { UserOnboardingForm } from '@/services/users/forms'
import AlertTemplate from '@/services/alerts/'
import BuildYourOwn from '@/views/settings/alerts/create/BuildYourOwn'
import AlertsEditPanel from '@/views/settings/alerts/view/_AlertsEditPanel'
import User from '@/services/users'
import AlertsHeader from '@/components/AlertsHeader'
import ConfigureWorkflows from './ConfigureWorkflows.vue'
import LargeOpps from '@/views/settings/alerts/create/templates/LargeOpps.vue'
import CloseDatePassed from '@/views/settings/alerts/create/templates/CloseDatePassed.vue'
import NextStepDate from '@/views/settings/alerts/create/templates/NextStepDate.vue'
import EmptyField from '@/views/settings/alerts/create/templates/EmptyField.vue'
import ClosingThisMonth from '@/views/settings/alerts/create/templates/ClosingThisMonth.vue'
import ClosingNextMonth from '@/views/settings/alerts/create/templates/ClosingNextMonth.vue'
import ClosingThisQuarter from '@/views/settings/alerts/create/templates/ClosingThisQuarter.vue'
import TeamPipeline from '@/views/settings/alerts/create/templates/TeamPipeline.vue'
import CloseDateApproaching from '@/views/settings/alerts/create/templates/CloseDateApproaching.vue'
import DealRotting from '@/views/settings/alerts/create/templates/DealRotting.vue'
import UpdateForecast from '@/views/settings/alerts/create/templates/UpdateForecast.vue'
import LogZoom from '@/views/settings/alerts/create/templates/LogZoom.vue'
import ZoomRecap from '@/views/settings/alerts/create/templates/ZoomRecap.vue'

export default {
  name: 'ConfigureAlerts',
  components: {
    CollectionManager,
    BuildYourOwn,
    AlertsEditPanel,
    AlertsHeader,
    ConfigureWorkflows,
    LargeOpps,
    CloseDatePassed,
    NextStepDate,
    EmptyField,
    ClosingThisMonth,
    ClosingNextMonth,
    ClosingThisQuarter,
    TeamPipeline,
    CloseDateApproaching,
    DealRotting,
    UpdateForecast,
    LogZoom,
    ZoomRecap,
  },
  props: {
    config: {
      type: Object,
    }
  },
  data() {
    return {
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      // userOnboardingForm: new UserOnboardingForm({}),
      buildingCustom: false,
      canSave: false,
      editingWorkflow: false,
      creatingTemplate: false,
      currentAlert: null,
      templateName: '',
    }
  },

  methods: {
    closeBuilder() {
      this.buildingCustom = false
      this.editingWorkflow = false
      this.creatingTemplate = false
    },
    // onboardComplete() {
    //   this.userOnboardingForm.field.onboarding.value = false
    //   User.api
    //     .update(this.user.id, this.userOnboardingForm.value)
    //     .then((response) => {
    //       this.$store.dispatch('updateUser', User.fromAPI(response.data))
    //       this.$router.push({ name: 'ListTemplates' })
    //       this.$toast('Onboarding Complete!', {
    //         timeout: 2000,
    //         position: 'top-left',
    //         type: 'success',
    //         toastClassName: 'custom',
    //         bodyClassName: ['custom'],
    //       })
    //     })
    //     .catch((e) => {
    //       console.log(e)
    //     })
    // },
    updateWorkflow() {
      this.$refs.editAlertsPanel.updateWorkflow()
      this.buildingCustom = false
      this.editingWorkflow = false
      this.creatingTemplate = false
      this.$toast('Workflow Updated', {
        timeout: 2000,
        position: 'top-left',
        type: 'success',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
    },
    // deleteWorkflow(id) {
    //   this.$emit('delete-workflow')
    // },
    switchBuildCustom() {
      this.buildingCustom = !this.buildingCustom
    },
    deletedTitle(id) {
      let newList = []
      newList = this.templates.list.filter((val) => val.id === id)
      this.deleteTitle = newList[0].title
    },
    handleUpdate() {
      User.api
        .update(this.user.id)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
    },
    async deleteWorkflow(id) {
      console.log('hit upper')
      this.deletedTitle(id)
      try {
        console.log(1)
        await AlertTemplate.api.deleteAlertTemplate(id)
        console.log(2)
        this.$router.go()
      } catch (e) {
        this.$toast('Error removing workflow', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.editingWorkflow = false
        this.creatingTemplate = false
      }
    },
    deletedTitle(id) {
      let newList = []
      newList = this.templates.list.filter((val) => val.id === id)
      this.deleteTitle = newList[0].title
    },
    handleUpdate() {
      User.api
        .update(this.user.id)
        .then((response) => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
        })
        .catch((e) => {
          console.log(e)
        })
    },
    openEditWorkflow(alert) {
      this.editingWorkflow = true
      this.currentAlert = alert
    },
    openCreateTemplate(alert) {
      this.creatingTemplate = true
      this.templateName = alert
    },
    saveWorkflow() {
      this.$refs.workflowBuilder.onSave()
    },
    setCanSave(val) {
      this.canSave = val
    },
  },
  created() {
    this.templates.refresh()
  },
  computed: {
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    isOnboarding() {
      return this.$store.state.user.onboarding
    },
    // hasZoomChannel() {
    //   if (this.hasSlack) {
    //     return this.$store.state.user.slackAccount.zoomChannel
    //   }
    // },
    // hasSlack() {
    //   return this.$store.state.user.slackAccount
    // },
    user() {
      return this.$store.state.user
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.shimmer {
  display: inline-block;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  max-width: 200px;
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}

@keyframes tooltips-horz {
  to {
    opacity: 0.9;
    transform: translate(10%, 0%);
  }
}
// .primary-button {
//   box-shadow: none;
//   font-size: 13px;
// }
// .primary-button:disabled:hover {
//   background-color: $soft-gray !important;
// }
.delete {
  background-color: $coral;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  padding: 8px 16px;
  margin-left: 8px;
}
.gray-text {
  color: $light-gray-blue;
}
h5 {
  font-size: 0.8rem;
  font-weight: 700px;
}
img {
  filter: invert(90%);
  margin-left: 0.5rem;
}
.alerts {
  // height: 100vh;
  // width: 94vw;
  // overflow-y: scroll;

  border-radius: 6px;
}
a {
  text-decoration: none;
  color: $base-gray;
  cursor: pointer;
}
a:hover {
  border-radius: 0.2rem;
  cursor: pointer;
}
a:hover div {
  color: $dark-green;
  border-radius: 0.2rem;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
a:hover span {
  border-color: $dark-green;
  color: $dark-green;
}
.inactive {
  color: $light-gray-blue;
  transition: all 0.2s;
}
// .inactive:hover {
//   color: $base-gray;
//   transform: translateY(-10%);
// }
.header {
  position: fixed;
  z-index: 100;
  margin-left: -12px;
  top: 0;
  background-color: $white;
  width: 96vw;
  border-bottom: 1px solid $soft-gray;
  padding-top: 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
  }
}

// .onboarding-header {
//   position: fixed;
//   z-index: 100;
//   top: 0;
//   left: 0;
//   background-color: $white;
//   letter-spacing: 0.75px;
//   width: 100vw;
//   border-bottom: 1px solid $soft-gray;
//   padding-top: 8px;
//   display: flex;
//   flex-direction: row;
//   align-items: center;
//   justify-content: space-between;
//   // gap: 24px;

//   h3 {
//     font-size: 16px;
//     font-weight: 400;
//     letter-spacing: 0.75px;
//     line-height: 1.2;
//     cursor: pointer;
//   }
// }
.left-margin {
  margin-left: 30px;
}
.left-margin-s {
  margin-left: 16px;
}
.right-margin {
  margin-right: 40px;
}
.center-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.tooltip {
  position: relative;
  display: inline-block;
}
/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 140px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  opacity: 0.7;

  /* Position the tooltip text - */
  position: absolute;
  z-index: 1;
  top: 5px;
  right: 105%;
}
/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
}
// .tooltip .tooltiptext::after {
//   content: ' ';
//   position: absolute;
//   bottom: 100%; At the top of the tooltip
//   left: 50%;
//   margin-left: -5px;
//   border-width: 5px;
//   border-style: solid;
//   border-color: transparent transparent black transparent;
// }
.green_button {
  @include primary-button();
  max-height: 2rem;
  padding: 0.5rem 1.25rem;
  font-size: 12px;
}
::v-deep .multiselect * {
  font-size: 13px;
  font-family: $base-font-family;
  border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}
::v-deep .multiselect__content-wrapper {
  border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}
</style>
