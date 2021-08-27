<template>
  <div class="alerts-template-list">
    <div class="col">
      <h2 style="color: white; font-weight: bold; text-align: center">
        Run/edit your Smart Alerts
      </h2>
      <div>
        <p
          v-if="!templates.list.length"
          style="color: #beb5cc; font-weight: bold; text-align: center"
        >
          No alerts found. <router-link to="templates">Templates</router-link> are a great place to
          start, or you can <router-link to="templates">build your own!</router-link>
        </p>
      </div>
    </div>
    <template v-if="!templates.isLoading && templates.list.length">
      <div class="alert_cards">
        <div :key="i" v-for="(alert, i) in templates.list" class="card__">
          <div :data-key="alert.id" class="card__header">
            <h3>{{ alert.title.toUpperCase() }}</h3>
          </div>
          <div class="row">
            <button @click.stop="onRunAlertTemplateNow(alert.id)" class="green_button">
              Run now
            </button>
            <div>
              <button class="edit_button" style="margin-right: 0.25rem">Edit</button>
              <button class="delete_button" @click.stop="onDeleteTemplate(alert.id)">Delete</button>
            </div>
          </div>

          <div class="row__two">
            <div class="row__">
              <p style="margin-right: 0.25rem">OFF</p>
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
              <p style="margin-left: 0.25rem">ON</p>
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
    <template> </template>
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
  components: { ExpandablePanel, PulseLoadingSpinner, ToggleCheckBox, FormField, AlertsEditPanel },
  data() {
    return {
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
    }
  },
  async created() {
    this.templates.refresh()
  },
  methods: {
    async onDeleteTemplate(id) {
      try {
        await AlertTemplate.api.deleteAlertTemplate(id)
        await this.templates.refresh()
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
          message: 'There was an error removing your alert',
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
          message: 'There was an error removing your alert',
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
.green_button {
  color: $dark-green;
  background-color: white;
  width: 8vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  border: none;
  cursor: pointer;
}
.delete_button {
  color: $panther-silver;
  border: 1px solid $panther-silver;
  background-color: $panther;
  width: 5vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
}
.edit_button {
  color: $panther-purple;
  background-color: white;
  width: 5vw;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-weight: bold;
  font-size: 16px;
  border: none;
  cursor: pointer;
}
.debug {
  border: 2px solid red;
}
</style>
