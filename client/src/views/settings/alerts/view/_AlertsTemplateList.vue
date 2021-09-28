<template>
  <div class="alerts-template-list">
    <Modal v-if="deleteOpen" dimmed>
      <div class="delete_modal">
        <h2 style="color: white">Delete Alert</h2>
        <div>
          <p>This action cannot be undone, are you sure ?</p>
          <div class="center">
            <button style="margin-right: 0.5rem" class="no__button" @click="deleteClose">No</button>
            <button class="yes__button" @click.stop="onDeleteTemplate(deleteId)">Yes</button>
          </div>
        </div>
      </div>
    </Modal>

    <div class="col">
      <h2 v-if="editing && templates.list.length" class="titles">Run your Smart Alerts</h2>
      <h2 v-if="!editing" class="titles">Edit your Smart Alert</h2>
      <h2 v-if="!templates.list.length" class="titles">Smart Alerts</h2>
      <div v-if="!templates.list.length">
        <p class="center" style="font-weight: bold; color: #5d5e5e; margin-top: -0.5rem">
          Automated workflows that help keep you on track
        </p>
        <p style="color: #5d5e5e; font-weight: bold; text-align: center; margin-top: 2rem">
          No alerts found.
          <router-link to="templates" class="alert-links">Templates</router-link>
          are a great place to start, or you can
          <router-link to="build-your-own" class="alert-links">build your own!</router-link>
        </p>
      </div>
    </div>
    <template v-if="!templates.isLoading && templates.list.length">
      <div class="middle" v-if="!editing">
        <div class="edit__modal">
          <div>
            <AlertsEditPanel :alert="currentAlert" />
          </div>
          <button style="margin-bottom: 1rem" class="no__button" @click="closeEdit">Done</button>
        </div>
      </div>
      <div class="alert_cards" v-if="editing">
        <div :key="i" v-for="(alert, i) in templates.list" class="card__">
          <div :data-key="alert.id" class="card__header">
            <h3>{{ alert.title.toUpperCase() }}</h3>
          </div>
          <div class="row">
            <button @click.stop="onRunAlertTemplateNow(alert.id)" class="green_button">
              Run now
            </button>
            <!-- <div class="centered">
              <button @click="onTest(alert.id)" class="test-button">Test Alert</button>

              <p style="margin-left: 0.5rem">Results: {{ alert.instances.length }}</p>
            </div> -->
          </div>
          <div class="row__start">
            <p style="margin: 0.5rem 0.5rem">Schedule</p>
            <div class="row__">
              <p style="margin-right: 0.25rem">OFF</p>
              <ToggleCheckBox
                @input="onToggleAlert(alert.id, alert.isActive)"
                v-model="alert.isActive"
                offColor="#aaaaaa"
                onColor="#199e54"
              />
              <p style="margin-left: 0.25rem">ON</p>
            </div>

            <div class="row__two">
              <img
                @click="makeAlertCurrent(alert)"
                src="@/assets/images/settings.png"
                style="height: 2rem; cursor: pointer"
              />

              <img
                src="@/assets/images/whitetrash.png"
                style="height: 2rem; cursor: pointer"
                @click="deleteClosed(alert.id)"
              />
            </div>
          </div>

          <template slot="panel-content">
            <div>
              <AlertsEditPanel :alert="alert" />
            </div>
          </template>
        </div>
      </div>

      <!-- <ExpandablePanel :key="i" v-for="(alert, i) in templates.list">
        <template v-slot:panel-header="{ classes, expand }">
          <div :data-key="alert.id" @click="expand" :class="classes">
            <span class="alerts-template-list__header-item alerts-template-list__header-item--main"
              >{{ alert.title }} <img src="@/assets/images/edit.png" style="height: 1rem" alt=""
            /></span>
            <span
              @click.stop="onRunAlertTemplateNow(alert.id)"
              class="alerts-template-list__header-item alerts-template-list__header-item"
            >
              <svg class="icon" fill="black" viewBox="0 0 30 30">
                <use xlink:href="@/assets/images/loop.svg#loop" />
              </svg>
            </span>

            <span class="alerts-template-list__header-item alerts-template-list__header-item">
              <ToggleCheckBox
                @input="onToggleAlert(alert.id, alert.isActive)"
                v-model="alert.isActive"
                offColor="#aaaaaa"
                onColor="#199e54"
                @click="
                  () => {
                    console.log('log')
                  }
                "
              />
            </span>

            <span
              class="alerts-template-list__header-item alerts-template-list__header-item"
              @click.stop="onDeleteTemplate(alert.id)"
            >
              <svg class="icon" fill="black" viewBox="0 0 30 30">
                <use xlink:href="@/assets/images/remove.svg#remove" />
              </svg>
            </span>
            <span
              @click.stop="onTest(alert.id)"
              class="alerts-template-list__header-item alerts-template-list__header-item"
            >
              <svg class="icon" fill="black" viewBox="0 0 30 30">
                <use xlink:href="@/assets/images/loop.svg#loop" />
              </svg>
            </span>
          </div>
        </template>
        <template slot="panel-content">
          <div>
            <AlertsEditPanel :alert="alert" />
          </div>
        </template>
      </ExpandablePanel> -->
    </template>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges

