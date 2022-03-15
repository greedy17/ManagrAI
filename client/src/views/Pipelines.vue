<template>
  <div class="pipelines">
    <Modal
      v-if="modalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetNotes()
        }
      "
    >
      <div v-if="notes.length" class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.75rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Notes</h2>
          </div>

          <img
            src="@/assets/images/closer.png"
            style="height: 1.5rem; margin-top: -0.5rem; margin-right: 0.5rem; cursor: pointer"
            @click="resetNotes"
            alt=""
          />
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{ note.saved_data__meeting_type ? note.saved_data__meeting_type + ':' : 'Untitled:' }}
          </p>
          <p class="note-section__body">{{ note.saved_data__meeting_comments }}</p>
          <p class="note-section__date">{{ formatDateTime(note.submission_date) }}</p>
        </section>
      </div>
      <div v-else class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.5rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Notes</h2>
          </div>
          <img
            src="@/assets/images/closer.png"
            style="height: 1.75rem; margin-top: -0.5rem; margin-right: 0.5rem; cursor: pointer"
            @click="resetNotes"
            alt=""
          />
        </div>
        <section class="note-section">
          <p class="note-section__title">No notes for this opportunity</p>
        </section>
      </div>
    </Modal>
    <Modal
      v-if="addOppModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetAddOpp()
        }
      "
    >
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.5rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h3>Create Opportunity</h3>
          </div>
          <div class="close-button">
            <img
              src="@/assets/images/clear.png"
              style="height: 1.2rem"
              @click="resetAddOpp"
              alt=""
            />
          </div>
        </div>
        <div class="opp-modal">
          <section :key="field.id" v-for="field in createOppForm">
            <div
              v-if="
                field.dataType === 'TextArea' ||
                (field.dataType === 'String' && field.apiName === 'NextStep')
              "
              class="flex-col"
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <textarea
                id="update-input"
                ccols="30"
                rows="4"
                style="width: 30vw; border-radius: 0.4rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div v-else-if="field.dataType === 'Reference' || field.dataType === 'String'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="update-input"
                type="text"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>

            <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                id="update-input"
              >
                <option v-for="(option, i) in picklistQueryOpts[field.apiName]" :key="i">
                  <p>{{ option.label }}</p>
                </option>
              </select>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="date"
                id="update-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'DateTime'">
              <p>
                {{ field.referenceDisplayLabel }}
              </p>
              <input
                type="datetime-local"
                id="start"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="update-input"
                type="number"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
          </section>
        </div>
        <div class="flex-end">
          <button class="add-button" @click="createResource">Create Opportunity</button>
        </div>
      </div>
    </Modal>
    <Modal
      v-if="editOpModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetEdit()
        }
      "
    >
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.75rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Update Opportunity</h2>
          </div>

          <img
            src="@/assets/images/closer.png"
            style="height: 1.75rem; margin-top: -0.5rem; cursor: pointer"
            @click="resetEdit"
            alt=""
          />
        </div>
        <div class="opp-modal">
          <section :key="field.id" v-for="field in oppFormCopy">
            <div v-if="field.apiName === 'meeting_type'">
              <p>Note Title:</p>
              <textarea
                id="update-input"
                cols="30"
                rows="2"
                style="width: 30vw; border-radius: 0.2rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div v-else-if="field.apiName === 'meeting_comments'">
              <p>Notes:</p>
              <textarea
                id="update-input"
                ccols="30"
                rows="3"
                style="width: 30vw; border-radius: 0.2rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                field.dataType === 'TextArea' || (field.length > 250 && field.dataType === 'String')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <textarea
                id="update-input"
                ccols="30"
                rows="4"
                :placeholder="currentVals[field.apiName]"
                style="width: 30vw; border-radius: 0.4rem; padding: 7px"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                (field.dataType === 'String' && field.apiName !== 'meeting_type') ||
                (field.dataType === 'String' && field.apiName !== 'meeting_comments') ||
                (field.dataType === 'String' && field.apiName !== 'NextStep')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="update-input"
                type="text"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Picklist' ||
                field.dataType === 'MultiPicklist' ||
                field.dataType === 'Reference'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                v-model="currentVals[field.apiName]"
                @input="
                  ;(value = $event.target.value),
                    setUpdateValues(
                      field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                      value,
                    )
                "
                id="update-input"
              >
                <option value="" disabled selected hidden>{{ currentVals[field.apiName] }}</option>
                <option v-for="(option, i) in picklistQueryOpts[field.apiName]" :key="i">
                  <p>{{ option.label }}</p>
                </option>
              </select>
            </div>
            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="text"
                onfocus="(this.type='date')"
                onblur="(this.type='text')"
                :placeholder="currentVals[field.apiName]"
                v-model="currentVals[field.apiName]"
                id="update-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'DateTime'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="datetime-local"
                id="start"
                v-model="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="update-input"
                type="number"
                v-model="currentVals[field.apiName]"
                :placeholder="currentVals[field.apiName]"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
          </section>
        </div>
        <div class="flex-end-opp">
          <p @click="resetEdit" class="cancel">Cancel</p>
          <button @click="updateResource()" class="add-button__">Update</button>
        </div>
      </div>
    </Modal>
    <div v-if="!loading">
      <section style="margin-bottom: 1rem" class="flex-row-spread">
        <div v-if="!workflowCheckList.length && !primaryCheckList.length" class="flex-row">
          <button @click="showList = !showList" class="select-btn">
            {{ currentList }}
            <img
              v-if="!showList"
              style="height: 1rem; margin-left: 0.5rem"
              src="@/assets/images/rightArrow.png"
              alt=""
            />
            <img
              v-else
              style="height: 1rem; margin-left: 0.5rem"
              src="@/assets/images/downArrow.png"
              alt=""
            />
          </button>
          <div v-show="showList" class="list-section">
            <div class="list-section__title flex-row-spread">
              <p>{{ currentList }}</p>
              <img
                @click="showList = !showList"
                class="exit"
                src="@/assets/images/close.png"
                alt=""
              />
            </div>
            <p @click="showPopularList = !showPopularList" class="list-section__sub-title">
              Popular Lists
              <img v-if="showPopularList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <button v-if="showPopularList" @click="allOpportunities" class="list-button">
              All Opportunities
              <span class="filter" v-if="currentList === 'All Opportunities'"> active</span>
            </button>
            <button v-if="showPopularList" @click="closeDatesThisMonth" class="list-button">
              Closing this month
              <span class="filter" v-if="currentList === 'Closing this month'"> active</span>
            </button>
            <button v-if="showPopularList" @click="closeDatesNextMonth" class="list-button">
              Closing next month
              <span class="filter" v-if="currentList === 'Closing next month'"> active</span>
            </button>
            <p @click="showWorkflowList = !showWorkflowList" class="list-section__sub-title">
              Pipeline Monitoring
              <img v-if="showWorkflowList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <div style="width: 100%" v-if="showWorkflowList">
              <button
                :key="i"
                v-for="(template, i) in templates.list"
                @click="selectList(template.configs[0], template.title, template.id)"
                class="list-button"
              >
                {{ template.title }}
                <span class="filter" v-if="currentList === template.title"> active</span>
              </button>
            </div>
          </div>
          <button class="soon-button">
            <img
              src="@/assets/images/plusOne.png"
              style="height: 1rem; margin-right: 0.25rem"
              alt=""
            />Filter <span class="soon-button__soon">(Coming Soon)</span>
          </button>
          <h5>
            {{ currentList }}:
            <span>{{ selectedWorkflow ? currentWorkflow.list.length : allOpps.length }}</span>
          </h5>
        </div>
        <div v-else>
          <div v-if="!updatingOpps" class="bulk-action">
            <div v-if="!closeDateSelected && !advanceStageSelected && !forecastSelected">
              <!-- <p class="bulk-action__title">Select Update or <span class="cancel">cancel</span></p> -->
              <div class="flex-row">
                <button @click="closeDateSelected = !closeDateSelected" class="select-btn">
                  Push Close Date
                  <img
                    src="@/assets/images/date.png"
                    style="height: 1.25rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>
                <button @click="advanceStageSelected = !advanceStageSelected" class="select-btn">
                  Advance Stage
                  <img
                    src="@/assets/images/stairs.png"
                    style="height: 1.25rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>
                <button @click="forecastSelected = !forecastSelected" class="select-btn">
                  Change Forecast
                  <img
                    src="@/assets/images/monetary.png"
                    style="height: 1.1rem; width: 1.35rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>
              </div>
            </div>
            <div class="flex-row-pad" v-if="closeDateSelected">
              <p style="font-size: 14px">How many days ?:</p>
              <input class="number-input" v-model="daysForward" type="number" />
              <button
                :disabled="!daysForward"
                class="add-button"
                @click="pushCloseDates(currentCheckList, daysForward)"
              >
                Push Close Date
              </button>
            </div>
            <div class="flex-row-pad" v-if="advanceStageSelected">
              <p style="font-size: 14px">Select Stage:</p>
              <select
                style="margin-left: 0.5rem; margin-right: 0.5rem"
                @input=";(value = $event.target.value), setStage(value)"
                id="update-input"
              >
                <option v-for="(stage, i) in allStages" :key="i" :value="stage.value">
                  <p>{{ stage.label }}</p>
                </option>
              </select>
              <button @click="advanceStage(currentCheckList)" class="add-button">
                Advance Stage
              </button>
            </div>
            <div class="flex-row-pad" v-if="forecastSelected">
              <p style="font-size: 14px">Select Forecast:</p>
              <select
                style="margin-left: 0.5rem; margin-right: 0.5rem"
                @input=";(value = $event.target.value), setForecast(value)"
                id="update-input"
              >
                <option v-for="(forecast, i) in allForecasts" :key="i" :value="forecast.value">
                  <p>{{ forecast.label }}</p>
                </option>
              </select>
              <button @click="changeForecast(currentCheckList)" class="add-button">
                Change Forecast
              </button>
            </div>
          </div>
          <div class="bulk-action" v-else>
            <SkeletonBox width="400px" height="22px" />
          </div>
        </div>
        <div class="flex-row">
          <div v-if="!selectedWorkflow" class="search-bar">
            <input type="search" v-model="filterText" placeholder="search" />
            <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
          </div>
          <div v-else class="search-bar">
            <input type="search" v-model="workflowFilterText" placeholder="search" />
            <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
          </div>
          <button @click="createOppInstance()" class="add-button">
            <img src="@/assets/images/plusOne.png" style="height: 1rem" alt="" />
            Create Opportunity
          </button>
          <!-- <button @click="resourceSync" class="select-btn">
            <img src="@/assets/images/refresh.png" class="invert" style="height: 1.15rem" alt="" />
          </button> -->
        </div>
      </section>
      <!-- <p @click="test">TESTING SYNC DAY</p> -->
      <section v-show="!selectedWorkflow" class="table-section">
        <div class="table">
          <PipelineHeader
            :oppFields="oppFields"
            @check-all="onCheckAll"
            :allSelected="allSelected"
          />
          <PipelineTableRow
            :key="i"
            v-for="(opp, i) in allOppsFiltered"
            @create-form="createFormInstance(opp.id)"
            @get-notes="getNotes(opp.id)"
            @checked-box="selectPrimaryCheckbox(opp.id)"
            :opp="opp"
            :index="i"
            :oppFields="oppFields"
            :primaryCheckList="primaryCheckList"
            :updateList="updateList"
          />
        </div>
      </section>
      <section v-if="selectedWorkflow && currentWorkflow.list.length > 0" class="table-section">
        <div class="table">
          <WorkflowHeader
            :oppFields="oppFields"
            @check-all="onCheckAllWorkflows"
            :allWorkflowsSelected="allWorkflowsSelected"
          />
          <WorkflowRow
            :key="i"
            v-for="(workflow, i) in filteredWorkflows"
            @create-form="createFormInstance(workflow.resourceRef.id)"
            @get-notes="getNotes(workflow.resourceRef.id)"
            @checked-box="selectWorkflowCheckbox(workflow.resourceRef.id)"
            :workflow="workflow"
            :index="i + 1 * 1000"
            :oppFields="oppFields"
            :workflowCheckList="workflowCheckList"
            :updateList="updateList"
          />
        </div>
      </section>
      <section
        v-if="currentWorkflow && currentWorkflow.list.length < 1"
        class="empty-table-section"
      >
        <div v-if="!loadingWorkflows">
          <div class="empty-table">
            <div class="table-row">
              <div class="flex-row table-cell-header">
                <h5 style="margin-left: 1rem">No results for the {{ currentList }} workflow.</h5>
              </div>
            </div>
          </div>
        </div>
        <div style="padding: 2rem" v-else>
          <SkeletonBox width="400px" height="25px" />
        </div>
      </section>
    </div>
    <div v-if="loading">
      <PipelineLoader />
      <!-- <img src="@/assets/images/loading-gif.gif" class="invert" style="height: 8rem" alt="" /> -->
    </div>
  </div>
