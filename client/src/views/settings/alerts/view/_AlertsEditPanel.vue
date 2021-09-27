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
            Alert Message
          </div>
        </div>
      </div>
    </div>
    <div class="tab__panel">
      <div style="display: flex; justify-content: center">
        <PulseLoadingSpinner v-if="savingInTab" />
        <div v-show="savedChanges">Saved Changes</div>
      </div>
      <div class="alerts-template-list__content">
        <div v-if="selectedTab == 'TEMPLATE'" class="alerts-template-list__content-template">
          <FormField
            :id="`resource-type-${alert.id}`"
            :disabled="true"
            v-model="alert.resourceType"
          />
          <span>Edit Title: </span>
          <FormField
            :id="`resource-title-${alert.id}`"
            :errors="templateTitleField.errors"
            @input="executeUpdateTemplate(templateTitleField)"
            v-model="templateTitleField.value"
          />
        </div>
        <div v-if="selectedTab == 'GROUPS'" class="alerts-template-list__content-groups">
          <div
            style="margin-top: 1rem"
            v-for="(group, index) in alert.groupsRef"
            :key="index"
            class="alerts-template-list__content-conditions__group"
          >
            <span v-if="group.groupOrder != 0">{{ group.groupCondition }}</span>
            <div class="alerts-template-list__content-conditions__operand">
              <div style="margin-left: 0.5rem; color: #beb5cc; display: flex; flex-direction: row">
                <button class="row__button" @click="onShowOperandModal(index)">
                  Add a new row
                  <img
                    style="height: 1rem; margin-left: 0.15rem"
                    src="@/assets/images/plusOne.png"
                    alt=""
                  />
                </button>
                <button class="row__button" @click="onShowGroupModal()">
                  Add a Group
                  <img
                    style="height: 1rem; margin-left: 0.15rem"
                    src="@/assets/images/plusOne.png"
                    alt=""
                  />
                </button>
              </div>
              <ListContainer horizontal>
                <template v-slot:list>
                  <img
                    style="margin-right: 0.5rem; margin-top: 0.25rem; height: 1rem"
                    src="@/assets/images/remove.png"
                    alt=""
                  />
                  <ListItem
                    @item-selected="onDeleteOperand(operand.id, i, index)"
                    medium
                    v-for="(operand, i) in group.operandsRef"
                    :key="i"
                    :item="`${
                      operand.operandOrder != 0 ? operand.operandCondition : ''
                    } ${getReadableOperandRow(operand)}`"
                    :active="true"
                  />
                </template>
              </ListContainer>
            </div>
            <button
              class="remove__button"
              @click.stop="onRemoveAlertGroup(group.id, index)"
              :disabled="index <= 0"
              style="margin-left: 0.5rem"
            >
              Remove Group
            </button>
          </div>
        </div>
        <div v-if="selectedTab == 'MESSAGE'" class="alerts-template-list__content-message">
          <div style="margin-top: 1rem" class="alerts-template-list__content-message__form">
            <div class="alerts-template-list__content-message__form-body">
              <FormField :errors="messageTemplateForm.field.body.errors">
                <template v-slot:input>
                  <quill-editor
                    style="width: 100%; height: 6rem"
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
            <!-- <div class="alerts-page__message-options-body__bindings">
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
                auto
                class="left"
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
            </div> -->
          </div>
          <!-- <div
            class="alerts-template-list__content-message__preview"
            style="width: 40rem; height: 20rem; overflow-y: scroll"
          >
            <SlackMessagePreview :alert="alertObj" />
          </div> -->
        </div>
        <div v-if="selectedTab == 'CONFIG'" class="alerts-template-list__content-settings">
          <div style="margin-top: 1rem" class="alerts-template-list__content-settings__group">
            <button style="margin-left: 1rem" class="row__button" @click="onShowSettingsModal">
              Add a row
              <img
                style="height: 0.875rem; margin-left: 0.25rem"
                src="@/assets/images/plusOne.png"
                alt=""
              />
            </button>

            <ListContainer horizontal>
              <template v-slot:list>
                <img
                  style="margin-right: 0.5rem; margin-top: 0.25rem; height: 1rem"
                  src="@/assets/images/remove.png"
                  alt=""
                />
                <ListItem
                  @item-selected="onDeleteConfig(config.id, index)"
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
import AlertOperandModal from '@/views/settings/alerts/view/_AlertOperandModal'
import AlertGroupModal from '@/views/settings/alerts/view/_AlertGroupModal'
import AlertSettingsModal from '@/views/settings/alerts/view/_AlertSettingsModal'
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
import { toNumberSuffix } from '@/services/filters'
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
    AlertOperandModal,
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
    onShowOperandModal(groupIndex) {
      let newForm = new AlertOperandForm({
        operandOrder: this.alert.groupsRef[groupIndex].operandsRef.length,
        groupId: this.alert.groupsRef[groupIndex].id,
      })

      this.$modal.show(
        AlertOperandModal,
        { form: newForm, resourceType: this.alert.resourceType },

        {
          name: 'alert-operands-modal',
          minHeight: 600,
          minWidth: 600,
          height: 600,
          width: 600,
        },
        {
          'before-close': (e) => {
            if (e.params && e.params.createdObj) {
              this.alert.groupsRef[groupIndex].operandsRef = [
                ...this.alert.groupsRef[groupIndex].operandsRef,
                e.params.createdObj,
              ]
              this.alert.groupsRef[groupIndex].operands = [
                ...this.alert.groupsRef[groupIndex].operandsRef.map((op) => op.id),
              ]
            }
          },
        },
      )
    },
    onShowGroupModal() {
      let newForm = new AlertGroupForm({
        groupOrder: this.alert.groupsRef.length,
        alertTemplateId: this.alert.id,
      })

      this.$modal.show(
        AlertGroupModal,
        { form: newForm, resourceType: this.alert.resourceType },

        {
          name: 'alert-groups-modal',

          minHeight: 600,
          minWidth: 600,
          height: 600,
          width: 600,

          adaptive: true,
        },
        {
          'before-close': (e) => {
            if (e.params && e.params.createdObj) {
              this.alert.groupsRef = [...this.alert.groupsRef, e.params.createdObj]
              this.alert.groups = [...this.alert.groupsRef.map((op) => op.id)]
            }
          },
        },
      )
    },
    onShowSettingsModal() {
      let newForm = new AlertConfigForm({
        alertTemplateId: this.alert.id,
      })

      this.$modal.show(
        AlertSettingsModal,
        { form: newForm },

        {
          name: 'alert-settings-modal',
          minHeight: 600,
          minWidth: 600,
          height: 600,
          width: 600,
        },
        {
          'before-close': (e) => {
            if (e.params && e.params.createdObj) {
              this.alert.configsRef = [...this.alert.configsRef, e.params.createdObj]
              this.alert.configs = [...this.alert.configsRef.map((op) => op.id)]
            }
          },
        },
      )
    },
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
      let operandOperatorLabel = operandOpts.find((opt) => opt.value == operandOperator)
        ? operandOpts.find((opt) => opt.value == operandOperator).label
        : operandOperator
      let dataType = this.selectedFieldType(rowData.operandIdentifierRef)
      if (dataType == 'DATETIME' || dataType == 'DATE') {
        if (value.startsWith('-')) {
          valueLabel = `${value} days before run date`
        } else {
          valueLabel = `${value} days after run date`
        }
      }
      return `${rowData.operandIdentifier}     ${operandOperatorLabel}     ${valueLabel} `
    },
    addSuffix(num) {
      if ((num > 3 && num < 21) || (num > 23 && num < 31)) {
        return num + 'th'
      } else if (num == 1 || num == 21 || num == 31) {
        return num + 'st'
      } else if (num == 2 || num == 22) {
        return num + 'nd'
      } else if (num == 3 || num == 23) {
        return num + 'rd'
      }
    },
    getReadableConfig(config) {
      let recurrenceDayString = config.recurrenceDay

      if (config.recurrenceFrequency == 'WEEKLY') {
        let day = this.weeklyOpts.find((opt) => opt.value == config.recurrenceDay)
          ? this.weeklyOpts.find((opt) => opt.value == config.recurrenceDay).key
          : config.recurrenceDay
        recurrenceDayString = `Run every ${day} (Weekly)`
      } else if ((config.recurrenceFrequency = 'MONTHLY')) {
        let day = config.recurrenceDay
        recurrenceDayString = `Run every ${this.addSuffix(day)} Monthly`
      }
      return `${recurrenceDayString} and alert ${
        config.recipientType === 'USER_LEVEL'
          ? config.recipientsRef.map((rec) => rec.key).join(',')
          : 'a #channel'
      } filtering against ${config.alertTargetsRef.map((target) => target.key).join(',')}'s data`
    },

    async onDeleteConfig(id, index) {
      let confirmation = confirm('Delete this row ?')
      if (confirmation) {
        try {
          await AlertConfig.api.delete(id)

          this.alert.configsRef = [
            ...this.alert.configsRef.slice(0, index),
            ...this.alert.configsRef.slice(index + 1, this.alert.configsRef.length),
          ]
          this.alert.configs = this.alert.configsRef.map((config) => config.id)
        } catch (e) {
          console.log(e)
        }
      }
    },
    async onDeleteOperand(id, index, groupIndex) {
      let confirmation = confirm('Delete this row ?')
      let countOperands = this.alert.groupsRef[groupIndex].operandsRef.length
      if (confirmation) {
        if (countOperands <= 1) {
          return this.$Alert.alert({
            type: 'error',
            message: 'Groups must have at least one operand',
            timeout: 2000,
          })
        }

        try {
          await AlertGroupOperand.api.delete(id)
          this.alert.groupsRef[groupIndex].operandsRef = [
            ...this.alert.groupsRef[groupIndex].operandsRef.slice(0, index),
            ...this.alert.groupsRef[groupIndex].operandsRef.slice(
              index + 1,
              this.alert.groupsRef[groupIndex].operandsRef.length,
            ),
          ]
          this.alert.groupsRef[groupIndex].operands = this.alert.groupsRef[
            groupIndex
          ].operandsRef.map((op) => op.id)
        } catch (e) {
          console.log(e)
        }
      }
    },
    async onRemoveAlertGroup(id, index) {
      let confirmation = confirm('Delete this Group and all its rows ?')

      if (confirmation) {
        if (this.alert.groupsRef[index] <= 1) {
          return this.$Alert.alert({
            type: 'error',
            message: 'Groups must have at least one operand',
            timeout: 2000,
          })
        }
        try {
          await AlertGroup.api.delete(id)
          this.alert.groupsRef = [
            ...this.alert.groupsRef.slice(0, index),
            ...this.alert.groupsRef.slice(index + 1, this.alert.groupsRef.length),
          ]
          this.alert.groups = this.alert.groupsRef.map((group) => group.id)
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

.filtered {
  filter: invert(66%) sepia(64%) saturate(3377%) hue-rotate(380deg) brightness(100%) contrast(105%);
}
.row__button {
  border: none;
  color: $dark-green;
  background: transparent;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
  padding-top: 0.2rem;
  margin-left: -0.1rem;
}
.remove__button {
  border: none;
  color: $panther-silver;
  background: transparent;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
  padding-top: 0.2rem;
  margin-left: -0.1rem;
}
.disabled__button {
  border: none;
  color: $panther-silver;
  background: transparent;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
  padding-top: 0.2rem;
  margin-left: -0.1rem;
}
::v-deep .input-content {
  background-color: $panther-silver;
  border: none;
  font-weight: bold;
  color: white;
}
::v-deep .input-content:focus {
  background-color: $panther-silver;
  box-shadow: 2px 4px 7px black;
  border: none;
  font-weight: bold;
  color: white;
}
::v-deep .ls-container__list--horizontal {
  background-color: transparent;
}
.tab__header-items {
  display: flex;
  padding: 0.25rem 0 0;

  &__item {
    padding: 1rem 2rem;
    border-bottom: none;
    color: #bcbcc1;
    font-weight: normal;
    cursor: pointer;
    &--active {
      padding: 1rem 2rem;
      color: white;
      border-bottom: 2px solid white;
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
.left {
  margin-bottom: 5rem;
}
.alerts-template-list__add-opts {
  display: flex;
  align-items: center;
}
</style>
