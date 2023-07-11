<template>
  <div class="slack-form-builder">
    <div class="opportunity__row">
      <div class="collection_fields">
        <div v-if="formType === 'STAGE_GATING'">
          <p class="section-title">Add Stage Specific Fields</p>
        </div>
        <div>
          <div v-if="formType === 'STAGE_GATING'">
            <div class="center">
              <button
                v-if="!addingFields"
                @click="
                  () => {
                    addingFields = !addingFields
                  }
                "
                class="default_button"
              >
                Add Fields
                <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
              </button>
            </div>
          </div>

          <div v-if="resource === 'OpportunityLineItem'">
            <!-- <div v-if="!addedFieldNames.includes('PricebookEntryId')" class="centered">
              <p style="margin-left: 0.5rem">
                PricebookEntry <span style="color: #fa646a">*</span>
              </p>
              <Multiselect
                placeholder="Select Pricebook field"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
                :loading="dropdownLoading"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>

                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Pricebook field
                  </p>
                </template>
              </Multiselect>
            </div>

            <div v-if="!addedFieldNames.includes('Quantity')" class="centered">
              <p style="margin-left: 0.5rem">Quantity <span style="color: #fa646a">*</span></p>

              <Multiselect
                placeholder="Select Quantity field"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Quantity field
                  </p>
                </template>
              </Multiselect>
            </div> -->
          </div>
        </div>

        <div v-if="resource === 'Contact' || resource === 'Lead' || resource === 'Account'">
          <p class="section-title">
            Select all the fields you typically need to create a Contact :
          </p>

          <div>
            <Multiselect
              :placeholder="
                formType === 'STAGE_GATING' ? 'Search for Validation Fields' : 'Search Fields'
              "
              :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
              @input="onAddField($event)"
              openDirection="below"
              selectLabel="Enter"
              :customLabel="
                ({ referenceDisplayLabel }) =>
                  referenceDisplayLabel === 'PricebookEntry' ? 'Products' : referenceDisplayLabel
              "
              track-by="apiName"
              label="referenceDisplayLabel"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">
                  Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  {{
                    formType === 'STAGE_GATING' ? 'Search for Validation Fields' : 'Search Fields'
                  }}
                </p>
              </template>
            </Multiselect>
          </div>
        </div>

        <div
          style="position: sticky; z-index: 2; top: 0; background-color: white"
          v-if="resource === 'Opportunity' && formType !== 'STAGE_GATING'"
        >
          <p class="section-title">
            Select all the fields you typically need to update an Opportunity :
          </p>

          <div>
            <Multiselect
              :placeholder="
                formType === 'STAGE_GATING' ? 'Search for Validation Fields' : 'Search Fields'
              "
              :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
              @input="onAddField($event)"
              openDirection="below"
              selectLabel="Enter"
              :customLabel="
                ({ referenceDisplayLabel }) =>
                  referenceDisplayLabel === 'PricebookEntry' ? 'Products' : referenceDisplayLabel
              "
              track-by="apiName"
              label="referenceDisplayLabel"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">
                  Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  {{
                    formType === 'STAGE_GATING' ? 'Search for Validation Fields' : 'Search Fields'
                  }}
                </p>
              </template>
            </Multiselect>
          </div>
        </div>

        <draggable
          style="margin-top: 0.5rem"
          v-model="addedFields"
          group="fields"
          @start="drag = true"
          @end="drag = false"
        >
          <div v-for="field in addedFields" :key="field.id">
            <div :class="unshownIds.includes(field.id) ? 'invisible' : 'centered'">
              <div class="drag-item">
                <img
                  :class="unshownIds.includes(field.id) ? 'invisible' : 'invert2'"
                  src="@/assets/images/drag.svg"
                  id="drag"
                  style="height: 22px; width: auto; cursor: grab; margin-right: 16px"
                  alt=""
                />
                <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                  {{ field.referenceDisplayLabel }}
                </p>
              </div>

              <img
                src="@/assets/images/remove.svg"
                height="18px"
                style="margin-right: 8px"
                alt=""
                id="remove"
                :class="unshownIds.includes(field.id) ? 'invisible' : 'invert'"
                @click="
                  () => {
                    onRemoveField(field)
                  }
                "
              />
            </div>
          </div>
        </draggable>

        <div class="example--footer">
          <PulseLoadingSpinnerButton
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'

import ActionChoice from '@/services/action-choices'
import draggable from 'vuedraggable'
import ToggleCheckBox from '@thinknimble/togglecheckbox'

import SlackOAuth from '@/services/slack'
import { SObjectField } from '@/services/salesforce'

