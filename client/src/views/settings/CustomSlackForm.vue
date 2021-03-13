<template>
  <div class="slack-form-builder">
    <div>
      <div class="slack-from-builder__sf-validations">
        <!-- <h4>Validations</h4> -->
        <template v-if="showValidations">
          <template v-if="sfValidations.length">
            <ul :key="val.id" v-for="val in sfValidations">
              <li>
                <strong>Title:</strong>
                {{ val.description }}
                <strong>Message:</strong>
                {{ val.message }}
              </li>
            </ul>
          </template>
          <template v-else>{{ resource }} does not appear to have any custom validations</template>
        </template>
      </div>
    </div>

    <div style="display:flex;">
      <div>
        <PulseLoadingSpinner v-if="loading" />

        <div v-if="!loading" class="slack-form-builder__sf-fields">
          <div
            v-for="field in sfFieldsAvailableToAdd"
            class="slack-form-builder__container"
            @click="()=> onAddField(field)"
            :key="field.id"
          >
            <CheckBox :checked="addedFieldIds.includes(field.id)" />
            <div
              :key="field.apiName"
              class="slack-form-builder__sf-field"
            >{{ field.referenceDisplayLabel }}</div>
          </div>
        </div>
      </div>

      <div class="slack-form-builder__form">
        <div class="form-header">
          <div class="form-header__left">
            <h3>Your Slack Form</h3>
          </div>
          <div class="form-header__right"></div>
        </div>

        <div v-for="(field, index) in [...addedFields]" :key="field.apiName" class="form-field">
          <div
            v-if="field.referenceDisplayLabel === 'Meeting Type' || field.referenceDisplayLabel === 'Meeting Comments' || field.referenceDisplayLabel === 'How Did It go?'"
            class="form-field__label"
          >{{ field.referenceDisplayLabel }}</div>
          <div style="display: flex; width: 100%;">
            <div class="form-field__left">
              <div
                v-if="field.referenceDisplayLabel === 'Meeting Type'"
                class="form-field__body"
              >{{"This logs the type of meeting you’ve had, ie 'Discovery Call, Follow Up, etc.'" }}</div>
              <div
                v-if=" field.referenceDisplayLabel === 'Meeting Comments' "
                class="form-field__body"
              >{{ "Logs the rep’s comments about the meeting"}}</div>
              <div
                v-if=" field.referenceDisplayLabel === 'How Did It go?'"
                class="form-field__body"
              >{{"Gives reps the ability to tell you how they think the meeting went (Great, Fine, Not Well)" }}</div>

              <div
                class="form-field__label"
                v-if="field.referenceDisplayLabel !== 'Meeting Type' && field.referenceDisplayLabel !== 'Meeting Comments' && field.referenceDisplayLabel !== 'How Did It go?'"
              >{{ field.referenceDisplayLabel }}</div>
            </div>

            <div class="form-field__middle">{{field.required? 'required':''}}</div>
            <div class="form-field__right">
              <div
                class="form-field__btn form-field__btn--flipped"
                @click="() => onMoveFieldUp(field, index)"
              >
                <img src="@/assets/images/dropdown-arrow-green.svg" />
              </div>
              <div class="form-field__btn" @click="() => onMoveFieldDown(field, index)">
                <img src="@/assets/images/dropdown-arrow-green.svg" />
              </div>
            </div>
          </div>
        </div>
        <div class="save-button">
          <PulseLoadingSpinnerButton
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
            :disabled="!$store.state.user.isAdmin"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'
import CheckBox from '../../components/CheckBoxUpdated'

