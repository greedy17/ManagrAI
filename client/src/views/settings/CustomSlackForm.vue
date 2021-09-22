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
      <div class="opportunity__column">
        <div class="fields_title" style="text-align: center">1. Select your fields</div>

        <div class="collection_fields">
          <div>
            <p v-if="resource == OPPORTUNITY" class="popular_fields">
              These
              <span @click="$refs.modalName.openModal()" class="popularModal">fields</span> are the
              most popular
            </p>
            <p v-else-if="resource == CONTACT" class="popular_fields">
              These
              <span @click="$refs.ContactModal.openModal()" class="popularModal">fields</span> are
              the most popular
            </p>
            <p v-else-if="resource == ACCOUNT" class="popular_fields">
              These
              <span @click="$refs.AccountModal.openModal()" class="popularModal">fields</span> are
              the most popular
            </p>
            <p v-else class="popular_fields">
              These
              <span @click="$refs.LeadModal.openModal()" class="popularModal">fields</span> are the
              most popular
            </p>
          </div>
          <CollectionSearch
            :collection="formFields"
            itemDisplayKey="referenceDisplayLabel"
            :showSubmitBtn="false"
            @onClickItem="
              (e) => {
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
                <div class="slack-form-builder__sf-field">
                  {{ result['referenceDisplayLabel'] }}
                </div>
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
      </div>

      <div class="opportunity__column" v-if="customForm">
        <div class="fields_title" style="text-align: center">2. Re-order</div>
        <div class="slack-form-builder__form">
          <div class="slack-form-builder__form-meta" v-if="customForm.stage">
            <h5>Previous stage specific forms</h5>
            <small v-if="!orderedStageForm.length"> This is your first stage specific form </small>

            <div :key="key" v-for="(form, key) in orderedStageForm">
              <div style="margin-top: 1rem">
                <i style="text-transform: uppercase; font-size: 12px"
                  >Fields from <strong>{{ form.stage }}</strong> stage</i
                >
              </div>
              <div class="stages-list">
                <ListContainer horizontal>
                  <template v-slot:list>
                    <ListItem
                      @item-selected="onAddField(val)"
                      :key="key"
                      v-for="(val, key) in form.fieldsRef"
                      :item="val.referenceDisplayLabel"
                      :active="addedFieldIds.includes(val.id)"
                      showIcon
                    />
                  </template>
                </ListContainer>
              </div>
            </div>
          </div>

          <!-- <div v-if="customForm.formType == 'CREATE' || customForm.stage" class="recap">
            <h5>Include in recap</h5>
          </div> -->

          <h2 style="text-align: center; margin-bottom: 1rem">Slack form</h2>

          <div v-for="(field, index) in [...addedFields]" :key="field.apiName" class="form-field">
            <!-- <div
              v-if="
                field.id === '6407b7a1-a877-44e2-979d-1effafec5035' ||
                field.id === '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' ||
                field.id === 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d' ||
                field.id === 'fae88a10-53cc-470e-86ec-32376c041893'
              "
              class="form-field__label"
            >
              {{ field.referenceDisplayLabel }}
            </div> -->
            <div style="display: flex; width: 100%">
              <div class="form-field__left">
                <!-- <div
                  v-if="field.id === '6407b7a1-a877-44e2-979d-1effafec5035'"
                  class="form-field__body"
                >
                  {{
                    "This logs the type of meeting you’ve had, ie 'Discovery Call, Follow Up, etc.'"
                  }}
                </div>

                <div
                  v-if="field.id === '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'"
                  class="form-field__body"
                >
                  {{ 'Logs the rep’s comments about the meeting' }}
                </div>

                <div
                  v-if="field.id === 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d'"
                  class="form-field__body"
                >
                  {{ 'Gives the reps the option to send a recap to leadership' }}
                </div>
                <div
                  v-if="field.id === 'fae88a10-53cc-470e-86ec-32376c041893'"
                  class="form-field__body"
                >
                  {{ 'Gives the reps the option to send themselves a recap' }}
                </div> -->
                <img
                  v-if="canRemoveField(field)"
                  style="height: 1rem; margin-right: 0.5rem"
                  src="@/assets/images/remove.png"
                  @click="() => onRemoveField(field)"
                />

                <div
                  class="form-field__label"
                  v-if="
                    field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                    field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' &&
                    field.id !== 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d' &&
                    field.id !== 'fae88a10-53cc-470e-86ec-32376c041893' &&
                    field.id !== 'fd4207a6-fec0-4f0b-9ce1-6aaec31d39ed'
                  "
                >
                  {{ field.referenceDisplayLabel }}
                </div>
              </div>

              <div class="form-field__middle orange">
                {{ field.required ? 'required' : '' }}
              </div>
              <div class="form-field__right">
                <div
                  v-if="
                    field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                    field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' &&
                    field.id !== 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d' &&
                    field.id !== 'fae88a10-53cc-470e-86ec-32376c041893' &&
                    field.id !== 'fd4207a6-fec0-4f0b-9ce1-6aaec31d39ed'
                  "
                  class="form-field__btn"
                  @click="() => onMoveFieldUp(field, index)"
                >
                  <img src="@/assets/images/upArrow.png" />
                </div>
                <div
                  v-if="
                    field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                    field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' &&
                    field.id !== 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d' &&
                    field.id !== 'fae88a10-53cc-470e-86ec-32376c041893' &&
                    field.id !== 'fd4207a6-fec0-4f0b-9ce1-6aaec31d39ed'
                  "
                  class="form-field__btn"
                  @click="() => onMoveFieldDown(field, index)"
                >
                  <img src="@/assets/images/downArrow.png" />
                </div>
                <!-- <div
                  v-if="
                    customForm.formType == 'CREATE' ||
                    customForm.formType == 'MEETING_REVIEW' ||
                    customForm.stage
                  "
                  class="form-field__right"
                  @click="field.includeInRecap = !field.includeInRecap"
                >
                  <CheckBox :checked="field.includeInRecap" />
                  <h5 class="space">
                    <small
                      ><i>{{
                        customForm.stage ? ' (only available for create forms)' : ''
                      }}</i></small
                    >
                  </h5>
                </div> -->
              </div>
            </div>
            <div style="display: flex; align-items: center">
              <input
                v-if="field.id === '6407b7a1-a877-44e2-979d-1effafec5035'"
                placeholder="Enter Meeting Type"
                class="meeting-type"
                v-model="meetingType"
                @keypress="updateMeeting"
              />
              <small v-if="meetingType.length" style="margin-left: 1rem">Press Enter to Save</small>
            </div>

            <div
              v-if="field.id === '6407b7a1-a877-44e2-979d-1effafec5035' && actionChoices.length"
              class="meeting-type__list"
            >
              <template v-if="!loadingMeetingTypes">
                <ListContainer horizontal>
                  <template v-slot:list>
                    <ListItem
                      @item-selected="removeMeetingType(val.id)"
                      :key="key"
                      v-for="(val, key) in actionChoices"
                      :item="val.title"
                      :active="true"
                      showIcon
                    />
                  </template>
                </ListContainer>
              </template>
              <template v-else>
                <PulseLoadingSpinner :loading="loadingMeetingTypes" />
              </template>
            </div>
          </div>
        </div>
      </div>

      <div class="opportunity__column">
        <div class="fields_title" style="text-align: center">3. Save</div>

        <div class="collection_fields">
          <div class="save-button">
            <button @click="goToCustomize" class="back__button">
              <img src="@/assets/images/back.png" style="height: 1.2rem" alt="" />
              back
            </button>
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

          <!-- <div v-if="formType == 'UPDATE' && resource == OPPORTUNITY" class="save-button">
            <button @click="goToContacts" v-if="canContinue" class="continue__button">
              Continue
            </button>
            <button v-else class="cant__continue">Continue</button>
          </div> -->
          <div class="save-button" style="flex-direction: column; align-items: center">
            <button @click="goToCustomize" v-if="canContinue" class="continue__button">
              Continue
            </button>
            <button v-else class="cant__continue">Continue</button>
          </div>
        </div>
      </div>
      <!-- <div class="form-header">
          <div class="save-button">
            <PulseLoadingSpinnerButton
              @click="onSave"
              class="primary-button"
              text="Save"
              :loading="savingForm"
              :disabled="!$store.state.user.isAdmin"
            />
          </div>
          <div class="heading">
            <h2>
              {{ customForm.stage ? `${customForm.stage} Stage` : `${resource} Slack Form` }}
            </h2>
            <p class="muted">Add fields that you’d like to update using Slack</p>
          </div>
        </div> -->
      <!-- <div>
          <div class="save-button">
          <PulseLoadingSpinnerButton
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
            :disabled="!$store.state.user.isAdmin"
          />
        </div> -->
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
    width: 24vw;
    padding: 2rem;
    box-shadow: 0 5px 10px 0 rgba(132, 132, 132, 0.26);
    background-color: $panther;
    height: 50vh;
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
  padding: 1rem;
  border-radius: 0.5rem;
  height: 50vh;
  width: 22vw;
  overflow-y: scroll;
  overflow-x: hidden;
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
  width: 4px;
}
::-webkit-scrollbar-thumb {
  border-radius: 2px;
  background-color: $panther-silver;
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
