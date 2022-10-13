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
      <div v-if="notes.length" class="modal-container rel">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h4>Notes</h4>
          </div>

          <div class="flex-row">
            <small class="note-border">Total: {{ notesLength }}</small>
            <small class="note-border light-green-bg"
              >Most recent: {{ formatMostRecent(notes[0].submission_date) }} days</small
            >
            <small class="note-border"
              >Oldest: {{ formatMostRecent(notes[notes.length - 1].submission_date) }} days</small
            >
          </div>
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{ note.saved_data__meeting_type ? note.saved_data__meeting_type : 'Untitled' }}
          </p>
          <p class="note-section__date">{{ formatDateTime(note.submission_date) }}</p>
          <pre v-html="note.saved_data__meeting_comments" class="note-section__body"></pre>
        </section>
      </div>
      <div v-else class="modal-container">
        <div class="flex-row-spread sticky border-bottom">
          <div class="flex-row">
            <img src="@/assets/images/logo.png" class="logo" alt="" />
            <h4>Notes</h4>
          </div>

          <div class="flex-row">
            <small class="note-border">Total: {{ notesLength }}</small>
            <small class="note-border light-green-bg">Most recent: 0 days</small>
            <small class="note-border">Oldest: 0 days</small>
          </div>
        </div>
        <section class="note-section">
          <p class="note-section__body">No notes for selected Record</p>
        </section>
      </div>
    </Modal>
    <section
      v-if="meetingOpen"
      dimmed
      @close-modal="
        () => {
          //$emit('cancel'), resetMeeting()
        }
      "
    >
      <div class="create-modal">
        <div class="form-field">
          <p>Meeting Title</p>
          <input v-model="meetingTitle" class="zoom-input" type="text" id="title" />
        </div>

        <div class="form-field">
          <p for="description">Meeting Description</p>
          <textarea v-model="description" class="zoom-input-ta" type="text" id="description" />
        </div>

        <div class="form-field">
          <p for="startDate">Date</p>
          <input id="startDate" v-model="startDate" class="zoom-input" type="date" />
        </div>

        <div class="form-field">
          <p for="startTime">Time</p>
          <input id="startTime" v-model="startTime" class="zoom-input" type="time" />
        </div>

        <div class="form-field">
          <p>Duration</p>
          <Multiselect
            placeholder="Duration"
            style="width: 32vw"
            v-model="meetingDuration"
            :options="fiveMinuteIntervals"
            openDirection="below"
            :multiple="false"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
        </div>

        <div class="form-field">
          <p>Internal Participants</p>
          <Multiselect
            placeholder="Internal Users"
            style="width: 32vw"
            v-model="internalParticipantsSelected"
            :options="internalParticipants"
            openDirection="below"
            selectLabel="Enter"
            track-by="id"
            :custom-label="internalCustomLabel"
            :multiple="true"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
        </div>

        <div class="form-field">
          <p>External Participants</p>
          <Multiselect
            placeholder="External Users"
            style="width: 32vw; margin-bottom: 1rem"
            v-model="externalParticipantsSelected"
            :options="externalParticipants"
            openDirection="above"
            selectLabel="Enter"
            track-by="id"
            :custom-label="externalCustomLabel"
            :multiple="true"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
            <template slot="afterList">
              <p v-if="hasNext" @click="addMoreContacts" class="multi-slot__more">
                Load more <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
              </p>
              <p v-else class="multi-slot__more" style="color: #4d4e4c; cursor: text">
                End of list
              </p>
            </template>
          </Multiselect>
        </div>

        <div class="form-field">
          <p class="label">Additional Users</p>
          <input
            :class="
              extraParticipantsSelected.length ? 'zoom-input' : 'light-gray-placeholder zoom-input'
            "
            v-model="extraParticipantsSelected"
            type="text"
            placeholder="Separate emails by commas"
          />
        </div>
      </div>
    </section>

    <div v-if="editOpModalOpen">
      <UpdateForm
        @reset-edit="resetEdit"
        @add-product="addProduct"
        @set-update-values="setUpdateValues"
        @set-template="setTemplate"
        @update-resource="updateResource"
        @update-meeting="onMakeMeetingUpdate"
        @create-product="createProduct"
        @set-create-values="setCreateValues"
        @set-validation-values="setUpdateValidationValues"
        @get-pricebooks="getPricebookEntries"
        @get-accounts="getAccounts"
        @load-more="loadMore"
        @edit-product="editProduct"
        @update-product="updateProduct"
        @cancel-edit-product="cancelEditProduct"
        @set-product-values="setProductValues"
        @go-to-profile="goToProfile"
        :resource="resourceType"
        :productReferenceOpts="productReferenceOpts"
        :fields="resourceFields"
        :currentVals="currentVals"
        :noteTitle="noteTitle"
        :allAccounts="allAccounts"
        :selectedAccount="selectedAccount"
        :hasProducts="hasProducts"
        :allPicklistOptions="apiPicklistOptions"
        :pricebooks="pricebooks"
        :noteValue="noteValue"
        :noteTemplates="noteTemplates"
        :dropdownLoading="dropdownLoading"
        :stageGateField="stageGateField"
        :stagePicklistQueryOpts="stagePicklistQueryOpts"
        :stageValidationFields="stageValidationFields"
        :currentAccount="currentAccount"
        :referenceOpts="currentRefList"
        :loadingAccounts="loadingAccounts"
        :addingProduct="addingProduct"
        :pricebookId="pricebookId"
        :createProductForm="createProductForm"
        :loadingProducts="loadingProducts"
        :savingCreateForm="savingCreateForm"
        :showLoadMore="showLoadMore"
        :currentProducts="currentProducts"
        :editingProduct="editingProduct"
        :productName="productName"
        :savingProduct="savingProduct"
        :currentSelectedProduct="currentSelectedProduct"
        :dropdownProductVal="dropdownProductVal"
        :dropdownVal="dropdownVal"
      />
    </div>

    <div class="alerts-header">
      <div class="results-title">
        <p v-if="!meetingOpen">
          Meetings : <span>{{ meetings.length }}</span>
        </p>

        <button class="back-button" @click="resetMeeting()" v-else>
          <img src="@/assets/images/left.svg" height="12px" alt="" /> Back
        </button>
      </div>

      <h3 v-if="meetingOpen">Create Zoom Meeting</h3>

      <div v-if="!meetingOpen" class="flex-row">
        <div class="tooltip">
          <button @click="refreshCalEvents" class="img-button">
            <img src="@/assets/images/refresh.svg" alt="" style="height: 22px" />
          </button>
          <span class="tooltiptext">Sync Calendar</span>
        </div>

        <button
          @click="resetMeeting()"
          style="margin-left: 8px"
          class="green_button"
          :disabled="!hasZoomIntegration"
        >
          Schedule Zoom
        </button>
      </div>

      <div v-else>
        <button v-if="!submitting" class="green_button" @click="submitZoomMeeting">
          Create Meeting
        </button>
        <div v-else>
          <PipelineLoader />
        </div>
      </div>
    </div>

    <div class="container" ref="pipelines" v-if="!loading && !meetingOpen">
      <div v-if="meetings.length">
        <MeetingWorkflow
          v-for="(meeting, i) in meetings"
          :key="i"
          @map-opp="mapOpp"
          @update-Opportunity="updateMeeting"
          @no-update="NoMeetingUpdate"
          @remove-participant="removeParticipant"
          @add-participant="addParticipant"
          @get-notes="getNotes"
          @filter-accounts="getAccounts"
          @change-resource="changeResource"
          :dropdowns="picklistQueryOptsContacts"
          :contactFields="createContactForm"
          :meeting="meeting.meeting_ref"
          :participants="meeting.meeting_ref.participants"
          :workflowId="meeting.id"
          :resourceId="meeting.resource_id"
          :resourceRef="meeting.resource_ref"
          :resourceType="meeting.resource_type ? meeting.resource_type : resourceType"
          :meetingUpdated="meeting.is_completed"
          :owners="allUsers"
          :accounts="allAccounts"
          :meetingLoading="meetingLoading"
          :allOpps="allOpps"
          :allPicklistOptions="allPicklistOptions"
          :referenceOpts="contactCreateReferenceOpts"
          :dropdownLoading="dropdownLoading"
          :accountSobjectId="accountSobjectId"
          :index="i"
        />
      </div>
      <div v-else class="empty-list">
        <section class="bg-img"></section>
        <h3>No meetings found.</h3>
        <p>You may need to sync your calendar</p>
        <button @click="refreshCalEvents" class="green_button">Sync calendar</button>
      </div>
    </div>

    <div v-if="loading">
      <Loader :loaderText="loaderText" />
    </div>
  </div>
