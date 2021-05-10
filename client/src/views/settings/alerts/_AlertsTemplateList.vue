<template>
  <div class="alerts-template-list">
    <template v-if="!templates.isLoading && templates.list.length">
      <ExpandablePanel>
        <template v-slot:panel-header="{ classes, expand }">
          <div :class="classes">
            <span>Title</span>
            <span>Run Now</span>
            <span>Delete</span>
            <span>Active</span>
          </div>
        </template>
      </ExpandablePanel>
      <ExpandablePanel v-for="(alert, i) in templates.list">
        <template v-slot:panel-header="{ classes, expand }">
          <div :data-key="alert.id" @click="expand" :class="classes">
            {{ alert.title }}
            <div>
              <svg class="icon" fill="black" viewBox="0 0 30 30">
                <use xlink:href="@/assets/images/loop.svg#loop" />
              </svg>
            </div>
            <div @click.stop="onDeleteTemplate(alert.id)">
              <svg class="icon" fill="black" viewBox="0 0 30 30">
                <use xlink:href="@/assets/images/remove.svg#remove" />
              </svg>
            </div>
            <div>
              <div class="alerts-template-list__item__header">
                <ToggleCheckBox :value="alert.isActive" offColor="#aaaaaa" onColor="#199e54" />
              </div>
            </div>
          </div>
        </template>
        <template slot="panel-content">
          <div class="no-data">
            Page building in progress
          </div>
        </template>
      </ExpandablePanel>
    </template>
    <template v-else-if="!templates.isLoading && !templates.list.length">
      <div class="no-data">
        No alert templates
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
  components: { ExpandablePanel, PulseLoadingSpinner, ToggleCheckBox },
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
  @include muted-font();
}
.alerts-template-list__item__header {
  display: flex;
}
.icon {
  display: block;
  cursor: pointer;
  width: 20px;
  height: 30px;
}
</style>
