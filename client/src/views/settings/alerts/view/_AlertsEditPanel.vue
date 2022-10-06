<template>
  <div>
    <BuildYourOwn :oldAlert="alert" />
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
import debounce from 'lodash.debounce'

//Internal
// import AlertOperandModal from '@/views/settings/alerts/view/_AlertOperandModal'
// import AlertGroupModal from '@/views/settings/alerts/view/_AlertGroupModal'
// import AlertSettingsModal from '@/views/settings/alerts/view/_AlertSettingsModal'
import FormField from '@/components/forms/FormField'
import BuildYourOwn from '@/views/settings/alerts/create/BuildYourOwn'
/**
 * Services
 *
 */
import { CollectionManager } from '@thinknimble/tn-models'
import { FormField as FormFieldService } from '@thinknimble/tn-forms'
import { RequiredValidator } from '@thinknimble/tn-validators'

import AlertTemplate, {
  AlertMessageTemplate,
  AlertConfig,
  AlertGroup,
  AlertGroupForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertGroupOperand,
  AlertOperandForm,
} from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { SObjectField } from '@/services/salesforce'
import { ALERT_DATA_TYPE_MAP, STRING } from '@/services/salesforce/models'
const TABS = [
  { key: 'TEMPLATE', label: 'Workflow Title' },
  { key: 'GROUPS', label: 'Conditions' },
  { key: 'MESSAGE', label: 'Message' },
  { key: 'CONFIG', label: 'Delivery Options' },
]
export default {
  name: 'AlertsEditPanel',
  components: {
    FormField,
    // AlertOperandModal,
    // AlertGroupModal,
    // AlertSettingsModal,
    quillEditor,
    BuildYourOwn,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    alert: {
      type: AlertTemplate,
      required: true,
    },
  },
  data() {
    return {
      dropdownLoading: false,
      templateTitleField: new FormFieldService({ validators: [new RequiredValidator()] }),
      executeUpdateTemplate: debounce(this.updateTemplate, 900),
      executeUpdateMessageTemplate: debounce(this.updateMessageTemplate, 900),
      messageTemplateForm: new AlertMessageTemplateForm(),
      TABS,
      selectedTab: TABS[0].key,
      savedChanges: false,
      savingInTab: false,
      crmValue: null,
      templateNames: [
        'Close Date Passed',
        'Close Date Approaching',
        'Update Forecast',
        'Deal Rotting',
        'Upcoming Next Step',
        'Required Field Empty',
        'Large Opportunities',
      ],
      fields: CollectionManager.create({
        ModelClass: SObjectField,
        pagination: { size: 200 },
      }),
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
          height: 500,
          width: 820,
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

          height: 400,
          width: 800,

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
          height: 650,
          width: 580,
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
        recurrenceDayString = `Run your selected days (Weekly)`
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
          this.$toast('Must have at least 1 operand', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
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
          this.$toast('Must have at least 1 operand', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
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
    async fieldNextPage() {
      this.dropdownLoading = true
      await this.fields.addNextPage()
      setTimeout(() => {
        this.dropdownLoading = false
      })
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
          this.$toast('Error updating template', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
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
          this.$toast('Error updating template', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.savingInTab = false
        }
      }
    },
  },
  // async created() {

  //   if (this.alert) {
  //     this.templateTitleField.value = this.alert.title
  //     this.messageTemplateForm.field.body.value = this.alert.messageTemplateRef.body
  //   }
  // },
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

::v-deep .input-content {
  width: 13vw;
  border: 1px solid #e8e8e8 !important;
  border-radius: 0.3rem;
  background-color: white;
  box-shadow: none !important;
}
::v-deep .input-form {
  width: 13vw;
}
::v-deep .input-form__active {
  border: none;
}
@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
h3 {
  font-weight: 400;
  letter-spacing: 0.25px;
}
.img-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
  border-radius: 0.2rem;
  cursor: pointer;
  padding: 0.15rem 0.3rem;
  margin-right: 0.5rem;
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.card-rows {
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  margin-top: 2rem;
}
.group-card {
  border-radius: 0.3rem;
  background-color: $white;
  padding: 1.2rem;
  width: 58%;
  margin-bottom: 2rem;
  color: $base-gray;
  font-size: 14px;
  border: 1px solid #e8e8e8;

  &__title {
    width: 100%;
    height: 2rem;
    text-align: center;
    font-size: 1.05rem;
  }
}

.condition-button {
  background-color: $dark-green;
  color: white;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  padding: 0.5rem 1rem;
  margin: 0.5rem;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;

  cursor: pointer;
}
.even {
  color: $gray;
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: text;
  font-size: 14px;
  img {
    height: 1rem;
    filter: invert(70%);
  }
}
.remove-color {
  filter: invert(30%);
  cursor: pointer;
}
.invert {
  filter: invert(80%);
}
.message__box {
  margin-bottom: 2rem;
  height: 16vh;
  width: 32vw;
  border-radius: 0.25rem;
  background-color: transparent;
}
.tab__header-items {
  display: flex;
  overflow: scroll;
  &__item {
    display: flex;
    align-items: center;
    justify-content: space-evenly;
    padding: 0.5rem;
    border-bottom: none;
    color: $base-gray;
    letter-spacing: 0.5px;
    cursor: pointer;
    width: 17vw;
    &--active {
      background-color: $dark-green;
      border-radius: 0.2rem;
      color: white;
      position: relative;
    }
    &--active:hover {
      color: white !important;
    }
  }
  &__item:hover {
    color: $dark-green;
  }
  &__group {
    display: flex;
    padding: 0.75rem;
  }
}
.tab__panel {
  padding: 0.5rem 3rem;
}
.alerts-template-list__content-message {
  font-size: 14px;
  letter-spacing: 0.2px;
  display: flex;
  justify-content: flex-start;
  padding: 0.5rem 2rem;
  height: 100%;
  &__form {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    height: 100%;
  }
}
</style>
