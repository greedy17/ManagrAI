<template>
  <div class="slack-form-builder">
    <Modal v-if="customObjectModalView" dimmed>
      <div class="opp-modal-container">
        <div v-if="modalLoading">
          <Loader :loaderText="loaderText" />
        </div>
        <div v-else>
          <div class="flex-row-spread header">
            <div class="flex-row">
              <img src="@/assets/images/logo.png" class="logo" height="26px" alt="" />
              <h3>Add Custom Object</h3>
            </div>
            <img
              src="@/assets/images/close.svg"
              style="height: 1.25rem; margin-top: -1rem; margin-right: 0.75rem; cursor: pointer"
              @click="toggleCustomObjectModalView"
              alt=""
            />
          </div>
          <div class="opp-modal">
            <section>
              <div style="display: flex; justify-content: center">
                <Multiselect
                  @input="getCustomObjectFields"
                  :options="customObjects"
                  openDirection="below"
                  style="width: 94%; margin-left: 1rem"
                  :max-height="400"
                  selectLabel="Enter"
                  :track-by="userCRM === 'HUBSPOT' ? 'label' : 'name'"
                  :customLabel="customLabel"
                  v-model="selectedCustomObject" 
                  class="custom-picklist-font"
                >
                  <template slot="noResult">
                    <p class="multi-slot custom-picklist-font">No results.</p>
                  </template>

                  <template slot="placeholder">
                    <p class="slot-icon custom-picklist-font">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Custom Object
                    </p>
                  </template>

                  <template slot="option" slot-scope="props">
                    <div>
                      <span class="option__title">{{ removeAmp(props.option.label) }}</span
                      ><span
                        v-if="currentStagesWithForms.includes(props.option.label)"
                        class="option__small"
                      >
                        edit
                      </span>
                    </div>
                  </template>
                </Multiselect>
              </div>
            </section>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="modalOpen">
      <div class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/warning.svg" class="logo2" alt="" />
            <p>Switching forms. Changes wont be saved!</p>
          </div>
        </div>
        <section class="modal-buttons">
          <div class="">
            <button @click="closeModal" class="cancel">Discard</button>
          </div>
          <div class="">
            <button @click="modalSave" class="save">Save</button>
          </div>
        </section>
      </div>
    </Modal>
    <!-- <Modal v-if="confirmDeleteModal">
      <div class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/warning.svg" class="logo2" alt="" />
            <p>Would you like to delete this stage form?</p>
          </div>
        </div>
        <section class="modal-buttons">
          <div class="">
            <button @click="closeDeleteModal" class="cancel">Cancel</button>
          </div>
          <div class="">
            <button @click="deleteForm(activeForm)" class="save">Delete</button>
          </div>
        </section>
      </div>
    </Modal> -->
    <Modal v-if="confirmCODeleteModal">
      <div class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/warning.svg" class="logo2" alt="" />
            <p>Would you like to delete this form?</p>
          </div>
        </div>
        <section class="modal-buttons">
          <div class="">
            <button @click="closeDeleteModal" class="cancel">Cancel</button>
          </div>
          <div class="">
            <button @click="deleteForm(newCustomForm)" class="save">Delete</button>
          </div>
        </section>
      </div>
    </Modal>
    <Modal
      v-if="confirmDeleteModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), closeDeleteModal()
        }
      "
    >
    <!-- modal-form confirm-form -->
      <form v-if="true /*hasSlack*/" class="invite-form crm-form form-margin-small" style="height: 25vh;">
        <div class="header-crm">
          <div class="flex-row-wrapper inner-crm">
            <div class="flex-row-modal" style="margin: 0;">
              <!-- <img src="@/assets/images/logo.png" class="logo" alt="" /> -->
              <h3 class="invite-form__title">Are you sure?</h3>
            </div>
            <div class="flex-row-modal" style="margin: 0;">
              <img
                @click="closeDeleteModal"
                src="@/assets/images/close.svg"
                alt=""
                style="
                  filter: invert(30%);
                  cursor: pointer;
                  width: 20px;
                  height: 20px;
                  margin-right: 5px;
                "
              />
            </div>
          </div>
        </div>
        <div class="flex-row-modal inner-crm" style="margin: 0; justify-content: flex-start; width: 90%;">
          <h4 class="card-text" style="margin-left: 0; margin-top: 0; margin-bottom: 0.75rem;">
            By clicking Delete, you will be removing 
            {{ this.activeForm ? `your ${this.activeForm.stage} form` : 'this form' }}.
          </h4>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="confirm-cancel-container" style="width: 90%; margin-bottom: 0.6rem;">
            <div class="img-border-modal cancel-button" @click="closeDeleteModal" style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem;">
              Cancel
            </div>
            <button class="img-border-modal red-button" @click="deleteForm(activeForm)" style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 0rem; margin-right: 5%;">
              Delete
            </button>
          </div>
          <!-- <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="onRevoke(removeApp)"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Confirm"
                :loading="pulseLoading"
                >Confirm</PulseLoadingSpinnerButton
              >
            </template>
          </div> -->
        </div>
      </form>
    </Modal>

    <!-- <div class="alerts-header">
      <section class="row__" style="gap: 0px">
        <h3>Field Mapping</h3>
        <div class="side-wrapper">
          <label class="side-icon side-workflow" style="margin-top: 0">
            <span class="side-tooltip">{{
              user.crm === 'SALESFORCE'
                ? `Select the Salesforce fields you'd like to update using Managr.`
                : `Select the HubSpot properties you'd like to update using Managr.`
            }}</span>
            <span>?</span>
          </label>
        </div>
      </section>
      <div class="save-refresh-section">
        <button v-if="!pulseLoading" class="img-button img-border" @click="refreshForms">
          <img src="@/assets/images/refresh.svg" />
        </button>
        <PulseLoadingSpinnerButton
          v-else
          @click="refreshForms"
          class="img-button"
          text="Refresh"
          :loading="pulseLoading"
          ><img src="@/assets/images/refresh.svg"
        /></PulseLoadingSpinnerButton>
        <button @click="onSave" class="save">Save Form</button>
      </div>
    </div> -->
    <div class="fields-container">
      <div class="row__ border-bottom-top" style="margin: 1rem 1.5rem 0 2rem; padding-bottom: 0;">
        <!-- :style="user.crm === 'SALESFORCE' ? 'justify-content: space-between;' : 'justify-content: space-around;'" -->
        <div class="display-flex">
          <div v-for="object in resources" :key="object.value" class="small-margin-right">
            <h4
              :class="selectedObject.label === object.label ? 'header-text green-highlight cursor' : 'header-text cursor'"
              @click="clickChangeObject(object.label, object.value)"
              style="margin-bottom: 0; padding-bottom: 0.75rem"
            >
              {{ object.label }}
            </h4>
          </div>
        </div>
        <div class="save-refresh-section">
          <button v-if="!pulseLoading" class="img-button img-border" style="padding: 0.5rem 0.5rem;" @click="refreshForms">
            <img src="@/assets/images/cycle.svg" class="refresh-button" style="height: 13px;" />
          </button>
          <PulseLoadingSpinnerButton
            v-else
            @click="refreshForms"
            class="img-button"
            text="Refresh"
            :loading="pulseLoading"
            ><img src="@/assets/images/cycle.svg"
          /></PulseLoadingSpinnerButton>
          <button @click="onSave" class="save">Save Form</button>
        </div>
      </div>
      <div class="row__" style="justify-content: space-between">
        <section
          v-if="
            newResource &&
            (selectedType && selectedType.value === 'STAGE_GATING' ? currentlySelectedStage : true)
          "
          style="margin-left: 1rem; width: 23.5vw"
        >
          <div
            v-if="selectedObject"
            class="row__"
            style="margin: 0"
          >
            <div style="display: flex; flex-direction: column">
              <div v-if="selectedObject && selectedObject.value !== 'CustomObject'" class="half-view-flex" style="align-items: center; margin-top: 1rem;">
                <div class="row__" style="gap: 6px; margin-left: 0;">
                  <div class="header-text">View:</div>
                  <div class="gray-background">
                    <div class="toggle-update-create-container" :class="selectedType.value === 'UPDATE' ? 'active' : ''" @click="changeSelectedType({ value: 'UPDATE', label: 'Update' })">
                      <p>Update</p>
                    </div>
                    <div class="toggle-update-create-container" :class="selectedType.value === 'CREATE' ? 'active' : ''" @click="changeSelectedType({ value: 'CREATE', label: 'Create' })">
                      <p>Create</p>
                    </div>
                    <div class="toggle-update-create-container" :class="(selectedType.value !== 'UPDATE' && selectedType.value !== 'CREATE') ? 'active' : ''" v-if="selectedObject.value === 'Opportunity' || selectedObject.value === 'Deal'" @click="changeSelectedType({ value: 'STAGE', label: 'Stage' })">
                      <p>Stages</p>
                    </div>
                  </div>
                  <!-- <Multiselect
                    v-if="formattedTypes.length"
                    @input="changeObject(selectedObject, $event, false)"
                    :options="formattedTypes"
                    openDirection="below"
                    style="width: 11.5vw"
                    :showLabels="false"
                    track-by="label"
                    :customLabel="customLabelView"
                    v-model="selectedType"
                    class="multiselect-font custom-picklist-font"
                  >
                    <template slot="noResult">
                      <p class="multi-slot custom-picklist-font">No results.</p>
                    </template>
  
                    <template slot="placeholder">
                      <p class="slot-icon custom-picklist-font">
                        <img src="@/assets/images/search.svg" alt="" />
                        {{ selectedType && selectedType.label && selectedType.value !== 'UPDATE' && selectedType.value !== 'CREATE' ? selectedType.label : 'Select Type' }}
                      </p>
                    </template>
  
                    <template slot="option" slot-scope="props">
                      <div>
                        <span class="option__title">{{ removeAmp(props.option.label) }}</span
                        ><span
                          v-if="currentStagesWithForms.includes(props.option.label)"
                          class="option__small"
                        >
                          <img
                            class="green-check"
                            style=""
                            src="@/assets/images/configCheck.svg"
                            alt=""
                          />
                        </span>
                      </div>
                    </template>
                  </Multiselect> -->
                  <!-- <div class="wrapper">
                    <label
                      v-if="newResource === 'Deal' || newResource === 'Opportunity'"
                      class="icon workflow"
                      style="margin-top: 0"
                    >
                      <span class="tooltip"
                        >You can also add {{ user.crm === 'SALESFORCE' ? 'fields' : 'properties' }} to
                        Stages. These {{ user.crm === 'SALESFORCE' ? 'fields' : 'properties' }} will
                        appear as you move to the Stage.</span
                      >
                      <span>?</span>
                    </label>
                  </div> -->
                </div>
                <div style="display: flex; align-items: center;">
                  <button
                    v-if="
                      selectedType.value !== 'CREATE' &&
                      selectedType.value !== 'UPDATE' &&
                      addedFields.length &&
                      activeForm
                    "
                    @click="confirmDeleteModal = !confirmDeleteModal"
                    class="img-button"
                    style="padding: 0.5rem; margin: 0;"
                  >
                    <!-- Delete Form -->
                    <!-- <img src="@/assets/images/trash.svg" class="trash-button" /> -->
                    <img src="@/assets/images/chat-trash.svg" class="filtered-red" style="height: 14px" alt="" />
                  </button>
                </div>
              </div>
              <div v-else-if="selectedObject && selectedObject.value === 'CustomObject'" class="half-view-flex">
                <div v-if="modalLoading">
                  <Loader :loaderText="loaderText" />
                </div>
                <div v-else>
                  <div
                    v-if="createdCustomObjects.length"
                    style="margin-top: 1rem;"
                    class="half-view-flex"
                  >
                    <Multiselect
                      @input="getCreatedCO"
                      :options="createdCustomObjects"
                      openDirection="below"
                      style="width: 23.5vw; margin-left: 0rem"
                      selectLabel="Enter"
                      :track-by="userCRM === 'HUBSPOT' ? 'label' : 'name'"
                      label="name"
                      v-model="selectedCustomObject"
                      class="custom-picklist-font"
                    >
                      <template slot="noResult">
                        <p class="multi-slot custom-picklist-font">No results.</p>
                      </template>

                      <template slot="placeholder">
                        <p class="slot-icon custom-picklist-font">
                          <img src="@/assets/images/search.svg" alt="" />
                          Custom Object
                        </p>
                      </template>

                      <template slot="option" slot-scope="props">
                        <div>
                          <span class="option__title">{{ props.option.name }}</span>
                        </div>
                      </template>
                    </Multiselect>
                    <button v-if="!selectedCustomObject" @click="toggleCustomObjectModalView" class="custom-object-button">
                      Add Custom Object
                    </button>
                    <button v-else @click="confirmCODeleteModal = !confirmCODeleteModal" class="red-button" style="margin-top: 0">
                      Delete
                    </button>
                  </div>
                  <div v-else class="half-view-flex" style="margin-top: 1rem;">
                    <Multiselect
                      @input="getCustomObjectFields"
                      :options="customObjects"
                      openDirection="below"
                      style="width: 23.5vw; margin-left: 0rem"
                      :max-height="400"
                      selectLabel="Enter"
                      :track-by="userCRM === 'HUBSPOT' ? 'label' : 'name'"
                      :customLabel="customLabel"
                      v-model="selectedCustomObject"
                      class="custom-picklist-font"
                    >
                      <template slot="noResult">
                        <p class="multi-slot custom-picklist-font">No results.</p>
                      </template>

                      <template slot="placeholder">
                        <p class="slot-icon custom-picklist-font">
                          <img src="@/assets/images/search.svg" alt="" />
                          Custom Object
                        </p>
                      </template>

                      <template slot="option" slot-scope="props">
                        <div>
                          <span class="option__title">{{ removeAmp(props.option.label) }}</span
                          ><span
                            v-if="currentStagesWithForms.includes(props.option.label)"
                            class="option__small"
                          >
                            edit
                          </span>
                        </div>
                      </template>
                    </Multiselect>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="search-bar-container">
            <Multiselect
              v-if="formattedTypes.length && (selectedType.value !== 'CREATE' && selectedType.value !== 'UPDATE')"
              @input="changeObject(selectedObject, $event, false)"
              :options="formattedTypes"
              openDirection="below"
              style="width: 11.5vw"
              :showLabels="false"
              track-by="label"
              :customLabel="customLabelView"
              v-model="selectedType"
              class="multiselect-align custom-picklist-font"
            >
              <template slot="noResult">
                <p class="multi-slot custom-picklist-font">No results.</p>
              </template>
  
              <template slot="placeholder">
                <p class="slot-icon custom-picklist-font">
                  <img src="@/assets/images/search.svg" alt="" />
                  {{ selectedType && selectedType.label && selectedType.value !== 'UPDATE' && selectedType.value !== 'CREATE' && selectedType.value !== 'STAGE' ? selectedType.label : 'Select Type' }}
                </p>
              </template>
  
              <template slot="option" slot-scope="props">
                <div>
                  <span class="option__title">{{ removeAmp(props.option.label) }}</span
                  ><span
                    v-if="currentStagesWithForms.includes(props.option.label)"
                    class="option__small"
                  >
                    <img
                      class="green-check"
                      style=""
                      src="@/assets/images/configCheck.svg"
                      alt=""
                    />
                  </span>
                </div>
              </template>
            </Multiselect>
            <div v-else class="choose-fields-container">
              <h5>Choose CRM fields:</h5>
              <div class="wrapper">
                <label
                  class="icon workflow"
                  style="margin-top: 0"
                >
                  <!-- <span class="tooltip"
                    >You can also add {{ user.crm === 'SALESFORCE' ? 'fields' : 'properties' }} to
                    Stages. These {{ user.crm === 'SALESFORCE' ? 'fields' : 'properties' }} will
                    appear as you move to the Stage.</span
                  > -->
                  <span class="tooltip">
                    <!-- Select the fields you'd like to interact with.  -->
                    We recommend: Name, Stage,
                    Forecast, Close Date, Next Step, Next Step Date, along with MEDDICC / BANT
                    fields.
                  </span>
                  <span>?</span>
                </label>
              </div>
            </div>
            <div class="search-bar">
              <img class="search" src="@/assets/images/search.svg" />
              <input
                @input="searchFields"
                type="search"
                :placeholder="`Search`"
                v-model="filterText"
              />
            </div>
          </div>

          <div class="field-section__fields">
            <div>
              <p v-for="(field, i) in filteredFields" :key="field.id" :title="field.label" class="light-gray-blue">
                <input @click="onAddField(field)" type="checkbox" :id="i" :value="field" />
                <label :for="i"></label>
                {{
                  field.label == 'Price Book Entry ID'
                    ? 'Products'
                    : truncate(removeAmp(field.label), 38)
                }}
              </p>
            </div>
          </div>
        </section>
        <section v-else>
          <div v-if="selectedCustomObjectName">
            <div class="search-bar">
              <input
                type="search"
                :placeholder="`Search ${selectedCustomObjectName} Fields`"
                v-model="COfilterText"
              />
            </div>

            <div class="field-section__fields">
              <div>
                <p v-if="!COfilteredFields.length && createdCustomFields">
                  Fields still syncing...
                </p>
                <p
                  v-else-if="COfilteredFields.length"
                  v-for="(field, i) in COfilteredFields"
                  :key="field.id"
                >
                  <input @click="onAddField(field)" type="checkbox" :id="i" :value="field" />
                  <label :for="i"></label>
                  {{ removeAmp(field.label) }}
                  <span v-if="field.required" class="red-text">required</span>
                </p>
                <p v-else>Nothing here. Try selecting an object</p>
              </div>
            </div>
          </div>

          <div v-else>
            <div class="search-bar">
              <input type="search" placeholder="Search Object Fields" />
            </div>

            <div class="field-section__fields">
              <div>
                <p v-if="createdCustomFields">Fields still syncing...</p>
                <p v-else>Nothing here. Try selecting an object</p>
              </div>
            </div>
          </div>
        </section>
        <div class="selected-container">
          <h5>Selected CRM Fields:</h5>
          <div class="selected" style="margin-left: 1rem">
            <draggable
              v-model="addedFields"
              group="fields"
              @start="drag = true"
              @end="drag = false"
              class="drag-section"
              v-if="selectedType.value !== 'STAGE_GATING' || currentlySelectedStage"
            >
              <div v-for="field in addedFields" :key="field.id">
                <div v-if="!unshownIds.includes(field.id)">
                  <div class="drag-item">
                    <div class="drag-item-left">
                      <img src="@/assets/images/drag.svg" height="16px" alt="" />
                      <p id="formField" :title="field.label">
                        {{ truncate(field.label, 38) }}
                      </p>
                    </div>
                    <div class="drag-item-right">
                      <span
                        alt=""
                        id="remove"
                        @click="
                          () => {
                            onRemoveField(field)
                          }
                        "
                        >x</span
                      >
                    </div>
                  </div>
                </div>
              </div>
            </draggable>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