import SlackOAuth, { salesforceFields } from '@/services/slack'
import { SObjectField, SObjectValidations } from '@/services/salesforce'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'CustomSlackForm',
  components: {
    PulseLoadingSpinnerButton,
    CheckBox,
    PulseLoadingSpinner,
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
    fields: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      salesforceFields,
      customSlackFormConfig: [],
      formHasChanges: false,
      savingForm: false,
      addedFields: [],
      removedFields: [],
      ...FORM_CONSTS,
    }
  },
  watch: {
    customForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.fields) {
          this.addedFields = [...val.fieldsRef]
        }
      },
    },
  },
  computed: {
    sfFieldsAvailableToAdd() {
      return this.fields
    },
    currentFields() {
      return this.customForm ? this.customForm.fields : []
    },
    addedFieldIds() {
      return this.addedFields.map(field => {
        return field.id
      })
    },
  },
  created() {},
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
      if (this.addedFieldIds.includes(field.id)) {
        this.canRemoveField(field) && this.onRemoveField(field)
        return
      }
      this.addedFields.push({ ...field, order: this.addedFields.length })
    },

    onRemoveField(field) {
      // remove from the array if  it exists

      this.addedFields = [...this.addedFields.filter(f => f.id != field.id)]

      // if it exists in the current fields add it to remove field

      if (~this.currentFields.findIndex(f => f == field.id)) {
        this.removedFields = [this.removedFields, field]
      }
    },
    onMoveFieldUp(field, index) {
      // Disallow move if this is the first field
      if (index === 0) {
        return
      }

      // Make a copy of fields and do the swap
      const newFields = [...this.addedFields]
      newFields[index] = this.addedFields[index - 1]
      newFields[index - 1] = field

      // Apply update to the view model
      this.addedFields = newFields
    },
    onMoveFieldDown(field, index) {
      // Disallow move if this is the last field
      if (index + 1 === this.addedFields.length) {
        return
      }

      // Make a copy of slides and do the swap
      const newFields = [...this.addedFields]
      newFields[index] = this.addedFields[index + 1]
      newFields[index + 1] = field

      // Apply update to the view model
      this.addedFields = newFields
    },
    onSave() {
      this.savingForm = true
      let fields = new Set([...this.addedFields.map(f => f.id)])
      fields = Array.from(fields).filter(f => !this.removedFields.map(f => f.id).includes(f))
      SlackOAuth.api
        .postOrgCustomForm({
          ...this.customForm,
          fields: fields,
          removedFields: this.removedFields,
        })
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
@import '@/styles/mixins/inputs.scss';

.slack-form-builder {
  display: flex;
  flex-direction: column;
  position: relative;

  &__sf-fields,
  &__sf-validations {
    margin-right: 2rem;
  }

  &__container {
    display: flex;
  }

  &__sf-field {
    padding: 0.25rem;
    font-size: 0.75rem;
    font-display: #{$bold-font-family};

    &:hover {
      background-color: $dark-gray-blue;
      cursor: pointer;
    }
  }

  &__form {
    // flex: 10;

    width: 50vw;
    position: absolute;
    margin: 45px 108px 1px 35px;
    padding: 25px 17px 32px 39.6px;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(132, 132, 132, 0.26);
    border: solid 2px #dcdddf;
    background-color: #ffffff;
    left: 13rem;
    top: -6rem;
    min-height: 70vh;
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
  background-color: white;
  padding: 1rem;
  margin: 0.5rem 0;

  &__left {
    flex: 10;

    display: flex;
    align-items: center;
  }

  &__middle {
    flex: 2;

    display: flex;
    align-items: center;
  }

  &__body {
    font-size: 0.75rem;
  }

  &__label {
    font-weight: 600;
  }

  &__right {
    flex: 2;
    display: flex;

    display: flex;
    align-items: center;
  }

  &__btn {
    padding: 0.35rem;
    cursor: pointer;
    color: $dark-gray-blue;

    transition: color 0.3s linear;

    &:hover {
      color: black;
    }

    &--flipped {
      transform: rotateX(180deg);
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
.save-button {
  display: flex;
  justify-content: flex-end;
}

.primary-button {
  position: absolute;

  width: 10rem;
  bottom: 1.5rem;
}

.search-bar {
  @include input-field();
  height: 2.5rem !important;
  width: 13rem;
  padding: 0 0 0 1rem;
  margin: 1rem;
}

.field-title {
  font-size: 0.75rem;
  margin-left: 1rem;

  &__bold {
    font-family: #{$bold-font-family};
    margin: 2rem 0 0 1rem;
  }
}
</style>
