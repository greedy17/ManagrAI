<template>
  <div class="slack-form-builder">
    <Modal ref="modalName">
      <template v-slot:header>
        <p>Search for these fields & add them to your slack form</p>
      </template>

      <template v-slot:body>
        <div>
          <p style="color: #ff7649; font-weight: bold">Required:</p>
          <ul>
            <li>"Name"</li>
            <li>"Stage"</li>
            <li>"Close Date"</li>
          </ul>
        </div>
        <p style="color: #5f8cff">Suggested:</p>
        <ul>
          <li>"Amount" or "MRR"</li>
          <li>"Forecast Category"</li>
          <li>"Next Step"</li>
          <li>"Next Step Date"</li>
        </ul>
      </template>
    </Modal>
    <Modal ref="ContactModal">
      <template v-slot:header>
        <p>Search for these fields & add them to your slack form</p>
      </template>

      <template v-slot:body>
        <div>
          <p style="color: #ff7649; font-weight: bold">Required:</p>
          <ul>
            <li>"Last Name"</li>
          </ul>
        </div>
        <p style="color: #5f8cff">Suggested:</p>
        <ul>
          <li>"First Name"</li>
          <li>"Title"</li>
          <li>"Email"</li>
          <li>"Phone"</li>
          <li>"Account Name"</li>
        </ul>
      </template>
    </Modal>
    <Modal ref="AccountModal">
      <template v-slot:header>
        <p>Search for these fields & add them to your slack form</p>
      </template>

      <template v-slot:body>
        <div>
          <p style="color: #ff7649; font-weight: bold">Required:</p>
          <ul>
            <li>"Name"</li>
          </ul>
        </div>
        <p style="color: #5f8cff">Suggested:</p>
        <ul>
          <li>"Type"</li>
        </ul>
      </template>
    </Modal>
    <Modal ref="LeadModal">
      <template v-slot:header>
        <p>Search for these fields & add them to your slack form</p>
      </template>

      <template v-slot:body>
        <div>
          <p style="color: #ff7649; font-weight: bold">Required:</p>
          <ul>
            <li>"Last name"</li>
          </ul>
        </div>
        <p style="color: #5f8cff">Suggested:</p>
        <ul>
          <li>"Title"</li>
          <li>"Phone"</li>
          <li>"Email"</li>
          <li>"Company Name"</li>
          <li>"Status"</li>
        </ul>
      </template>
    </Modal>
    <div>
      <div class="slack-from-builder__sf-validations">
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

    <div class="opportunity__row">
      <div class="collection_fields">
        <div class="header">
          <div style="margin-right: 2rem" class="center">
            <img style="height: 2rem" src="@/assets/images/slackLogo.png" alt="" />
            <p>Fields you'll see in slack</p>
          </div>
          <div class="center">
            <img style="width: 2.5rem; height: 2rem" src="@/assets/images/salesforce.png" alt="" />
            <p>SFDC fields you'll be updating</p>
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
import ListItem from '@/components/ListItem'
import ListContainer from '@/components/ListContainer'
import Modal from '@/components/Modal'

import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import CollectionSearch from '@thinknimble/collection-search'
import Paginator from '@thinknimble/paginator'
import ActionChoice from '@/services/action-choices'

import SlackOAuth, { salesforceFields } from '@/services/slack'
import { SObjectField, SObjectValidations, SObjectPicklist } from '@/services/salesforce'