import { CollectionManager } from '@thinknimble/tn-models'

import Modal from '@/components/InviteModal'
import AlertsHeader from '@/components/AlertsHeader.vue'

import ActionChoice from '@/services/action-choices'
import draggable from 'vuedraggable'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import { mapState } from 'vuex'

import SlackOAuth from '@/services/slack'
import { SObjectPicklist } from '@/services/salesforce'
import { ObjectField } from '@/services/crm'
import * as FORM_CONSTS from '@/services/slack'
import { SObjects } from '@/services/salesforce'

export default {
  name: 'ConfigureForms',
  components: {
    PulseLoadingSpinnerButton,
    Modal,
    draggable,
    ToggleCheckBox,
    AlertsHeader,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
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
      default: false,
    },
    resource: {
      type: String,
      required: true,
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
    fromAdmin: {
      type: Boolean,
      default: false,
    },
    goBackAdmin: {
      type: Function,
      default: () => null,
    },
    updateAllForms: {
      type: Function
    }
  },
  data() {
    return {
      activeForm: null,
      currentlySelectedForm: null,
      customObjects: [],
      createdCustomObjects: [],
      pulseLoading: false,
      loaderTextList: ['Gathering your Fields...', 'Syncing with Object...', 'Syncing fields...'],
      selectedCustomObject: null,
      selectedCustomObjectName: null,
      currentlySelectedStage: null,
      currentlySelectedCO: null,
      selectedForm: null,
      selectedStage: null,
      allForms: [],
      filterText: '',
      COfilterText: '',
      createdCustomFields: false,
      newCustomObject: false,
      modalLoading: false,
      loaderText: '',
      formFields: CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 500 },
        filters: {
          crmObject: this.newResource,
        },
      }),
      tabs: [],
      customFields: null,
      newFormType: this.formType,
      newResource: this.resource,
      customResource: null,
      removeCustomObj: false,
      newCustomForm: this.customForm,
      savingForm: false,
      addedFields: [],
      removedFields: [],
      ...FORM_CONSTS,
      meetingType: '',
      actionChoices: [],
      loadingMeetingTypes: false,
      customObjectView: false,
      customObjectModalView: false,
      confirmDeleteModal: false,
      confirmCODeleteModal: false,
      modalOpen: false,
      formChange: false,
      storedField: null,
      formStages: [],
      stages: [],
      timeout: null,
      selectedObject: { label: 'Opportunity', value: 'Opportunity' },
      selectedType: { value: 'UPDATE', label: 'Update' },
      resources: [],
      types: [
        // { value: 'UPDATE', label: 'Update' },
        // { value: 'CREATE', label: 'Create' },
      ],
      formattedTypes: [
        // { value: 'UPDATE', label: 'Update' },
        // { value: 'CREATE', label: 'Create' },
      ],
      oppTypes: [
        { value: 'UPDATE', label: 'Update' },
        { value: 'CREATE', label: 'Create' },
        { value: 'STAGE_GATING', label: 'Stage Gating' },
      ],
      oppLineItemType: [{ value: 'CREATE', label: 'Create' }],
      storedModalFunction: () => null,
      storedModalVariables: {},
      noteTitle: {
        model: 'crm.ObjectField',
        id: '6407b7a1-a877-44e2-979d-1effafec5034', // '6407b7a1-a877-44e2-979d-1effafec5035'
        includeInRecap: true,
        apiName: 'meeting_type',
        createable: true,
        required: false,
        updateable: true,
        dataType: 'String',
        displayValue: '',
        label: 'Note Subject',
        reference: false,
        referenceToInfos: [],
        relationshipName: null,
        options: [],
        length: 0,
        isPublic: true,
        filterable: true,
        datetimeCreated: '2020-08-03 11:39:23.632256Z',
        lastEdited: '2020-08-03 11:39:23.632256Z',
      },
      noteTitleHubspot: {
        model: 'crm.ObjectField',
        id: '6407b7a1-a877-44e2-979d-1effafec5034', //'6407b7a1-a877-44e2-979d-1effafec5035',
        includeInRecap: true,
        apiName: 'meeting_type',
        createable: true,
        required: false,
        updateable: true,
        dataType: 'String',
        displayValue: '',
        label: 'Note Subject',
        reference: false,
        referenceToInfos: [],
        relationshipName: null,
        options: [],
        length: 0,
        isPublic: true,
        filterable: true,
        datetimeCreated: '2020-08-03 11:39:23.632256Z',
        lastEdited: '2020-08-03 11:39:23.632256Z',
      },
      noteSubject: {
        model: 'crm.ObjectField',
        id: '0bb152b5-aac1-4ee0-9c25-51ae98d55af2', // '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
        includeInRecap: true,
        apiName: 'meeting_comments',
        createable: true,
        updateable: true,
        required: false,
        dataType: 'String',
        displayValue: '',
        label: 'Notes',
        reference: false,
        referenceToInfos: [],
        relationshipName: null,
        options: [],
        length: 255,
        isPublic: true,
        filterable: true,
        datetimeCreated: '2020-08-03 11:39:23.632256Z',
        lastEdited: '2020-08-03 11:39:23.632256Z',
      },
      noteSubjectHubspot: {
        model: 'crm.ObjectField',
        id: '0bb152b5-aac1-4ee0-9c25-51ae98d55af2', //'0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        includeInRecap: true,
        apiName: 'meeting_comments',
        createable: true,
        updateable: true,
        required: false,
        dataType: 'String',
        displayValue: '',
        label: 'Notes',
        reference: false,
        referenceToInfos: [],
        relationshipName: null,
        options: [],
        length: 255,
        isPublic: true,
        filterable: true,
        datetimeCreated: '2020-08-03 11:39:23.632256Z',
        lastEdited: '2020-08-03 11:39:23.632256Z',
      },
    }
  },
  watch: {
    selectedStage: 'setNewForm',
    selectedForm: 'setCustomForm',
    task: 'checkAndClearInterval',
    customResource: 'watcherCustomResource',
    formFields: 'watcherCustomResource',
    customForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.customFields.length) {
          this.addedFields = [...val.fieldsRef]
          if (this.formType == 'UPDATE') {
            let currentFormFields = this.addedFields.map((field) => {
              return field.id
            })
            if (
              currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false &&
              currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5034') == false
            ) {
              let fieldsToAdd =
                this.userCRM === 'SALESFORCE'
                  ? [this.noteTitle, this.noteSubject]
                  : [this.noteTitleHubspot, this.noteSubjectHubspot]
              let copyArray = this.addedFields
              fieldsToAdd = fieldsToAdd.concat(copyArray)
              this.addedFields = fieldsToAdd.map((field, i) => {
                let altField = { ...field }
                altField.order = i
                if (
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5034' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' ||
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af2'
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
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5034' &&
                field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' &&
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                field.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af2'
              )
            })
          }
        } else if (val && val.formType == 'STAGE_GATING' && !val.customFields.length) {
          this.addedFields = []
        }
      },
    },

    newCustomForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.customFields.length && !this.removeCustomObj) {
          this.addedFields = [...val.fieldsRef]
          if (this.newFormType == 'UPDATE') {
            let currentFormFields = this.addedFields.map((field) => {
              return field.id
            })
            if (
              currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false &&
              currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5034') == false
            ) {
              let fieldsToAdd =
                this.userCRM === 'SALESFORCE'
                  ? [this.noteTitle, this.noteSubject]
                  : [this.noteTitleHubspot, this.noteSubjectHubspot]
              let copyArray = this.addedFields
              fieldsToAdd = fieldsToAdd.concat(copyArray)
              this.addedFields = fieldsToAdd.map((field, i) => {
                let altField = { ...field }
                altField.order = i
                if (
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5034' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' ||
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af2'
                ) {
                  altField.includeInRecap = true
                }
                return altField
              })
            }
          }
          if (this.newFormType !== 'UPDATE') {
            this.addedFields = this.addedFields.filter((field) => {
              return (
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5034' &&
                field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1' &&
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af2'
              )
            })
          }
        } else if (val && !val.customFields.length) {
          this.addedFields = []
        } else {
          this.addedFields = []
        }
        this.removeCustomObj = false
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
                crmObject: val,
                ...fieldParam,
              }
              this.formFields.refresh()
              if (this.formType == 'UPDATE') {
                // this.onSave()
              }
            } catch (e) {
              console.log(e)
            }
          }
        }
      },
    },

    newResource: {
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
                crmObject: val,
                ...fieldParam,
              }
              this.formFields.refresh()
              if (this.formType == 'UPDATE') {
                // this.onSave()
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
                crmObject: this.resource,
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

    newFormType: {
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
                crmObject: this.newResource,
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
    ...mapState(['user']),
    currentStagesWithForms() {
      return this.formStages.map((sf) => sf.stage)
    },
    customForms() {
      return this.allForms.filter((form) => form.customObject)
    },
    filteredFields() {
      return this.formFields.list.filter((field) => !this.addedFieldNames.includes(field.apiName))
    },
    COfilteredFields() {
      if (!this.customFields) {
        return []
      }
      return this.customFields.list
        .filter(
          (field) =>
            field.referenceDisplayLabel.toLowerCase().includes(this.COfilterText.toLowerCase()) &&
            field.integrationSource === this.userCRM,
        )
        .filter((field) => !this.addedFieldNames.includes(field.apiName))
    },
    currentFields() {
      return this.customForm ? this.customForm.customFields : []
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
    unshownIds() {
      return [
        '6407b7a1-a877-44e2-979d-1effafec5035',
        '0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        '6407b7a1-a877-44e2-979d-1effafec5034',
        '0bb152b5-aac1-4ee0-9c25-51ae98d55af2',
        'e286d1d5-5447-47e6-ad55-5f54fdd2b00d',
        'fae88a10-53cc-470e-86ec-32376c041893',
      ]
    },
    opportunityClassLogic() {
      return this.newResource == 'Opportunity' && this.newFormType !== 'STAGE_GATING' && !this.customObjectView ? 'green' : ''
    },
    dealClassLogic() {
      return this.newResource == 'Deal' && this.newFormType !== 'STAGE_GATING' ? 'green' : ''
    },
    oppStageClassLogic() {
      return this.newResource == 'Opportunity' && this.newFormType == 'STAGE_GATING' && !this.customObjectView ? 'green' : ''
    },
    dealStageClassLogic() {
      return this.newResource == 'Deal' && this.newFormType == 'STAGE_GATING' ? 'green' : ''
    },
    accountClassLogic() {
      return this.newResource == 'Account' && !this.customObjectView ? 'green' : ''
    },
    companyClassLogic() {
      return this.newResource == 'Company' ? 'green' : ''
    },
    contactClassLogic() {
      return this.newResource == 'Contact' && !this.customObjectView ? 'green' : ''
    },
    hsContactClassLogic() {
      return this.newResource == 'Contact' ? 'green' : ''
    },
    leadClassLogic() {
      return this.newResource == 'Lead' && !this.customObjectView ? 'green' : ''
    },
    productClassLogic() {
      return this.newResource == 'OpportunityLineItem' && !this.customObjectView ? 'green' : ''
    },
    customObjectClassLogic() {
      return this.customObjectView ? 'green' : ''
    },
    user() {
      return this.$store.state.user
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    task() {
      return this.$store.state.customObject.task
    },
    checker() {
      return this.$store.state.customObject.task
    },
  },
  async created() {
    try {
      this.getActionChoices()
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      this.$store.commit('SAVE_CRM_FORMS', this.allForms)
      let object = this.userCRM === 'SALESFORCE' ? this.OPPORTUNITY : this.DEAL
      if (this.userCRM === 'SALESFORCE') {
        this.resources = [
          { value: 'Opportunity', label: 'Opportunity' },
          { value: 'Account', label: 'Account' },
          { value: 'Contact', label: 'Contact' },
          { value: 'Lead', label: 'Lead' },
          { value: 'OpportunityLineItem', label: 'Products' },
        ]
        if (this.user.organizationRef.isPaid) {
          this.resources.push({value: 'CustomObject', label: 'Custom Object'})
        }
      } else {
        this.resources = [
          { value: 'Deal', label: 'Deal' },
          { value: 'Company', label: 'Company' },
          { value: 'Contact', label: 'Contact' },
        ]
      }
      this.selectedObject = this.resources[0]
      this.newCustomForm = this.customForm
      await this.listPicklists({
        crmObject: object,
        picklistFor: this.userCRM === 'SALESFORCE' ? 'StageName' : 'dealstage',
      })
      if (this.userCRM == 'SALESFORCE') {
        this.getCustomObjects()
        this.tabs = [
          {
            name: 'Opportunity',
            classLogic: this.opportunityClassLogic,
            function: this.changeToOpportunity,
          },
          {
            name: 'Opp - Stage related',
            classLogic: this.oppStageClassLogic,
            function: this.changeToStage,
          },
          {
            name: 'Account',
            classLogic: this.accountClassLogic,
            function: this.changeToAccount,
          },
          {
            name: 'Contact',
            classLogic: this.contactClassLogic,
            function: this.changeToContact,
          },
          {
            name: 'Lead',
            classLogic: this.leadClassLogic,
            function: this.changeToLead,
          },
          {
            name: 'Products',
            classLogic: this.productClassLogic,
            function: this.changeToProducts,
          },
          {
            name: 'Custom Object',
            classLogic: this.customObjectClassLogic,
            function: this.toggleCustomObjectView,
          },
        ]
      }
      if (this.userCRM === 'HUBSPOT') {
        this.tabs = [
          {
            name: 'Deal',
            classLogic: this.dealClassLogic,
            function: this.changeToDeal,
          },
          {
            name: 'Deal - Stage related',
            classLogic: this.dealStageClassLogic,
            function: this.changeToStage,
          },
          {
            name: 'Account',
            classLogic: this.companyClassLogic,
            function: this.changeToCompany,
          },
          {
            name: 'Contact',
            classLogic: this.hsContactClassLogic,
            function: this.changeToContact,
          },
        ]
      }
    } catch (e) {
      console.log(e)
    }
    this.getStageForms()
    this.formattedTypes = [...this.types, ...this.stages]
    this.formattedTypes = this.formattedTypes.filter(f => f.value !== 'STAGE')
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    changeSelectedType(type) {
      if (type.value === 'STAGE') {
        if (this.formattedTypes[0]) {
          this.selectedType = this.formattedTypes[0]
        } else {
          this.selectedType = { value: 'UPDATE', label: 'Update' }
        }
      } else {
        this.selectedType = type
      }
      this.changeObject(this.selectedObject, this.selectedType)
    },
    customLabel(prop) {
      const label = prop.customObject ? `${prop.customObject}` : `${prop.label}`
      return label.replace('&amp;', '&')
    },
    truncate(text, max) {
      return `${text.slice(0, max)} ${text.length > max ? '...' : ''}`
    },
    removeAmp(label) {
      return label.replace('&amp;', '&')
      // Global Term Line Item Recurring Billing
    },
    clickChangeObject(label, value) {
      this.selectedObject = { label, value }
      this.changeObject(this.selectedObject, this.selectedType)
      if (this.selectedObject.value === 'Opportunity' || this.selectedObject.value === 'Deal') {
        this.formattedTypes = [...this.types, ...this.stages]
        this.formattedTypes = this.formattedTypes.filter(f => f.value !== 'STAGE')
      } else if (this.selectedObject.label === 'Products') {
        this.formattedTypes = [
          // { value: 'CREATE', label: 'Create' }
        ]
      } else {
        this.formattedTypes = [
          // { value: 'UPDATE', label: 'Update' },
          // { value: 'CREATE', label: 'Create' },
        ]
      }
      if (this.selectedType.label !== 'Create' && this.selectedType.label !== 'Update') {
        this.selectedType = this.formattedTypes[1]
      }
      this.selectedCustomObject = null
    },
    searchFields() {
      let fieldParam = {}

      if (this.newFormType == 'CREATE') {
        fieldParam['createable'] = true
      } else if (this.newFormType == 'UPDATE') {
        fieldParam['updateable'] = true
      }

      this.formFields = CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 500 },
        filters: {
          crmObject: this.newResource,
          search: this.filterText,
          ...fieldParam,
        },
      })
    },
    async refreshForms() {
      this.pulseLoading = true
      const res = await SlackOAuth.api.refreshForms()
      setTimeout(() => {
        this.pulseLoading = false
        this.$router.go()
      }, 300)
    },
    checkAndClearInterval() {
      if (this.task && this.task.completed) {
        this.stopChecker()
        this.updateCustomFields()
        this.loaderText = ''
        this.modalLoading = false
        this.createdCustomFields = false
      } else {
        return
      }
    },
    toggleCustomObjectModalView() {
      this.customObjectModalView = !this.customObjectModalView
    },
    closeCustomModal() {
      if (this.selectedCustomObject) {
        this.customFields = CollectionManager.create({
          ModelClass: ObjectField,
          pagination: { size: 500 },
          filters: {
            crmObject: this.customResource,
          },
        })
        this.customFields.refresh()
      }
      this.formFields.refresh()
      // if (this.selectedCustomObject) {
      //   this.selectedCustomObject = null
      // }
      this.customObjectModalView = false
    },
    async getCustomObjectFields() {
      if (!this.selectedCustomObject) {
        return
      }
      this.selectedCustomObjectName = this.selectedCustomObject.name
      try {
        // this.modalLoading = true
        this.loaderText = this.loaderTextList[0]
        const customForm = {
          config: {},
          customFields: [],
          customObject: this.selectedCustomObjectName,
          fields: [],
          fieldsRef: [],
          formType: 'CREATE',
          id: '',
          organization: this.allForms[0].organization,
          resource: 'CustomObject',
          stage: '',
        }
        this.newCustomForm = customForm

        this.addedFields = []
        const res = await SlackOAuth.api.postOrgCustomForm({
          ...this.newCustomForm,
        })
        this.updateCustomFields()
        this.createdCustomFields = true
        this.newCustomObject = true
        this.getAllForms()
        if (this.userCRM == 'SALESFORCE') {
          this.getCustomObjects()
        }
        setTimeout(() => {
          this.$store.dispatch('setCustomObject', this.selectedCustomObjectName)
          // setTimeout(() => {
          //   this.loaderText = 'Reloading page, please be patient...'
          //   setTimeout(() => {
          //     this.$router.go()
          //   }, 1000)
          // }, 2000)
          this.searchFields()
        }, 400)
      } catch (e) {
        console.log(e)
      }
    },
    getCreatedCO() {
      if (!this.selectedCustomObject) {
        this.newCustomForm = null
        this.newFormType = null
        this.customResource = null
        // this.newResource = null
        return
      }
      this.selectedCustomObjectName = this.selectedCustomObject.name

      this.loaderText = this.loaderTextList[0]
      this.newCustomForm = this.allForms.find(
        (f) =>
          f.resource == 'CustomObject' &&
          f.formType == 'CREATE' &&
          f.customObject == this.selectedCustomObjectName,
      )
      this.newFormType = 'CREATE'
      this.updateCustomFields()
      this.searchFields()
    },
    stopChecker() {
      clearInterval(this.$store.state.customObject.checker)
    },
    updateCustomFields() {
      if (this.selectedCustomObject) {
        this.customResource = this.selectedCustomObjectName
        this.newResource = this.selectedCustomObjectName
      }
      // if (this.customObjectModalView) {
      this.closeCustomModal()
      // }
    },
    watcherCustomResource() {
      this.formFields.refresh()
    },
    async getCustomObjects() {
      const res = await SObjects.api.getCustomObjects()
      const names = []
      for (let i = 0; i < this.customForms.length; i++) {
        const form = this.customForms[i]
        names.push(form.customObject)
      }
      const createdCustomObjects = []
      const filteredCustomObjects = res.sobjects.filter((co) => {
        if (!names.includes(co.name)) {
          return co
        } else {
          createdCustomObjects.push(co)
        }
      })
      this.customObjects = filteredCustomObjects
      this.createdCustomObjects = createdCustomObjects
    },
    clearStageData() {
      this.selectedForm = null
      this.currentlySelectedStage = null
      this.selectedStage = null
    },
    async deleteForm(form) {
      if (form && form.id && form.id.length) {
        const id = form.id

        SlackOAuth.api
          .delete(id)
          .then(async (res) => {
            this.$router.go()
            this.$toast('Form removed', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
          .catch((e) => {
            this.$toast('Error, please try again', {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
          .finally(() => {})
      } else {
        const forms = this.allForms.filter((f) => {
          if (form) {
            return f.id !== form.id
          }
        })
        this.allForms = [...forms]
        if (this.storedField) {
          this.$router.go()
        }
      }
    },
    closeModal() {
      this.modalOpen = false
      this.formChange = false
      this.changeObject(
        { value: this.storedModalVariables.resource, label: this.storedModalVariables.resource },
        {
          value: this.storedModalVariables.formType,
          label:
            this.storedModalVariables.formType[0] +
            this.storedModalVariables.formType.slice(1, this.storedModalVariables.formType.length),
        },
      )
    },
    closeDeleteModal() {
      if (this.storedField) {
        this.addedFields = [this.storedField]
      }
      this.storedField = null
      this.confirmDeleteModal = false
      this.confirmCODeleteModal = false
    },
    setNewForm() {
      this.addForm(this.selectedStage)
    },
    async selectForm(resource, formType, stage = '') {
      this.selectedForm = this.allForms.find(
        (f) => f.resource == resource && f.formType == formType && f.stage == stage,
      )
      this.newFormType = formType
      this.selectedStage = stage
    },
    setCustomForm() {
      this.newCustomForm = this.selectedForm
      this.customResource =
        this.newCustomForm && this.newCustomForm.customObject
          ? this.newCustomForm.customObject
          : this.resource
      this.newResource = this.customResource
      this.formFields = CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 500 },
        filters: {
          crmObject: this.customResource,
        },
      })
    },
    setStage(n) {
      if (!n) return
      if (this.userCRM === 'SALESFORCE') {
        if (n.value == this.selectedStage) {
          this.selectedStage = n.value
          this.addForm(this.selectedStage)
        }
        this.selectedStage = n.value
      } else if (this.userCRM === 'HUBSPOT') {
        if (n.label == this.selectedStage) {
          this.selectedStage = n.label
          this.addForm(this.selectedStage)
        }
        this.selectedStage = n.label
      }
    },
    addForm(stage) {
      /** Method for Creating a new stage-gating form, this is only available for Opportunities at this time */
      if (this.currentStagesWithForms.includes(stage)) {
        this.activeForm = this.formStages.find((form) => form.stage == stage)
      }
      let newForm = SlackOAuth.customSlackForm.create({
        resource: this.userCRM === 'SALESFORCE' ? this.OPPORTUNITY : this.DEAL,
        formType: this.STAGE_GATING,
        stage: stage,
      })
      newForm.fieldsRef = this.formStages.reduce((acc, curr) => {
        let fields = curr.fieldsRef.filter((f) => !acc.map((af) => af.id).includes(f.id))
        acc = [...acc, ...fields]
        return acc
      }, [])
      this.allForms = [...this.allForms, newForm]
      this.selectForm(this.userCRM === 'SALESFORCE' ? 'Opportunity' : 'Deal', 'STAGE_GATING', stage)
      this.getStageForms()
    },
    async listPicklists(query_params = {}) {
      try {
        let res
        if (this.userCRM === 'HUBSPOT') {
          res = await ObjectField.api.listFields({
            crmObject: this.DEAL,
            search: 'Deal Stage',
          })
          let dealStages = []
          for (let i = 0; i < res.length; i++) {
            if (res[i].apiName === 'dealstage') {
              dealStages = res[i]
              break
            }
          }
          let dealStage = []
          if (dealStages.optionsRef.length) {
            for (let i = 0; i < dealStages.optionsRef.length; i++) {
              dealStage = [...dealStage, ...dealStages.optionsRef[i]]
            }
          }
          // dealStage.map(stage => stage.label = 'Stage: ' + stage.label)
          this.stages = dealStage && dealStage.length ? dealStage : []
        } else if (this.userCRM === 'SALESFORCE') {
          res = await SObjectPicklist.api.listPicklists(query_params)
          let values = res[0]['values']
          // values.map(val => val.label = 'Stage: ' + val.label)
          this.stages = res.length ? res[0]['values'] : []
        }
      } catch (e) {
        console.log(e)
      }
    },
    getStageForms() {
      // users can only create one form for the stage orderd by stage
      let forms = []
      this.stages.forEach((s) => {
        this.allForms
          .filter((f) => f.formType == this.STAGE_GATING)
          .forEach((sf) => {
            if (this.userCRM === 'SALESFORCE') {
              if (sf.stage == s.value) {
                forms.push(sf)
              }
            } else if (this.userCRM === 'HUBSPOT') {
              if (sf.stage == s.label) {
                forms.push(sf)
              }
            }
          })
      })
      this.formStages = [...forms]
    },
    toggleCustomObjectView() {
      this.customObjectView = true
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == 'CustomObject' && f.formType == this.UPDATE,
      )
    },
    changeObject(object, type, switchedObject = false) {
      if (type.label !== 'Create' && type.label !== 'Update') { //&& type.label !== '--- Stages ---') {
        console.log('before setStage', type)
        this.setStage(type)
        return
      } else {
        this.selectedStage = null
      }
      if (!type.value) {
        this.selectedType = { value: 'UPDATE', label: 'Update' }
        this.changeResource(object.value, this.selectedType.value)
        return
      }
      if (object && object.value === 'OpportunityLineItem') {
        this.selectedType = { value: 'CREATE', label: 'Create' }
        this.changeResource(object.value, this.selectedType.value)
        return
      } else if (switchedObject || !object || !type || !object.value || !type.value) {
        if (this.formChange) {
          this.modalOpen = !this.modalOpen
          this.storedModalVariables = { resource, formType }
          return
        }
        this.selectedType = null
        this.clearForms()
      } else if (type.value === 'STAGE_GATING' && !switchedObject) {
        this.selectedObject =
          this.userCRM === 'SALESFORCE'
            ? { value: 'Opportunity', label: 'Opportunity' }
            : { value: 'Deal', label: 'Deal' }
        this.changeResource(this.selectedObject.value, type.value)
      } else if (object.value === 'OpportunityLineItem') {
        this.selectedType = { value: 'CREATE', label: 'Create' }
        this.changeResource(object.value, this.selectedType.value)
      } else {
        this.changeResource(object.value, type.value)
      }
    },
    clearForms() {
      this.customObjectView = false
      this.customResource = null
      this.filterText = ''
      this.newResource = ''
      this.newFormType = ''
      this.newCustomForm = null
      this.storedField = null
    },
    customLabelView(prop) {
      if (prop.value !== 'UPDATE' && prop.value !== 'CREATE' && prop.value !== 'STAGE') {
        return prop.label
      }
    },
    changeResource(resource, formType) {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalVariables = { resource, formType }
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newResource = resource
      this.newFormType = formType
      setTimeout(() => {
        this.newCustomForm = this.allForms.find(
          (f) => f.resource == resource && f.formType == this[formType],
        )
      }, 0)
      this.storedField = null
    },
    changeToAccount() {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToAccount
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newResource = 'Account'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.ACCOUNT && f.formType == this.UPDATE,
      )
      this.storedField = null
    },
    changeToCompany() {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToCompany
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newResource = 'Company'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.COMPANY && f.formType == this.UPDATE,
      )
      this.storedField = null
    },
    changeToOpportunity() {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToOpportunity
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newResource = 'Opportunity'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.OPPORTUNITY && f.formType == this.UPDATE,
      )
      this.storedField = null
    },
    changeToDeal() {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToDeal
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newResource = 'Deal'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.DEAL && f.formType == this.UPDATE,
      )
      this.storedField = null
    },
    changeToProducts() {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToProducts
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newResource = 'OpportunityLineItem'
      this.newFormType = 'CREATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.OPPORTUNITYLINEITEM && f.formType == this.CREATE,
      )
      this.storedField = null
    },
    changeToStage(stage = '') {
      this.customObjectView = false
      this.clearStageData()
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToStage
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newFormType = 'STAGE_GATING'
      this.newResource = 'Opportunity'

      if (this.userCRM === 'SALESFORCE') {
        this.newResource = 'Opportunity'
        this.newCustomForm = this.allForms.find(
          (f) =>
            f.resource == this.OPPORTUNITY && f.formType == this.STAGE_GATING && f.stage == stage,
        )
      } else if (this.userCRM === 'HUBSPOT') {
        this.newResource = 'Deal'
        this.newCustomForm = this.allForms.find(
          (f) => f.resource == this.DEAL && f.formType == this.STAGE_GATING && f.stage == stage,
        )
      }
      this.storedField = null
    },
    changeToContact() {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToContact
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newResource = 'Contact'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.CONTACT && f.formType == this.UPDATE,
      )
      this.storedField = null
    },
    changeToLead() {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToLead
        return
      }
      this.customResource = null
      this.filterText = ''
      this.newResource = 'Lead'
      this.newFormType = 'UPDATE'
      this.newCustomForm = this.allForms.find((f) => f.resource == 'Lead' && f.formType == 'UPDATE')
      this.storedField = null
    },
    switchFormType() {
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.switchFormType
        return
      }
      this.filterText = ''
      this.newFormType === 'CREATE' ? (this.newFormType = 'UPDATE') : (this.newFormType = 'CREATE')

      this.newCustomForm = this.allForms.find(
        (f) => f.resource == this.newResource && f.formType == this.newFormType,
      )
    },
    modalSave() {
      this.formChange = false
      this.onSave()
      this.modalOpen = false
      setTimeout(() => {
        this.changeObject(
          { value: this.storedModalVariables.resource, label: this.storedModalVariables.resource },
          {
            value: this.storedModalVariables.formType,
            label:
              this.storedModalVariables.formType[0] +
              this.storedModalVariables.formType.slice(
                1,
                this.storedModalVariables.formType.length,
              ),
          },
        )
        // this.$router.go()
      }, 400)
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
      this.formChange = true
      if (this.addedFieldIds.includes(field.id)) {
        this.canRemoveField(field) && this.onRemoveField(field)
        return
      }
      this.addedFields.push({ ...field, order: this.addedFields.length, includeInRecap: true })
    },
    changeCustomObjectName() {
      this.newCustomForm.customObject = this.customResource
      this.newCustomForm.resource = 'CustomObject'
    },
    onRemoveField(field) {
      // remove from the array if  it exists

      this.addedFields = [...this.addedFields.filter((f) => f.id != field.id)]

      if (!this.addedFields.length) {
        this.storedField = field
        this.confirmDeleteModal = true
        return
      }

      // if it exists in the current fields add it to remove field

      if (~this.currentFields.findIndex((f) => f == field.id)) {
        this.removedFields = [...this.removedFields, field]
      }
      this.formChange = true
    },
    async onSave() {
      if (this.newCustomObject) {
        this.newCustomForm = this.allForms.find(
          (f) =>
            f.resource == 'CustomObject' &&
            f.formType == 'CREATE' &&
            f.customObject == this.selectedCustomObjectName,
        )
        this.newCustomObject = false
      }
      if (!this.newCustomForm) {
        this.newCustomForm = this.customForm
      }
      if (
        (this.newResource == 'Opportunity' || this.newResource == 'Account') &&
        this.newCustomForm.formType == FORM_CONSTS.MEETING_REVIEW
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

      let currentFormFields = this.addedFields.map((field) => {
        return field.id
      })

      if (this.newFormType == 'UPDATE' && this.newResource !== 'OpportunityLineItem') {
        if (
          currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false &&
          currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5034') == false
        ) {
          let fieldsToAdd =
            this.userCRM === 'SALESFORCE'
              ? [this.noteTitle, this.noteSubject]
              : [this.noteTitleHubspot, this.noteSubjectHubspot]
          let copyArray = this.addedFields
          this.addedFields = fieldsToAdd.concat(copyArray)
        }
      }

      let fields = new Set([...this.addedFields.map((f) => f.id)])
      fields = Array.from(fields).filter((f) => !this.removedFields.map((f) => f.id).includes(f))
      let fieldsCheck = []
      fields.forEach((field) => {
        if (
          field === '6407b7a1-a877-44e2-979d-1effafec5034' ||
          field === '6407b7a1-a877-44e2-979d-1effafec5035' ||
          field === '0bb152b5-aac1-4ee0-9c25-51ae98d55af2' ||
          field === '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
        ) {
          return
        }
        fieldsCheck.push(field)
      })
      if (!fieldsCheck.length && this.newCustomForm.formType === 'STAGE_GATING') {
        this.$toast('Please add fields', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      let fields_ref = this.addedFields.filter((f) => fields.includes(f.id))
      if (
        this.customResource &&
        this.customResource !== 'Opportunity' &&
        this.customResource !== 'Deal' &&
        this.customResource !== 'Lead' &&
        this.customResource !== 'Company' &&
        this.customResource !== 'Contact' &&
        this.customResource !== 'Account'
      ) {
        this.changeCustomObjectName()
      }
      SlackOAuth.api
        .postOrgCustomForm({
          ...this.newCustomForm,
          fields: fields,
          removedFields: this.removedFields,
          fields_ref: fields_ref,
          custom_object: this.newCustomForm.customObject ? this.newCustomForm.customObject : '',
        })
        .then((res) => {
          // this.$emit('update:selectedForm', res)

          const filteredForm = this.allForms.filter(form => form.resource === res.resource && form.formType === res.formType)[0]

          if (filteredForm) {
            const withoutNewForm = this.allForms.filter(form => !(form.resource === res.resource && form.formType === res.formType))
            this.$store.commit('SAVE_CRM_FORMS', [...withoutNewForm, res])
          } else {
            this.$store.commit('SAVE_CRM_FORMS', [...this.allForms, res])
          }

          this.newCustomForm = res

          this.$toast('Form saved', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.removedFields = []
          // setTimeout(() => {
          //   this.removedFields = []
          //   // this.$router.go()
          // }, 300)
          this.addedFields = fields_ref
        })
        .finally(() => {
          this.savingForm = false
          this.getAllForms()
          this.formChange = false
          if (this.newCustomForm.formType === 'STAGE_GATING') {
            this.$router.go()
          }
        })
    },
    async getAllForms() {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      this.$store.commit('SAVE_CRM_FORMS', this.allForms)
      this.updateAllForms(this.allForms)
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
@import '@/styles/modals';

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.alerts-header {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 60px;
  background-color: white;
  width: 96vw;
  border-bottom: 1px solid $soft-gray;
  padding: 4px 32px 0px 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.75px;
    line-height: 1.2;
  }
}
.red-text {
  color: $coral;
}
.red-filter {
  filter: invert(51%) sepia(74%) saturate(2430%) hue-rotate(320deg) brightness(104%) contrast(121%);
}
.option {
  &__small {
    background-color: $white-green;
    border-radius: 4px;
    margin-left: 8px;
    margin-top: 8px;
    padding: 4px 4px 2px 4px;
    color: $dark-green;
  }
}
input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 0.9ex;
  left: 0.4ex;
  border: 2px solid $dark-green;
  border-top: none;
  border-right: none;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}

input[type='checkbox'] {
  line-height: 2.1ex;
}

input[type='checkbox'] {
  position: absolute;
  left: -999em;
}

input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

input[type='checkbox'] + label::before {
  content: '';
  display: inline-block;
  vertical-align: -22%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}
.search-bar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid $soft-gray;
  h5 {
    margin: 0;
    color: $light-gray-blue;
  }
}
.multiselect-align {
  // display: flex;
  // flex-direction: column;
  // justify-content: center;
  // margin-top: 0.5rem;
}
.search {
  height: 16px;
  margin-right: 0.5rem;
  filter: invert(20%);
}
.search-bar {
  // background-color: white;
  border: 1px solid $very-light-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3px 6px;
  border-radius: 8px;
  // margin-top: 16px;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
input[type='search'] {
  width: 6.5vw;
  letter-spacing: 0.75px;
  border: none;
  padding: 4px 0;
  margin: 0;
  background: none;
  font-size: 12px;
}
input[type='search']:focus {
  outline: none;
}
::placeholder {
  color: $very-light-gray;
  font-size: 12px;
}
.selected-container {
  height: 52vh; 
  margin-right: 1rem; 
  // margin-top: 3rem; 
  width: 30vw;
  h5 {
    margin-left: 1rem;
    margin-bottom: 1.3rem;
    color: $light-gray-blue;
  }
}
.selected {
  margin-left: 1rem;
  border-top: 1px solid $soft-gray;
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
      // outline: 1px solid $soft-gray;
      border-radius: 6px;
      padding: 4px 0px;
      // margin-top: 16px;
      // height: 76vh;
      height: 52vh;
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
.wrapper {
  // width: 100%;
  // margin: 0 auto;
  font-size: 14px;
  letter-spacing: 0.75px;
}
.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
#formSection {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  // border: 1px dashed $base-gray;
  padding-bottom: 32px;
  margin-top: 16px;
  border-radius: 0.3rem;
  height: 72vh;
  overflow: scroll;

  section {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    background-color: white;
    border-radius: 6px;
    min-height: 24vh;
    margin-top: 16px;
    width: 100%;
    padding: 0px 40px 0px 0px;

    input {
      width: 100%;
      border: 1px solid $soft-gray;
      border-radius: 0.3rem;
      background-color: white;
      min-height: 2.5rem;
      font-family: $base-font-family;
      margin-bottom: 16px;
      padding-left: 8px;
    }
    textarea {
      width: 100%;
      border: 1px solid $soft-gray;
      border-radius: 0.3rem;
      background-color: white;
      min-height: 2.5rem;
      font-family: $base-font-family;
      resize: none;
      padding-left: 8px;
    }
  }

  div {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: 99%;
    div {
      display: flex;
      flex-direction: row;
      align-items: flex-end;
      img {
        filter: invert(45%);
        margin: 0px 8px 8px 12px;
      }
    }
  }
}
// #formField {
//   width: 100%;
//   display: flex;
//   align-items: center;
//   padding: 4px 8px;
//   border: 1px solid $soft-gray;
//   border-radius: 0.3rem;
//   background-color: white;
//   font-family: $base-font-family;
//   margin-top: 8px;
//   cursor: grab;
//   img {
//     padding-top: 8px;
//     cursor: grab;
//   }
// }
//////END TAB STYLE//////

.sticky {
  top: 0;
  position: sticky;
  background-color: red;
  padding-top: 0px;
  margin-top: 0;
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
.margin-right {
  margin-right: 2.75vw;
}
.gray {
  color: $light-gray-blue;
  opacity: 0.7;
}
.light-gray {
  color: $light-gray-blue;
  cursor: pointer;
}
.green {
  color: $dark-green !important;
  background-color: $white-green;
  padding: 6px 8px;
  border-radius: 4px;
  font-weight: bold;
}
.invisible {
  visibility: hidden;
}
#drag {
  filter: invert(60%);
}
#remove {
  // filter: invert(40%);
}
// .drag-item {
//   display: flex;
//   flex-direction: row;
//   align-items: center !important;
//   border-radius: 0.2rem;
// }
.drag-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  margin-right: 8px;
  margin-bottom: 8px;
  border-radius: 4px;
  background-color: $white;
  // color: $base-gray;
  outline: 1px solid $soft-gray;
  font-size: 13px;
  // width: fit-content;
  white-space: nowrap;
  img {
    filter: invert(10%);
    cursor: grab;
  }
  label {
    color: $very-light-gray !important;
    padding-left: 2px;
  }
}
.drag-item-left {
  display: flex;
  align-items: center;
  img {
    filter: invert(10%);
    cursor: grab;
    margin: 0 0.75rem 0 0.5rem;
  }
  p {
    font-size: 12px;
    // filter: invert(45%);
  }
}
.drag-item-right {
  display: flex;
  align-items: center;
  height: 1.5rem;
  padding: 0 0.5rem;
  border-left: 1px solid $very-light-gray;
  label {
    color: $very-light-gray !important;
    padding-left: 2px;
  }
  span {
    color: #7b8580;
    font-size: 16px;
    padding: 0px 6px 4px 6px;
    border-radius: 4px;
  }
  span:hover {
    background-color: rgba(153, 153, 153, 0.6);
    cursor: pointer;
    color: white;
  }
}
.slack-form-builder {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  padding: 0rem;
  margin-top: 10vh;
  overflow: hidden;
  // color: $base-gray;
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
img:hover {
  cursor: pointer;
}
.save {
  // @include base-button();
  // background-color: $dark-green;
  // color: $white;
  // font-size: 12px;
  // transition: all 0.3s;
  @include primary-button();
  margin-right: 0.1rem;
}
// .red-button {
//   @include button-danger();
//   padding: 8px 20px;
//   margin-top: 1rem;
// }
.red-button {
  @include button-danger();
}
.custom-object-button {
  padding: 8px 20px;
  font-size: 13px;
  background-color: white;
  color: $dark-green;
  border: 1px solid $dark-green;
  border-radius: 0.25rem;
  margin-right: 8px;
  cursor: pointer;
}
:disabled {
  padding: 12px 20px;
  background-color: $soft-gray;
  color: $light-gray-blue;
  border: none;
  border-radius: 0.25rem;
  font-size: 13px;
  margin-left: 0.5rem;
  opacity: 0.8;
  cursor: text;
}
.row__ {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-left: 16px;
  letter-spacing: 0.75px;
  font-size: 14px;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
}
.opp-modal-container {
  @include medium-modal();
  padding: 1rem;
}
.modal-container {
  // @include large-modal();
  overflow: auto;
  min-width: 36vw;
  max-width: 36vw;
  min-height: 20vh;
  max-height: 80vh;
  align-items: center;
  border-radius: 0.5rem;
  z-index: 20;
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
.header {
  font-size: 18px;
  padding: 0;
  letter-spacing: 0.5px;
  margin-bottom: 0.2rem;
}
.sticky {
  position: sticky;
  background-color: white;
  width: 100%;
  left: 0;
  top: 0;
  padding: 0px 6px 8px -2px;
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
.flex-row-modal {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  margin: 0 5%;
  letter-spacing: 1px;
}
.logo {
  margin: 0px 8px 0px 16px;
  background-color: $white-green;
  border-radius: 4px;
  padding: 4px 6px;
  img {
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
// .cancel {
//   color: $dark-green;
//   font-weight: bold;
//   margin-left: 1rem;
//   cursor: pointer;
//   padding-top: 8px;
//   padding-bottom: 0;
//   letter-spacing: 0.75px;
//   color: $base-gray;

//   h4 {
//     font-weight: 400;
//   }
// }
.logo2 {
  height: 1.75rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
  filter: invert(40%);
}
.modal-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 3rem;
  div {
    margin-left: 0.5rem;
  }
}
.cancel {
  @include gray-text-button();
  padding: 8px 12px;
  font-size: 13px;
  margin-right: 0.5rem;
  color: $coral !important;
}
.save-refresh-section {
  display: flex;
}
.img-button {
  @include gray-text-button();
  padding: 4px 6px 3px 6px;
  margin-right: 0.5rem;
}
.img-border {
  border: 1px solid #eeeeee;
  padding: 4px 6px 3px 6px;
  border-radius: 6px;
  background-color: white;
}
.fields-container {
  border: 1px solid $soft-gray;
  background-color: white;
  border-radius: 4px;
  // box-shadow: 0 0 10px $very-light-gray;
  width: 60vw;
  height: 75vh;
  // margin: 0rem auto;
  margin: 0 1.5rem;
}
.drag-section {
  height: 48vh;
  overflow: auto;
  // outline: 1px solid #eeeeee;
  // border-radius: 6px;
  padding: 18px 4px 4px;
}
.border-bottom-top {
  border-bottom: 1px solid $soft-gray;
  overflow: auto;
}
.green-highlight {
  color: $dark-green !important;
  border-bottom: 3px solid $dark-green;
}
.cursor {
  cursor: pointer;
}
.small-subtitle {
  font-size: 12px;
  margin-top: 0.5rem;
  margin-left: 0.5rem;
  color: $very-light-gray;
}
.side-wrapper {
  display: flex;
  flex-direction: row;
}
.side-wrapper .side-icon {
  position: relative;
  background: #ffffff;
  border-radius: 50%;
  padding: 10px;
  margin: 20px 12px 0px 12px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  outline: 1px solid $mid-gray;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip {
  display: block;
  width: 250px;
  height: auto;
  position: absolute;
  top: 0;
  left: 30px;
  font-size: 14px;
  background: #ffffff;
  color: #ffffff;
  padding: 6px 8px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: 50%;
  left: 0%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-icon:hover .side-tooltip {
  top: -15px;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.side-wrapper .side-icon:hover span,
.side-wrapper .side-icon:hover .side-tooltip {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}
.side-wrapper .side-workflow:hover,
.side-wrapper .side-workflow:hover .side-tooltip,
.side-wrapper .side-workflow:hover .side-tooltip::before {
  background: $base-gray;
  color: #ffffff;
}
.wrapper {
  display: flex;
  flex-direction: row;
}
.wrapper .icon {
  position: relative;
  background: #ffffff;
  border-radius: 50%;
  padding: 10px;
  margin: 20px 12px 0px 12px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  outline: 1px solid $mid-gray;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.wrapper .tooltip {
  display: block;
  width: 325px;
  height: auto;
  position: absolute;
  top: 0;
  font-size: 14px;
  background: #ffffff;
  color: #ffffff;
  padding: 6px 8px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.wrapper .tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: -3px;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.wrapper .icon:hover .tooltip {
  top: -125px;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.wrapper .icon:hover span,
.wrapper .icon:hover .tooltip {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}
.wrapper .workflow:hover,
.wrapper .workflow:hover .tooltip,
.wrapper .workflow:hover .tooltip::before {
  background: $base-gray;
  color: #ffffff;
}
// .multiselect-font {
//   font-size: 12px !important;
// }
::v-deep .multiselect * {
  font-size: 13px;
  font-family: $base-font-family;
  border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}
::v-deep .multiselect__content-wrapper {
  border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  min-width: 250px;
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}
::v-deep .multiselect__single {
  margin-bottom: 0;
}
::v-deep .multiselect__tags {
  min-height: 32px;
  padding-top: 4px;
}
::v-deep .multiselect__select {
  height: 32px;
}
::v-deep .multiselect {
  min-height: 0;
}
.green-check {
  height: 0.6rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
  // margin-left: 1.75rem;
  // margin-top: 0.1rem;
}
.custom-picklist-font {
  font-size: 12px;
}
::v-deep .custom-picklist-font input::placeholder {
  font-size: 12px;
}
::v-deep .custom-picklist-font span {
  font-size: 12px;
}
.light-gray-blue {
  color: $light-gray-blue;
}
.header-text {
  font-size: 11px;
  // filter: invert(45%);
  // color: #7b8580;
  color: $light-gray-blue;
}
.refresh-button {
  height: 14px;
  filter: invert(45%)
}
.trash-button {
  height: 14px;
  filter: invert(43%) sepia(45%) saturate(682%) hue-rotate(308deg) brightness(109%) contrast(106%);
}
.display-flex {
  display: flex;
}
.small-margin-right {
  margin-right: 2rem;
}
.invite-form {
  @include small-modal();
  min-width: 37vw;
  // min-height: 64vh;
  align-items: center;
  justify-content: space-between;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
    font-size: 22px;
  }
  &__subtitle {
    text-align: left;
    font-size: 16px;
    margin-left: 1rem;
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    // margin-top: -4rem;
  }
  &__inner_actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    border-top: 1px solid $soft-gray;
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
  }
}
.crm-form {
  height: 30vh;
  width: 32vw;
}
.form-margin-small {
  margin-top: 10rem;
}
.header-crm {
  // background-color: $soft-gray;
  width: 100%;
  // border-bottom: 1px solid $soft-gray;
  position: relative;
  border-top-right-radius: 4px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-top-left-radius: 4px;
  display: flex;
  justify-content: center;
  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: flex-start;

  h3 {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $base-gray;
  }
}
.flex-row-wrapper {
  display: flex;
  justify-content: space-between;
}
.inner-crm {
  border-bottom: 1px solid $soft-gray;
  width: 90%;
  padding-bottom: 0.4rem;
}
.card-text {
  font-size: 14px;
  color: $light-gray-blue;
  margin-top: 0.5rem;
  // text-align: center;
}
.confirm-cancel-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 94%
}
.img-border-modal {
  // @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  // padding: 4px 6px;
  margin-right: 8px;
  margin-top: 0.5rem;
}
.cancel-button {
  @include gray-button();
}
.half-view-flex {
  display: flex; 
  justify-content: space-between; 
  width: 55.75vw;
}
.filtered-red {
  filter: invert(43%) sepia(45%) saturate(682%) hue-rotate(308deg) brightness(109%) contrast(106%);
}
.gray-background {
  display: flex;
  align-items: center;
  background-color: $soft-gray;
  height: 4vh;
  border-radius: 8px;
}
.toggle-update-create-container {
  border: 1px solid $soft-gray;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 5vw;
  height: 3vh;
  border-radius: 8px;
  margin: 0 0.25rem;
  p {
    margin: 0;
    color: $light-gray-blue;
    font-size: 12px;
    // text-align: center;
  }
}
.active {
  background-color: $white;
  border-radius: 8px;
}
.choose-fields-container {
  display: flex;
}
</style>