</template>
<script>
import { SObjects, SObjectPicklist, MeetingWorkflows } from '@/services/salesforce'
import AlertTemplate from '@/services/alerts/'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth from '@/services/slack'
import Zoom from '@/services/zoom/account'
import MeetingWorkflow from '@/components/MeetingWorkflow'
import MeetingWorkflowHeader from '@/components/MeetingWorkflowHeader'
import UpdateForm from '@/components/updateForm/'
import User from '@/services/users'

export default {
  name: 'Meetings',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    SkeletonBox: () => import(/* webpackPrefetch: true */ '@/components/SkeletonBox'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    MeetingWorkflowHeader,
    MeetingWorkflow,
    UpdateForm,
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  data() {
    return {
      selectedDate: null,
      contactCreateReferenceOpts: {},
      currentSelectedProduct: null,
      savingProduct: null,
      productName: null,
      editingProduct: false,
      productId: null,
      productIntegrationId: null,
      currentProducts: [],
      updateProductData: {},
      resourceType: 'Opportunity',
      resourceFields: null,
      selectedPricebook: null,
      pricebookId: null,
      createData: {},
      productRefCopy: {},
      productReferenceOpts: {},
      allPicklistOptions: {},
      apiPicklistOptions: {},
      createReferenceOpts: {},
      page: 1,
      savingCreateForm: false,
      hasNext: false,
      noteTitle: null,
      noteTemplates: null,
      noteValue: null,
      addingTemplate: false,
      submitting: false,
      meetingOpen: false,
      integrationId: null,
      stageGateField: null,
      stageValidationFields: {},
      stagesWithForms: [],
      dropdownVal: {},
      countSets: 0,
      dropdownLoading: false,
      loadingProducts: false,
      pricebooks: null,
      selectedPriceBook: null,
      pricebookPage: 1,
      savedPricebookEntryId: '',
      showLoadMore: false,
      updatingMeeting: false,
      meetingWorkflowId: null,
      meetingLoading: null,
      updatingOpps: false,
      oppInstanceId: null,
      oppId: null,
      primaryCheckList: [],
      workflowCheckList: [],
      allSelected: false,
      allWorkflowsSelected: false,
      createQueryOpts: {},
      updateList: [],
      recapList: [],
      currentVals: [],
      closeDateSelected: false,
      advanceStageSelected: false,
      forecastSelected: false,
      selection: false,
      allStages: [],
      allForecasts: [],
      originalList: null,
      daysForward: null,
      allOpps: null,
      loading: false,
      loadingWorkflows: false,
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      users: CollectionManager.create({ ModelClass: User }),
      stagePicklistQueryOpts: {},
      currentWorkflow: null,
      selectedWorkflow: false,
      modalOpen: false,
      editOpModalOpen: false,
      addOppModalOpen: false,
      refreshId: null,
      currentList: "Today's Meetings",
      alertInstanceId: null,
      showList: false,
      showWorkflowList: true,
      loadingAccounts: false,
      accountSobjectId: null,
      currentOwner: null,
      currentAccount: null,
      selectedAccount: null,
      selectedOwner: null,
      showPopularList: true,
      updateOppForm: null,
      oppFormCopy: null,
      createContactForm: null,
      updateContactForm: null,
      updateAccountForm: null,
      updateLeadForm: null,
      instanceId: null,
      contactInstanceId: null,
      formData: {},
      picklistQueryOpts: {},
      picklistQueryOptsContacts: {},
      allAccounts: null,
      allUsers: null,
      showMeetingList: true,
      selectedMeeting: false,
      createProductForm: null,
      // meetings: null,
      referenceOpts: {},
      accountReferenceOpts: {},
      contactReferenceOpts: {},
      leadReferenceOpts: {},
      currentRefList: null,
      fiveMinuteIntervals: [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
      meetingTitle: '',
      description: '',
      startDate: null,
      startTime: null,
      meetingDuration: 30,
      internalParticipants: null,
      externalParticipants: null,
      internalParticipantsSelected: [],
      externalParticipantsSelected: [],
      extraParticipantsSelected: '',
      stageGateId: null,
      notes: [],
      notesLength: 0,
      addingProduct: false,
      stageGateCopy: null,
      stageReferenceOpts: {},
      days: {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
      },
      loaderText: 'Pulling in your meetings',
    }
  },
  computed: {
    allMeetingsUpdated() {
      return this.$store.state.meetings.every((meeting) => meeting.is_completed)
      // console.log(this.$store.state.meetings.every((meeting) => meeting.is_completed))
    },
    user() {
      return this.$store.state.user
    },
    hasZoomIntegration() {
      return !!this.$store.state.user.zoomAccount && this.$store.state.user.hasZoomIntegration
    },
    hasProducts() {
      return this.$store.state.user.organizationRef.hasProducts
    },
    meetings() {
      return this.$store.state.meetings
    },
  },
  created() {
    // this.getMeetingList()
    // this.$store.dispatch('loadMeetings')
    // this.getObjects()
    this.getAllForms()
    this.getAllPicklist()
    this.getPricebooks()
    this.templates.refresh()
  },
  beforeMount() {
    this.getUsers()
    this.getExternalParticipants()
  },
  mounted() {
    this.getTemplates()
  },
  watch: {
    accountSobjectId: 'getInitialAccounts',
    updateOppForm: ['setForms', 'filtersAndOppFields'],
    stageGateField: 'stageGateInstance',
    resourceType: ['selectFormFields'],
  },
  methods: {
    // resourceSelect(resType) {
    //   let i = 'Opportunity'
    //   resType !== this.resourceType ? i = this.resourceType : i = resType
    //   return i
    // },
    cancelEditProduct() {
      this.dropdownProductVal = {}
      this.editingProduct = !this.editingProduct
    },
    editProduct(integrationId, id, name, secondaryData) {
      this.editingProduct = true
      this.productIntegrationId = integrationId
      this.productId = id
      this.productName = name
      this.currentSelectedProduct = secondaryData
    },
    changeResource(i) {
      this.resourceType = i
    },
    selectFormFields() {
      switch (this.resourceType) {
        case 'Opportunity':
          this.resourceFields = this.oppFormCopy
          this.currentRefList = this.referenceOpts
          break
        case 'Account':
          this.resourceFields = this.updateAccountForm
          this.currentRefList = this.accountReferenceOpts
          break
        case 'Contact':
          this.resourceFields = this.updateContactForm
          this.currentRefList = this.contactReferenceOpts
          break
        case 'Lead':
          this.resourceFields = this.updateLeadForm
          this.currentRefList = this.leadReferenceOpts
          break
        default:
          return
      }
    },
    async getTemplates() {
      try {
        const res = await User.api.getTemplates()
        this.noteTemplates = res.results
      } catch (e) {
        console.log(e)
      }
    },
    setTemplate(val, field, title) {
      this.noteTitle = title
      this.addingTemplate = false
      this.noteValue = val
      this.setUpdateValues(field, val)
      this.setUpdateValues('meeting_type', title ? title : null)
    },
    addProduct() {
      this.addingProduct = !this.addingProduct
    },
    resetMeeting() {
      this.clearData()
      this.meetingOpen = !this.meetingOpen
    },
    async submitZoomMeeting() {
      this.submitting = true
      if (
        !this.meetingTitle ||
        !this.startDate ||
        !this.startTime ||
        !this.meetingDuration ||
        !this.externalParticipantsSelected
      ) {
        this.$toast('Please input all information', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.submitting = false
        return
      }
      let noSpacesExtra = ''
      for (let i = 0; i < this.extraParticipantsSelected.length; i++) {
        this.extraParticipantsSelected[i] !== ' '
          ? (noSpacesExtra += this.extraParticipantsSelected[i])
          : null
      }
      let extraParticipants = []
      if (noSpacesExtra) {
        extraParticipants = noSpacesExtra.split(',')
      }
      let extra_participants = []
      for (let i = 0; i < extraParticipants.length; i++) {
        const participant = extraParticipants[i]
        if (participant.length) {
          extra_participants.push(participant)
        }
      }
      if (
        !(
          this.internalParticipantsSelected.length ||
          this.externalParticipantsSelected.length ||
          extra_participants.length
        )
      ) {
        this.$toast('Please add participants to the meeting', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.submitting = false
        return
      }
      const hourMinute = this.startTime.split(':')
      const contacts = this.externalParticipantsSelected.map((contact) => contact.id)
      const internal = this.internalParticipantsSelected.map((internal) => internal.id)
      const data = {
        meeting_topic: this.meetingTitle,
        meeting_description: this.description,
        meeting_date: this.startDate,
        meeting_hour: hourMinute[0],
        meeting_minute: hourMinute[1],
        meeting_time: this.startTime,
        meeting_duration: this.meetingDuration,
        contacts,
        internal,
        extra_participants,
      }

      try {
        const res = await Zoom.api.createZoomMeeting(data)
        if (res.status === 200) {
          this.$toast('Meeting Scheduled', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Error Scheduling Meeting', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } catch (e) {
        console.log(e)
      } finally {
        this.submitting = false
        this.resetMeeting()
      }
    },
    setCreateValues(key, val) {
      if (val) {
        this.createData[key] = val
      }
    },
    async createProduct(id = this.integrationId) {
      if (this.addingProduct) {
        try {
          const res = await SObjects.api.createResource({
            integration_ids: [id],
            form_type: 'CREATE',
            resource_type: 'OpportunityLineItem',
            // stage_name: this.stageGateField ? this.stageGateField : null,
            resource_id: this.oppId,
            form_data: this.createData,
          })

          this.$toast('Product created successfully', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } catch (e) {
          this.$toast(`${e.response.data.error}`, {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.addingProduct = !this.addingProduct
        }
      } else {
        return
      }
    },
    resetNotes() {
      this.modalOpen = !this.modalOpen
      this.notes = []
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
            this.notesLength = this.notes.length
          }
        }
      } catch (e) {
        this.$toast('Error gathering Notes!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    clearData() {
      this.meetingTitle = ''
      this.description = ''
      this.startDate = null
      this.startTime = null
      this.meetingDuration = 30
      this.internalParticipantsSelected = []
      this.externalParticipantsSelected = []
      this.extraParticipantsSelected = ''
    },
    async getAllPicklist() {
      try {
        const res = await SObjectPicklist.api.listPicklists({ pageSize: 1000 })
        for (let i = 0; i < res.length; i++) {
          this.allPicklistOptions[res[i].fieldRef.id] = res[i].values
          this.apiPicklistOptions[res[i].fieldRef.apiName] = res[i].values
        }
      } catch (e) {
        console.log(e)
      }
    },
    async stageGateInstance(field) {
      this.stageGateId = null
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'STAGE_GATING',
          stageName: field ? field : this.stageGateField,
        })
        this.stageGateId = res.form_id
      } catch (e) {
        this.$toast('Error creating stage form instance', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getReferenceFieldList(key, val, type, eventVal) {
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: val,
          value: eventVal ? eventVal : '',
        })
        if (type === 'update') {
          this.referenceOpts[key] = res
        } else if (type === 'createProduct') {
          this.productReferenceOpts[key] = res
        } else if (type === 'updateAccount') {
          this.accountReferenceOpts[key] = res
        } else if (type === 'updateContact') {
          this.contactReferenceOpts[key] = res
        } else if (type === 'createContact') {
          this.contactCreateReferenceOpts[key] = res
        } else if (type === 'updateLead') {
          this.leadReferenceOpts[key] = res
        }
        this.referenceOpts[key] = res
      } catch (e) {
        this.$toast('Error gathering reference fields', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async refreshCalEvents() {
      let response
      try {
        response = await User.api.refreshCalendarEvents()
      } catch (e) {
        console.log('Error in refreshCalEvents: ', e)
      } finally {
        this.loading = true
        this.loaderText = 'Pulling your calendar events...'
        setTimeout(() => {
          this.loaderText = 'Mapping to Salesforce...'
          this.getMeetingList()
          setTimeout(() => {
            this.loading = false
            this.loaderText = 'Pulling in your meetings'
            this.getMeetingList()
            if (response.status === 200) {
              this.$toast('Calendar Successfully Synced', {
                timeout: 2000,
                position: 'top-left',
                type: 'success',
                toastClassName: 'custom',
                bodyClassName: ['custom'],
              })
            } else {
              this.$toast('Error Syncing Calendar', {
                timeout: 2000,
                position: 'top-left',
                type: 'error',
                toastClassName: 'custom',
                bodyClassName: ['custom'],
              })
            }
          }, 3000)
        }, 2000)
      }
    },
    async getMeetingList() {
      try {
        const res = await MeetingWorkflows.api.getMeetingList()
        this.meetings = res.results
      } catch (e) {
        this.$toast('Error gathering Meetings!', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
      }
    },
    async mapOpp(workflow, resource, resourceType) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api
          .mapMeeting(workflow, resource, resourceType)
          .then(() => {
            this.getMeetingList()
          })
      } catch (e) {
        this.$toast('Error mapping record', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        setTimeout(() => {
          this.meetingLoading = false
        }, 500)
      }
    },
    async removeParticipant(workflow, participant) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api.removeParticipant(workflow, participant).then(() => {
          this.getMeetingList()
        })
      } catch (e) {
        this.$toast('Error removing participant', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        setTimeout(() => {
          this.meetingLoading = false
        }, 500)
      }
    },
    async addParticipant(workflow, participant, data) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api
          .updateParticipant({
            workflow_id: workflow,
            tracking_id: participant,
            form_data: data,
          })
          .then(() => {
            this.getMeetingList()
          })
      } catch (e) {
        console.log(e)
        // this.$toast('Error adding contact', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'error',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
      } finally {
        setTimeout(() => {
          this.meetingLoading = false
          this.$toast('Contact Added Successfully', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }, 500)
      }
    },
    goToProfile() {
      this.$router.push({ name: 'InviteUsers' })
    },
    selectMeeting(name) {
      this.currentList = name
      this.showList = false
      this.selectedMeeting = true
      this.selectedWorkflow = false
    },
    closeListSelect() {
      this.showList = false
    },
    async listPicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.picklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listStagePicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.stagePicklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listCreatePicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.createQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
    },
    resetAddOpp() {
      this.addOppModalOpen = !this.addOppModalOpen
    },
    async updateContactInstance() {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Contact',
          formType: 'UPDATE',
        })
        this.contactInstanceId = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    async NoMeetingUpdate(meetingWorkflow) {
      this.meetingLoading = true
      try {
        const res = await MeetingWorkflows.api
          .updateWorkflow({
            workflow_id: meetingWorkflow,
            form_data: {
              meeting_type: 'No Update',
              meeting_comments: 'No Update',
            },
            stage_form_id: [],
          })
          .then(() => {
            this.getMeetingList()
          })
      } catch (e) {
        this.$toast('Meeting log unsuccessful, error with no update', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.meetingLoading = false
        this.$toast('Meeting logged Successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async updateProduct() {
      this.savingProduct = true
      try {
        const res = await SObjects.api
          .updateResource({
            form_data: this.updateProductData,
            from_workflow: this.selectedWorkflow ? true : false,
            workflow_title: this.selectedWorkflow ? this.currentWorkflowName : 'None',
            form_type: 'UPDATE',
            integration_ids: [this.productIntegrationId],
            resource_type: 'OpportunityLineItem',
            resource_id: this.productId,
            stage_name: null,
          })
          .then(async (res) => {
            const res2 = await SObjects.api.getCurrentValues({
              resourceType: 'Opportunity',
              resourceId: this.oppId,
            })
            this.currentProducts = res2.current_products
          })
        this.$toast('Product updated successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast('Error updating Product', {
          timeout: 1500,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.editingProduct = false
        this.savingProduct = false
      }
    },
    async updateMeeting(resourceType, meetingWorkflow, id, integrationId, pricebookId) {
      this.resourceType = resourceType
      pricebookId ? (this.pricebookId = pricebookId) : (this.pricebookId = null)
      this.dropdownLoading = true
      this.currentVals = []
      this.editOpModalOpen = true
      this.updatingMeeting = true
      this.meetingWorkflowId = meetingWorkflow
      this.dropdownVal = {}
      this.formData = {}
      this.createData = {}
      this.oppId = id
      this.integrationId = integrationId
      this.noteValue = null
      this.noteTitle = null
      this.addingProduct = false
      this.updateProductData = {}
      this.productId = null
      this.productIntegrationId = null
      this.dropdownProductVal = {}
      this.editingProduct = false
      try {
        const res = await SObjects.api.getCurrentValues({
          resourceType: resourceType,
          resourceId: id,
        })
        this.currentVals = res.current_values
        this.currentProducts = res.current_products

        this.currentOwner = this.allUsers.filter(
          (user) => user.salesforce_account_ref.salesforce_id === this.currentVals['OwnerId'],
        )[0].full_name

        this.allOpps.filter((opp) => opp.id === this.oppId)[0].account_ref
          ? (this.currentAccount = this.allOpps.filter(
              (opp) => opp.id === this.oppId,
            )[0].account_ref.name)
          : (this.currentAccount = 'Account')
      } catch (e) {
        // this.$toast('Error creating update form', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'error',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
      } finally {
        pricebookId ? this.getPricebookEntries(pricebookId) : null
        this.dropdownLoading = false
      }
    },
    async onMakeMeetingUpdate() {
      this.meetingLoading = true
      this.editOpModalOpen = false
      try {
        const res = await MeetingWorkflows.api
          .updateWorkflow({
            workflow_id: this.meetingWorkflowId,
            stage_form_id: this.stageGateId ? [this.stageGateId] : [],
            form_data: this.formData,
          })
          .then((res) => {
            this.getMeetingList()
          })
        this.$toast('Meeting logged Successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast(`${e.response.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.updatingMeeting = false
        this.meetingLoading = false
      }
    },
    async loadMore() {
      if (!this.savedPricebookEntryId) {
        return
      }
      try {
        this.loadingProducts = true
        this.savedProductedReferenceOps = [...this.productReferenceOpts['PricebookEntryId']]
        const res = await SObjects.api.getObjects('PricebookEntry', this.pricebookPage, true, [
          ['EQUALS', 'Pricebook2Id', this.savedPricebookEntryId],
        ])
        this.productReferenceOpts['PricebookEntryId'] = [
          ...res.results,
          ...this.savedProductedReferenceOps,
        ]
        if (res.next) {
          this.pricebookPage++
          this.showLoadMore = true
        } else {
          this.showLoadMore = false
        }
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingProducts = false
        }, 1000)
      }
    },
    async getPricebooks() {
      const res = await SObjects.api.getObjects('Pricebook2')
      this.pricebooks = res.results
    },
    async getPricebookEntries(id) {
      try {
        this.loadingProducts = true
        const res = await SObjects.api.getObjects('PricebookEntry', 1, true, [
          ['EQUALS', 'Pricebook2Id', id],
        ])
        this.productReferenceOpts['PricebookEntryId'] = res.results
        this.productList = res.results
        if (res.next) {
          this.pricebookPage++
          this.showLoadMore = true
        } else {
          this.pricebookPage = 1
          this.showLoadMore = false
        }
        this.savedPricebookEntryId = id
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingProducts = false
        }, 1000)
      }
    },

    setUpdateValues(key, val, multi = null) {
      if (multi) {
        this.formData[key] = this.formData[key]
          ? this.formData[key] + ';' + val
          : val.split(/&#39;/g)[0]
      }
      if (val && !multi) {
        this.formData[key] = val
      }
      if (key === 'StageName') {
        this.stagesWithForms.includes(val)
          ? (this.stageGateField = val)
          : (this.stageGateField = null)
      }
    },
    setUpdateValidationValues(key, val) {
      if (val) {
        this.formData[key] = val
      }
    },
    setProductValues(key, val) {
      if (val) {
        this.updateProductData[key] = val
      }
    },
    async updateResource() {
      this.updateList.push(this.oppId)
      this.editOpModalOpen = false
      try {
        const res = await SObjects.api.updateResource({
          form_data: this.formData,
          stage_name: this.stageGateField ? this.stageGateField : null,
          integration_ids: [this.integrationId],
          resource_type: 'Opportunity',
          form_type: 'UPDATE',
          resource_id: this.oppId,
        })
        // .then(async () => {
        //   let updatedRes = await SObjects.api.getObjects('Opportunity')
        //   this.allOpps = updatedRes.results
        //   this.originalList = updatedRes.results
        // })
        this.updateList = []
        this.formData = {}
        this.$toast('Salesforce Update Successful', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        this.$toast(`${e.response.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    setForms() {
      this.countSets += 1
      if (this.countSets < 2) {
        for (let i = 0; i < this.oppFormCopy.length; i++) {
          if (this.oppFormCopy[i].dataType === 'Reference') {
            this.referenceOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].id
            this.currentRefList = this.referenceOpts
          }
        }

        for (let i = 0; i < this.updateContactForm.length; i++) {
          if (this.updateContactForm[i].dataType === 'Reference') {
            this.contactReferenceOpts[this.updateContactForm[i].apiName] =
              this.updateContactForm[i].id
          }
        }

        for (let i = 0; i < this.createContactForm.length; i++) {
          if (this.createContactForm[i].dataType === 'Reference') {
            this.contactCreateReferenceOpts[this.createContactForm[i].apiName] =
              this.createContactForm[i].id
          }
        }

        if (this.stageGateCopy) {
          for (let i = 0; i < this.stageGateCopy.length; i++) {
            if (this.stageGateCopy[i].dataType === 'Reference') {
              this.stageReferenceOpts[this.stageGateCopy[i].apiName] = this.stageGateCopy[i].id
            }
          }
        }

        for (let i = 0; i < this.updateAccountForm.length; i++) {
          if (this.updateAccountForm[i].dataType === 'Reference') {
            this.accountReferenceOpts[this.updateAccountForm[i].apiName] =
              this.updateAccountForm[i].id
          }
        }

        for (let i = 0; i < this.updateLeadForm.length; i++) {
          if (this.updateLeadForm[i].dataType === 'Reference') {
            this.LeadReferenceOpts[this.updateLeadForm[i].apiName] = this.updateLeadForm[i].id
          }
        }

        if (this.hasProducts) {
          for (let i = 0; i < this.createProductForm.length; i++) {
            if (this.createProductForm[i].dataType === 'Reference') {
              this.productRefCopy[this.createProductForm[i].apiName] = this.createProductForm[i]
              this.productReferenceOpts[this.createProductForm[i].apiName] =
                this.createProductForm[i].id
            }
          }
        }

        for (let i in this.referenceOpts) {
          this.referenceOpts[i] = this.getReferenceFieldList(i, this.referenceOpts[i], 'update')
        }
        if (this.stageReferenceOpts) {
          for (let i in this.stageReferenceOpts) {
            this.stageReferenceOpts[i] = this.getReferenceFieldList(
              i,
              this.stageReferenceOpts[i],
              'stage',
            )
          }
        }
        for (let i in this.accountReferenceOpts) {
          this.accountReferenceOpts[i] = this.getReferenceFieldList(
            i,
            this.accountReferenceOpts[i],
            'updateAccount',
          )
        }
        for (let i in this.contactReferenceOpts) {
          this.contactReferenceOpts[i] = this.getReferenceFieldList(
            i,
            this.contactReferenceOpts[i],
            'updateContact',
          )
        }

        for (let i in this.contactCreateReferenceOpts) {
          this.contactCreateReferenceOpts[i] = this.getReferenceFieldList(
            i,
            this.contactCreateReferenceOpts[i],
            'createContact',
          )
        }

        for (let i in this.leadReferenceOpts) {
          this.leadReferenceOpts[i] = this.getReferenceFieldList(
            i,
            this.leadReferenceOpts[i],
            'updateLead',
          )
        }

        if (this.hasProducts) {
          for (let i in this.productReferenceOpts) {
            this.productReferenceOpts[i] = this.getReferenceFieldList(
              i,
              this.productReferenceOpts[i],
              'createProduct',
            )
          }
        }
      }
    },
    filtersAndOppFields() {
      this.updateOppForm[0].fieldsRef.filter((field) => field.apiName === 'AccountId').length
        ? (this.accountSobjectId = this.updateOppForm[0].fieldsRef.filter(
            (field) => field.apiName === 'AccountId',
          )[0].id)
        : (this.accountSobjectId = null)
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()

        this.updateOppForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Opportunity',
        )
        let stageGateForms = res.filter(
          (obj) => obj.formType === 'STAGE_GATING' && obj.resource === 'Opportunity',
        )
        this.createContactForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'Contact',
        )[0].fieldsRef
        this.updateContactForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Contact',
        )[0].fieldsRef
        this.updateAccountForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Account',
        )[0].fieldsRef
        this.updateLeadForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Lead',
        )[0].fieldsRef
        this.createProductForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'OpportunityLineItem',
        )[0].fieldsRef

        let stages = stageGateForms.map((field) => field.stage)
        this.stagesWithForms = stages
        this.oppFormCopy = this.updateOppForm[0].fieldsRef
        this.resourceFields = this.updateOppForm[0].fieldsRef
        this.stageGateCopy = stageGateForms[0].fieldsRef

        for (const field of stageGateForms) {
          this.stageValidationFields[field.stage] = field.fieldsRef
        }

        // let stageArrayOfArrays = stageGateForms.map((field) => field.fieldsRef)
        // let allStageFields = [].concat.apply([], stageArrayOfArrays)
        // let dupeStagesRemoved = [
        //   ...new Map(allStageFields.map((v) => [v.referenceDisplayLabel, v])).values(),
        // ]

        // for (let i = 0; i < dupeStagesRemoved.length; i++) {
        //   if (
        //     dupeStagesRemoved[i].dataType === 'Picklist' ||
        //     dupeStagesRemoved[i].dataType === 'MultiPicklist'
        //   ) {
        //     this.stagePicklistQueryOpts[dupeStagesRemoved[i].apiName] = dupeStagesRemoved[i].apiName
        //   } else if (dupeStagesRemoved[i].dataType === 'Reference') {
        //     this.stagePicklistQueryOpts[dupeStagesRemoved[i].referenceDisplayLabel] =
        //       dupeStagesRemoved[i].referenceDisplayLabel
        //   }
        // }
      } catch (error) {
        // this.$toast('Error setting forms', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'error',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
        console.log(error)
      }
    },

    async getUsers() {
      try {
        const res = await SObjects.api.getObjects('User')
        this.allUsers = res.results.filter((user) => user.has_salesforce_integration)
        this.internalParticipants = this.allUsers
      } catch (e) {
        console.log(e)
      }
    },
    internalCustomLabel({ full_name, email }) {
      return `${full_name} (${email})`
    },
    externalCustomLabel({ secondary_data, email }) {
      return `${secondary_data.Name ? secondary_data.Name : 'N/A'} (${email ? email : 'N/A'})`
    },
    async addMoreContacts() {
      this.page += 1
      try {
        const res = await SObjects.api.getObjects('Contact', this.page)
        this.externalParticipants = [...res.results, ...this.externalParticipants]
        res.next ? (this.hasNext = true) : (this.hasNext = false)
      } catch (e) {
        console.log(e)
      }
    },
    async getExternalParticipants() {
      try {
        const res = await SObjects.api.getObjects('Contact')
        this.externalParticipants = res.results
        res.next ? (this.hasNext = true) : (this.hasNext = false)
      } catch (e) {
        this.$toast('Error gathering users', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getInitialAccounts() {
      this.loadingAccounts = true
      if (this.accountSobjectId) {
        try {
          const res = await SObjects.api.getSobjectPicklistValues({
            sobject_id: this.accountSobjectId,
          })
          this.allAccounts = res
        } catch (e) {
          this.$toast('Error gatherign accounts', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } finally {
          this.loadingAccounts = false
        }
      }
    },
    async getAccounts(val) {
      this.loadingAccounts = true
      try {
        const res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: this.accountSobjectId,
          value: val,
        })
        this.allAccounts = res
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingAccounts = false
      }
    },
    async getObjects() {
      this.loading = true
      try {
        const res = await SObjects.api.getObjectsForWorkflows(this.resourceType)
        this.allOpps = res.results
        this.originalList = res.results
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
    },

    allOpportunities() {
      this.$router.replace({ path: '/Pipelines' })
    },
    weekDay(input) {
      let newer = new Date(input)
      return this.days[newer.getDay()]
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    formatMostRecent(date2) {
      let today = new Date()
      let d = new Date(date2)
      let diff = today.getTime() - d.getTime()
      let days = diff / (1000 * 3600 * 24)
      return Math.floor(days)
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.container {
  min-height: 85vh;
  padding: 16px 0px;
  width: 40vw;
  outline: 1px solid $soft-gray;
  border-radius: 8px;
  background-color: white;
}
.back-button {
  color: $base-gray;
  background-color: transparent;
  display: flex;
  align-items: center;
  border: none;
  cursor: pointer;
  font-size: 16px;
  letter-spacing: 0.75px;

  img {
    margin-right: 8px;
  }
}
.transparent-container {
  min-height: 94vh;
  width: 48vw;
  background-color: transparent;
  position: relative;
}
#container {
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  background-color: $base-gray;
  opacity: 0.4;
  z-index: 10;
  border-radius: 8px;
}
#calendar {
  z-index: 11;
  color: white;
  position: absolute;
  bottom: 50%;
  left: 40%;
  font-size: 24px;
}
.alerts-header {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 72px;
  background-color: white;
  width: 96vw;
  border-bottom: 1px solid $soft-gray;
  padding: 8px 32px 0px 8px;
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
.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $light-gray-blue;
  letter-spacing: 0.76px !important;

  .bg-img {
    background-image: url(../assets/images/logo.png);
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    height: 72px;
    width: 120px;
    opacity: 0.5;
  }
  h3 {
    color: $base-gray;
    margin-bottom: 0;
    margin-top: 12px;
  }
  p {
    font-size: 13px;
  }
}

@mixin epic-sides() {
  position: relative;
  z-index: 1;

  &:before {
    position: absolute;
    content: '';
    display: block;
    top: 0;
    left: -5000px;
    height: 100%;
    width: 15000px;
    z-index: -1;
    @content;
  }
}

.input-container {
  position: relative;
  display: inline-block;
  margin: 30px 10px;
  @include epic-sides() {
    background: inherit;
  }
}

.greenBackground {
  background-color: $white-green;
  color: $dark-green;
}
.basic-slide {
  display: inline-block;
  width: 36vw;
  margin-left: -8px;
  padding: 9px 0 10px 16px;
  font-family: $base-font-family !important;
  font-weight: 400;
  color: $base-gray;
  background: $white;
  border: 1px solid $soft-gray !important;
  border: 0;
  border-radius: 3px;
  outline: 0;
  text-indent: 70px; // Arbitrary.
  transition: all 0.3s ease-in-out;

  &::-webkit-input-placeholder {
    color: #efefef;
    text-indent: 0;
    font-weight: 300;
  }

  + label {
    display: inline-block;
    position: absolute;
    top: 0;
    left: 0;
    padding: 9px 8px;
    font-size: 15px;
    text-align: center;
    margin-left: -8px;
    width: 80px;
    // text-shadow: 0 1px 0 rgba(19, 74, 70, 0.4);
    background: $white-green;
    color: $dark-green;
    transition: all 0.3s ease-in-out;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 2px;
  }
}
.basic-slide:focus,
.basic-slide:active {
  color: $base-gray;
  text-indent: 0;
  background: #fff;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;

  &::-webkit-input-placeholder {
    color: #aaa;
  }
  + label {
    transform: translateX(-100%);
  }
}

:disabled {
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  background-color: $soft-gray !important;
  cursor: text !important;
  color: $base-gray !important;
  transition: all 0.3s;
  font-size: 12px;
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 16px;
}

.dark-button {
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
  font-size: 12px;
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 16px;

  img {
    filter: invert(99%);
    margin-left: 8px;
  }
}
.light-green-bg {
  background-color: $white-green;
  color: $dark-green !important;
  border: 1px solid $dark-green !important;
}
.note-border {
  border: 1px solid $very-light-gray;
  border-radius: 6px;
  padding: 4px;
  margin: 0px 6px;
  font-size: 12px;
}
.border-bottom {
  border-bottom: 1.25px solid $soft-gray;
}
.sticky {
  position: sticky;
  background-color: white;
  width: 100%;
  left: 0;
  top: 0;
  padding: 0px 6px 8px -2px;
}
.rel {
  position: relative;
}
.adding-stage-gate {
  // border: 2px solid $coral;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  width: 42vw;
  // min-height: 30vh;
  &__header {
    font-size: 11px;
    color: white;
    padding: 0.5rem;
    width: 100%;
    // border-bottom: 1px solid $coral;
    // background-color: $coral;
    display: flex;
    align-items: center;
    flex-direction: row;
    img {
      height: 16px;
      filter: invert(90%);
    }
  }
  &__body {
    // padding: 0.25rem;
    font-size: 11px !important;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.2rem;
    overflow: auto;
    // height: 30vh;
    input {
      width: 10vw;
      height: 1.5rem !important;
    }
    .multiselect {
      width: 12vw;
      font-weight: 11px !important;
    }
    p {
      margin-left: 0.25rem;
    }
  }
  &__body::-webkit-scrollbar {
    width: 2px; /* Mostly for vertical scrollbars */
    height: 0px; /* Mostly for horizontal scrollbars */
  }
  &__body::-webkit-scrollbar-thumb {
    background-color: $coral;
    box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track {
    box-shadow: inset 2px 2px 4px 0 $soft-gray;
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track-piece {
    margin-top: 1rem;
  }
}

.hide {
  display: none;
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

.results {
  width: 100%;
  position: sticky;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 20;
  padding: 0 12px 16px 12px;
  h4 {
    span {
      background-color: $yellow;
      color: white;
      padding: 4px 6px;
      border-radius: 4px;
    }
  }
}

.results-title {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  margin-left: 4px;

  p {
    font-size: 16px;
    margin-left: 2px;
    color: $base-gray;
    span {
      // background-color: $white-green;
      color: $light-gray-blue;
      border-radius: 6px;
      padding: 2px;
      margin-left: 4px;
      font-size: 14px;
    }
  }
}

select {
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  background-color: #fafafa;
  height: 40px;
  width: 100%;
  background-image: url('../assets/images/dropdown.svg');
  background-size: 1rem;
  background-position: 100%;
  background-repeat: no-repeat;
  border: 1px solid #ccc;
  padding-left: 0.75rem;
  border-radius: 0;
}
.select-btn:hover {
  transform: scale(1.02);
  box-shadow: 1px 2px 3px $very-light-gray;
}
[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    // border-top: 1px solid #e8e8e8;
    width: 100%;
    height: 40px;
    padding: 0px;
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
input:focus {
  outline: none;
}

textarea:focus {
  outline: none;
}
input[type='date']:focus {
  outline: none;
  color: $dark-green;
}
input[type='date']::-webkit-datetime-edit-text,
input[type='date']::-webkit-datetime-edit-month-field,
input[type='date']::-webkit-datetime-edit-day-field,
input[type='date']::-webkit-datetime-edit-year-field {
  color: #888;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
}
input {
  padding: 7px;
}

.table-section {
  margin: 0;
  padding: 0;
  min-height: 78vh;
  max-height: 80vh;
  overflow: scroll;
  margin-top: 0.5rem;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  background-color: white;
}

.table {
  display: table;
  overflow: scroll;
  border-collapse: separate;
  border-spacing: 4px;
  width: 100vw;
}
.modal-container {
  background-color: $white;
  overflow: auto;
  min-width: 36vw;
  max-width: 36vw;
  min-height: 44vh;
  max-height: 80vh;
  align-items: center;
  border-radius: 0.5rem;
  border: 1px solid #e8e8e8;
}
.opp-modal-container {
  overflow: hidden;
  background-color: white;
  width: 44vw;
  align-items: center;
  border-radius: 0.6rem;
  padding: 1rem;
  border: 1px solid #e8e8e8;
}
.opp-modal {
  width: 42vw;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: 56vh;
  border-radius: 0.3rem;
  border-bottom: 3px solid $white;
  color: $base-gray;
  font-size: 16px;
  letter-spacing: 0.75px;
}
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
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
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-top: 8px;
  padding-bottom: 0;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.pipelines {
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-left: 80px;
  margin-top: 12vh;
}
.invert {
  filter: invert(85%);
}
.add-button:disabled {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $gray;
  cursor: text;
  color: white;
}
.add-button:disabled:hover {
  transform: none;
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
  img {
    margin-left: 0.5rem;
  }
}
.add-button__ {
  display: flex;
  align-items: center;
  border: none;
  padding: 8px 12px;
  font-size: 14px;
  border-radius: 6px;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}
.product-text {
  display: flex;
  align-items: center;
  color: $dark-green;
  border-radius: 4px;
  padding: 4px 6px;
  background-color: $white-green;
  font-size: 14px;
  letter-spacing: 0.5px;
  font-weight: bold;
  cursor: pointer;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
    height: 16px;
    margin-left: 4px;
  }
}
.select-btn1 {
  border: 0.7px solid $dark-green;
  padding: 0.45rem 1.25rem;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
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

.adding-product {
  border: 1px solid $dark-green;
  border-radius: 0.3rem;
  margin: 0.5rem 0rem;
  width: 40.25vw;
  min-height: 30vh;
  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    font-size: 14px;
    padding: 0.5rem;
    color: $white;
    width: 100%;
    border-bottom: 1px solid $dark-green;
    background-color: $dark-green;
    img {
      height: 1rem;
      margin-right: 0.5rem;
    }
  }
  &__body {
    padding: 0.25rem;
    font-size: 11px !important;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.2rem;
    overflow: auto;
    height: 30vh;
    input {
      width: 10vw;
      height: 1.5rem !important;
    }
    .multiselect {
      width: 12vw;
      font-weight: 11px !important;
    }
    p {
      margin-left: 0.25rem;
    }
    span {
      color: $coral;
    }
  }

  &__body::-webkit-scrollbar {
    width: 2px; /* Mostly for vertical scrollbars */
    height: 0px; /* Mostly for horizontal scrollbars */
  }
  &__body::-webkit-scrollbar-thumb {
    background-color: $dark-green;
    box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track {
    box-shadow: inset 2px 2px 4px 0 $soft-gray;
    border-radius: 0.3rem;
  }
  &__body::-webkit-scrollbar-track-piece {
    margin-top: 0.25rem;
  }
}

.fullInvert {
  filter: invert(99%);
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
  box-shadow: 1px 2px 2px $very-light-gray;
}
.add-button__:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.search-bar {
  height: 4.5vh;
  background-color: $off-white;
  border: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 5px;
  margin-right: 0.5rem;
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 40.25vw;
}
.zoom-input {
  border: 1px solid $soft-gray;
  border-radius: 6px;
  padding: 12px 8px;

  width: 40vw;
  font-family: inherit;
}
.zoom-input-ta {
  border: 1px solid $soft-gray;
  border-radius: 6px;
  height: 80px;
  padding: 8px;
  width: 40vw;
  font-family: inherit;
}
#user-input:focus {
  outline: 1px solid $dark-green;
}
.header {
  font-size: 18px;
  padding: 0;
  letter-spacing: 0.5px;
  margin-bottom: 0.2rem;
}
.list-section {
  z-index: 4;
  position: absolute;
  top: 20vh;
  left: 1rem;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 20vw;
  max-height: 70vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    position: sticky;
    top: 0;
    z-index: 5;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.25px;
    padding-left: 0.75rem;
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
.cancel {
  color: $dark-green;
  font-weight: bold;
  margin-left: 1rem;
  cursor: pointer;
}
.flex-end {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.flex-end-opp {
  width: 100%;
  padding: 0.25rem 1.5rem;
  height: 4rem;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}
textarea {
  resize: vertical;
}
a {
  text-decoration: none;
}
.green_button {
  color: white;
  background-color: $dark-green;
  max-height: 2rem;
  border-radius: 0.25rem;
  padding: 0.5rem 1.25rem;
  font-weight: bold;
  font-size: 12px;
  border: none;
  cursor: pointer;
}
.white_button {
  color: $dark-green;
  background-color: white;
  max-height: 2rem;
  border-radius: 0.25rem;
  padding: 0.5rem 1.25rem;
  font-weight: bold;
  font-size: 12px;
  border: 1px solid $soft-gray;
  cursor: pointer;
}

.sized {
  height: 3em;
  align-self: center;
}
.logo {
  height: 1.75rem;
  margin-left: 0.5rem;
  margin-right: 0.25rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.note-section {
  padding: 0.25rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 19px;
    font-weight: bolder;
    letter-spacing: 0.6px;
    color: $base-gray;
    padding: 0;
  }
  &__body {
    color: $base-gray;
    font-family: $base-font-family;
    word-wrap: break-word;
    white-space: pre-wrap;
    border-left: 2px solid $dark-green;
    padding-left: 8px;
    font-size: 14px;
  }
  &__date {
    color: $mid-gray;
    font-size: 12px;
    margin-top: -14px;
    margin-bottom: 8px;
    letter-spacing: 0.6px;
  }
}
.logged {
  border-left: 1px solid $dark-green;
}
.light-gray-placeholder::placeholder {
  color: #adadad;
}
.multiselect-span {
  display: flex;
  align-items: center;

  label {
    margin-right: 0.5rem;
  }
}
.multiselect-width {
  // max-width: 23vw;
  width: 23vw;
}
.label {
  margin-right: 0.5rem;
  margin-top: 8px;
}
.select-btn {
  border: 0.5px solid $dark-green;
  padding: 0.375rem 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  color: $dark-green;
  letter-spacing: 0.2px;
  margin-right: 0.5rem;
  transition: all 0.25s;

  img {
    // filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
    // height: 1rem !important;
    margin-left: 0.25rem;
  }
}
.select-btn:disabled {
  border: none;
  box-shadow: none;
  background-color: $soft-gray;
  cursor: text;
  color: $base-gray;
  opacity: 0.6;
}
.select-btn:disabled:hover {
  transform: none;
}
.form-field {
  background-color: white;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);

  color: $base-gray;
  border-radius: 6px;
  width: 50vw;
  // min-height: 25vh;
  letter-spacing: 0.75px;
  padding: 2px 16px 32px 16px;
  margin-top: 16px;
  &__head {
    padding: 8px 12px;
    background-color: white;
    margin-bottom: 0;
    // color: $very-light-gray;
  }
  &__body {
    padding: 6px 12px;
    background-color: white;
    font-size: 11px;
    color: $light-gray-blue;
    p {
      margin-top: 0;
    }
  }
}
.create-modal {
  width: 100%;
  // background-color: white;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  padding-bottom: 16px;
}
label {
  display: inline-block;
  padding: 6px;
  font-size: 14px;
  text-align: center;
  min-width: 80px;
  background-color: $white-green;
  color: $dark-green;
  font-weight: bold;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
.cloud {
  display: flex;
  align-items: center;
  justify-content: center;
  // color: #41b883;
  background-color: white;
  transition: all 0.25s;
  img {
    height: 1.05rem !important;
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
@keyframes tooltips-horz {
  to {
    opacity: 0.95;
    transform: translate(0%, 50%);
  }
}
.tooltip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2px 0px;
  z-index: 5;
}
.tooltip .tooltiptext {
  visibility: hidden;
  background-color: $base-gray;
  color: white;
  text-align: center;
  // border: 1px solid $soft-gray;
  letter-spacing: 0.5px;
  padding: 8px 4px;
  border-radius: 6px;
  font-size: 12px;

  /* Position the tooltip text */
  position: absolute;
  z-index: 1;
  width: 100px;
  top: 100%;
  left: 50%;
  margin-left: -50px;

  /* Fade in tooltip */
  opacity: 0;
  transition: opacity 0.3s;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
  animation: tooltips-horz 300ms ease-out forwards;
}
.close-template {
  position: absolute;
  bottom: 56px;
  right: 8px;
  z-index: 3;
  cursor: pointer;
  background-color: black;
  border-radius: 3px;
  opacity: 0.6;
  img {
    filter: invert(99%);
  }
}
.note-templates {
  margin-left: 2px;
  display: flex;
  justify-content: flex-end;
  font-size: 12px;
  padding: 12px 6px;
  margin-top: -34px;
  border: 1px solid $soft-gray;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  cursor: pointer;
  width: 40.25vw;
  margin-left: 10px;

  &__content {
    display: flex;
    flex-direction: row;
    align-items: center;
  }
  img {
    filter: invert(50%);
    height: 12px;
  }
  &__content:hover {
    opacity: 0.6;
  }
}

.note-templates2 {
  margin-left: 2px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  padding: 12px 6px;
  margin-top: -34px;
  margin-left: 10px;
  border: 1px solid $soft-gray;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  width: 40.25vw;
  height: 80px;
  overflow: scroll;

  &__content {
    border-radius: 4px;
    border: 0.5px solid $base-gray;
    color: $base-gray;
    padding: 8px 6px;
    margin-bottom: 8px;
    cursor: pointer;
  }
  &__content:hover {
    opacity: 0.6;
  }
}
.close-template {
  position: absolute;
  bottom: 56px;
  right: 8px;
  z-index: 3;
  cursor: pointer;
  background-color: black;
  border-radius: 3px;
  opacity: 0.6;
  img {
    filter: invert(99%);
  }
}
.divArea:focus {
  outline: none;
}
.divArea {
  -moz-appearance: textfield-multiline;
  -webkit-appearance: textarea;
  resize: both;
  height: 30px;
  width: 40.25vw;
  min-height: 20vh;
  margin-bottom: 4px;
  border: 1px solid #e8e8e8;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  overflow-y: scroll;
  font-family: inherit;
  font-style: inherit;
  font-size: 13px;
  padding: 12px;
}
.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.red-label {
  background-color: #fa646a;
  color: white;
  display: inline-block;
  padding: 6px;
  font-size: 14px;
  text-align: center;
  min-width: 80px;
  margin-top: 12px;
  margin-left: 2px;
  font-weight: bold;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
.img-button {
  background-color: transparent;
  padding: 4px 6px;
  border: none;
}
</style>