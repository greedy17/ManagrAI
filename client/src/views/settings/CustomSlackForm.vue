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
        <CollectionSearch
          :collection="formFields"
          itemDisplayKey="referenceDisplayLabel"
          :showSubmitBtn="false"
          @onClickItem="
            e => {
              onAddField(e)
            }
          "
          @onSearch="
            () => {
              formFields.pagination = new Pagination()
            }
          "
        >
          <template v-slot:item="{ result }">
            <div class="slack-form-builder__container">
              <CheckBox :checked="addedFieldIds.includes(result.id)" />
              <div class="slack-form-builder__sf-field">{{ result['referenceDisplayLabel'] }}</div>
            </div>
          </template>
        </CollectionSearch>
        <div
          class="paginator__container"
          v-if="formFields.pagination.next || formFields.pagination.previous"
        >
          <div class="paginator__text">View More</div>

          <Paginator
            :pagination="formFields.pagination"
            @next-page="nextPage"
            @previous-page="previousPage"
            :loading="formFields.loadingNextPage"
            arrows
            size="small"
            class="paginator"
          />
        </div>
      </div>

      <div class="slack-form-builder__form">
        <div class="form-header">
          <div class="form-header__left">
            <h3>{{ customForm.stage ? `${customForm.stage} Stage` : 'Your Slack Form' }}</h3>
          </div>
          <div class="form-header__right">
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

        <div v-for="(field, index) in [...addedFields]" :key="field.apiName" class="form-field">
          <div
            v-if="
              field.referenceDisplayLabel === 'Meeting Type' ||
                field.referenceDisplayLabel === 'Meeting Comments' ||
                field.referenceDisplayLabel === 'How Did It go?'
            "
            class="form-field__label"
          >{{ field.referenceDisplayLabel }}</div>
          <div style="display: flex; width: 100%;">
            <div class="form-field__left">
              <div v-if="field.referenceDisplayLabel === 'Meeting Type'" class="form-field__body">
                {{
                "This logs the type of meeting you’ve had, ie 'Discovery Call, Follow Up, etc.'"
                }}
              </div>
              <div
                v-if="field.referenceDisplayLabel === 'Meeting Comments'"
                class="form-field__body"
              >{{ 'Logs the rep’s comments about the meeting' }}</div>
              <div v-if="field.referenceDisplayLabel === 'How Did It go?'" class="form-field__body">
                {{
                'Gives reps the ability to tell you how they think the meeting went (Great, Fine, Not Well)'
                }}
              </div>

              <div
                class="form-field__label"
                v-if="
                  field.referenceDisplayLabel !== 'Meeting Type' &&
                    field.referenceDisplayLabel !== 'Meeting Comments' &&
                    field.referenceDisplayLabel !== 'How Did It go?'
                "
              >{{ field.referenceDisplayLabel }}</div>
            </div>

            <div class="form-field__middle">{{ field.required ? 'required' : '' }}</div>
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
      </div>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'
import CheckBox from '../../components/CheckBoxUpdated'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import CollectionSearch from '@thinknimble/collection-search'
import Paginator from '@thinknimble/paginator'

import SlackOAuth, { salesforceFields } from '@/services/slack'
import { SObjectField, SObjectValidations } from '@/services/salesforce'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'CustomSlackForm',
  components: {
    PulseLoadingSpinnerButton,
    CheckBox,
    PulseLoadingSpinner,
    Paginator,
    CollectionSearch,
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
      formFields: CollectionManager.create({ ModelClass: SObjectField }),
      salesforceFields,
      customSlackFormConfig: [],
      formHasChanges: false,
      savingForm: false,
      addedFields: [],
      removedFields: [],
      ...FORM_CONSTS,
      Pagination,
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
    selectedFormResourceType: {
      immediate: true,

      async handler(val) {
        if (val) {
          let searchParams = val.split('.')
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams[0] == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: searchParams[1],

                ...fieldParam,
              }
              this.formFields.refresh()
            } catch (e) {
              console.log(e)
            }
          }
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
    selectedFormResourceType() {
      return `${this.customForm.formType}.${this.resource}`
    },
  },
  created() {},
  methods: {
    nextPage() {
      this.formFields.nextPage()
    },
    previousPage() {
      this.formFields.prevPage()
    },

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
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/buttons';
.slack-form-builder
  ::v-deep
  .collection-search
  .collection-search__results
  .collection-search__result-item {
  border: none;
}
.slack-form-builder
  ::v-deep
  .collection-search
  .collection-search__form
  .collection-search__input
  .search__input {
  @include input-field();
  height: 2.5rem !important;
  width: 13rem;
  padding: 0 0 0 1rem;
  margin: 1rem;
}

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
      //ackground-color: $dark-gray-blue;
      cursor: pointer;
    }
  }

  &__form {
    // flex: 10;

    width: 60%;
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
.paginator {
  @include paginator();
  &__container {
    border: none;
    display: flex;
    justify-content: flex-start;
    width: 11rem;
    font-size: 0.75rem;
    margin-top: 1rem;
  }
  &__text {
    width: 6rem;
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
  width: 10rem;
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
