<template>
  <div class="alerts-template-list">
    <template v-if="!templates.isLoading && templates.list.length">
      <ExpandablePanel>
        <template v-slot:panel-header="{ classes, expand }">
          <div
            :class="classes"
            class="alerts-template-list__header alerts-template-list__header--heading"
          >
            <span class="alerts-template-list__header-item alerts-template-list__header-item--main"
              >Title</span
            >
            <span class="alerts-template-list__header-item">Run Now</span>
            <span class="alerts-template-list__header-item">Schedule</span>
            <span class="alerts-template-list__header-item">Delete</span>
          </div>
        </template>
      </ExpandablePanel>
      <ExpandablePanel :key="i" v-for="(alert, i) in templates.list">
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
            <!-- <span
              @click.stop="onTest(alert.id)"
              class="alerts-template-list__header-item alerts-template-list__header-item"
            >
              <svg class="icon" fill="black" viewBox="0 0 30 30">
                <use xlink:href="@/assets/images/loop.svg#loop" />
              </svg>
            </span> -->
          </div>
        </template>
        <template slot="panel-content">
          <div>
            <AlertsEditPanel :alert="alert" />
          </div>
        </template>
      </ExpandablePanel>
    </template>
    <template v-else-if="!templates.isLoading && !templates.list.length">
      <div class="no-data">
        <p>No alerts found. Click <strong>''Build''</strong> to create your first Smart Alert!</p>
      </div>
    </template>
    <template v-else>
      <PulseLoadingSpinner />
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

.icon {
  display: block;
  cursor: pointer;
  width: 20px;
  height: 30px;
}
.pink {
  color: $candy;
}
</style>