</template>
<script>
import { SObjects, SObjectPicklist } from '@/services/salesforce'
import AlertTemplate, { AlertConfig, AlertInstance } from '@/services/alerts/'
import SkeletonBox from '@/components/SkeletonBox'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth, { salesforceFields } from '@/services/slack'
import DropDownSearch from '@/components/DropDownSearch'
import Modal from '@/components/InviteModal'
import PipelineNameSection from '@/components/PipelineNameSection'
import PipelineField from '@/components/PipelineField'
import PipelineTableRow from '@/components/PipelineTableRow'
import WorkflowRow from '@/components/WorkflowRow'
import PipelineHeader from '@/components/PipelineHeader'
import PipelineLoader from '@/components/PipelineLoader'
import WorkflowHeader from '@/components/WorkflowHeader'
import User from '@/services/users'

export default {
  name: 'Pipelines',
  components: {
    Modal,
    DropDownSearch,
    SkeletonBox,
    PipelineNameSection,
    PipelineField,
    PipelineTableRow,
    PipelineHeader,
    WorkflowHeader,
    WorkflowRow,
    PipelineLoader,
  },
  data() {
    return {
      updatingOpps: false,
      key: 0,
      oppId: null,
      allUsers: null,
      primaryCheckList: [],
      workflowCheckList: [],
      allSelected: false,
      allWorkflowsSelected: false,
      updateList: [],
      currentVals: [],
      closeDateSelected: false,
      advanceStageSelected: false,
      forecastSelected: false,
      selection: false,
      allStages: [],
      allForecasts: [],
      newStage: null,
      newForecast: null,
      originalList: null,
      daysForward: null,
      allOpps: null,
      loading: false,
      loadingWorkflows: false,
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      team: CollectionManager.create({ ModelClass: User }),
      currentWorkflow: null,
      selectedWorkflow: false,
      modalOpen: false,
      editOpModalOpen: false,
      addOppModalOpen: false,
      refreshId: null,
      filterText: '',
      workflowFilterText: '',
      currentList: 'All Opportunities',
      showList: false,
      showWorkflowList: true,
      showPopularList: true,
      notes: [],
      updateOppForm: null,
      oppFormCopy: null,
      createOppForm: null,
      oppFields: [],
      instanceId: null,
      formData: {},
      noteTitle: '',
      noteInfo: '',
      picklistQueryOpts: {},
      instanceIds: [],
    }
  },
  computed: {
    currentCheckList() {
      if (this.primaryCheckList.length > 0) {
        return this.primaryCheckList
      } else if (this.workflowCheckList.length > 0) {
        return this.workflowCheckList
      } else {
        return []
      }
    },
    user() {
      return this.$store.state.user
    },
    allOppsFiltered() {
      return this.allOpps.filter((opp) =>
        opp.name.toLowerCase().includes(this.filterText.toLowerCase()),
      )
    },
    filteredWorkflows() {
      return this.currentWorkflow.list.filter((opp) =>
        opp.resourceRef.name.toLowerCase().includes(this.workflowFilterText.toLowerCase()),
      )
    },
    currentMonth() {
      let date = new Date()
      return date.getMonth()
    },
    currentDay() {
      let date = new Date()
      return date
        .toLocaleDateString()
        .substring(date.toLocaleDateString().indexOf('/') + 1)
        .substring(0, date.toLocaleDateString().indexOf('/') + 1)
    },
    syncDay() {
      return this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime)
        .substring(
          this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime).indexOf(
            '/',
          ) + 1,
        )
        .substring(
          0,
          this.formatDateTime(this.$store.state.user.salesforceAccountRef.lastSyncTime).indexOf(
            '/',
          ),
        )
    },
  },
  created() {
    this.getObjects()
    this.templates.refresh()
    this.getAllForms()
    this.listStages()
    this.listForecast()
    this.resourceSync()
  },
  watch: {
    primaryCheckList: 'closeAll',
    workflowCheckList: 'closeAll',
  },
  methods: {
    test() {
      console.log(this.syncDay)
      console.log(this.currentDay)
    },
    selectPrimaryCheckbox(id) {
      if (this.primaryCheckList.includes(id)) {
        this.primaryCheckList = this.primaryCheckList.filter((opp) => opp !== id)
      } else {
        this.primaryCheckList.push(id)
      }
    },
    selectWorkflowCheckbox(id) {
      if (this.workflowCheckList.includes(id)) {
        this.workflowCheckList = this.workflowCheckList.filter((opp) => opp !== id)
      } else {
        this.workflowCheckList.push(id)
      }
    },
    closeAll() {
      if (this.primaryCheckList.length === 0 || this.workflowCheckList === 0) {
        this.closeDateSelected = false
        this.advanceStageSelected = false
        this.forecastSelected = false
      }
    },
    setStage(val) {
      this.newStage = val
    },
    setForecast(val) {
      this.newForecast = val
    },
    onCheckAll() {
      if (this.primaryCheckList.length < 1) {
        for (let i = 0; i < this.allOppsFiltered.length; i++) {
          this.primaryCheckList.push(this.allOppsFiltered[i].id)
        }
      } else if (
        this.primaryCheckList.length > 0 &&
        this.primaryCheckList.length < this.allOppsFiltered.length
      ) {
        for (let i = 0; i < this.allOppsFiltered.length; i++) {
          !this.primaryCheckList.includes(this.allOppsFiltered[i].id)
            ? this.primaryCheckList.push(this.allOppsFiltered[i].id)
            : (this.primaryCheckList = this.primaryCheckList)
        }
      } else {
        this.primaryCheckList = []
      }
    },
    onCheckAllWorkflows() {
      if (this.workflowCheckList.length < 1) {
        for (let i = 0; i < this.filteredWorkflows.length; i++) {
          this.workflowCheckList.push(this.filteredWorkflows[i].resourceRef.id)
        }
      } else if (
        this.workflowCheckList.length > 0 &&
        this.workflowCheckList.length < this.filteredWorkflows.length
      ) {
        for (let i = 0; i < this.filteredWorkflows.length; i++) {
          !this.workflowCheckList.includes(this.filteredWorkflows[i].resourceRef.id)
            ? this.workflowCheckList.push(this.filteredWorkflows[i].resourceRef.id)
            : (this.workflowCheckList = this.workflowCheckList)
        }
      } else {
        this.workflowCheckList = []
      }
    },
    async listPicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.picklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listStages() {
      try {
        const res = await SObjectPicklist.api.listPicklists({
          salesforceObject: 'Opportunity',
          picklistFor: 'StageName',
        })
        this.allStages = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listForecast() {
      try {
        const res = await SObjectPicklist.api.listPicklists({
          salesforceObject: 'Opportunity',
          picklistFor: 'ForecastCategoryName',
        })
        this.allForecasts = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async refresh(id) {
      this.loadingWorkflows = true
      let counter = 0
      try {
        await AlertTemplate.api.runAlertTemplateNow(id)
        while (counter < 100) {
          this.currentWorkflow.refresh()
          counter += 1
        }
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingWorkflows = false
        }, 3500)
      }
    },
    resetNotes() {
      this.modalOpen = !this.modalOpen
      this.notes = []
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
    },
    resetAddOpp() {
      this.addOppModalOpen = !this.addOppModalOpen
    },
    async createFormInstance(id) {
      this.currentVals = []
      this.editOpModalOpen = true
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'UPDATE',
          resourceId: id,
        })
        this.currentVals = res.current_values
        this.oppId = id
        this.instanceId = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    async createOppInstance() {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'CREATE',
        })
        this.addOppModalOpen = true
        this.instanceId = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    futureDate(val) {
      let currentDate = new Date()
      currentDate.setDate(currentDate.getDate() + Number(val))
      let currentDayOfMonth = currentDate.getDate()
      let currentMonth = currentDate.getMonth()
      let currentYear = currentDate.getFullYear()
      let dateString = currentYear + '-' + (currentMonth + 1) + '-' + currentDayOfMonth
      return dateString
    },
    pushCloseDates(ids, val) {
      this.instanceIds = []
      let data = this.futureDate(val)
      this.createBulkInstance(ids)
      setTimeout(() => {
        this.bulkUpdateCloseDate(this.instanceIds, data)
      }, 1000)
    },
    advanceStage(ids) {
      this.instanceIds = []
      this.createBulkInstance(ids)
      setTimeout(() => {
        this.bulkUpdateStage(this.instanceIds, this.newStage)
      }, 1000)
    },
    changeForecast(ids) {
      this.instanceIds = []
      this.createBulkInstance(ids)
      setTimeout(() => {
        this.bulkChangeForecast(this.instanceIds, this.newForecast)
      }, 1000)
    },
    async createBulkInstance(ids) {
      for (let i = 0; i < ids.length; i++) {
        this.updateList.push(ids[i])
        try {
          const res = await SObjects.api.createFormInstance({
            resourceType: 'Opportunity',
            formType: 'UPDATE',
            resourceId: ids[i],
          })
          this.instanceIds.push(res.form_id)
        } catch (e) {
          console.log(e)
        }
      }
    },
    setUpdateValues(key, val) {
      if (val) {
        this.formData[key] = val
      }
    },
    async bulkUpdateCloseDate(ids, data) {
      this.updatingOpps = true
      for (let i = 0; i < ids.length; i++) {
        try {
          const res = await SObjects.api
            .updateResource({
              form_id: ids[i],
              form_data: { CloseDate: data },
            })
            .then(async () => {
              let updatedRes = await SObjects.api.getObjects('Opportunity')
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
            })
          this.formData = {}
          this.updateList.length > 1 ? this.updateList.shift() : (this.updateList = [])
          this.primaryCheckList.length > 1
            ? this.primaryCheckList.shift()
            : (this.primaryCheckList = [])
          this.workflowCheckList.length > 1
            ? this.workflowCheckList.shift()
            : (this.workflowCheckList = [])
          if (this.selectedWorkflow) {
            this.currentWorkflow.refresh()
          } else if (this.currentList === 'Closing this month') {
            this.stillThisMonth()
          } else if (this.currentList === 'Closing next month') {
            this.stillNextMonth()
          }
        } catch (e) {
          console.log(e)
        }
      }
      this.updatingOpps = false
      this.closeDateSelected = false
      console.log(this.primaryCheckList)
      this.$Alert.alert({
        type: 'success',
        timeout: 3000,
        message: 'Salesforce update successful!',
        sub: 'Some changes may take longer to reflect',
      })
    },
    async bulkUpdateStage(ids, data) {
      this.updatingOpps = true
      for (let i = 0; i < ids.length; i++) {
        try {
          const res = await SObjects.api
            .updateResource({
              form_id: ids[i],
              form_data: { StageName: data },
            })
            .then(async () => {
              let updatedRes = await SObjects.api.getObjects('Opportunity')
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
            })
          this.formData = {}
          this.updateList.length > 1 ? this.updateList.shift() : (this.updateList = [])
          this.primaryCheckList.length > 1
            ? this.primaryCheckList.shift()
            : (this.primaryCheckList = [])
          this.workflowCheckList.length > 1
            ? this.workflowCheckList.shift()
            : (this.workflowCheckList = [])
          if (this.selectedWorkflow) {
            this.currentWorkflow.refresh()
          } else if (this.currentList === 'Closing this month') {
            this.stillThisMonth()
          } else if (this.currentList === 'Closing next month') {
            this.stillNextMonth()
          }
        } catch (e) {
          console.log(e)
        }
      }
      this.updatingOpps = false
      this.advanceStageSelected = false
      this.$Alert.alert({
        type: 'success',
        timeout: 3000,
        message: 'Salesforce update successful!',
        sub: 'Some changes may take longer to reflect',
      })
    },
    async bulkChangeForecast(ids, data) {
      this.updatingOpps = true
      for (let i = 0; i < ids.length; i++) {
        try {
          const res = await SObjects.api
            .updateResource({
              form_id: ids[i],
              form_data: { ForecastCategoryName: data },
            })
            .then(async () => {
              let updatedRes = await SObjects.api.getObjects('Opportunity')
              this.allOpps = updatedRes.results
              this.originalList = updatedRes.results
            })
          this.formData = {}
          this.updateList.length > 1 ? this.updateList.shift() : (this.updateList = [])
          this.primaryCheckList.length > 1
            ? this.primaryCheckList.shift()
            : (this.primaryCheckList = [])
          this.workflowCheckList.length > 1
            ? this.workflowCheckList.shift()
            : (this.workflowCheckList = [])
          if (this.selectedWorkflow) {
            this.currentWorkflow.refresh()
          } else if (this.currentList === 'Closing this month') {
            this.stillThisMonth()
          } else if (this.currentList === 'Closing next month') {
            this.stillNextMonth()
          }
        } catch (e) {
          console.log(e)
        }
      }
      this.updatingOpps = false
      this.forecastSelected = false
      this.$Alert.alert({
        type: 'success',
        timeout: 3000,
        message: 'Salesforce update successful!',
        sub: 'Some changes may take longer to reflect',
      })
    },
    async resourceSync() {
      if (this.currentDay !== this.syncDay) {
        this.loading = true
        try {
          const res = await SObjects.api.resourceSync()
          console.log(res)
        } catch (e) {
          console.log(e)
        } finally {
          this.getObjects()
          this.loading = false
          this.$Alert.alert({
            type: 'success',
            timeout: 3000,
            message: 'Daily Sync complete',
            sub: 'All fields reflect your current SFDC data',
          })
        }
      }
    },
    async updateResource() {
      this.updateList.push(this.oppId)
      this.editOpModalOpen = false
      try {
        const res = await SObjects.api
          .updateResource({
            form_id: this.instanceId,
            form_data: this.formData,
          })
          .then(async () => {
            let updatedRes = await SObjects.api.getObjects('Opportunity')
            this.allOpps = updatedRes.results
            this.originalList = updatedRes.results
          })
        this.updateList = []
        this.formData = {}
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Salesforce update successful!',
          sub: 'Some changes may take longer to reflect',
        })
        if (this.selectedWorkflow) {
          this.currentWorkflow.refresh()
        } else if (this.currentList === 'Closing this month') {
          this.stillThisMonth()
        } else if (this.currentList === 'Closing next month') {
          this.stillNextMonth()
        }
      } catch (e) {
        console.log(e)
      }
    },
    async createResource() {
      this.addOppModalOpen = false
      try {
        const res = await SObjects.api.createResource({
          form_id: this.instanceId,
          form_data: this.formData,
        })
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Opportunity created successfully!',
          sub: 'Refresh to see changes',
        })
      } catch (e) {
        console.log(e)
      }
      this.getAllForms()
    },
    async selectList(configId, title, id) {
      this.refreshId = id
      this.currentList = title
      try {
        this.currentWorkflow = CollectionManager.create({
          ModelClass: AlertInstance,
          filters: {
            byConfig: configId,
          },
        })
        this.currentWorkflow.refresh()
        setTimeout(() => {
          if (this.currentWorkflow.list.length < 1) {
            this.refresh(this.refreshId)
          }
        }, 300)
      } catch (error) {
        console.log(error)
      }
      this.selectedWorkflow = true
      this.showList = false
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.updateOppForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Opportunity',
        )
        this.createOppForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'Opportunity',
        )
        this.oppFormCopy = this.updateOppForm[0].fieldsRef
        this.createOppForm = this.createOppForm[0].fieldsRef
        for (let i = 0; i < this.oppFormCopy.length; i++) {
          if (
            this.oppFormCopy[i].dataType === 'Picklist' ||
            this.oppFormCopy[i].dataType === 'MultiPicklist'
          ) {
            this.picklistQueryOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].apiName
          } else if (this.oppFormCopy[i].dataType === 'Reference') {
            this.picklistQueryOpts[this.oppFormCopy[i].referenceDisplayLabel] =
              this.oppFormCopy[i].referenceDisplayLabel
          }
        }
        console.log(this.picklistQueryOpts)
        for (let i in this.picklistQueryOpts) {
          this.picklistQueryOpts[i] = this.listPicklists(i, { picklistFor: i })
        }
        this.oppFields = this.updateOppForm[0].fieldsRef.filter(
          (field) =>
            field.apiName !== 'meeting_type' &&
            field.apiName !== 'meeting_comments' &&
            field.apiName !== 'Name' &&
            field.apiName !== 'AccountId' &&
            field.apiName !== 'OwnerId',
        )
      } catch (error) {
        console.log(error)
      }
    },
    async getObjects() {
      try {
        const res = await SObjects.api.getObjects('Opportunity')
        this.allOpps = res.results
        this.originalList = res.results
      } catch {
        this.$Alert.alert({
          type: 'error',
          timeout: 2000,
          message: 'There was an error collecting objects',
        })
      }
    },
    async getNotes(id) {
      try {
        const res = await SObjects.api.getNotes({
          resourceId: id,
        })
        this.modalOpen = true
        if (res.length) {
          for (let i = 0; i < res.length; i++) {
            this.notes.push(res[i])
            this.notes = this.notes.filter((note) => note.saved_data__meeting_comments !== null)
          }
        }
      } catch (e) {
        console.log(e)
      }
    },
    async handleCancel() {
      await this.refresh()
      this.resetNotes()
      this.$emit('cancel')
    },
    addOpp() {
      this.addOppModalOpen = true
    },
    closeDatesThisMonth() {
      this.allOpps = this.originalList
      this.selectedWorkflow = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.close_date).getMonth() == this.currentMonth,
      )
      this.currentList = 'Closing this month'
      this.showList = !this.showList
    },
    stillThisMonth() {
      this.allOpps = this.originalList
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.close_date).getMonth() == this.currentMonth,
      )
      this.currentList = 'Closing this month'
    },
    closeDatesNextMonth() {
      this.allOpps = this.originalList
      this.selectedWorkflow = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.close_date).getMonth() == this.currentMonth + 1,
      )
      this.currentList = 'Closing next month'
      this.showList = !this.showList
    },
    stillNextMonth() {
      this.allOpps = this.originalList
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.close_date).getMonth() == this.currentMonth + 1,
      )
      this.currentList = 'Closing next month'
    },
    allOpportunities() {
      this.selectedWorkflow = false
      this.allOpps = this.originalList
      this.currentList = 'All Opportunities'
      this.showList = !this.showList
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
  },
}
</script>
<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';
.select-btn {
  border: none;
  min-height: 4.5vh;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 1px 1px 2px $very-light-gray;
  border-radius: 0.25rem;
  background-color: white;
  cursor: pointer;
  color: $dark-green;
  letter-spacing: 0.2px;
  margin-right: 0.5rem;
  transition: all 0.25s;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
.select-btn:hover {
  transform: scale(1.02);
  box-shadow: 1px 2px 3px $very-light-gray;
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
input[type='date']::-webkit-datetime-edit-text,
input[type='date']::-webkit-datetime-edit-month-field,
input[type='date']::-webkit-datetime-edit-day-field,
input[type='date']::-webkit-datetime-edit-year-field {
  color: #888;
  cursor: pointer;
  padding-left: 0.5rem;
}
input {
  padding: 7px;
}
h3 {
  font-size: 22px;
}
.table-section {
  margin: 0;
  padding: 0;
  max-height: 76vh;
  overflow: scroll;
  margin-top: 0.5rem;
  border-radius: 5px;
  box-shadow: 2px 2px 20px 2px $soft-gray;
  background-color: $off-white;
}
.empty-table-section {
  height: 30vh;
  margin-top: 2rem;
  border-radius: 5px;
  box-shadow: 1px 1px 20px 1px $soft-gray;
  background-color: $off-white;
}
.table {
  display: table;
  overflow: scroll;
  width: 100vw;
}
.empty-table {
  display: table;
  width: 98vw;
}
.table-row {
  display: table-row;
}
.table-cell {
  display: table-cell;
  position: sticky;
  min-width: 12vw;
  background-color: $off-white;
  padding: 2vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.table-cell-wide {
  display: table-cell;
  position: sticky;
  min-width: 26vw;
  background-color: $off-white;
  padding: 2vh 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.table-cell:hover {
  cursor: text;
  background-color: white;
}
.modal-container {
  background-color: $white;
  overflow: hidden;
  width: 30vw;
  min-height: 60vh;
  align-items: center;
  border-radius: 0.3rem;
  padding: 0.25rem;
  box-shadow: 2px 2px 10px 2px $base-gray;
}
.close-button {
  border-radius: 50%;
  background-color: white;
  box-shadow: 1px 1px 1px 1px $very-light-gray;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -1rem;
  padding: 0.25rem;
  cursor: pointer;
  img {
    filter: invert(80%);
  }
}
.opp-modal-container {
  overflow: hidden;
  background-color: white;
  height: 80vh;
  max-width: 34vw;
  align-items: center;
  border-radius: 0.6rem;
  padding: 1rem;
  box-shadow: 1px 3px 7px $base-gray;
}
.opp-modal {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  overflow-y: scroll;
  height: 56vh;
  border-radius: 0.25rem;
  border-bottom: 3px solid $white;
  color: $base-gray;
  font-size: 16px;
  div {
    margin-right: 1rem;
  }
}
.note-section {
  padding: 0.5rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 16px;
    font-weight: bold;
    color: $dark-green;
    letter-spacing: 1px;
  }
  &__body {
    color: $base-gray;
  }
  &__date {
    color: $mid-gray;
    font-size: 11px;
  }
}
.table-cell-checkbox {
  display: table-cell;
  padding: 2vh;
  width: 3.75vw;
  border: none;
  left: 0;
  position: sticky;
  z-index: 1;
  border-bottom: 1px solid $soft-gray;
  background-color: $off-white;
}
.table-cell-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 2;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
.limit-cell-height {
  max-height: 4rem;
  width: 110%;
  overflow: auto;
  direction: rtl;
  padding: 0px 0.25rem;
}
.cell-name-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 3;
  left: 3.5vw;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
.table-cell-checkbox-header {
  display: table-cell;
  padding: 2vh 1vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  z-index: 3;
  width: 4vw;
  top: 0;
  left: 0;
  position: sticky;
  background-color: $off-white;
}
.cell-name {
  background-color: white;
  color: $base-gray;
  letter-spacing: 0.25px;
  position: sticky;
  left: 3.5vw;
  z-index: 2;
}
input[type='search'] {
  border: none;
  background-color: $off-white;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
input[type='text']:focus {
  outline: none;
  cursor: text;
}
input[type='checkbox'] {
  cursor: pointer;
}
select {
  cursor: pointer;
}
option:not(:first-of-type) {
  color: black;
}
header,
section {
  margin: 0;
  padding: 0px;
}
.flex-row {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
}
.flex-row-pad {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0rem 0.5rem;
}
.bulk-action {
  margin: 0.75rem 0rem;
  &__title {
    font-weight: bold;
    font-size: 14px;
    color: $base-gray;
    margin-left: 0.5rem;
  }
}
.flex-col {
  display: flex;
  flex-direction: column;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.pipelines {
  margin-top: 4rem;
  color: $base-gray;
}
.invert {
  filter: invert(80%);
}
.add-button:disabled {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $gray;
  cursor: not-allowed;
  color: white;
}
.add-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}
.add-button__ {
  display: flex;
  align-items: center;
  border: none;
  min-height: 4.5vh;
  padding: 0.5rem 1rem;
  font-size: 16px;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}
.soon-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $very-light-gray;
  cursor: text;
  color: $base-gray;
  font-weight: bold;
  font-size: 11px;

  img {
    filter: invert(80%);
  }
}

.add-button:hover {
  transform: scale(1.03);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.add-button__:hover {
  transform: scale(1.03);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.search-bar {
  height: 4.5vh;
  background-color: $off-white;
  box-shadow: 1px 1px 1px $very-light-gray;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 5px;
  margin-right: 0.5rem;
}
#update-input {
  border: 1px solid $very-light-gray;
  border-radius: 0.25rem;
  background-color: transparent;
  min-height: 4.5vh;
  min-width: 14vw;
}
.number-input {
  background-color: $off-white;
  box-shadow: 1px 1px 1px $gray;
  border: 2px solid $light-orange-gray;
  border-radius: 5px;
  min-height: 4vh;
  margin-right: 1rem;
  margin-left: 0.5rem;
  width: 6vw;
}
#update-input:focus,
.number-input:focus {
  outline: 1px solid $lighter-green;
}
.loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  filter: invert(99%);
}
.invert {
  filter: invert(99%);
}
.gray {
  filter: invert(44%);
}
.name-cell-note-button {
  cursor: pointer;
  border: none;
  border-radius: 0.2rem;
  padding: 0.2rem;
  background-color: white;
  box-shadow: 1px 1px 3px $very-light-gray;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: space-around;
  font-size: 10px;
  font-weight: 700px;
  letter-spacing: 0.25px;
  img {
    height: 0.8rem;
  }
}
.name-cell-note-button:hover,
.name-cell-edit-note-button:hover {
  transform: scale(1.03);
  box-shadow: 1px 1px 1px 1px $very-light-gray;
}
.name-cell-edit-note-button {
  cursor: pointer;
  border: none;
  border-radius: 0.2rem;
  padding: 0.2rem;
  background-color: $dark-green;
  color: white;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 10px;
  box-shadow: 1px 1px 2px $very-light-gray;
  font-weight: 700px;
  letter-spacing: 0.25px;
  margin-bottom: 0.5rem;

  img {
    height: 0.8rem;
    margin-left: 0.25rem;
  }
}
.header {
  font-size: 18px;
  letter-spacing: 0.5px;
  margin-bottom: 0.2rem;
}
.list-section {
  z-index: 4;
  position: absolute;
  top: 8vh;
  left: 0;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 16vw;
  max-height: 40vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    color: $dark-green;
    letter-spacing: 0.25px;
    margin-left: 0.75rem;
    font-weight: bold;
    font-size: 15px;
    width: 100%;
  }
  &__sub-title {
    font-size: 12px;
    font-weight: bold;
    display: flex;
    align-items: center;
    margin-left: 0.75rem;
    color: $base-gray;
    cursor: pointer;
    width: 100%;
    img {
      margin: 2px 0px 0px 3px;
      height: 0.75rem;
      filter: invert(70%);
    }
  }
}
.list-button {
  display: flex;
  align-items: center;
  height: 4.5vh;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75rem;
  border-radius: 0.2rem;
  color: $mid-gray;
  cursor: pointer;
  font-size: 11px;
  font-weight: bold;
}
.list-button:hover {
  color: $dark-green;
  background-color: $off-white;
}
.filter {
  color: #199e54;
  margin-left: 0.2rem;
}
.exit {
  padding-right: 1.25rem;
  margin-top: -0.5rem;
  height: 1rem;
  cursor: pointer;
}
.cancel {
  color: $dark-green;
  font-weight: bold;
  margin-right: 1rem;
  cursor: pointer;
}
.flex-end {
  width: 100%;
  padding: 2rem 0.25rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.flex-end-opp {
  width: 100%;
  padding: 0.5rem 0.25rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
</style>