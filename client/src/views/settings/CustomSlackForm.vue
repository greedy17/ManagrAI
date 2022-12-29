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
              <div style="display: flex; justify-content: center;">
                <Multiselect
                  @input="getCustomObjectFields"
                  :options="customObjects"
                  openDirection="below"
                  style="width: 94%; margin-left: 1rem;"
                  :max-height="400"
                  selectLabel="Enter"
                  :track-by="userCRM === 'HUBSPOT' ? 'label' : 'name'"
                  :customLabel="customLabel"
                  :value="currentlySelectedCO"
                  v-model="selectedCustomObject"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
      
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Custom Object
                    </p>
                  </template>
      
                  <template slot="option" slot-scope="props">
                    <div>
                      <span class="option__title">{{
                        userCRM === 'SALESFORCE' ? props.option.label : props.option.label
                      }}</span
                      ><span
                        v-if="
                          currentStagesWithForms.includes(
                            userCRM === 'SALESFORCE' ? props.option.label : props.option.label,
                          )
                        "
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
    <Modal v-if="confirmDeleteModal">
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
    </Modal>

    <div v-if="userCRM !== 'HUBSPOT'" class="alerts-header">
      <section class="row__ light-gray">
        <p
          @click="changeToOpportunity"
          :class="
            newResource == 'Opportunity' && newFormType !== 'STAGE_GATING' && !customObjectView
              ? 'green'
              : ''
          "
        >
          Opportunity
        </p>
        <p
          @click="changeToStage"
          :class="
            newResource == 'Opportunity' && newFormType == 'STAGE_GATING' && !customObjectView
              ? 'green'
              : ''
          "
        >
          Opp - Stage related
        </p>
        <p
          @click="changeToAccount"
          :class="newResource == 'Account' && !customObjectView ? 'green' : ''"
        >
          Account
        </p>
        <p
          @click="changeToContact"
          :class="newResource == 'Contact' && !customObjectView ? 'green' : ''"
        >
          Contact
        </p>
        <p @click="changeToLead" :class="newResource == 'Lead' && !customObjectView ? 'green' : ''">
          Lead
        </p>
        <p
          @click="changeToProducts"
          :class="newResource == 'OpportunityLineItem' && !customObjectView ? 'green' : ''"
        >
          Products
        </p>
        <p @click="toggleCustomObjectView" :class="customObjectView ? 'green' : ''">
          Custom Object
          <span 
            v-if="customForms && customForms.length" 
            class="option__small" 
            style="margin-left: 0; font-size: .7rem"
            >active
          </span>
        </p>
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
    </div>

    <div v-else class="alerts-header">
      <section class="row__ light-gray">
        <p
          @click="changeToDeal"
          :class="newResource == 'Deal' && newFormType !== 'STAGE_GATING' ? 'green' : ''"
        >
          Deal
        </p>
        <p
          @click="changeToStage"
          :class="newResource == 'Deal' && newFormType == 'STAGE_GATING' ? 'green' : ''"
        >
          Deal - Stage related
        </p>
        <p @click="changeToCompany" :class="newResource == 'Company' ? 'green' : ''">Company</p>
        <p @click="changeToContact" :class="newResource == 'Contact' ? 'green' : ''">
          Contact
        </p>
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
    </div>

    <section class="wrapper">
      <div v-if="newFormType !== 'STAGE_GATING' && !customObjectView" class="tab-content">
        <section>
          <div v-if="newResource !== 'OpportunityLineItem'" class="tab-content__div">
            <div class="row">
              <label :class="newFormType !== 'CREATE' ? 'gray' : ''">Create</label>
              <ToggleCheckBox
                style="margin-left: 0.5rem; margin-right: 0.5rem"
                @input="switchFormType"
                :value="newFormType == 'UPDATE'"
                offColor="#41b883"
                onColor="#41b883"
              />
              <label :class="newFormType == 'CREATE' ? 'gray' : ''">Update</label>
            </div>
          </div>
          <div v-else class="tab-content__div">
            <label class="gray">Create</label>
          </div>
          <div id="formSection">
            <draggable
              v-model="addedFields"
              group="fields"
              @start="drag = true"
              @end="drag = false"
              class="drag-section"
            >
              <div v-for="field in addedFields" :key="field.id">
                <div v-if="!unshownIds.includes(field.id)">
                  <div class="drag-item">
                    <p id="formField" :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                      <img src="@/assets/images/drag.svg" alt="" />
                      {{ field.label == 'Price Book Entry ID' ? 'Products' : field.label }}
                    </p>
                    <img
                      src="@/assets/images/remove.svg"
                      alt=""
                      id="remove"
                      :class="unshownIds.includes(field.id) ? 'invisible' : ''"
                      @click="
                        () => {
                          onRemoveField(field)
                        }
                      "
                    />
                  </div>
                </div>
              </div>
            </draggable>
          </div>
        </section>
      </div>

      <div v-else-if="!customObjectView" class="tab-content">
        <section style="margin-top: -16px" class="space-between">
          <h4 style="cursor: pointer" @click="clearStageData" v-if="selectedForm">
            <img
              style="margin-right: 8px; margin-top: -16px"
              src="@/assets/images/left.svg"
              height="13px"
              alt=""
            />
            Back
          </h4>

          <div class="row__">
            <h4 style="margin-right: 16px" v-if="selectedForm">
              {{ selectedForm.stage + ' Form' }}
            </h4>
            <h4 style="margin-right: 16px" v-else>{{ currentlySelectedForm }}</h4>

            <div
              class="margin-right"
              @click.prevent="deleteForm(activeForm)"
              v-if="selectedForm && selectedForm.customFields.length"
            >
              <img src="@/assets/images/removeFill.svg" class="red-filter" alt="" />
            </div>
          </div>
        </section>

        <div>
          <div class="row__">
            <Multiselect
              v-if="!selectedForm"
              @input="setStage($event)"
              :options="stages"
              openDirection="below"
              style="width: 40vw; margin-top: -24px"
              selectLabel="Enter"
              track-by="value"
              label="label"
              :value="currentlySelectedStage"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>

              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  {{ selectedStage ? selectedStage : 'Select stage to create/edit form' }}
                </p>
              </template>

              <template slot="option" slot-scope="props">
                <div>
                  <span class="option__title">{{
                    userCRM === 'SALESFORCE' ? props.option.value : props.option.label
                  }}</span
                  ><span
                    v-if="
                      currentStagesWithForms.includes(
                        userCRM === 'SALESFORCE' ? props.option.label : props.option.label,
                      )
                    "
                    class="option__small"
                  >
                    edit
                  </span>
                </div>
              </template>
            </Multiselect>
          </div>
        </div>

        <div v-if="selectedForm" id="formSection">
          <draggable
            v-model="addedFields"
            group="fields"
            @start="drag = true"
            @end="drag = false"
            class="drag-section"
          >
            <div v-for="field in addedFields" :key="field.id">
              <div v-if="!unshownIds.includes(field.id)">
                <div class="drag-item">
                  <p id="formField" :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                    <img src="@/assets/images/drag.svg" alt="" />
                    {{ field.label }}
                  </p>
                  <img
                    src="@/assets/images/remove.svg"
                    alt=""
                    id="remove"
                    :class="unshownIds.includes(field.id) ? 'invisible' : ''"
                    @click="
                      () => {
                        onRemoveField(field)
                      }
                    "
                  />
                </div>
              </div>
            </div>
          </draggable>
        </div>
      </div>

      <div class="tab-content" v-else>
        <div v-if="modalLoading">
          <Loader :loaderText="loaderText" />
        </div>

        <div v-else>
          <div v-if="!customResource">
            <div v-if="createdCustomObjects.length" style="width: 100%; display: flex; justify-content: space-between;">
              <Multiselect
                @input="getCreatedCO"
                :options="createdCustomObjects"
                openDirection="below"
                style="width: 40vw; margin-left: 1rem"
                selectLabel="Enter"
                :track-by="userCRM === 'HUBSPOT' ? 'label' : 'name'"
                label="name"
                :value="currentlySelectedCO"
                v-model="selectedCustomObject"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
    
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Custom Object
                  </p>
                </template>
    
                <template slot="option" slot-scope="props">
                  <div>
                    <span class="option__title">{{props.option.name}}</span
                    >
                  </div>
                </template>
              </Multiselect>
              <button
                @click="toggleCustomObjectModalView"
                class="custom-object-button"
              >
                Add Custom Object
              </button>
            </div>
            <Multiselect
              v-else
              @input="getCustomObjectFields"
              :options="customObjects"
              openDirection="below"
              style="width: 40vw; margin-left: 1rem"
              selectLabel="Enter"
              :track-by="userCRM === 'HUBSPOT' ? 'label' : 'name'"
              :customLabel="customLabel"
              :value="currentlySelectedCO"
              v-model="selectedCustomObject"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
  
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Select Custom Object
                </p>
              </template>
  
              <template slot="option" slot-scope="props">
                <div>
                  <span class="option__title">{{
                    userCRM === 'SALESFORCE' ? props.option.label : props.option.label
                  }}</span
                  ><span
                    v-if="
                      currentStagesWithForms.includes(
                        userCRM === 'SALESFORCE' ? props.option.label : props.option.label,
                      )
                    "
                    class="option__small"
                  >
                    edit
                  </span>
                </div>
              </template>
            </Multiselect>
          </div>
          <section v-else>
            <div class="space-between">
              <h4 style="cursor: pointer" @click="customResource = null">
                <img
                  style="margin-right: 8px; margin-top: -16px"
                  src="@/assets/images/left.svg"
                  height="13px"
                  alt=""
                />
                Back
              </h4>
  
              <div class="row__">
                <h4 style="margin-right: 16px">
                  {{ selectedCustomObjectName + ' Form' }}
                </h4>
                <div
                  class="margin-right"
                  @click.prevent="deleteForm(newCustomForm)"
                >
                  <img src="@/assets/images/removeFill.svg" class="red-filter" alt="" />
                </div>
              </div>
            </div>
            <div id="formSection">
              <draggable
                v-model="addedFields"
                group="fields"
                @start="drag = true"
                @end="drag = false"
                class="drag-section"
              >
                <div v-for="field in addedFields" :key="field.id">
                  <div v-if="!unshownIds.includes(field.id)">
                    <div class="drag-item">
                      <p id="formField" :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                        <img src="@/assets/images/drag.svg" alt="" />
                        {{ field.label }}
                      </p>
                      <img
                        src="@/assets/images/remove.svg"
                        alt=""
                        id="remove"
                        :class="unshownIds.includes(field.id) ? 'invisible' : ''"
                        @click="
                          () => {
                            onRemoveField(field)
                          }
                        "
                      />
                    </div>
                  </div>
                </div>
              </draggable>
            </div>
          </section>
        </div>
      </div>
    </section>

    <div class="field-section">
      <section v-if="!customObjectView">
        <div class="search-bar">
          <img src="@/assets/images/search.svg" style="height: 18px; cursor: pointer" alt="" />
          <input
            @input="searchFields"
            type="search"
            :placeholder="`Search ${newResource} Fields`"
            v-model="filterText"
          />
        </div>

        <div class="field-section__fields">
          <div>
            <p v-for="(field, i) in filteredFields" :key="field.id">
              <input @click="onAddField(field)" type="checkbox" :id="i" :value="field" />
              <label :for="i"></label>
              {{ field.label == 'Price Book Entry ID' ? 'Products' : field.label }}
              <!-- <span v-if="field.required" class="red-text">required</span> -->
            </p>
          </div>
        </div>
      </section>

      <section v-else>
        <div v-if="selectedCustomObject || customResource">
          <div class="search-bar">
            <img src="@/assets/images/search.svg" style="height: 18px; cursor: pointer" alt="" />
            <input
              type="search"
              :placeholder="`Search ${selectedCustomObjectName} Fields`"
              v-model="COfilterText"
            />
          </div>

          <div class="field-section__fields">
            <div>
              <p v-for="(field, i) in COfilteredFields" :key="field.id">
                <input @click="onAddField(field)" type="checkbox" :id="i" :value="field" />
                <label :for="i"></label>
                {{ field.label }}
                <span v-if="field.required" class="red-text">required</span>
              </p>
            </div>
          </div>
        </div>

        <div v-else>
          <div class="search-bar">
            <img src="@/assets/images/search.svg" style="height: 18px; cursor: pointer" alt="" />
            <input type="search" placeholder="Search Object Fields" />
          </div>

          <div class="field-section__fields">
            <div>
              <p>Nothing here. Try selecting an object</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

