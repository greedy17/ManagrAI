<template>
  <div class="edit-panel">
    <Modal v-if="modalOpen" dimmed>
      <div class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="margin-right: 8px; margin-left: 4px"
              class="logo"
              height="26px"
              alt=""
            />
            <h4>Add condition</h4>
          </div>
          <div class="flex-row">
            <img
              @click="resetModal"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="margin-right: 16px; filter: invert(30%); cursor: pointer"
            />
          </div>
        </div>

        <div class="margin-top">
          <AlertOperandRow :resourceType="alert.resourceType" :form.sync="currentForm" />
          <div class="bottom">
            <button @click="onSaveOperand()" class="green_button" :disabled="!currentForm.isValid">
              Add Condition
            </button>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="groupModalOpen" dimmed>
      <div class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="margin-right: 8px; margin-left: 4px"
              class="logo"
              height="26px"
              alt=""
            />
            <h4>Add Group</h4>
          </div>
          <div class="flex-row">
            <img
              @click="resetGroupModal"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="margin-right: 16px; filter: invert(30%); cursor: pointer"
            />
          </div>
        </div>

        <div class="margin-top">
          <AlertGroup :resourceType="alert.resourceType" :form.sync="groupForm" />

          <div class="bottom">
            <button @click="onSaveGroup()" class="green_button" :disabled="!groupForm.isValid">
              Add Group
            </button>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="deliveryModalOpen" dimmed>
      <div class="modal-container-large rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="margin-right: 8px; margin-left: 4px"
              class="logo"
              height="26px"
              alt=""
            />
            <h4>Delivery Method</h4>
          </div>
          <div class="flex-row">
            <img
              @click="resetDeliveryModal"
              src="@/assets/images/close.svg"
              height="24px"
              alt=""
              style="margin-right: 16px; filter: invert(30%); cursor: pointer"
            />
          </div>
        </div>

        <div class="margin-top">
          <AlertSettingsModal
            @close-settings-modal="closeSettingsModal"
            :resourceType="alert.resourceType"
            :form.sync="deliveryForm"
          />
        </div>
      </div>
    </Modal>
    <div class="title">
      <h4 class="title__head">General</h4>

      <section v-if="!templateNames.includes(alert.title)" class="title__body">
        <div style="display: flex; justify-content: center">
          <div style="color: #41b883" v-show="savedChanges">Saved Changes!</div>
        </div>
        <p>Edit workflow title</p>
        <input
          :id="`resource-title-${alert.id}`"
          :errors="templateTitleField.errors"
          v-model="templateTitleField.value"
        />
      </section>

      <section class="title__body" v-else>
        <p>Cant edit templated alert titles</p>
        <h2 style="color: #4d4e4c; font-size: 16px">{{ alert.title }}</h2>
      </section>
    </div>

    <div class="title">
      <h4 class="title__head">Conditions</h4>

      <section class="title__body">
        <p>Edit your workflow conditions</p>
      </section>
      <div
        style="padding-top: 8px; padding-bottom: 8px"
        v-for="(group, index) in alert.groupsRef"
        :key="index"
        :class="index > 0 ? 'top-border' : ''"
      >
        <div
          v-if="alert.groupsRef.length > 1"
          style="display: flex; justify-content: flex-end; width: 100%"
        >
          <div class="remove__group">
            <img
              @click.stop="onRemoveAlertGroup(group.id, index)"
              style="height: 18px; cursor: pointer; filter: invert(40%)"
              src="@/assets/images/trash.svg"
              alt=""
            />
          </div>
        </div>

        <div>
          <p
            @click="onDeleteOperand(operand.id, i, index)"
            class="row"
            :key="i"
            v-for="(operand, i) in group.operandsRef"
          >
            <span class="remove__group" style="margin-right: 8px">
              <img class="remove-color" src="@/assets/images/remove.svg" style="16px" alt="" />
            </span>
            {{ 'Condition ' + (i + 1) + ': ' }}
            {{ getReadableOperandRow(operand) }}
          </p>

          <div v-if="group.operandsRef.length < 3" style="margin-left: 12px" class="plus_button">
            <button @click="onShowOperandModal(index)">+</button>
          </div>
        </div>
      </div>

      <div class="flex-end" v-if="alert.groupsRef.length < 3">
        <button class="condition-button" @click="onShowGroupModal()">Add Group</button>
      </div>
    </div>

    <div class="title">
      <h4 class="title__head">Delivery</h4>

      <section class="title__body">
        <p>Edit your delivery options</p>
      </section>

      <p class="row" :key="index" v-for="(config, index) in alert.configsRef">
        <span class="remove__group" style="margin-right: 8px">
          <img
            class="remove-color"
            @click="onDeleteConfig(config.id, index)"
            src="@/assets/images/remove.svg"
            style="height: 22px"
            alt=""
          />
        </span>

        {{ 'Option ' + (index + 1) + ': ' }}
        {{ getReadableConfig(config) }}
      </p>

      <div style="margin-left: 12px" class="plus_button">
        <button @click="onShowSettingsModal">+</button>
      </div>
    </div>

    <div style="margin-bottom: 8px; display: flex" class="title">
      <div style="">
        <h4 class="title__head">Slack Message</h4>
        <section class="title__body">
          <p style="margin-bottom: 0">
            This is the message you'll recieve in slack with your workflow.
          </p>
        </section>
        <div style="display: flex; overflow-y: auto; height: 28.75vh">
          <div style="margin-bottom: 1rem">
            <div v-if="formattedSlackMessage.length">
              <draggable
                v-model="formattedSlackMessage"
                group="fields"
                @start="drag = true"
                @end="dragEnd"
                class="drag-section"
              >
                <div
                  v-for="(message, i) in formattedSlackMessage"
                  :key="i"
                  style="
                    margin: 0.5rem 1rem;
                    padding: 6px 12px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    width: 27.5vw;
                    border: 1px solid #eeeeee;
                    border-radius: 8px;
                    cursor: pointer;
                  "
                >
                  <div style="justify-self: start">
                    <div style="font-weight: 900; font-size: 0.75rem; display: flex">
                      <img src="@/assets/images/drag.svg" alt="" />
                      <div style="margin-top: 0.25rem; margin-left: 0.5rem">
                        {{ message.title }}
                      </div>
                    </div>
                    <!-- <div style="font-size: .6rem;">{ {{message.val}} }</div> -->
                  </div>
                  <div @click="removeMessage(i, message)">
                    <img src="@/assets/images/remove.svg" style="height: 1.2rem" />
                  </div>
                </div>
              </draggable>
            </div>
            <div
              v-else
              style="
                margin: 0.5rem 1rem;
                padding: 6px 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 27.5vw;
                border: 1px solid #eeeeee;
                border-radius: 8px;
              "
            >
              <div style="justify-self: start">
                <div style="font-weight: 900; font-size: 0.75rem; margin-bottom: 0.1rem">
                  Please Select an Option from the List
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div style="margin-right: 8px; height: fit-content" class="start">
        <section style="max-width: 19vw;">
          <div class="search-bar">
            <img src="@/assets/images/search.svg" style="height: 18px" alt="" />
            <input
              @input="searchFields"
              type="search"
              :placeholder="`Search Fields`"
              v-model="filterText"
            />
          </div>

          <div class="field-section__fields">
            <div>
              <p v-for="(field, i) in filteredFields" :key="field.id" style="margin: 4px 0">
                <input
                  @click="onAddField(field)"
                  type="checkbox"
                  :id="i"
                  :value="field"
                  style="width: 10%; cursor: pointer"
                />
                <label :for="i"></label>
                {{ field.label == 'Price Book Entry ID' ? 'Products' : field.label }}
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import Modal from '@/components/InviteModal'
import draggable from 'vuedraggable'

