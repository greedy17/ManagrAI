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
            :errors="templateTitleField.errors"
            @input="executeUpdateTemplate(templateTitleField)"
            v-model="templateTitleField.value"
          />
          <FormField :disabled="true" v-model="alert.resourceType" />
        </div>
        <div v-if="selectedTab == 'GROUPS'" class="alerts-template-list__content-groups">
          <div
            v-for="(group, index) in alert.groupsRef"
            :key="index"
            class="alerts-template-list__content-conditions__group"
          >
            {{ group.groupCondition }}
            <div class="alerts-template-list__content-conditions__operand">
              <ListContainer horizontal>
                <template v-slot:list>
                  <ListItem
                    large
                    v-for="(operand, i) in group.operandsRef"
                    :key="i"
                    :item="
                      `${operand.operandIdentifier}     ${operand.operandOperator}     ${operand.operandValue} `
                    "
                    :active="true"
                    showIcon
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
            />
            <div
              class="alerts-template-list__content-message__form-body"
              style="height:5rem;width:30rem;"
            >
              <FormField :errors="messageTemplateForm.field.body.errors">
                <template v-slot:input>
                  <quill-editor
                    @blur="messageTemplateForm.field.body.validate()"
                    ref="message-body"
                    v-model="messageTemplateForm.field.body.value"
                    :options="{
                      modules: { toolbar: { container: ['bold', 'italic', 'strike'] } },
                    }"
                  />
                </template>
              </FormField>
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
                  large
                  :key="index"
                  v-for="(config, index) in alert.configsRef"
                  :item="
                    `Send an alert on day ${config.recurrenceDay}, ${
                      config.recurrenceFrequency
                    } to ${config.recipients.join(',')} `
                  "
                  :active="true"
                  showIcon
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
import ListContainer from '@/components/ListContainer'
import ListItem from '@/components/ListItem'

//Internal

import ExpandablePanel from '@/components/ExpandablePanel'
import FormField from '@/components/forms/FormField'
import SlackNotificationTemplate from '@/views/settings/alerts/create/SlackNotificationTemplate'
import SlackMessagePreview from '@/views/settings/alerts/create/SlackMessagePreview'
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
  AlertGroupForm,
  AlertTemplateForm,
  AlertConfigForm,
  AlertMessageTemplateForm,
  AlertOperandForm,
} from '@/services/alerts/'
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
    }
  },
  computed: {
    alertObj() {
      return {
        title: this.templateTitleField.value,
        message: this.messageTemplateForm.field.body.value,
        resourceType: this.alert.resourceType,
      }
    },
  },
  methods: {
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
      this.messageTemplateForm.validate()
      if (this.messageTemplateForm.isValid) {
        try {
          this.savingInTab = true
          await AlertMessageTemplate.api.updateMessageTemplate(this.alert.messageTemplateRef.id, {
            body: this.messageTemplateForm.field.body.value,
            notificationText: this.messageTemplateForm.field.notificationText.value,
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
  created() {
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
  justify-content: space-between;

  &__form {
  }
  &__preview {
  }
}
</style>