import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'CustomSlackForm',
  components: {
    PulseLoadingSpinnerButton,
    CheckBox,
    PulseLoadingSpinner,
    Paginator,
    CollectionSearch,
    ListItem,
    ListContainer,
    Modal,
  },
  props: {
    stageForms: {
      type: Array,
      default: () => [],
    },
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
    managrFields: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      currentStageForm: null,
      formFields: CollectionManager.create({ ModelClass: SObjectField }),
      salesforceFields,
      customSlackFormConfig: [],
      formHasChanges: false,
      savingForm: false,
      addedFields: [],
      removedFields: [],
      ...FORM_CONSTS,
      Pagination,
      meetingType: '',
      actionChoices: [],
      loadingMeetingTypes: false,
      requiredFields: [],
      canContinue: false,
    }
  },
  watch: {
    customForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.fields) {
          this.addedFields = [...val.fieldsRef]
          if (this.formType == 'UPDATE') {
            let currentFormFields = this.addedFields.map((field) => {
              return field.id
            })
            if (currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false) {
              let fieldsToAdd = this.managrFields.filter((field) => {
                return (
                  field.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  field.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
                )
              })
              let copyArray = this.addedFields
              fieldsToAdd = fieldsToAdd.concat(copyArray)
              this.addedFields = fieldsToAdd.map((field, i) => {
                let altField = { ...field }
                altField.order = i
                if (
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
                ) {
                  altField.includeInRecap = true
                }
                return altField
              })
            }
          }
          if (this.formType !== 'UPDATE') {
            this.addedFields = this.addedFields.filter((field) => {
              return (
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
              )
            })
          }
        }
      },
    },
    resource: {
      async handler(val) {
        if (val) {
          let searchParams = this.formType
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: val,

                ...fieldParam,
              }
              this.formFields.refresh()
              if (this.formType == 'UPDATE') {
                this.onSave()
              }
            } catch (e) {
              console.log(e)
            }
          }
        }
      },
    },
    formType: {
      immediate: true,

      async handler(val) {
        if (val) {
          let searchParams = val
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: this.resource,

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
    orderedStageForm() {
      let forms = []
      if (this.customForm.stage) {
        let index = this.stageForms.findIndex((f) => f.stage == this.customForm.stage)
        if (~index) {
          forms = this.stageForms.slice(0, index)
        }
      }
      return forms
    },
    sfFieldsAvailableToAdd() {
      return this.fields
    },
    currentFields() {
      return this.customForm ? this.customForm.fields : []
    },
    addedFieldIds() {
      return this.addedFields.map((field) => {
        return field.id
      })
    },
    selectedFormResourceType() {
      return `${this.formType}.${this.resource}`
    },
  },
  created() {
    this.getActionChoices()
  },
  methods: {
    getActionChoices() {
      this.loadingMeetingTypes = true
      const action = ActionChoice.api
        .list({})
        .then((res) => {
          this.actionChoices = res.results
        })
        .finally((this.loadingMeetingTypes = false))
    },
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
      if (
        this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource] &&
        ~this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource].findIndex((f) => field.id == f)
      ) {
        return false
      } else {
        return true
      }
    },
    onAddField(field) {
      if (this.addedFieldIds.includes(field.id)) {
        this.canRemoveField(field) && this.onRemoveField(field)
        return
      }
      this.addedFields.push({ ...field, order: this.addedFields.length, includeInRecap: true })
    },

    goToCustomize() {
      this.$router.push({ name: 'CustomizeLandingPage' })
    },
    goToContacts() {
      this.$router.push({ name: 'CreateContacts' })
    },
    goToUpdateOpp() {
      this.$router.push({ name: 'UpdateOpportunity' })
    },
    onRemoveField(field) {
      // remove from the array if  it exists

      this.addedFields = [...this.addedFields.filter((f) => f.id != field.id)]

      // if it exists in the current fields add it to remove field

      if (~this.currentFields.findIndex((f) => f == field.id)) {
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

    async updateMeeting(e) {
      if (e.keyCode == 13 && this.meetingType.length) {
        this.loadingMeetingTypes = true
        if (
          (this.resource == 'Opportunity' || this.resource == 'Account') &&
          this.customForm.formType == FORM_CONSTS.MEETING_REVIEW
        ) {
          if (!this.meetingType.length && !this.actionChoices.length) {
            this.$Alert.alert({
              type: 'error',
              message: 'Please enter a Meeting Type',
              timeout: 2000,
            })
            return
          } else {
            const obj = {
              title: this.meetingType,
              organization: this.$store.state.user.organization,
            }

            await ActionChoice.api
              .create(obj)
              .then((res) => {
                this.$Alert.alert({
                  type: 'success',
                  message: 'New meeting type created',
                  timeout: 2000,
                })
              })
              .finally((this.loadingMeetingTypes = false))

            this.getActionChoices()
            this.meetingType = ''
          }
        }
      }
    },
    async removeMeetingType(id) {
      if (!this.$store.state.user.isAdmin) {
        return
      }
      try {
        await ActionChoice.api.delete(id)
        await this.getActionChoices()
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingMeetingTypes = false
      }
    },

    async onSave() {
      if (
        (this.resource == 'Opportunity' || this.resource == 'Account') &&
        this.customForm.formType == FORM_CONSTS.MEETING_REVIEW
      ) {
        if (!this.meetingType.length && !this.actionChoices.length) {
          this.$Alert.alert({
            type: 'error',
            message: 'Please enter a Meeting Type',
            timeout: 2000,
          })
          return
        }
      }
      this.savingForm = true

      let fields = new Set([...this.addedFields.map((f) => f.id)])
      fields = Array.from(fields).filter((f) => !this.removedFields.map((f) => f.id).includes(f))
      let fields_ref = this.addedFields.filter((f) => fields.includes(f.id))
      SlackOAuth.api
        .postOrgCustomForm({
          ...this.customForm,
          fields: fields,
          removedFields: this.removedFields,
          fields_ref: fields_ref,
        })
        .then((res) => {
          this.$emit('update:selectedForm', res)
        })
        .finally(() => {
          this.savingForm = false
          this.canContinue = true
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

.center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 0.85rem;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
}
.slack-form-builder
  ::v-deep
  .collection-search
  .collection-search__results
  .collection-search__result-item {
  border: none;
  background-color: $panther;
}
.slack-form-builder
  ::v-deep
  .collection-search
  .collection-search__form
  .collection-search__input
  .search__input {
  @include input-field();
  height: 2.5rem;
  background-color: $panther-silver;
  border: 1px solid $panther-gray;
  width: 10rem;
  padding: 0 0 0 1rem;
  margin: 1rem;
  box-shadow: 1px 4px 7px black;
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
    background-color: $panther;
  }

  &__sf-field {
    padding: 0.25rem;
    font-size: 0.85rem;
    font-weight: bold;
    font-display: #{$bold-font-family};
    background-color: $panther;
    &:hover {
      background-color: $panther;
      cursor: pointer;
      color: $panther-silver;
    }
  }

  &__required {
    padding: 0.25rem;
    font-size: 0.85rem;
    font-weight: bold;
    font-display: #{$bold-font-family};
    background-color: $panther;
    &:hover {
      background-color: $panther;
      cursor: pointer;
      color: $panther-orange;
    }
  }

  &__form {
    // flex: 10;
    width: 26vw;
    padding: 2rem;
    box-shadow: 0 5px 10px 0 rgba(132, 132, 132, 0.26);
    background-color: $panther;
    height: 54vh;
    overflow-y: scroll;
    overflow-x: hidden;
    border-radius: 0.5rem;
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

  align-items: center;

  position: -webkit-sticky;
  position: sticky;
  background-color: $panther;
  top: 0;
  > .save-button {
    flex: 0.5 0 auto;
  }
  > .heading {
    flex: 1 0 auto;
  }
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
  background-color: $panther;
  margin-top: 0.5rem;
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
    font-weight: bold;
  }

  &__right {
    // flex: 2;
    display: flex;
    padding-left: 1rem;
    margin-right: -0.5rem;

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
  justify-content: center;
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.primary-button {
  width: 10rem;
}

.field-title {
  font-size: 0.75rem;
  margin-left: 1rem;

  &__bold {
    font-family: #{$bold-font-family};
    margin: 2rem 0 0 1rem;
  }
}

.meeting-type {
  @include input-field();
  padding: 0.5rem;
  width: 15rem;

  &__list {
    margin-top: 0.2rem;
    width: 80%;
    overflow: hidden;
  }
}
.stages-list {
  top: 0.1rem;
}

.space {
  margin: 1em;
}
h2 {
  margin: -2px;
  font-size: 1.5rem;
}
.recap {
  display: flex;
  justify-content: flex-end;
  margin-bottom: -2rem;
}
img:hover {
  cursor: pointer;
}
.collection_fields {
  background-color: $panther;
  padding: 2rem;
  border-radius: 0.5rem;
  min-height: 66vh;
  min-width: 44vw;
}
.fields_title {
  background-color: $panther;
  margin: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  width: 100%;
}
.heading {
  background-color: $panther;
}
.opportunity__column {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-right: 2rem;
}
.opportunity__row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}
.orange {
  color: $panther-orange;
}
.required__fields {
  color: $panther-orange;
}
::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 6px;
}
::-webkit-scrollbar-thumb {
  border-radius: 2px;
  background-color: $dark-green;
}
.popular_fields {
  font-weight: bold;
  text-align: center;
}
.popularModal {
  color: $panther-silver;
  text-decoration: underline;
  cursor: pointer;
}
.continue__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: $dark-green;
  background-color: white;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
  margin-right: 0.5rem;
}
.cant__continue {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $panther-silver;
  color: $panther-gray;
  cursor: not-allowed;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
  margin-right: 0.5rem;
}
.back__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $panther-orange;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
  margin-right: 0.5rem;
}
.warning {
  margin-top: 1rem;
  padding: 0.5rem;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  color: $panther-gold;
}
</style>

