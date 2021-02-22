<template>
  <div class="slack-form-builder">
    <div>
      <div class="slack-from-builder__sf-validations">
        <h4>Validations</h4>
        <template v-if="showValidations">
          <div v-for="val in sfValidations">
            <span>{{ val.description }}</span>
            <span>{{ val.message }}</span>
          </div>
        </template>
      </div>
    </div>
    <div style="display:flex;">
      <div class="slack-form-builder__sf-fields">
        <h4>Available Fields</h4>
        <p><i>Click a field to add it to the form.</i></p>
        <div
          v-for="field in sfOpportunityFieldsAvailableToAdd"
          :key="field.key"
          class="slack-form-builder__sf-field"
          @click="() => onAddField(field)"
        >
          {{ field.label }}
        </div>
      </div>

      <div class="slack-form-builder__form">
        <div class="form-header">
          <div class="form-header__left">
            <h3>Customize Your Slack Form</h3>
          </div>
          <div class="form-header__right">
            <PulseLoadingSpinnerButton
              @click="onSave"
              class="primary-button"
              text="Save"
              :loading="savingForm"
              :disabled="!$store.state.user.isAdmin"
            />
          </div>
        </div>
        <div
          v-for="(field, index) in customSlackFormConfig.fields"
          :key="field.key"
          class="form-field"
        >
          <div class="form-field__left">
            <div class="form-field__label">
              {{ field.label }}
            </div>
          </div>
          <div class="form-field__right">
            <div class="form-field__btn" @click="() => onMoveFieldUp(field, index)">▲</div>
            <div class="form-field__btn" @click="() => onMoveFieldDown(field, index)">▼</div>
            <div
              class="form-field__btn form-field__remove-btn"
              :class="{ 'form-field__remove-btn--disabled': !canRemoveField(field) }"
              :title="
                canRemoveField(field)
                  ? 'Remove this field from the form'
                  : 'This field is required and cannot be removed.'
              "
              @click="() => canRemoveField(field) && onRemoveField(field)"
            >
              {{ !canRemoveField(field) ? 'required' : '× remove' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

import SlackOAuth, { salesforceFields } from '@/services/slack'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'CustomSlackForm',
  components: {
    PulseLoadingSpinnerButton,
  },
  props: {
    customForm: {
      type: Object,
    },
    formType: {
      type: String,
      required: true,
    },
    resource: {
      type: String,
      required: true,
    },
    showValidations: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      salesforceFields,
      customSlackFormConfig: { fields: [] },
      formHasChanges: false,
      savingForm: false,
      ...FORM_CONSTS,
    }
  },
  watch: {
    customForm: {
      deep: true,
      handler(val) {
        if (val) {
          this.customSlackFormConfig = { ...this.customForm.config }
        } else {
          this.customSlackFormConfig = { fields: [] }
        }
      },
    },
  },
  computed: {
    formFields() {
      return this.customSlackFormConfig ? this.customSlackFormConfig.fields : []
    },
    hasConfig() {
      return (
        this.store.state.user.salesforceAccountRef &&
        this.store.state.user.salesforceAccountRef.objectFields
      )
    },
    sfValidations() {
      return this.$store.state.user.salesforceAccountRef.objectFields[this.resource].validations
    },
    sfOpportunityFieldsAsList() {
      // Flatten the Salesforce-provided object of fields to a list of fields
      const oppFields = this.$store.state.user.salesforceAccountRef.objectFields[this.resource]
        .fields
      const result = []
      for (const [key, value] of Object.entries(oppFields)) {
        result.push({ ...value })
      }
      return result
    },
    sfOpportunityFieldsAvailableToAdd() {
      // Get SF fields that are updateable and not already added to the form
      // if the form is a create then show creatable or createable and updateable fields
      // if not show updateable only

      if (this.sfOpportunityFieldsAsList) {
        if (this.formType == 'CREATE') {
          return this.sfOpportunityFieldsAsList.filter(
            sfField =>
              sfField['createable'] &&
              sfField.type !== 'Reference' &&
              !this.customSlackFormConfig.fields.map(f => f.key).includes(sfField.key),
          )
        } else {
          return this.sfOpportunityFieldsAsList.filter(
            sfField =>
              sfField['updateable'] &&
              sfField.type !== 'Reference' &&
              !this.customSlackFormConfig.fields.map(f => f.key).includes(sfField.key),
          )
        }
      } else {
        return []
      }
    },
  },
  methods: {
    canRemoveField(field) {
      // If form is create required fields cannot be removed
      // if form is update required fields can be removed
      // if form is meeting review depening on the resource it can/cant be removed
      if (this.formType == this.CREATE) {
        if (field.required) {
          return false
        } else {
          return true
        }
      } else if (this.formType == this.MEETING_REVIEW) {
        if (
          this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource] &&
          ~this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource].findIndex(f => field.key == f)
        ) {
          return false
        } else {
          return true
        }
      } else {
        return true
      }
    },
    onAddField(field) {
      this.customSlackFormConfig.fields = [...this.customSlackFormConfig.fields, { ...field }]
      this.formHasChanges = true
    },
    onRemoveField(field) {
      // Block removal of 'required' fields.
      if (field.required) {
        return
      }

      this.customSlackFormConfig.fields = this.customSlackFormConfig.fields.filter(
        f => f.key !== field.key,
      )
      this.formHasChanges = true
    },
    onMoveFieldUp(field, index) {
      // Disallow move if this is the first field
      if (index === 0) {
        return
      }

      // Make a copy of fields and do the swap
      const newFields = [...this.customSlackFormConfig.fields]
      newFields[index] = this.customSlackFormConfig.fields[index - 1]
      newFields[index - 1] = field

      // Apply update to the view model
      this.customSlackFormConfig.fields = newFields
    },
    onMoveFieldDown(field, index) {
      // Disallow move if this is the last field
      if (index + 1 === this.customSlackFormConfig.fields.length) {
        return
      }

      // Make a copy of slides and do the swap
      const newFields = [...this.customSlackFormConfig.fields]
      newFields[index] = this.customSlackFormConfig.fields[index + 1]
      newFields[index + 1] = field

      // Apply update to the view model
      this.customSlackFormConfig.fields = newFields
    },
    onSave() {
      this.savingForm = true
      SlackOAuth.api
        .postOrgCustomForm({ ...this.customForm, config: this.customSlackFormConfig })
        .then(res => {
          this.$emit('update:selectedForm', res)
        })
        .finally(() => {
          this.savingForm = false
        })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.slack-form-builder {
  display: flex;
  flex-direction: column;

  &__sf-fields,
  &__sf-validations {
    flex: 2;
    margin-right: -1rem;
  }

  &__sf-field {
    padding: 0.25rem;

    &:hover {
      background-color: $dark-gray-blue;
      cursor: pointer;
    }
  }

  &__form {
    flex: 10;
  }
}

.form-header {
  display: flex;

  &__left {
    flex: 9;
  }

  &__right {
    flex: 3;
    display: flex;
    align-items: center;
    justify-content: flex-end;
  }
}

.form-field {
  display: flex;
  background-color: white;
  padding: 1rem;
  margin: 0.5rem 0;

  &__left {
    flex: 10;
  }

  &__label {
    font-weight: 600;
  }

  &__right {
    flex: 2;
    display: flex;
  }

  &__btn {
    padding: 0.35rem;
    cursor: pointer;
    color: $dark-gray-blue;

    transition: color 0.3s linear;

    &:hover {
      color: black;
    }
  }

  &__remove-btn {
    text-align: right;
    color: $coral;
    cursor: pointer;

    &:hover {
      font-weight: 600;
      color: $coral;
    }

    &--disabled {
      color: $dark-gray-blue;
      cursor: initial;

      &:hover {
        font-weight: initial;
        color: initial;
      }
    }
  }
}
</style>
