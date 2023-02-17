<template>
  <div class="alerts">
    <AlertsHeader
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
    />

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

    <div v-if="buildingCustom && !editingWorkflow">
      <BuildYourOwn ref="workflowBuilder" @can-save="setCanSave" />
    </div>

    <div v-if="editingWorkflow && !buildingCustom">
      <AlertsEditPanel :alert="currentAlert" ref="editAlertsPanel" />
    </div>

    <router-view
      v-show="!buildingCustom && !editingWorkflow"
      :key="$route.fullPath"
      @edit-workflow="openEditWorkflow"
      :templates="templates"
    ></router-view>
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

export default {
  name: 'AlertsDashboardMenu',
  components: {
    CollectionManager,
    BuildYourOwn,
    AlertsEditPanel,
    AlertsHeader,
  },
  data() {
    return {
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      // userOnboardingForm: new UserOnboardingForm({}),
      buildingCustom: false,
      canSave: false,
      editingWorkflow: false,
      currentAlert: null,
    }
  },

  methods: {
    closeBuilder() {
      this.buildingCustom = false
      this.editingWorkflow = false
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
      this.$toast('Workflow Updated', {
        timeout: 2000,
        position: 'top-left',
        type: 'success',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
    },
    deleteWorkflow(id) {
      this.$emit('delete-workflow')
    },
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
      this.deletedTitle(id)

      try {
        await AlertTemplate.api.deleteAlertTemplate(id)
        this.handleUpdate()
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
  height: 96vh;
  width: 94vw;
  overflow: scroll;
  // margin-top: 48px;
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
.green_button {
  color: white;
  background-color: $dark-green;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  border: none;
  cursor: pointer;
  text-align: center;
}
.green_button:disabled {
  background-color: $soft-gray;
  color: $gray;
}
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
</style>
