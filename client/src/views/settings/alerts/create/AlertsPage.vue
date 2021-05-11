<template>
  <div class="alerts-page">
    <ExpandablePanel :title="`${selectedResourceType ? selectedResourceType : 'Select Resource'}`">
      <template slot="panel-content">
        <FormField :errors="alertTemplateForm.field.resourceType.errors">
          <template v-slot:input>
            <DropDownSearch
              :items.sync="SOBJECTS_LIST"
              :itemsRef.sync="alertTemplateForm.field._resourceType.value"
              v-model="alertTemplateForm.field.resourceType.value"
              displayKey="key"
              valueKey="value"
              nullDisplay="Salesforce Resources"
              searchable
              local
              @input="alertTemplateForm.field.resourceType.validate()"
            />
          </template>
        </FormField>
      </template>
    </ExpandablePanel>
    <ExpandablePanel title="Build Alert">
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <FormField
            v-model="alertTemplateForm.field.title.value"
            placeholder="Alert Title"
            :errors="alertTemplateForm.field.title.errors"
            @blur="alertTemplateForm.field.title.validate()"
            large
          />
          <div
            :key="index"
            v-for="(alertGroup, index) in alertTemplateForm.field.alertGroups.groups"
          >
            <AlertGroup
              :form="alertGroup"
              :resourceType="alertTemplateForm.field.resourceType.value"
            />

            <div>
              <button
                class="btn btn--primary"
                @click.stop="onRemoveAlertGroup(index)"
                :disabled="alertTemplateForm.field.alertGroups.groups.length - 1 <= 0"
              >
                - Group
              </button>
            </div>
          </div>
          <button class="btn btn--primary" @click="onAddAlertGroup">+ Group</button>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">
            Please Select a resource to get started
          </div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel title="Construct Message">
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <div class="alerts-page__message">
            <div class="alerts-page__message-options">
              <FormField
                v-model="
                  alertTemplateForm.field.alertMessages.groups[0].field.notificationText.value
                "
                large
                placeholder="Snippet in slack notification"
              />
              <div class="alerts-page__message-options-body" style="height:5rem;width:30rem;">
                <FormField
                  :errors="alertTemplateForm.field.alertMessages.groups[0].field.body.errors"
                >
                  <template v-slot:input>
                    <quill-editor
                      @blur="alertTemplateForm.field.alertMessages.groups[0].field.body.validate()"
                      ref="message-body"
                      v-model="alertTemplateForm.field.alertMessages.groups[0].field.body.value"
                      :options="{
                        modules: { toolbar: { container: ['bold', 'italic', 'strike'] } },
                      }"
                    />
                  </template>
                </FormField>
                <div class="alerts-page__message-options-body__bindings">
                  <DropDownSearch
                    :items="fields.list"
                    @input="bindText(`${selectedResourceType}.${$event}`)"
                    displayKey="referenceDisplayLabel"
                    valueKey="apiName"
                    nullDisplay="Select a field"
                    searchable
                    :hasNext="!!fields.pagination.hasNextPage"
                    @load-more="fieldNextPage"
                    @search-term="onSearchFields"
                    small
                  />

                  <ListContainer
                    horizontal
                    v-if="NON_FIELD_ALERT_OPTS[selectedResourceType].length"
                  >
                    <template v-slot:list>
                      <ListItem
                        :key="key"
                        v-for="(val, key) in NON_FIELD_ALERT_OPTS[selectedResourceType]"
                        :item="val.referenceDisplayLabel"
                        :active="true"
                        @item-selected="bindText(`${selectedResourceType}.${val.apiName}`)"
                      />
                    </template>
                  </ListContainer>
                  <ListContainer horizontal>
                    <template v-slot:list>
                      <ListItem
                        :key="key"
                        v-for="(val, key) in recipientBindings"
                        :item="val.referenceDisplayLabel"
                        :active="true"
                        @item-selected="bindText(`__Recipient.${val.apiName}`)"
                      />
                    </template>
                  </ListContainer>
                </div>
              </div>
            </div>
            <div class="alerts-page__message-template">
              <div class="alerts-page__message-template__notification">
                <SlackNotificationTemplate
                  :msg="
                    alertTemplateForm.field.alertMessages.groups[0].field.notificationText.value
                  "
                />
              </div>
              <div class="alerts-page__message-template__message">
                <SlackMessagePreview :alert="alertObj" />
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">
            Please Select a resource to get started
          </div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel title="Alert Settings">
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <div
            class="alerts-page__settings"
            :key="i"
            v-for="(form, i) in alertTemplateForm.field.alertConfig.groups"
          >
            <div class="alerts-page__settings__frequency">
              <label class="alerts-page__settings__frequency-label">Weekly</label>
              <ToggleCheckBox
                @input="
                  form.field.recurrenceFrequency.value == 'WEEKLY'
                    ? (form.field.recurrenceFrequency.value = 'MONTHLY')
                    : (form.field.recurrenceFrequency.value = 'WEEKLY')
                "
                :value="form.field.recurrenceFrequency.value !== 'WEEKLY'"
                offColor="#199e54"
                onColor="#199e54"
              />
              <label class="alerts-page__settings__frequency-label">Monthly</label>
            </div>
            <div class="alerts-page__settings__day">
              <FormField
                placeholder="day"
                :errors="form.field.recurrenceDay.errors"
                @blur="form.field.recurrenceDay.validate()"
                v-model="form.field.recurrenceDay.value"
                small
              />
            </div>
            <div class="alerts-page__settings__recipients">
              <DropDownSearch
                :items.sync="alertRecipientOpts"
                :itemsRef.sync="form.field._recipients.value"
                v-model="form.field.recipients.value"
                displayKey="key"
                valueKey="value"
                nullDisplay="Salesforce Resources"
                searchable
                local
              />
            </div>
            <div>
              <button
                class="btn btn--primary"
                @click.stop="onRemoveSetting(i)"
                :disabled="alertTemplateForm.field.alertConfig.groups.length - 1 <= 0"
              >
                - Setting
              </button>
            </div>
          </div>
          <button class="btn btn--primary" @click="onAddAlertSetting">Add Setting</button>
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">
            Please Select a resource to get started
          </div>
        </template>
      </template>
    </ExpandablePanel>
    <ExpandablePanel title="Preview Alert Configuration">
      <template slot="panel-content">
        <template v-if="selectedResourceType">
          <AlertSummary :form="alertTemplateForm" />
          <PulseLoadingSpinnerButton
            :loading="savingTemplate"
            class="primary-button"
            text="Save"
            @click.stop="onSave"
            :disabled="!alertTemplateForm.isValid || savingTemplate"
          />
        </template>
        <template v-else>
          <div class="alerts-page__previous-step">
            Please Select a resource to get started
          </div>
        </template>
      </template>
    </ExpandablePanel>
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