import * as FORM_CONSTS from '@/services/slack'
import { decryptData } from '../../encryption'

export default {
  name: 'SlackForm',
  components: {
    PulseLoadingSpinnerButton,
    draggable,
    ToggleCheckBox,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
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
    fromAdmin: {
      type: Boolean,
      default: false,
    },
    goBackAdmin: {
      type: Function,
      default: () => null,
    },
  },
  data() {
    return {
      dropdownLoading: false,
      currentStageForm: null,
      formFields: CollectionManager.create({
        ModelClass: SObjectField,
        pagination: { size: 200 },
      }),
      formFieldList: [],
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
      // requiredProductFields: ['PricebookEntryId', 'Quantity'],
      requiredOpportunityFields: ['Name', 'StageName', 'CloseDate'],
      requiredLeadFields: ['LastName', 'Company', 'Status'],
      nameValue: '',
      amountValue: '',
      closeValue: '',
      priceValue: '',
      quantityValue: '',
      lineValue: '',
      lastNameValue: '',
      leadLastNameValue: '',
      companyValue: '',
      accountNameValue: '',
      statusValue: '',
      stageValue: '',
      addingFieldValue: '',
      addingFields: false,
      productSelected: false,
      addingProducts: false,
      noteTitle: {
        _fields: {
          length: {
            defaultVal: null,
            readOnly: false,
          },
          id: {
            defaultVal: '',
            readOnly: true,
          },
          apiName: {
            defaultVal: '',
            readOnly: false,
          },
          custom: {
            defaultVal: false,
            readOnly: false,
          },
          createable: {
            defaultVal: false,
            readOnly: false,
          },
          dataType: {
            defaultVal: '',
            readOnly: false,
          },
          label: {
            defaultVal: '',
            readOnly: false,
          },
          reference: {
            defaultVal: '',
            readOnly: false,
          },
          referenceToInfos: {
            defaultVal: null,
            readOnly: false,
          },
          updateable: {
            defaultVal: false,
            readOnly: false,
          },
          required: {
            defaultVal: false,
            readOnly: false,
          },
          unique: {
            defaultVal: false,
            readOnly: false,
          },
          value: {
            defaultVal: '',
            readOnly: false,
          },
          displayValue: {
            defaultVal: '',
            readOnly: false,
          },
          referenceDisplayLabel: {
            defaultVal: '',
            readOnly: true,
          },
          filterable: {
            defaultVal: '',
            readOnly: true,
          },
          order: {
            defaultVal: null,
            readOnly: false,
          },
          includeInRecap: {
            defaultVal: null,
            readOnly: false,
          },
        },
        length: 30,
        id: '6407b7a1-a877-44e2-979d-1effafec5035',
        apiName: 'meeting_type',
        custom: true,
        createable: true,
        dataType: 'String',
        label: 'Note Subject',
        reference: 'false',
        referenceToInfos: [],
        updateable: true,
        required: false,
        unique: false,
        value: '',
        displayValue: '',
        referenceDisplayLabel: 'Note Subject',
        filterable: 'false',
        order: null,
        includeInRecap: null,
      },
      noteSubject: {
        _fields: {
          length: {
            defaultVal: null,
            readOnly: false,
          },
          id: {
            defaultVal: '',
            readOnly: true,
          },
          apiName: {
            defaultVal: '',
            readOnly: false,
          },
          custom: {
            defaultVal: false,
            readOnly: false,
          },
          createable: {
            defaultVal: false,
            readOnly: false,
          },
          dataType: {
            defaultVal: '',
            readOnly: false,
          },
          label: {
            defaultVal: '',
            readOnly: false,
          },
          reference: {
            defaultVal: '',
            readOnly: false,
          },
          referenceToInfos: {
            defaultVal: null,
            readOnly: false,
          },
          updateable: {
            defaultVal: false,
            readOnly: false,
          },
          required: {
            defaultVal: false,
            readOnly: false,
          },
          unique: {
            defaultVal: false,
            readOnly: false,
          },
          value: {
            defaultVal: '',
            readOnly: false,
          },
          displayValue: {
            defaultVal: '',
            readOnly: false,
          },
          referenceDisplayLabel: {
            defaultVal: '',
            readOnly: true,
          },
          filterable: {
            defaultVal: '',
            readOnly: true,
          },
          order: {
            defaultVal: null,
            readOnly: false,
          },
          includeInRecap: {
            defaultVal: null,
            readOnly: false,
          },
        },
        length: 255,
        id: '0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        apiName: 'meeting_comments',
        custom: true,
        createable: true,
        dataType: 'String',
        label: 'Notes',
        reference: 'false',
        referenceToInfos: [],
        updateable: true,
        required: false,
        unique: false,
        value: '',
        displayValue: '',
        referenceDisplayLabel: 'Notes',
        filterable: 'false',
        order: null,
        includeInRecap: null,
      },
    }
  },
  watch: {
    customForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.fields.length) {
          this.addedFields = [...val.fieldsRef]
          if (this.formType == 'UPDATE') {
            let currentFormFields = this.addedFields.map((field) => {
              return field.id
            })
            if (currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false) {
              let fieldsToAdd = [this.noteTitle, this.noteSubject]
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
    currentFields() {
      return this.customForm ? this.customForm.fields : []
    },
    addedFieldIds() {
      return this.addedFields.map((field) => {
        return field.id
      })
    },
    addedFieldNames() {
      return this.addedFields.map((field) => {
        return field.apiName
      })
    },
    addedFieldLabels() {
      return this.addedFields.map((field) => {
        return field.referenceDisplayLabel
      })
    },
    unshownIds() {
      return [
        '6407b7a1-a877-44e2-979d-1effafec5035',
        '0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        'e286d1d5-5447-47e6-ad55-5f54fdd2b00d',
        'fae88a10-53cc-470e-86ec-32376c041893',
      ]
    },
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    userHasProducts() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.organizationRef.hasProducts
    },
  },
  created() {
    this.getActionChoices()
  },
  methods: {
    test() {},
    lowerCase(word1, word2) {
      return (word1 + ' ' + word2)
        .toLowerCase()
        .split(' ')
        .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
        .join(' ')
    },
    productSelect() {
      this.productSelected = !this.productSelected
    },
    getActionChoices() {
      this.loadingMeetingTypes = true
      const action = ActionChoice.api
        .list({})
        .then((res) => {
          this.actionChoices = res.results
        })
        .finally((this.loadingMeetingTypes = false))
    },
    async onFieldsNextPage() {
      this.dropdownLoading = true
      await this.formFields.addNextPage().then(() => {
        setTimeout(() => {
          this.dropdownLoading = false
        }, 1000)
      })
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
      // this.formFields.filters = { salesforceObject: this.resource }
      // this.formFields.refresh()
    },
    goBack() {
      if (this.fromAdmin) {
        this.goBackAdmin()
      } else {
        this.$router.push({ name: 'Required' })
      }
    },
    goToUpdateOpp() {
      this.$router.push({ name: 'UpdateOpportunity' })
    },
    goToValidations() {
      this.$emit('cancel-selected')
    },
    onRemoveField(field) {
      // remove from the array if  it exists

      this.addedFields = [...this.addedFields.filter((f) => f.id != field.id)]

      // if it exists in the current fields add it to remove field

      if (~this.currentFields.findIndex((f) => f == field.id)) {
        this.removedFields = [this.removedFields, field]
      }
    },
    async onSave() {
      if (
        (this.resource == 'Opportunity' || this.resource == 'Account') &&
        this.customForm.formType == FORM_CONSTS.MEETING_REVIEW
      ) {
        if (!this.meetingType.length && !this.actionChoices.length) {
          this.$toast('Please enter a meeting type', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
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

          this.$emit('close-modal')
          this.$toast('Form added successfully', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        })
        .finally(() => {
          this.savingForm = false
          if (this.fromAdmin) {
            this.$router.push({ name: 'Staff' })
          }
          this.$router.go()
        })
    },
    async goToProducts() {
      if (
        (this.resource == 'Opportunity' || this.resource == 'Account') &&
        this.customForm.formType == FORM_CONSTS.MEETING_REVIEW
      ) {
        if (!this.meetingType.length && !this.actionChoices.length) {
          this.$toast('Please enter a meeting type', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          return
        }
      }
      this.savingForm = true

      let fields = new Set([...this.addedFields.map((f) => f.id)])
      fields = Array.from(fields).filter((f) => !this.removedFields.map((f) => f.id).includes(f))
      let fields_ref = this.addedFields.filter((f) => fields.includes(f.id))

      try {
        const res = await SlackOAuth.api.postOrgCustomForm({
          ...this.customForm,
          fields: fields,
          removedFields: this.removedFields,
          fields_ref: fields_ref,
        })
        this.$emit('update:selectedForm', res)
        this.$store.dispatch('refreshCurrentUser')
        this.$toast('Form added successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.savingForm = false
        if (this.fromAdmin && this.formType !== 'UPDATE') {
          this.$router.push({ name: 'Staff' })
        } else {
          this.$router.push({ name: 'ProductForm' })
        }
      } catch (e) {
        console.log('error', e)
        this.$toast('Form submission failed', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.savingForm = false
      }
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

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.section-title {
  letter-spacing: 0.75px;
  font-size: 18px;
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
.invert {
  filter: invert(80%);
  height: 1rem;
}
.invert2 {
  filter: invert(80%);
}
.label {
  font-size: 0.85rem;
}
.green {
  color: $dark-green;
  font-size: 0.85rem;
}
.default_button {
  @include white-button();
  padding: 0.5rem 1rem;
  margin-top: 0.5rem;

  img {
    height: 0.75rem;
    filter: invert(39%) sepia(96%) saturate(373%) hue-rotate(94deg) brightness(75%) contrast(94%);
  }
}
.recommend {
  position: absolute;
  bottom: 20vh;
  left: 34vw;
  z-index: 5;
  background-color: white;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
  box-shadow: 1px 2px 2px $very-light-gray;
  height: 40vh;
  width: 30vw;
  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid #e8e8e8;
    height: 4rem;
    padding: 1rem;

    letter-spacing: 0.5px;
    img {
      height: 1rem;
      filter: invert(30%);
    }
  }

  &__body {
    height: 5rem;
    display: flex;
    align-items: flex-start;
    justify-content: space-evenly;
    flex-direction: row;
    margin-top: -0.5rem;
    font-size: 14px;
    padding: 0.5rem;
  }
}
.drop {
  border: 2px solid $soft-gray;
  border-radius: 0.25rem;
  color: $very-light-gray;
  padding: 0.25rem 0.5rem;
  max-height: 2rem;
}
.invisible {
  display: none;
}
.white-background {
  background-color: white;
  border-radius: 0.25rem;
  height: 1.7rem;
  width: 1.7rem;
  margin-right: 0.25rem;
}
#drag {
  filter: invert(60%);
}
#remove {
  filter: invert(40%);
}
.drag-item {
  display: flex;
  align-items: center;
  flex-direction: row;
  padding: 0.2rem 0rem;
  border-radius: 0.2rem;
}
.center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 0.85rem;
}
.centered {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
}

.slack-form-builder {
  padding: 0rem 2rem;
  color: $base-gray;
  letter-spacing: 0.75px;
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
.primary-button {
  padding: 0.4rem 1.5rem;
  box-shadow: none;
  font-weight: 400;
}
.primary-button:disabled {
  background-color: $soft-gray;
}
img:hover {
  cursor: pointer;
}
.close {
  padding: 0.5rem 1.5rem;
  background: transparent;
  color: $very-light-gray;
  border: 2px solid $soft-gray;
  border-radius: 0.25rem;
  opacity: 0.8;
}
.save {
  @include primary-button();
  padding: 0.6rem 1.5rem;
  margin-left: 0.5rem;
}
.disabled {
  padding: 0.5rem 1rem;
  min-width: 6rem;
  background-color: $soft-gray;
  color: $base-gray;
  border: none;
  border-radius: 0.25rem;
  margin-left: 0.5rem;
  opacity: 0.8;
  cursor: text;
}
.disabled__ {
  background-color: transparent;
  font-size: 14px;
  color: $dark-green;
  border: none;
  letter-spacing: 1px;
  cursor: pointer;
}
.example--footer {
  position: sticky;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  margin-top: auto;
  margin-right: -16px;
  bottom: 0;
  padding: 8px 0px;
  background-color: white;

  z-index: 2;
}
.example-text {
  position: absolute;
  bottom: 180px;
  left: 50px;
  opacity: 0.1;
  filter: alpha(opacity=50);
  font-size: 3.5rem;
  transform: rotate(-45deg);
}
.collection_fields {
  background-color: $white;
  padding: 0rem 2rem;
  margin: 1rem 0;
  border-radius: 0.3rem;
  //   border: 1px solid #e8e8e8;
  overflow: auto;
  height: 72vh;
  width: 42vw;
  display: flex;
  flex-direction: column;
  position: relative;
}
.stage_fields {
  background-color: $white;
  padding: 3rem 1rem;
  margin: -1.5rem 1rem 0rem 0rem;
  border-radius: 0.5rem;
  height: 74vh;
  width: 36vw;
  overflow-y: scroll;
  display: flex;
  flex-direction: column;
  position: relative;
  border: 1px solid #e8e8e8;
}
.opportunity__row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}
.row__ {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}
.drop-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
</style>