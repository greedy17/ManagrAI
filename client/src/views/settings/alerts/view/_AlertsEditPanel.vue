<template>
  <div class="tab">
    <div class="tab__header">
      <div class="tab__header-items">
        <div class="tab__header-items__group tab__header-items__group">
          <div
            :class="{ 'tab__header-items__item--active': selectedTab == 'TEMPLATE' }"
            @click="selectedTab = 'TEMPLATE'"
            class="tab__header-items__item"
          >
            General Info
          </div>
          <div
            :class="{ 'tab__header-items__item--active': selectedTab == 'GROUPS' }"
            @click="selectedTab = 'GROUPS'"
            class="tab__header-items__item"
          >
            Conditions
          </div>
          <div
            :class="{ 'tab__header-items__item--active': selectedTab == 'CONFIG' }"
            @click="selectedTab = 'CONFIG'"
            class="tab__header-items__item"
          >
            Settings
          </div>
          <div
            :class="{ 'tab__header-items__item--active': selectedTab == 'MESSAGE' }"
            @click="selectedTab = 'MESSAGE'"
            class="tab__header-items__item"
          >
            Message Template
          </div>
        </div>
      </div>
    </div>
    <div class="tab__panel">
      <div style="display:flex;justify-content:center;">
        <PulseLoadingSpinner v-if="savingInTab" />
        <div v-show="savedChanges">Saved Changes</div>
      </div>
      <div class="alerts-template-list__content">
        <div v-if="selectedTab == 'TEMPLATE'" class="alerts-template-list__content-template">
          <FormField
            :id="`resource-title-${alert.id}`"
            :errors="templateTitleField.errors"
            @input="executeUpdateTemplate(templateTitleField)"
            v-model="templateTitleField.value"
          />
          <FormField
            :id="`resource-type-${alert.id}`"
            :disabled="true"
            v-model="alert.resourceType"
          />
        </div>
        <div v-if="selectedTab == 'GROUPS'" class="alerts-template-list__content-groups">
          <div
            v-for="(group, index) in alert.groupsRef"
            :key="index"
            class="alerts-template-list__content-conditions__group"
          >
            <span v-if="group.groupOrder != 0">{{ group.groupCondition }}</span>
            <div class="alerts-template-list__content-conditions__operand">
              <ListContainer horizontal>
                <template v-slot:list>
                  <ListItem
                    @item-selected="onDeleteOperand(operand.id)"
                    medium
                    v-for="(operand, i) in group.operandsRef"
                    :key="i"
                    :item="
                      `${
                        operand.operandOrder != 0 ? operand.operandCondition : ''
                      } ${getReadableOperandRow(operand)}`
                    "
                    :active="true"
                  />
                </template>
              </ListContainer>
            </div>
          </div>
        </div>
        <div v-if="selectedTab == 'MESSAGE'" class="alerts-template-list__content-message">
          <div class="alerts-template-list__content-message__form">
            <FormField
              @input="executeUpdateMessageTemplate"
              v-model="messageTemplateForm.field.notificationText.value"
              :errors="messageTemplateForm.field.notificationText.errors"
            />
            <div class="alerts-template-list__content-message__form-body">
              <FormField :errors="messageTemplateForm.field.body.errors">
                <template v-slot:input>
                  <quill-editor
                    style="width:20rem;"
                    @blur="messageTemplateForm.field.body.validate()"
                    @input="executeUpdateMessageTemplate"
                    ref="message-body"
                    v-model="messageTemplateForm.field.body.value"
                    :options="{
                      modules: { toolbar: { container: ['bold', 'italic', 'strike'] } },
                    }"
                  />
                </template>
              </FormField>
            </div>
            <div class="alerts-page__message-options-body__bindings">
              <DropDownSearch
                :items="fields.list"
                @input="bindText(`${alert.resourceType}.${$event}`)"
                displayKey="referenceDisplayLabel"
                valueKey="apiName"
                nullDisplay="Select a field"
                searchable
                :hasNext="!!fields.pagination.hasNextPage"
                @load-more="fieldNextPage"
                @search-term="onSearchFields"
                small
              />
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
          <div class="alerts-template-list__content-message__preview">
            <SlackNotificationTemplate :msg="messageTemplateForm.field.notificationText.value" />
            <SlackMessagePreview :alert="alertObj" />
          </div>
        </div>
        <div v-if="selectedTab == 'CONFIG'" class="alerts-template-list__content-settings">
          <div class="alerts-template-list__content-settings__group">
            <ListContainer horizontal>
              <template v-slot:list>
                <ListItem
                  @item-selected="onDeleteConfig(config.id)"
                  large
                  :key="index"
                  v-for="(config, index) in alert.configsRef"
                  :item="getReadableConfig(config)"
                  :active="true"
                />
              </template>
            </ListContainer>
          </div>
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

import debounce from 'lodash.debounce'
import { quillEditor } from 'vue-quill-editor'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'
import moment from 'moment'
//Internal

