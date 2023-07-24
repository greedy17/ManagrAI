<template>
  <div class="alerts">
    <Modal
      v-if="popularWorkflowModal"
      @close-modal="
        () => {
          $emit('cancel'), closePopularModal()
        }
      "
      dimmed
    >
      <div v-if="true /*hasSlack*/" class="invite-form crm-form form-margin-small" style="justify-content: flex-start;">
        <div class="header-crm">
          <div class="flex-row-wrapper inner-crm">
            <div class="flex-row-modal" style="margin: 0;">
              <!-- <img src="@/assets/images/logo.png" class="logo" alt="" /> -->
              <h3 class="invite-form__title">
                <!-- {{formatTemplateName(templateName)}} -->
                {{templateName === 'LogZoom' ? formatTemplateName(templateName) : 'Build List'}}
              </h3>
            </div>
            <div class="flex-row-modal" style="margin: 0;">
              <img
                @click="closePopularModal"
                src="@/assets/images/close.svg"
                alt=""
                style="
                  filter: invert(30%);
                  cursor: pointer;
                  width: 20px;
                  height: 20px;
                  margin-right: 5px;
                "
              />
            </div>
          </div>
        </div>
        <div class="flex-row-modal inner-crm" style="margin: 0; justify-content: flex-start; width: 90%; height: 45vh; overflow-y: auto; border: none;">
          <div class="outer-height" v-if="templateName === 'CloseDatePassed'">
            <CloseDatePassed 
              :config="
                userCRM === 'HUBSPOT' ? allConfigs.CLOSE_DATE_PASSED_HUBSPOT : allConfigs.CLOSE_DATE_PASSED
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'UpcomingNextStep'">
            <NextStepDate 
              :config="
                userCRM === 'HUBSPOT' ? allConfigs.UPCOMING_NEXT_STEP_HUBSPOT : allConfigs.UPCOMING_NEXT_STEP
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'LargeOpportunities'">
            <LargeOpps 
              :config="
                userCRM === 'HUBSPOT' ? allConfigs.LARGE_DEALS_HUBSPOT : allConfigs.LARGE_OPPORTUNITIES
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'EmptyField'">
            <EmptyField 
              :config="
                userCRM === 'HUBSPOT' ? allConfigs.EMPTY_FIELD_HUBSPOT : allConfigs.EMPTY_FIELD
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'ClosingThisMonth'">
            <ClosingThisMonth 
              :config="
                userCRM == 'HUBSPOT' ? allConfigs.CLOSING_THIS_MONTH_HUBSPOT : allConfigs.CLOSING_THIS_MONTH
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'ClosingNextMonth'">
            <ClosingNextMonth 
              :config="
                userCRM == 'HUBSPOT' ? allConfigs.CLOSING_NEXT_MONTH_HUBSPOT : allConfigs.CLOSING_NEXT_MONTH
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'ClosingThisQuarter'">
            <ClosingThisQuarter 
              :config="
                allConfigs.CLOSING_THIS_QUARTER
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'TeamPipeline'">
            <TeamPipeline 
              :config="
                userCRM === 'HUBSPOT' ? allConfigs.TEAM_PIPELINE_HUBSPOT : allConfigs.TEAM_PIPELINE
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'CloseDateApproaching'">
            <CloseDateApproaching 
              :config="
                userCRM === 'HUBSPOT' ? allConfigs.CLOSE_DATE_APPROACHING_HUBSPOT : allConfigs.CLOSE_DATE_APPROACHING
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'DealReview'">
            <DealRotting 
              :config="
                userCRM === 'HUBSPOT' ? allConfigs.DEAL_REVIEW_HUBSPOT : allConfigs.DEAL_REVIEW
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === '30DayPipeline'">
            <UpdateForecast 
              :config="
                userCRM === 'HUBSPOT' ? allConfigs.THIRTY_DAY_PIPELINE_HUBSPOT : allConfigs.THIRTY_DAY_PIPELINE
              "
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
          <div class="outer-height" v-if="templateName === 'LogZoom'">
            <LogZoom 
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
              @close-modal="closePopularModal"
            />
          </div>
          <div class="outer-height" v-if="templateName === 'ZoomRecap'">
            <ZoomRecap 
              :canSave="canSaveWorkflow" 
              :closePopularModal="closePopularModal"
              :saveWorkflow="saveWorkflow" 
              :noRenderHeader="true" 
              :closeBuilder="closeBuilder" 
            />
          </div>
        </div>
        <!-- <div class="invite-form__actions"> -->
      </div>
      <!-- <div class="workflow__modal">
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
      </div> -->
    </Modal>
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
      <Modal
        v-if="popularWorkflowModal"
        @close-modal="
          () => {
            $emit('cancel'), closePopularModal()
          }
        "
        dimmed
      >
        <div class="workflow__modal">
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
      </Modal>
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
import allConfigs from '@/views/settings/alerts/configs'
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
import { decryptData } from '../../../encryption'

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
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  props: {
    config: {
      type: Object,
    }
  },
  data() {
    return {
      allConfigs,
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      // userOnboardingForm: new UserOnboardingForm({}),
      buildingCustom: false,
      canSave: false,
      editingWorkflow: false,
      creatingTemplate: false,
      popularWorkflowModal: false,
      ableToSave: false,
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
    canSaveWorkflow(bool) {
      this.ableToSave = bool
    },
    formatTemplateName(templateName) {
      let newTemplateName = templateName[0]
      for (let i = 1; i < templateName.length; i++) {
        const letter = templateName[i]
        // if letter is uppercase
        if (letter.toLowerCase() !== letter) {
          newTemplateName += ` ${letter}`
        } else {
          newTemplateName += letter
        }
      }
      return newTemplateName
    },
    // async saveWorkflow() {
    //   this.savingTemplate = true
    //   const newConfigs = this.config.newConfigs[0]
    //   const operandIden = this.config.newGroups[0].newOperands[0].operandIdentifier
    //   let largeOpsCheck = true
    //   if (this.largeOpps) {
    //     largeOpsCheck = false
    //     if (this.largeOppsBool) {
    //       largeOpsCheck = true
    //     }
    //   }
    //   if (
    //     (newConfigs.recurrenceDays.length || operandIden) &&
    //     newConfigs.alertTargets.length &&
    //     this.selectUsersBool &&
    //     largeOpsCheck &&
    //     (this.setDaysBool || this.selectFieldBool)
    //   ) {
    //     try {
    //       const res = await AlertTemplate.api.createAlertTemplate({
    //         ...this.config,
    //         user: this.$store.state.user.id,
    //         directToUsers: this.directToUsers,
    //       })

    //       if (res.status === 400 && res.data.message) {
    //         this.$toast(res.data.message, {
    //           timeout: 2000,
    //           position: 'top-left',
    //           type: 'error',
    //           toastClassName: 'custom',
    //           bodyClassName: ['custom'],
    //         })
    //         return
    //       }

    //       this.handleUpdate()

    //       this.$toast('Workflow saved Successfully', {
    //         timeout: 2000,
    //         position: 'top-left',
    //         type: 'success',
    //         toastClassName: 'custom',
    //         bodyClassName: ['custom'],
    //       })
    //       this.$router.push({ name: 'ListTemplates' })
    //     } catch (e) {
    //       console.log('e', e)
    //       this.$toast(`${e}`, {
    //         timeout: 2000,
    //         position: 'top-left',
    //         type: 'error',
    //         toastClassName: 'custom',
    //         bodyClassName: ['custom'],
    //       })
    //     } finally {
    //       this.savingTemplate = false
    //     }
    //   }
    // },
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
      this.deletedTitle(id)
      try {
        await AlertTemplate.api.deleteAlertTemplate(id)
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
      // this.creatingTemplate = true
      this.popularWorkflowModal = true
      this.templateName = alert
    },
    closePopularModal() {
      this.popularWorkflowModal = false 
      this.creatingTemplate = false
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
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.organizationRef.isPaid
    },
    isOnboarding() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
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
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/modals';

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
.workflow__modal {
  @include base-modal();
  color: $base-gray;
  min-height: 25vh;
  max-height: 70vh;
  padding: 0 1rem;
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    background-color: white;
    z-index: 2;
    top: 0;
    p {
      font-size: 16px;
    }
  }

  &__body {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    margin-bottom: 16px;
    width: 100%;

    div {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
      h4 {
        font-weight: 900;
        font-size: 13px;
        margin: 0;
        padding: 0;
        min-width: 32vw;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;

        span {
          // background-color: $off-white;
          color: $light-gray-blue;
          padding: 4px 8px;
          border-radius: 4px;
          margin-left: 12px;
          font-size: 13px;
          opacity: 0.9;
        }
      }

      p {
        font-weight: bold;
        font-size: 13px;
        color: $light-gray-blue;
        padding: 0;
        margin: 0;
        margin-top: 4px;
      }
    }
  }
}
.invite-form {
  @include small-modal();
  min-width: 37vw;
  // min-height: 64vh;
  align-items: center;
  justify-content: space-between;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
    font-size: 22px;
  }
  &__subtitle {
    text-align: left;
    font-size: 16px;
    margin-left: 1rem;
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    // margin-top: -4rem;
  }
  &__inner_actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    border-top: 1px solid $soft-gray;
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
  }
}
.crm-form {
  height: 60vh;
  width: 32vw;
}
.form-margin-small {
  margin-top: 2rem;
}
.header-crm {
  // background-color: $soft-gray;
  width: 100%;
  // border-bottom: 1px solid $soft-gray;
  position: relative;
  border-top-right-radius: 4px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-top-left-radius: 4px;
  display: flex;
  justify-content: center;
  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: flex-start;

  h3 {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $base-gray;
  }
}
.flex-row-wrapper {
  display: flex;
  justify-content: space-between;
}
.inner-crm {
  border-bottom: 1px solid $soft-gray;
  width: 90%;
  padding-bottom: 0.4rem;
  overflow-y: auto;
}
.flex-row-modal {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  margin: 0 5%;
  letter-spacing: 1px;
}
.img-border-modal {
  // @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  // padding: 4px 6px;
  margin-right: 8px;
  margin-top: 0.5rem;
}
.cancel-button {
  @include gray-button();
}
.save {
  // @include base-button();
  // background-color: $dark-green;
  // color: $white;
  // font-size: 12px;
  // transition: all 0.3s;
  @include primary-button();
  margin-right: 0.1rem;
}
.outer-height {
  height: 42vh;
  overflow-y: auto;
}
</style>