import { CollectionManager, Pagination } from '@thinknimble/tn-models'

import Modal from '@/components/InviteModal'

import ActionChoice from '@/services/action-choices'
import draggable from 'vuedraggable'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import { mapState } from 'vuex'

import SlackOAuth from '@/services/slack'
import User from '@/services/users'
import { SObjectPicklist } from '@/services/salesforce'
import { ObjectField } from '@/services/crm'
import * as FORM_CONSTS from '@/services/slack'
import { SObjects } from '../../services/salesforce'

export default {
  name: 'CustomSlackForm',
  components: {
    PulseLoadingSpinnerButton,
    Modal,
    draggable,
    ToggleCheckBox,
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
  },
  data() {
    return {
      activeForm: null,
      addingForm: false,
      currentlySelectedForm: null,
      customObjects: [],
      createdCustomObjects: [],
      pulseLoading: false,
      oldIndex: 0,
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
      reloadCustomObject: false,
      modalLoading: false,
      loaderText: '',
      formFields: CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 500 },
        filters: {
          crmObject: this.newResource,
        },
      }),
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
      Pagination,
      meetingType: '',
      actionChoices: [],
      loadingMeetingTypes: false,
      nameValue: '',
      customObjectView: false,
      customObjectModalView: false,
      confirmDeleteModal: false,
      modalOpen: false,
      formChange: false,
      storedField: null,
      formStages: [],
      stages: [],
      timeout: null,
      storedModalFunction: () => null,
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
          if (this.newNormType !== 'UPDATE') {
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
    formLength() {
      return this.formStages.length
    },
    customForms() {
      return this.allForms.filter(form => form.customObject)
    },
    filteredFields() {
      return this.formFields.list.filter((field) => !this.addedFieldNames.includes(field.apiName))
    },
    COfilteredFields() {
      if (!this.customFields) {
        return
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
    addedFieldLabels() {
      return this.addedFields.map((field) => {
        return field.referenceDisplayLabel
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
    user() {
      return this.$store.state.user
    },
    userHasProducts() {
      return this.$store.state.user.organizationRef.hasProducts
    },
    // userHasHubspot() {
    //   return this.$store.state.user.hasHubspotIntegration
    // },
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
      let object = this.userCRM === 'SALESFORCE' ? this.OPPORTUNITY : this.DEAL
      // if (this.userCRM === 'HUBSPOT') {
      //   object = this.DEAL
      // } else if (this.userCRM === 'SALESFORCE') {
      //   object = this.OPPORTUNITY
      // }
      this.newCustomForm = this.customForm
      await this.listPicklists({
        crmObject: object,
        picklistFor: this.userCRM === 'SALESFORCE' ? 'StageName' : 'dealstage',
      })
      if (this.userCRM == 'SALESFORCE') {
        this.getCustomObjects()
      }
    } catch (e) {
      console.log(e)
    }

    this.getStageForms()
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    customLabel(prop) {
      return prop.customObject ? `${prop.customObject}` : `${prop.label}`
    },
    searchFields() {
      this.formFields = CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 500 },
        filters: {
          crmObject: this.newResource,
          search: this.filterText,
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
        this.oldIndex = 0
        this.loaderText = ''
        this.modalLoading = false
        if (this.reloadCustomObject) {
          this.$router.go()
        }
      } else {
        return
      }
    },
    toggleCustomObjectModalView() {
      this.customObjectModalView = !this.customObjectModalView
    },
    closeCustomModal() {
      if (this.selectedCustomObject) {
        this.selectedCustomObject = null
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
    },
    async getCustomObjectFields() {
      if (!this.selectedCustomObject) {
        return
      }
      this.selectedCustomObjectName = this.selectedCustomObject.name
      try {
        this.modalLoading = true
        this.loaderText = this.loaderTextList[0]
        const customForm = {
          config: {},
          customFields: [],
          customObject: this.selectedCustomObjectName,
          fields: [],
          fieldsRef: [],
          formType: "CREATE",
          id: "",
          organization: this.allForms[0].organization,
          resource: "CustomObject",
          stage: "",
        }
        this.newCustomForm = customForm
        let currentFormFields = this.addedFields.map((field) => {
          return field.id
        })

        if (this.newCustomForm.formType == 'UPDATE') {
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
        this.addedFields = []
        const res = await SlackOAuth.api.postOrgCustomForm({
          ...this.newCustomForm,
        })
        this.reloadCustomObject = true
        setTimeout(() => {
          this.$store.dispatch('setCustomObject', this.selectedCustomObject.name)
          // setTimeout(() => {
          //   this.loaderText = 'Reloading page, please be patient...'
          //   setTimeout(() => {
          //     this.$router.go()
          //   }, 1000)
          // }, 2000)
        }, 400)
      } catch (e) {
        console.log(e)
      }
    },
    getCreatedCO() {
      if (!this.selectedCustomObject) {
        return
      }
      this.selectedCustomObjectName = this.selectedCustomObject.name

      this.modalLoading = true
      this.loaderText = this.loaderTextList[0]
      this.newCustomForm = this.allForms.find(
        (f) => f.resource == 'CustomObject' && f.formType == 'CREATE' && f.customObject == this.selectedCustomObjectName,
      )
      setTimeout(() => {
        this.$store.dispatch('setCustomObject', this.selectedCustomObject.name)
      }, 400)
    },
    changeLoaderText() {
      let newIndex
      if (this.oldIndex === 2) {
        newIndex = 2
      } else {
        newIndex = this.oldIndex + 1
        this.oldIndex = newIndex
      }
      return newIndex
    },
    stopChecker() {
      clearInterval(this.$store.state.customObject.checker)
    },
    updateCustomFields() {
      if (this.selectedCustomObject) {
        this.customResource = this.selectedCustomObjectName
        this.newResource = this.selectedCustomObjectName
      }
      this.closeCustomModal()
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
      const filteredCustomObjects = res.sobjects.filter(co => {
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
          .finally(() => {
            
          })
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
      this.storedModalFunction()
    },
    closeDeleteModal() {
      this.addedFields = [this.storedField]
      this.storedField = null
      this.confirmDeleteModal = false
    },
    setNewForm() {
      this.addForm(this.selectedStage)
      this.addingForm = false
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
          this.stages = dealStage && dealStage.length ? dealStage : []
        } else if (this.userCRM === 'SALESFORCE') {
          res = await SObjectPicklist.api.listPicklists(query_params)
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
    changeToAccount() {
      this.customObjectView = false
      if (this.formChange) {
        this.modalOpen = !this.modalOpen
        this.storedModalFunction = this.changeToAccount
        return
      }
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
      this.storedModalFunction()
      setTimeout(() => {
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
      this.newCustomForm.resource = "CustomObject"
    },
    goBack() {
      if (this.fromAdmin) {
        this.goBackAdmin()
      } else {
        this.$router.push({ name: 'Required' })
      }
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

          this.$toast('Form saved', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          setTimeout(() => {
            this.removedFields = []
            // this.$router.go()
          }, 300)
          this.addedFields = fields_ref
        })
        .finally(() => {
          this.savingForm = false
          this.getAllForms()
          this.formChange = false
        })
    },
    async getAllForms() {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
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
.alerts-header {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 72px;
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
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $light-gray-blue;
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
    margin-left: 16px;
    padding: 2px 6px;
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
  width: 25vw;
  letter-spacing: 0.75px;
  border: none;
  padding: 4px;
  margin: 0;
}
::placeholder {
  color: $very-light-gray;
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
      height: 76vh;
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
  width: 100%;
  margin: 0 auto;
  font-size: 14px;
  letter-spacing: 0.75px;
}

.tab-content {
  width: 100%;
  height: 86vh;
  padding: 32px 24px 16px 24px;
  background: #fff;
  color: $base-gray;
  overflow: scroll;
  border-radius: 6px;
  margin-top: 28px;

  section {
  }
  &__div {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
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
#formField {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 4px 8px;
  border: 1px solid $soft-gray;
  border-radius: 0.3rem;
  background-color: white;
  font-family: $base-font-family;
  margin-top: 8px;
  cursor: grab;
  img {
    padding-top: 8px;
    cursor: grab;
  }
}
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
  filter: invert(40%);
}
.drag-item {
  display: flex;
  flex-direction: row;
  align-items: center !important;
  border-radius: 0.2rem;
}
.drag-section {
}
.slack-form-builder {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  padding: 0rem;
  margin-top: 7vh;
  overflow: hidden;
  color: $base-gray;
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
  padding: 8px 20px;
  font-size: 13px;
  background-color: $dark-green;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
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
  justify-content: flex-start;
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
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  background-color: white;
  width: 35vw;
  height: 70vh;
  border-radius: 0.5rem;
  padding: 1rem;
}
.modal-container {
  background-color: $white;
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
.add-button {
  display: flex;
  align-items: center;
  border: none;
  margin: 0 0.5rem 0 0;
  padding: 9px 12px;
  font-size: 13px;
  border-radius: 6px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  letter-spacing: 0.75px;
}
.add-button:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.cancel {
  color: $dark-green;
  font-weight: bold;
  margin-left: 1rem;
  cursor: pointer;
  padding-top: 8px;
  padding-bottom: 0;
  letter-spacing: 0.75px;
  color: $base-gray;

  h4 {
    font-weight: 400;
  }
}

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
  border: 1px solid $soft-gray;
  font-weight: 400 !important;
  letter-spacing: 1px;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  margin-right: 0.5rem;
  color: $coral !important;
}
.save-refresh-section {
  display: flex;
}
.img-button {
  background-color: transparent;
  padding: 4px 6px;
  margin-right: 0.5rem;
  border: none;
}
.img-border {
  border: 1px solid #eeeeee;
  padding: 4px 6px 3px 6px;
  border-radius: 6px;
  background-color: white;
}

.flex-end-opp {
  width: 100%;
  padding: 4px 12px 4px 0px;
  height: 4rem;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}
</style>