/**
 * Services
 */

import { SOBJECTS_LIST } from '@/services/salesforce'
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
} from '@/services/salesforce'

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
  },
  data() {
    return {
      savingTemplate: false,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: [],
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      recipientBindings: [
        { referenceDisplayLabel: 'Recipient Name', apiName: 'recipientName' },
        { referenceDisplayLabel: 'Recipient Email', apiName: 'recipientEmail' },
      ],
      alertRecipientOpts: [
        { key: 'Myself', value: 'SELF' },
        { key: 'Owner', value: 'OWNER' },
        { key: 'All Managers', value: 'MANAGERS' },
        { key: 'All Reps', value: 'REPS' },
        { key: 'Everyone', value: 'ALL' },
      ],
    }
  },
  watch: {
    selectedResourceType: {
      immediate: true,
      async handler(val, prev) {
        if (prev && val !== prev) {
          this.alertTemplateForm = this.alertTemplateForm.reset()
          this.selectedResourceType = val
        }
        if (this.selectedResourceType) {
          this.fields.filters.salesforceObject = this.selectedResourceType
          await this.fields.refresh()
        }
      },
    },
  },
  methods: {
    async onSave() {
      this.savingTemplate = true
      this.alertTemplateForm.validate()
      if (this.alertTemplateForm.isValid) {
        try {
          const res = await AlertTemplate.api.createAlertTemplate(this.alertTemplateForm.toAPI)
          this.$router.push({ name: 'ListTemplates' })
        } catch (e) {
          this.$Alert.alert({
            message: 'An error occured saving template',
            timeout: 2000,
            type: 'error',
          })
        } finally {
          this.savingTemplate = false
        }
      }
    },
    bindText(val) {
      this.$refs['message-body'].quill.focus()
      let start = 0
      if (this.editor.selection.lastRange) {
        start = this.editor.selection.lastRange.index
      }
      this.editor.insertText(start, `{ ${val} }`)
    },
    onAddAlertGroup() {
      // length determines order
      const order = this.alertTemplateForm.field.alertGroups.groups.length
      if (order >= 3) {
        this.$Alert.alert({ message: 'You can only add 3 groups', timeout: 2000 })
        return
      }
      // set next order

      this.alertTemplateForm.addToArray('alertGroups', new AlertGroupForm())
      this.alertTemplateForm.field.alertGroups.groups[order].field.groupOrder.value = order
    },
    onAddAlertSetting() {
      if (this.alertTemplateForm.field.alertConfig.groups.length >= 3) {
        this.$Alert.alert({ message: 'You can only add 3 configurations', timeout: 2000 })
        return
      }
      this.alertTemplateForm.addToArray('alertConfig', new AlertConfigForm())
    },
    onRemoveAlertGroup(i) {
      // get order and update options

      if (this.alertTemplateForm.field.alertGroups.groups.length - 1 <= 0) {
        return
      }

      const order = this.alertTemplateForm.field.alertGroups.groups[i].field.groupOrder.value

      this.alertTemplateForm.removeFromArray('alertGroups', i)

      let greaterThan = this.alertTemplateForm.field.alertGroups.groups.slice(i)

      greaterThan.forEach((el, index) => {
        el.field.groupOrder.value = order + index
      })
    },
    onRemoveSetting(i) {
      if (this.alertTemplateForm.field.alertConfig.groups.length - 1 <= 0) {
        return
      }
      this.alertTemplateForm.removeFromArray('alertConfig', i)
    },
    async onSearchFields(v) {
      this.fields.pagination = new Pagination()
      this.fields.filters = {
        ...this.fields.filters,
        search: v,
      }
      await this.fields.refresh()
    },
    async fieldNextPage() {
      await this.fields.addNextPage()
    },
  },
  computed: {
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
.quill-editor {
  width: 100%;
}

textarea {
  @extend .textarea;
}
.alerts-page {
  &__previous-step {
    @include muted-font(12);
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
.alerts-page__settings {
  display: flex;
  align-items: center;
  &__frequency {
    display: flex;
    align-items: center;
    &-label {
      @include muted-font();
      margin: 0 0.5rem;
    }
  }
}
.btn {
  &--primary {
    @include primary-button();
  }
}
</style>