//Internal
import AlertSettingsModal from '@/views/settings/alerts/view/_AlertSettingsModal'
import FormField from '@/components/forms/FormField'
/**
 * Services
 *
 */
import AlertOperandRow from '../create/_AlertOperandRow.vue'
import AlertGroup from '../create/_AlertGroup'
import { CollectionManager } from '@thinknimble/tn-models'
import { FormField as FormFieldService } from '@thinknimble/tn-forms'
import { RequiredValidator } from '@thinknimble/tn-validators'
import AlertTemplate, {
  AlertMessageTemplate,
  AlertConfig,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertGroupOperand,
  AlertOperandForm,
  AlertGroupForm,
  AlertGroup as AlertGroupModel,
} from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { ObjectField } from '@/services/crm'
import { ALERT_DATA_TYPE_MAP, STRING } from '@/services/salesforce/models'

export default {
  name: 'AlertsEditPanel',
  components: {
    FormField,
    AlertSettingsModal,
    Modal,
    AlertGroup,
    AlertOperandRow,
    draggable,
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
      modalOpen: false,
      deliveryModalOpen: false,
      groupModalOpen: false,
      currentForm: null,
      groupForm: null,
      groupIndex: null,
      deliveryForm: null,
      templateTitleField: new FormFieldService({ validators: [new RequiredValidator()] }),
      // executeUpdateMessageTemplate: debounce(this.updateMessageTemplate, 900),
      messageTemplateForm: new AlertMessageTemplateForm(),
      savedChanges: false,
      savingInTab: false,
      valuePromise: null,
      slackMessage: [],
      formattedSlackMessage: [],
      fields: CollectionManager.create({
        ModelClass: ObjectField,
        filters: {
          crmObject: this.alert.resourceType,
          forAlerts: true,
        },
        pagination: { size: 1000 },
      }),
      filterText: '',
      addedFields: [],
      templateNames: [
        'Close Date Passed',
        'Close Date Approaching',
        'Update Forecast',
        'Deal Rotting',
        'Deal Review',
        'Upcoming Next Step',
        'Large Opportunities',
        'Large Deals',
        'Closing This Month',
        'Closing Next Month',
        'Closing This Quarter',
        'Empty Field',
        'Empty Property',
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
    }
  },

  computed: {
    filteredFields() {
      return this.fields.list.filter(
        (field) => !this.addedFieldNames.includes(`${this.alert.resourceType}.${field.apiName}`),
      )
    },
    addedFieldNames() {
      return this.formattedSlackMessage.map((field) => {
        return field.val.trim()
      })
    },
    stateRecordTypes() {
      return this.$store.state.recordTypes
    },
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    resetDeliveryModal() {
      this.deliveryModalOpen = !this.deliveryModalOpen
      this.deliveryForm = null
      this.groupIndex = null
    },
    updateWorkflow() {
      this.updateTemplate()
      this.updateMessageTemplate()
    },
    async updateTemplate() {
      this.templateTitleField.validate()
      if (this.templateTitleField.isValid) {
        try {
          this.savingInTab = true
          await AlertTemplate.api.updateAlertTemplate(this.alert.id, {
            title: this.templateTitleField.value,
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
    resetGroupModal() {
      this.groupModalOpen = !this.groupModalOpen
      this.groupForm = null
      this.groupIndex = null
    },
    resetModal() {
      this.modalOpen = !this.modalOpen
      this.currentForm = null
      this.groupIndex = null
    },
    async onSaveOperand() {
      this.currentForm.validate()
      if (this.currentForm.isValid) {
        try {
          const res = await AlertGroupOperand.api.createOperand(this.currentForm.toAPI)
          this.$toast('Successfully added operand', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })

          this.alert.groupsRef[this.groupIndex].operandsRef = [
            ...this.alert.groupsRef[this.groupIndex].operandsRef,
            res,
          ]
          this.alert.groupsRef[this.groupIndex].operands = [
            ...this.alert.groupsRef[this.groupIndex].operandsRef.map((op) => op.id),
          ]
        } finally {
          this.modalOpen = false
          this.groupIndex = null
          this.currentForm = null
        }
      }
    },
    onShowOperandModal(groupIndex) {
      this.groupIndex = groupIndex
      let newForm = new AlertOperandForm({
        operandOrder: this.alert.groupsRef[groupIndex].operandsRef.length,
        groupId: this.alert.groupsRef[groupIndex].id,
      })
      this.currentForm = newForm
      this.modalOpen = true
    },
    async onSaveGroup() {
      this.groupForm.validate()
      if (this.groupForm.isValid) {
        try {
          const res = await AlertGroupModel.api.createGroup(this.groupForm.toAPI)
          this.$toast('Successfully added group', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.alert.groupsRef = [...this.alert.groupsRef, res]
          this.alert.groups = [...this.alert.groupsRef.map((op) => op.id)]
        } finally {
          this.groupModalOpen = false
          this.groupForm = null
          this.groupIndex = null
        }
      }
    },
    onShowGroupModal() {
      let newForm = new AlertGroupForm({
        groupOrder: this.alert.groupsRef.length,
        alertTemplateId: this.alert.id,
      })
      this.groupForm = newForm
      this.groupModalOpen = true
    },
    onShowSettingsModal() {
      let newForm = new AlertConfigForm({
        alertTemplateId: this.alert.id,
      })
      this.deliveryForm = newForm
      this.deliveryModalOpen = true
    },
    closeSettingsModal(obj) {
      this.alert.configsRef = [...this.alert.configsRef, obj]
      this.alert.configs = [...this.alert.configsRef.map((op) => op.id)]

      setTimeout(() => {
        this.deliveryModalOpen = false
        this.deliveryForm = null
      }, 300)
    },
    selectedFieldType(operatorField) {
      if (operatorField) {
        return ALERT_DATA_TYPE_MAP[operatorField.dataType]
      } else {
        return STRING
      }
    },
    getRecordNames(value) {
      const option = this.stateRecordTypes.filter((item) => item.id === value)[0]
      return option ? option.label : value
    },
    getReadableOperandRow(rowData) {
      let operandOperator = rowData.operandOperator
      let value = rowData.operandValue
      if (rowData && rowData.operandIdentifier === 'RecordTypeId') {
        this.valuePromise = this.getRecordNames(value)
      }
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
      const operandString = `${rowData.operandIdentifier}     ${operandOperatorLabel}     ${
        this.valuePromise ? this.valuePromise : valueLabel
      } `
      this.valuePromise = null
      return operandString
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
    bindText(val, title) {
      const addedStr = `<strong>${title}</strong> \n { ${val} }`
      this.slackMessage.push(addedStr)
      this.formattedSlackMessage.push({ title, val })
      this.messageTemplateForm.field.body.value = this.slackMessage.join('\n\n')
      this.alert.messageTemplateRef.body = this.slackMessage.join('\n\n')
      // this.executeUpdateMessageTemplate()
    },
    removeMessage(i, removedField) {
      this.slackMessage = this.slackMessage.filter((mes, j) => j !== i)
      this.formattedSlackMessage = this.formattedSlackMessage.filter((mes, j) => j !== i)
      this.messageTemplateForm.field.body.value = this.slackMessage.join('\n\n')
      this.alert.messageTemplateRef.body = this.slackMessage.join('\n\n')
      this.addedFields = [...this.addedFields.filter((f) => f.id != removedField.id)]
      // this.executeUpdateMessageTemplate()
    },
    onAddField(field) {
      this.addedFields.push({ ...field, order: this.addedFields.length, includeInRecap: true })
      this.bindText(`${this.alert.resourceType}.${field.apiName}`, `${field.label}`)
    },
    searchFields() {
      this.fields = CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 1000 },
        filters: {
          crmObject: this.alert.resourceType,
          search: this.filterText,
        },
      })
      this.fields.refresh()
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
    dragEnd() {
      const slackMesArr = []
      const slackBindingsArr = []
      for (let i = 0; i < this.formattedSlackMessage.length; i++) {
        slackMesArr.push(
          '<strong>' +
            this.formattedSlackMessage[i].title +
            '</strong> \n { ' +
            this.formattedSlackMessage[i].val +
            ' }',
        )
        slackBindingsArr.push(` ${this.formattedSlackMessage[i].val} `)
      }
      this.slackMessage = slackMesArr
      this.messageTemplateForm.field.body.value = this.slackMessage.join('\n\n')
      this.alert.messageTemplateRef.body = this.slackMessage.join('\n\n')
      this.messageTemplateForm.field.bindings.value = slackBindingsArr
      this.alert.messageTemplateRef.bindings = slackBindingsArr
      this.updateMessageTemplate()
      this.drag = false
    },
    async onRemoveAlertGroup(id, index) {
      console.log(id, index)
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
          await AlertGroupModel.api.delete(id)
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
  async created() {
    // populate values for stand alone fields
    // for this version only allowing edit of certain fields or delete of array items
    this.fields.refresh()
    if (this.alert) {
      this.templateTitleField.value = this.alert.title
      // work here
      this.messageTemplateForm.field.body.value = this.alert.messageTemplateRef.body
    }
    if (this.messageTemplateForm.field.body.value) {
      this.slackMessage = this.messageTemplateForm.field.body.value.split('\n\n')
    }
    const slackFormat = []
    for (let i = 0; i < this.slackMessage.length; i++) {
      const titleAndVal = this.slackMessage[i].split('\n')
      const titleFormatted = titleAndVal[0].slice(8, titleAndVal[0].length - 10)
      const valFormatted = titleAndVal[1].slice(3, titleAndVal[1].length - 2)
      // valFormatted is needed for addedFieldNames, since it is more precise than just the title for filtering
      slackFormat.push({ title: titleFormatted, val: valFormatted })
    }
    this.formattedSlackMessage = slackFormat
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

::v-deep .ql-toolbar.ql-snow {
  display: none;
}
::v-deep .ql-container.ql-snow {
  outline: 1px solid $soft-gray;
  border: none;
  border-radius: 4px;
  margin-left: 12px;
  width: 48vw;
}
::v-deep .ql-editor p {
  color: $base-gray;
}
::v-deep .ql-editor.ql-blank::before {
  color: $very-light-gray;
}

.bottom {
  position: absolute;
  right: 1rem;
  bottom: 1rem;
}
@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.edit-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 16px 0px;
}
.title {
  background-color: white;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  border: 1px solid $soft-gray;
  color: $base-gray;
  border-radius: 6px;
  width: 50vw;
  // min-height: 25vh;
  letter-spacing: 0.75px;
  padding: 0px 0px 32px 0px;
  margin-top: 16px;
  &__head {
    padding: 8px 12px;
    background-color: white;
    margin-bottom: 0;
    // color: $very-light-gray;
  }
  &__body {
    padding: 6px 12px;
    background-color: white;
    font-size: 11px;
    color: $light-gray-blue;
    p {
      margin-top: 0;
    }
  }
}
.flex-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
}
.top-border {
  border-top: 1px solid #eeeeee;
}
.remove__group {
  background-color: $off-white;
  border-radius: 4px;
  cursor: pointer;
  padding: 3px 6px;
  margin-left: 8px;
  display: flex;
  align-items: center;
  width: fit-content;
  color: $base-gray;
}
.plus_button {
  border: none;
  background-color: transparent;
  border-radius: 0.3rem;
  padding: 0.1rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: $dark-green;
  margin-right: 8px;

  button {
    @include white-button();
    border-radius: 100%;
    font-size: 18px;
  }
}
h3 {
  font-weight: 400;
  letter-spacing: 0.25px;
}
input {
  border: none;
  letter-spacing: 0.8px;
  padding: 8px;
  color: $base-gray;
  width: 94%;
  border: 1px solid $soft-gray;
  border-radius: 4px;
  margin-top: 8px;
}
input:focus {
  outline: none;
}
.green_button {
  @include primary-button();
  max-height: 2rem;
  padding: 0.5rem 1.25rem;
  font-size: 12px;
}
.condition-button {
  @include white-button();
  padding: 0.5rem 1rem;
  margin: 0.5rem;
  font-size: 13px;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 14px;
  letter-spacing: 0.75px;
  cursor: pointer;
}
.remove-color {
  filter: invert(30%);
  cursor: pointer;
}
.search-bar {
  background-color: white;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  border-radius: 8px;
  margin-top: 16px;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
input[type='search'] {
  width: 15vw;
  letter-spacing: 0.75px;
  border: none;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
.field-section {
  width: 20vw;
  background-color: white;
  height: 100%;
  margin-top: 28px;
  margin-left: 16px;
  padding: 0px 32px;
  border-radius: 6px;
  letter-spacing: 0.75px;

  &__title {
    letter-spacing: 0.75px;
  }
  &__fields {
    h4 {
      font-size: 13px;
      font-weight: 400;
      margin-bottom: 8px;
    }
    p {
      font-size: 12px;
      letter-spacing: 0.75px;
    }
    div {
      outline: 1px solid $soft-gray;
      border-radius: 6px;
      padding: 4px 16px;
      margin-top: 16px;
      height: 32vh;
      overflow: scroll;
      section {
        span {
          color: $coral;
          margin-left: 4px;
        }
      }
    }
  }
}
.modal-container {
  background-color: $white;
  overflow-y: scroll;
  overflow-x: hidden;
  width: 58vw;
  // min-height: 50vh;
  height: 54vh;
  align-items: center;
  border-radius: 0.5rem;
  padding: 0px 4px;

  &__footer {
    position: absolute;
    display: flex;
    flex-direction: row;
    align-items: center;
    bottom: 0;
    right: 16px;
    padding: 0px 8px;
    background-color: white;

    p {
      font-size: 12px;
      color: $light-gray-blue;
    }

    button {
      margin-right: 0px;
      margin-left: 60vw;
      margin-bottom: 12px;
    }
  }
}
.modal-container-large {
  background-color: $white;
  overflow-y: scroll;
  overflow-x: hidden;
  width: 58vw;
  // min-height: 50vh;
  height: 62vh;
  align-items: center;
  border-radius: 0.5rem;
  padding: 0px 4px;

  &__footer {
    position: absolute;
    display: flex;
    flex-direction: row;
    align-items: center;
    bottom: 0;
    right: 16px;
    padding: 0px 8px;
    background-color: white;

    p {
      font-size: 12px;
      color: $light-gray-blue;
    }

    button {
      margin-right: 0px;
      margin-left: 60vw;
      margin-bottom: 12px;
    }
  }
}
.rel {
  position: relative;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.sticky {
  position: sticky;
  background-color: white;
  width: 100%;
  left: 0;
  top: 0;
  padding: 0px 6px 8px -2px;
  z-index: 2;
}
.border-bottom {
  border-bottom: 1.25px solid $soft-gray;
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  letter-spacing: 1px;
  h4 {
    font-size: 20px;
  }
}
.margin-top {
  margin-top: 2rem;
}
</style>