import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'

//Internal

import ExpandablePanel from '@/components/ExpandablePanel'
import FormField from '@/components/forms/FormField'
import AlertsEditPanel from '@/views/settings/alerts/view/_AlertsEditPanel'
import Modal from '@/components/InviteModal'

/**
 * Services
 *
 */
import { CollectionManager, Pagination } from '@thinknimble/tn-models'

import AlertTemplate, {
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertOperandForm,
} from '@/services/alerts/'

export default {
  name: 'AlertsTemplateList',
  components: {
    ExpandablePanel,
    PulseLoadingSpinner,
    ToggleCheckBox,
    FormField,
    AlertsEditPanel,
    Modal,
  },
  data() {
    return {
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      deleteOpen: false,
      deleteId: '',
      currentAlert: {},
      editing: true,
    }
  },
  async created() {
    this.templates.refresh()
  },
  methods: {
    makeAlertCurrent(val) {
      this.currentAlert = val
      this.editing = !this.editing
    },
    deleteClosed(val) {
      this.deleteOpen === false ? (this.deleteOpen = true) : (this.deleteOpen = false)
      this.deleteId = val
    },
    deleteClose() {
      this.deleteOpen === false ? (this.deleteOpen = true) : (this.deleteOpen = false)
    },
    closeEdit() {
      this.editing = !this.editing
    },
    async onDeleteTemplate(id) {
      try {
        await AlertTemplate.api.deleteAlertTemplate(id)
        await this.templates.refresh()
        this.deleteOpen = !this.deleteOpen
      } catch {
        this.$Alert.alert({
          message: 'There was an error removing your alert',
          type: 'error',
          timeout: 2000,
        })
      }
    },
    async onTest(id) {
      try {
        await AlertTemplate.api.testAlertTemplate(id)
        this.$Alert.alert({
          message: `Alert has been initiated to test against your data only`,
          type: 'success',
          timeout: 2000,
        })
      } catch {
        this.$Alert.alert({
          message: 'There was an error testing your alert',
          type: 'error',
          timeout: 2000,
        })
      }
    },
    async onToggleAlert(id, value) {
      try {
        await AlertTemplate.api.updateAlertTemplate(id, { is_active: value })
        await this.templates.refresh()
        this.$Alert.alert({
          message: `Alert is now ${value ? 'active' : 'inactive'}`,
          type: 'success',
          timeout: 2000,
        })
      } catch {
        this.$Alert.alert({
          message: 'There was an error toggling your alert',
          type: 'error',
          timeout: 2000,
        })
      }
    },
    async onRunAlertTemplateNow(id) {
      try {
        await AlertTemplate.api.runAlertTemplateNow(id)
        this.$Alert.alert({
          message: `Alert has been initiated`,
          type: 'success',
          timeout: 2000,
        })
      } catch {
        this.$Alert.alert({
          message: 'There was an error removing your alert',
          type: 'error',
          timeout: 2000,
        })
      }
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

::v-deep .item-container__label {
  color: white;
  border: none;
}
::v-deep .ls-container__list--horizontal {
  background-color: $panther;
  width: 50vw;
}
::v-deep .ls-container {
  background: transparent;
  box-shadow: none;
  margin-bottom: 1rem;
}
.titles {
  color: black;
  font-weight: bold;
  text-align: center;
}
.alert-links {
  color: #199e54;
  border-bottom: 3px solid #19954e;
}
.test-button {
  background-color: white;
  color: $dark-green;
  border: none;
  font-weight: bold;
  padding: 0.5rem 0.75rem;
  border-radius: 0.25rem;
  cursor: pointer;
}
.middle {
  display: flex;
  justify-content: center;
  align-items: center;
}
.delete_modal {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: $panther;
  border-radius: 0.5rem;
  color: white;
  height: 28vh;
}
.edit__modal {
  background-color: $panther;
  border-radius: 1rem;
  color: white;
  height: 40vh;
  width: 80%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
  overflow: scroll;
}

.yes__button {
  width: 8vw;
  background-color: $dark-green;
  border: none;
  border-radius: 0.25rem;
  color: white;
  cursor: pointer;
  margin-right: 0.5rem;
  padding: 0.5rem;
  font-weight: bold;
}
.no__button {
  width: 8vw;
  background-color: $panther-gray;
  border: none;
  border-radius: 0.25rem;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
  font-weight: bold;
}
.yes__button:hover,
.no__button:hover {
  filter: brightness(80%);
}
.no-data {
  color: $gray;
  margin-left: 0.5rem;
  font-size: 15px;
}
.alerts-template-list__header--heading {
  @include header-subtitle();
}
.alerts-template-list {
  margin-left: 7vw;
  &__header {
    display: flex;

    &-item {
      min-width: 10rem;
      &--main {
        flex: 1 0 auto;
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
  width: 10rem;
  min-height: 25vh;
  margin-right: 1rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 3px 4px 7px black;
  color: white;
  @media only screen and (min-width: 768px) {
    flex: 1 0 24%;
    min-width: 21rem;
    max-width: 30rem;
  }

  &header {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 3rem;
    font-weight: bold;
    margin-bottom: 1rem;
    color: white;
  }
}
.icon {
  display: block;
  cursor: pointer;
  width: 20px;
  height: 30px;
}
.pink {
  color: $candy;
}
a {
  text-decoration: none;
  color: white;
  cursor: pointer;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
}
.row__ {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin: 0 0.5rem 0 0.5rem;
  color: $panther-silver;
}
.row__two {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: 1rem;
  width: 100%;
}
.row__start {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-top: 1rem;
  width: 100%;
}
.green_button {
  color: white;
  background-color: $dark-green;
  width: 8vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  border: none;
  cursor: pointer;
}
.delete_button {
  color: $panther-orange;
  border: none;
  background-color: $panther;
  width: 8vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
}
.edit_button {
  color: $panther-blue;
  background-color: white;
  width: 8vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  border: 2px solid $white;
  cursor: pointer;
}
.debug {
  border: 2px solid red;
}
.center {
  display: flex;
  justify-content: center;
  align-items: center;
}
.centered {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}
// ::-webkit-scrollbar {
//   background-color: $panther;
//   -webkit-appearance: none;
//   width: 4px;
//   height: 100%;
// }
// ::-webkit-scrollbar-thumb {
//   border-radius: 2px;
//   background-color: $panther-silver;
// }
</style>