import ListContainer from '@/components/ListContainer'
import ListItem from '@/components/ListItem'
import ExpandablePanel from '@/components/ExpandablePanel'
import FormField from '@/components/forms/FormField'
import SlackNotificationTemplate from '@/views/settings/alerts/create/SlackNotificationTemplate'
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'
import DropDownSearch from '@/components/DropDownSearch'
/**
 * Services
 *
 */
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import Form, { FormArray, FormField as FormFieldService } from '@thinknimble/tn-forms'
import {
  MustMatchValidator,
  EmailValidator,
  RequiredValidator,
  MinLengthValidator,
  Validator,
} from '@thinknimble/tn-validators'

import AlertTemplate, {
  AlertMessageTemplate,
  AlertConfig,
  AlertGroup,
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertGroupOperand,
  AlertOperandForm,
} from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { SObjectField, SObjectValidations, SObjectPicklist } from '@/services/salesforce'
import {
  ALERT_DATA_TYPE_MAP,
  INPUT_TYPE_MAP,
  INTEGER,
  STRING,
  DATE,
  DECIMAL,
  BOOLEAN,
  DATETIME,
} from '@/services/salesforce/models'
const TABS = [
  { key: 'TEMPLATE', label: 'General Info' },
  { key: 'GROUPS', label: 'Conditions' },
  { key: 'MESSAGE', label: 'Message Template' },
  { key: 'CONFIG', label: 'Settings' },
]
export default {
  name: 'AlertsEditPanel',
  components: {
    FormField,
    SlackNotificationTemplate,
    SlackMessagePreview,
    quillEditor,
    ListItem,
    ListContainer,
    PulseLoadingSpinner,
    DropDownSearch,
  },
  props: {
    alert: {
      type: AlertTemplate,
      required: true,
    },
  },
  data() {
    return {
      templateTitleField: new FormFieldService({ validators: [new RequiredValidator()] }),
      executeUpdateTemplate: debounce(this.updateTemplate, 900),
      executeUpdateMessageTemplate: debounce(this.updateMessageTemplate, 900),
      messageTemplateForm: new AlertMessageTemplateForm(),
      TABS,
      selectedTab: TABS[0].key,
      savedChanges: false,
      savingInTab: false,
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      recipientBindings: [
        { referenceDisplayLabel: 'Recipient Full Name', apiName: 'full_name' },
        { referenceDisplayLabel: 'Recipient First Name', apiName: 'first_name' },
        { referenceDisplayLabel: 'Recipient Last Name', apiName: 'last_name' },
        { referenceDisplayLabel: 'Recipient Email', apiName: 'email' },
      ],
      intOpts: [
        { label: '>= (Greater or Equal)', value: '>=' },
        { label: '<= (Less or Equal)', value: '<=' },
        { label: '< (Less)', value: '<' },
        { label: '> (Greater)', value: '>' },
        { label: '= (Equals)', value: '=' },
        { label: '!= (Not Equals)', value: '!=' },
        // string based equality
      ],
      strOpts: [
        // string based equality
        { label: 'Contains', value: 'CONTAINS' },
        { label: 'Starts With', value: 'STARTSWITH' },
        { label: 'Ends With', value: 'ENDSWITH' },
        { label: '= (Equals)', value: '=' },
        { label: '!= (Not Equals)', value: '!=' },
      ],
      booleanValueOpts: [
        { label: 'True', value: 'true' },
        { label: 'False', value: 'false' },
      ],
      weeklyOpts: [
        { key: 'Monday', value: '0' },
        { key: 'Tuesday', value: '1' },
        { key: 'Wednesday', value: '2' },
        { key: 'Thursday', value: '3' },
        { key: 'Friday', value: '4' },
        { key: 'Saturday', value: '5' },
        { key: 'Sunday', value: '6' },
      ],
    }
  },
  watch: {
    async selectedTab(val, curr) {
      if (val && val == 'MESSAGE' && val != curr) {
        this.fields.filters.salesforceObject = this.alert.resourceType
        this.fields.refresh()
      }
    },
  },
  computed: {
    alertObj() {
      return {
        title: this.templateTitleField.value,
        message: this.messageTemplateForm.field.body.value,
        resourceType: this.alert.resourceType,
      }
    },

    editor() {
      return this.$refs['message-body'].quill
    },
  },
  methods: {
    selectedFieldType(operatorField) {
      if (operatorField) {
        return ALERT_DATA_TYPE_MAP[operatorField.dataType]
      } else {
        return STRING
      }
    },
    getInputType(type) {
      if (type && INPUT_TYPE_MAP[type.dataType]) {
        return INPUT_TYPE_MAP[type.dataType]
      }
      return 'text'
    },
    getReadableOperandRow(rowData) {
      let operandOperator = rowData.operandOperator
      let value = rowData.operandValue
      let operandOpts = [...this.intOpts, ...this.booleanValueOpts, ...this.strOpts]
      let valueLabel = value
      let operandOperatorLabel = operandOpts.find(opt => opt.value == operandOperator)
        ? operandOpts.find(opt => opt.value == operandOperator).label
        : operandOperator
      let dataType = this.selectedFieldType(rowData.operandIdentifierRef)
      if (dataType == 'DATETIME' || dataType == 'DATE') {
        if (value.startsWith('-')) {
          valueLabel = moment()
            .subtract(value, 'days')
            .format('MM-DD-YYYY')
        } else {
          valueLabel = moment()
            .add(value, 'days')
            .format('MM-DD-YYYY')
        }
      }
      return `${rowData.operandIdentifier}     ${operandOperatorLabel}     ${valueLabel} `
    },
    getReadableConfig(config) {
      let recurrenceDayString = config.recurrenceDay
      let recurrenceFrequencyString = config.recurrenceFrequency
      if (config.recurrenceFrequency == 'WEEKLY') {
        let day = this.weeklyOpts.find(opt => opt.value == config.recurrenceDay)
          ? this.weeklyOpts.find(opt => opt.value == config.recurrenceDay).key
          : config.recurrenceDay
        recurrenceDayString = `Check every ${day} (Weekly)`
      } else if ((config.recurrenceFrequency = 'MONTHLY')) {
        let day = config.recurrenceDay
        recurrenceFrequencyString = `Check on the ${day} of every Month`
      }
      return `${recurrenceDayString} and send alert to ${config.recipientsRef
        .map(rec => rec.key)
        .join(',')} filtering against ${config.alertTargetsRef
        .map(target => target.key)
        .join(',')}'s data`
    },

    async onDeleteConfig(id) {
      let confirmation = confirm('Delete this row ?')
      if (confirmation) {
        try {
          await AlertConfig.api.delete(id)
        } catch (e) {
          console.log(e)
        }
      }
    },
    async onDeleteOperand(id) {
      let confirmation = confirm('Delete this row ?')
      if (confirmation) {
        try {
          await AlertGroupOperand.api.delete(id)
        } catch (e) {
          console.log(e)
        }
      }
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

    bindText(val) {
      this.$refs['message-body'].quill.focus()
      let start = 0
      if (this.editor.selection.lastRange) {
        start = this.editor.selection.lastRange.index
      }
      this.editor.insertText(start, `{ ${val} }`)
    },
    async updateTemplate(field) {
      this.templateTitleField.validate()
      if (this.templateTitleField.isValid) {
        try {
          this.savingInTab = true
          await AlertTemplate.api.updateAlertTemplate(this.alert.id, { title: field.value })
          this.savedChanges = true
          setTimeout(() => {
            this.savedChanges = false
          }, 1000)
        } catch (e) {
          console.log(e)
          this.$Alert.alert({
            message: 'There was an error updating your template',
            type: 'error',
            timeout: 2000,
          })
        } finally {
          this.savingInTab = false
        }
      }
    },

    async updateMessageTemplate() {
      // TODO: Sanitize body PB 05/18/21
      this.messageTemplateForm.validate()
      if (this.messageTemplateForm.isValid) {
        try {
          this.savingInTab = true
          const bindings = stringRenderer('{', '}', this.messageTemplateForm.field.body.value)
          await AlertMessageTemplate.api.updateMessageTemplate(this.alert.messageTemplateRef.id, {
            body: this.messageTemplateForm.field.body.value,
            notificationText: this.messageTemplateForm.field.notificationText.value,
            bindings: bindings,
          })
          this.savedChanges = true
          setTimeout(() => {
            this.savedChanges = false
          }, 1000)
        } catch (e) {
          console.log(e)
          this.$Alert.alert({
            message: 'There was an error updating your template',
            type: 'error',
            timeout: 2000,
          })
        } finally {
          this.savingInTab = false
        }
      }
    },
  },
  async created() {
    // populate values for stand alone fields
    // for this version only allowing edit of certain fields or delete of array items
    if (this.alert) {
      this.templateTitleField.value = this.alert.title
      this.messageTemplateForm.field.notificationText.value = this.alert.messageTemplateRef.notificationText
      this.messageTemplateForm.field.body.value = this.alert.messageTemplateRef.body
    }
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
@import '@/styles/buttons';
.tab__header-items {
  display: flex;
  padding: 0.25rem 0 0;
  box-shadow: 0 1px 0 0 $soft-gray;
  &__item {
    padding: 1rem 2rem;
    border-bottom: none;
    color: #bcbcc1;
    font-weight: normal;
    cursor: pointer;
    &--active {
      padding: 1rem 2rem;
      color: #110f24;
      border-bottom: 2px solid #2f9e54;
    }
  }
  &__group {
    display: flex;
    &__items {
    }
    &--large {
      flex: 1.5 0 auto;
    }
    &--medium {
      flex: 1 0 auto;
    }
  }
}
.tab__panel {
  padding: 0.25rem 0 0;
}
.alerts-template-list__content-message {
  display: flex;
  justify-content: space-evenly;
  &__form {
    width: 30rem;
  }
  &__preview {
  }
}
</style>
